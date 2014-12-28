#!/usr/bin/python
# -*- encoding: utf8 -*-
"""imessage_export.py - this script takes the chat.db or sms.db SQL database
used to store messages on OS X or iOS and spits out a set of JSON files, one
for each thread.

The script is fairly rudimentary, and doesn't do anything to catch or
compensate for errors in the SQL, or malicious input. There also isn't any
support for merging and/or incremental updates (yet).

Use at your own risk, and back up your iMessage database before proceeding.

This depends on the following modules from my drabbles/ repo:
* confirmation.py
* filesequence.py
"""

import argparse
import datetime
from collections import namedtuple
import json
import os
import re
import sqlite3
import sys
from unidecode import unidecode

import confirmation
import filesequence

#------------------------------------------------------------------------------
# Utility functions
#------------------------------------------------------------------------------
def slugify(ustr):
    """Convert Unicode string into an ASCII slug.

    Written by Dr. Drang: http://www.leancrew.com/all-this/2014/10/asciifying/
    """
    ustr = re.sub(u'[–—/:;,.]', '-', ustr)   # replace separating punctuation
    astr = unidecode(ustr).lower()           # best ASCII subs, lowercase
    astr = re.sub(r'[^a-z0-9 -]', '', astr)  # delete any other characters
    astr = astr.replace(' ', '-')            # spaces to hyphens
    astr = re.sub(r'-+', '-', astr)          # condense repeated hyphens
    return astr

def imessage_date_str(date_int):
    """Dates in iMessage are stored as an integer, which counts the number of
    seconds since 1 Jan 2001. This function takes an int as input, and returns
    an ISO 8601 formatted date string.
    """
    start = datetime.datetime(2001, 1, 1)
    diff = datetime.timedelta(seconds=int(date_int))
    return str(start + diff)

def cp_attachment(src, dst):
    """Copy an attachment to the attachments/ directory. If a file by that name
    already exists, use the MD5 checksum to see if they're the same, and if
    not, go to the next sequential filename.
    """
    if src[0] == '~':
        src = os.environ['HOME'] + src[1:]
    safe_dst = filesequence.safe_file_copy(src, dst)
    return safe_dst

#------------------------------------------------------------------------------
# Set up namedtuple instances
#------------------------------------------------------------------------------
Attachment = namedtuple('Attachment', ['guid', 'filename'])
Message = namedtuple('Message', ['guid', 'text', 'handle_id', 'subject', 'date', 'is_from_me', 'attachments'])

def message_dict(message):
    """Convert a Message instance to a dict which can be written to JSON."""
    msg_dict = dict()

    msg_dict['guid'] = message.guid
    msg_dict['text'] = message.text
    msg_dict['handle_id'] = message.handle_id
    msg_dict['date'] = message.date
    msg_dict['is_from_me'] = bool(message.is_from_me)

    if message.subject is not None:
        msg_dict['subject'] = message.subject

    if message.attachments:
        msg_dict['attachments'] = message.attachments

    return msg_dict

#------------------------------------------------------------------------------
# Functions for reading the SQL database
#------------------------------------------------------------------------------
def handles(cursor):
    """Returns a dict of handles that form (ROWID, id) pairs."""
    sql_handles = cursor.execute("SELECT ROWID, id FROM handle").fetchall()
    all_handles = dict()

    for handle in sql_handles:
        rowid, contact_id = handle
        all_handles[rowid] = contact_id

    return all_handles

def chats(cursor):
    """Returns a dict of chats that form (ROWID, guid) pairs."""
    sql_chats = cursor.execute("SELECT ROWID, guid FROM chat").fetchall()
    all_chats = dict()

    for chat in sql_chats:
        rowid, guid = chat
        all_chats[rowid] = guid

    return all_chats

def attachments(cursor):
    """Returns a dict of attachments, in which the keys are the ROWIDs and the
    values are Attachment() namedtuple instances.
    """
    sql_attachments = cursor.execute("SELECT ROWID, guid, filename "
                                     "from attachment").fetchall()
    all_attachments = dict()

    for attachment in sql_attachments:
        ROWID, guid, filename = attachment
        new_attach = Attachment(guid, filename)
        all_attachments[ROWID] = new_attach

    return all_attachments

def messages(cursor):
    """Returns a dict of messages, in which the keys are the ROWIDs and the
    values are Message() instances.
    """
    sql_messages = cursor.execute("SELECT ROWID, guid, text, handle_id, "
                                  "subject, date, is_from_me from "
                                  "message").fetchall()
    all_messages = dict()

    for message in sql_messages:
        ROWID, args = message[0], message[1:]
        new_message = Message(*args, attachments=[])
        all_messages[ROWID] = new_message

    return all_messages

def join_table(cursor, row1, row2):
    """Returns a list of joins, in which the values are a dict of IDs from each
    table. row1 and row2 must be specified in the order the table is named.
    """
    sql_joins = cursor.execute("SELECT * from %s_%s_join" % (row1, row2))
    all_joins = list()

    for join in sql_joins:
        all_joins.append(join)

    return all_joins

