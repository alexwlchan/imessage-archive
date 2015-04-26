imessage-archive
================

## Useful information

*   Date values are stored as a number which means the number of seconds since 1 Jan 2001. The date stamps the tool produces are based on UTC.

    TODO: add timezone support.

*   I encountered an unusual row in the 'message' table of my database. Here's a selection of the fields:

    ```json
    {
        'is_from_me': 0,
        'text': None,
        'handle_id': 0,
        'ROWID': 63490,
        'date': '2015-01-03 10:28:05',
        'guid': u'E23C4C7A-BA37-4609-9FB1-E728EAC28CFD',
        'item_type': 2
    }
    ```

    This turned out to correspond to me renaming a group chat. It seems to be distinguished from a regular message by the `item_type` field, but I don't know exactly what this field means yet.

    These are the values I was able to guess from my database:

    *   0: regular message
    *   2: renaming a group chat
    *   5: audio message

    I couldn't find

## Open questions

* Are `guid` values consistent across devices?