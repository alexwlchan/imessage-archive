#!/usr/bin/env python
"""
Functions for taking an iMessage database (usually sms.db or chat.db), and
extracting useful information into Python objects.
"""

import datetime
import json

def __get_table_from_sql_db(conn, table):
    return conn.execute('SELECT * from %s' % table)
    
def parse_imessage_date(date):
    """The 'date' fields count seconds from the first second of 1 Jan 2001, the
    first time which can be represented with NSDate. We turn this into a more
    human-friendly string.
    """
    startdate = datetime.datetime(2001, 01, 01, 00, 00, 00)
    enddate   = startdate + datetime.timedelta(seconds=date)
    return enddate.strftime("%Y-%m-%d %X")

def __get_handle_table(conn):
    """Individual recipients are stored in the 'handle' table. We pick out
    the relevant information and store it in a dictionary."""
    handles = dict()
    for row in __get_table_from_sql_db(conn, 'handle'):
        handles[row[0]] = row[1]
    return handles

def __get_message_table(conn):
    """Individual messages are stored in the 'message' table. We extract the 
    information from this table. This isn't everything: we also need information
    about attachments, in a different table.
    """
    messages = dict()
    for row in __get_table_from_sql_db(conn, 'message'):
        messages[row[0]] = dict({
            "text":        row[2],
            "address_id":  row[5],
            "subject":     row[6],
            "country":     row[7],
            "service":     row[11],
            "date":        parse_imessage_date(row[15]),
            "is_from_me":  bool(row[21]),
            "attachments": list()
        })
    return messages

def __get_attachment_table(conn):
    """Individual attachments are stored in the 'attachment' table. We extract
    the relevant information, but we need the join table to associate these
    attachments to their messages.
    """
    attachments = dict()
    for row in __get_table_from_sql_db(conn, 'attachment'):
        attachments[row[0]] = dict({
            "date":          parse_imessage_date(row[2]),
            "filename":      row[4],
            "mime_type":     row[6],
            "is_outgoing":   bool(row[8]),
            "transfer_name": row[10]
        })
    return attachments

def get_messages(conn):
    """We use the message/attachment join table to get a complete list of 
    messages with attachments.
    """
    messages    = __get_message_table(conn)
    attachments = __get_attachment_table(conn)
    for row in __get_table_from_sql_db(conn, 'message_attachment_join'):
        msg_id    = row[0]
        attach_id = row[1]
        messages[msg_id]["attachments"].append(attachments.pop(attach_id, {}))
    return messages

def __get_chat_table(conn):
    """The 'chat' table contains the different thread. Each thread has two
    attributes: participants and messages.
    """
    chats   = dict()
    handles = __get_handle_table(conn)
    
    # The 'chat' table is mostly filler; it contains no information about who
    # is taking part in the conversation. Everything except the SQL id is
    # discarded immediately.
    for row in __get_table_from_sql_db(conn, 'chat'):
        chats[row[0]] = dict({
            "handles":  list(),
            "messages": list(),
        })

    # The 'chat_handle_join' table contains the interesting bits: who is taking
    # part in which conversation.
    for row in __get_table_from_sql_db(conn, 'chat_handle_join'):
        chat_id   = row[0]
        handle_id = row[1]
        chats[chat_id]["handles"].append(handles[handle_id])
    
    return chats

def get_messages_by_chat(conn):
    """The 'message' table isn't particularly useful, because it doesn't group
    message into chats. This function returns a dict of messages, grouped by
    individual chat/thread.
    """
    messages = get_messages(conn)
    chats    = __get_chat_table(conn)
    
    for row in __get_table_from_sql_db(conn, 'chat_message_join'):
        chat_id = row[0]
        msg_id  = row[1]
        chats[chat_id]["messages"].append(messages.pop(msg_id, {}))
    
    return chats