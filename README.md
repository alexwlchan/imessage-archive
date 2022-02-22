imessage-archive
================

**Note, 26 Apr 2015:** I rather let this languish, didn't I?

Since I'm stuck in bed for the next few weeks, I'm going to dust this off and see if I can't get it working properly. (Also, my Mac just erased two years of messages, so the merging stuff would be *really* nice.)

Plus, I have a slightly less crappy understanding of SQL now, so the code will be less awful.

New work is going on in the apr15 branch, but I'll eventually merge back to master when I have something working. :-)

---

Scripts for parsing the iOS message database.

Messages.app on OS X and iOS both store their messages databases in SQL (`chat.db` and `sms.db`, respectively). This is a handful of scripts which extract the messages from the SQL into human-readable JSON, and try to organise the attachments in a sensible way.

It requires two files from: `filesequence.py` and `confirmation.py`.
[Note: these files were originally kept in an external repository.
I don’t know how closely they resemble the versions I was using when I originally wrote the iMessage parsing code, but they should give you the general gist.]

So far the attachments functionality only really works with the OS X database, but I will add iOS support (eventually).

Planned improvements:

* Support for attachment organising from the iOS database
* Merging/incremental updates rather than creating a new export from scratch
