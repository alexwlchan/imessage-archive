imessage-archive
================

Scripts for parsing the iOS message database.

Messages.app on OS X and iOS both store their messages databases in SQL (`chat.db` and `sms.db`, respectively). This is a handful of scripts which extract the messages from the SQL into human-readable JSON, and try to organise the attachments in a sensible way.

It requires two files from [my drabbles repo][drabble]: `filesequence.py` and `confirmation.py`. So far the attachments functionality only really works with the OS X database, but I will add iOS support (eventually).

Planned improvements:

* Support for attachment organising from the iOS database
* Merging/incremental updates rather than creating a new export from scratch

[drabble]: https://github.com/alexwlchan/drabbles