#------------------------------------------------------------------------------
# Join everything together: given a list of messages, chats, handles and
# attachments, create a collection of human-readable threads
#------------------------------------------------------------------------------
def unify_message_threads(sql_path, output_dir):
    conn = sqlite3.connect(sql_path)
    cursor = conn.cursor()

    all_messages = messages(cursor)
    all_attachments = attachments(cursor)

    attachment_dir = os.path.join(output_dir, 'attachments')
    thread_dir = os.path.join(output_dir, 'threads')

    for output_dir in [attachment_dir, thread_dir]:
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

    # Go through the message_attachment_join table, and append each attachment
    # to the associated message.
    join_msg_attach = join_table(cursor, 'message', 'attachment')

    for join in join_msg_attach:
        msg_id, attach_id = join
        msg = all_messages[msg_id]
        new_attachment = all_attachments[attach_id]

        # Update the list of attachments
        updated_attachments = msg.attachments
        updated_attachments.append(new_attachment)
        msg = msg._replace(attachments=updated_attachments)

        all_messages[msg_id] = msg

    # Replace the handle_id in each Message instance with the actual handle,
    # and then discard the all_handles list: we won't use it again
    all_handles = handles(cursor)
    group_msgs_rowids = list()
    for ROWID in all_messages:
        msg = all_messages[ROWID]

        # For reasons unknown, anything in a group message has handle_id 0. I
        # haven't worked out how to work out who sent a particular message, so
        # for now I'm just dropping anything with handle_id 0.
        try:
            true_handle = all_handles[msg.handle_id]
        except KeyError:
            group_msgs_rowids.append(ROWID)
            continue

        msg = msg._replace(handle_id=true_handle)

        # While we're going through the messages, let's also replace the date
        # string with something more human friendly
        msg = msg._replace(date=imessage_date_str(msg.date))

        # And we'll copy all the attachments into an 'attachments' folder to
        # make them easier to find
        new_attachments = []
        for attachment in msg.attachments:
            dst = cp_attachment(attachment.filename, attachment_dir)
            new_attachments.append(os.path.basename(dst))
        msg = msg._replace(attachments=new_attachments)

        all_messages[ROWID] = msg

    # Clean up all the group messages
    for ROWID in group_msgs_rowids:
        del all_messages[ROWID]

    # Create a list of threads, go through and assign messages to that thread
    all_threads = dict()
    all_chats = chats(cursor)
    join_chat_message = join_table(cursor, 'chat', 'message')

    for join in join_chat_message:
        chat_id, msg_id = join

        chat_guid = all_chats[chat_id]

        # Skip group messages
        try:
            msg = message_dict(all_messages[msg_id])
        except KeyError:
            continue

        chat_messages = all_threads.get(chat_guid, [])
        chat_messages.append(msg)

        all_threads[chat_guid] = chat_messages

    return all_threads

#------------------------------------------------------------------------------
# Mainline program flow
#------------------------------------------------------------------------------
def main():
    """Main program flow. This function gets input from the user about where
    the SQL database is and where to save the files, checks that it's not about
    to overwrite any existing exports
    """

    #--------------------------------------------------------------------------
    # Set up the options for argparse
    #--------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="A script for exporting threads and attachments from the "
                    "iMessage database to JSON.",
        epilog="You should back up your iMessage database BEFORE using this "
               "script. I am not responsible for any damage caused to your "
               "database by this script."
    )
    parser.add_argument('-i', '--input', dest='sql_path',
                        help="path to the chat.db or sms.db SQL file from "
                             "the iMessage database")
    parser.add_argument('-o', '--output', dest='output_dir',
                        help="path to the output directory to write the "
                             "thread and attachment data")

    args = parser.parse_args()

    #--------------------------------------------------------------------------
    # Validate user input: check that we have both an input and output file,
    # that the input file exists, and that we don't already have export in
    # the output directory.
    #--------------------------------------------------------------------------
    if (args.sql_path is None) and (args.output_dir is None):
        print("Use the -h or --help flag for a help message.")
        sys.exit(1)

    if (args.sql_path is None) or (args.output_dir is None):
        print("Please supply both --input and --output arguments. Use the -h "
              "or --help flag for a help message.")
        sys.exit(1)

    if not os.path.exists(args.sql_path):
        print("The database file %s does not exist." % args.sql_path)
        sys.exit(1)

    attach_dir = os.path.join(args.output_dir, 'attachments')
    thread_dir = os.path.join(args.output_dir, 'threads')

    if os.path.isdir(attach_dir) or os.path.isdir(thread_dir):
        result = confirmation.twostep_confirm(
            "There is already an export of the iMessage database in the "
            "directory %s. Part of this export may be overwritten if you "
            "proceed with the script." % args.output_dir,
            'continue'
        )
        if not result:
            print("Okay, stopping. Nothing has been changed.")
            sys.exit(1)

    #--------------------------------------------------------------------------
    # Assuming we've validated the output, go ahead and export the database.
    #--------------------------------------------------------------------------
    unified_threads = unify_message_threads(args.sql_path, args.output_dir)
    for thread_guid, messages in unified_threads.iteritems():
        output_dict = dict({
            'guid': thread_guid,
            'messages': messages
        })
        outfile = os.path.join(thread_dir,
                               "thread_%s.json" % slugify(thread_guid))

        with open(outfile, 'w') as ff:
            json.dump(output_dict, ff, sort_keys=True, indent=2)

if __name__ == '__main__':
    main()
