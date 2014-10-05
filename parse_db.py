#!/usr/bin/env python

import sqlite3
conn = sqlite3.connect('sms.db')

# Construct a dictionary of addresses. Here an "address" is a phone number or
# email address, used to identify different recipients.

addresses = dict()
for row in conn.execute('SELECT * from handle'):
    addresses[row[0]] = dict({
        "address": row[1],
        "country": row[2],
        "service": row[3]
    })

