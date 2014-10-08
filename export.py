#!/usr/bin/env python

import os
import shutil
import sqlite3
import json

from imessage import SQLReader, HTMLRender

from jinja2 import Environment, PackageLoader

# conn1 = sqlite3.connect('sms.db')
# conn2 = sqlite3.connect('chat.db')
#
# chat1 = SQLReader.get_messages_by_chat(conn1)
# SQLReader.export_messages_to_json(chat1, 'chats')
#
env = Environment(loader=PackageLoader('imessage', 'templates'))

template = env.get_template('thread.html')

shutil.rmtree(os.path.join('output', 'static'))
shutil.copytree(os.path.join('imessage', 'static'), os.path.join('output', 'static'))

if not os.path.isdir('output'):
    os.mkdir('output')

with open(os.path.join('chats', 'chat_16.json'), 'r') as infile:
    chat = json.loads(infile.read())
    handle_str = HTMLRender.handle_str(chat["handles"])
    messages   = chat["messages"]
    
    print len(messages)
    for idx, msg in enumerate(messages):
        # print idx, msg
        if idx == 0:
            messages[0] = HTMLRender.process_message(None, messages[0], messages[1])
        elif idx == len(messages) - 1:
            messages[idx] = HTMLRender.process_message(messages[idx-1], messages[idx], None)
        else:
            messages[idx] = HTMLRender.process_message(messages[idx-1], messages[idx], messages[idx+1])
    
    # messages = map(, chat["messages"])

with open(os.path.join('output', 'mythread.html'), 'w') as outfile:
    outfile.write(template.render(handle_str = handle_str,
                                  messages   = messages).encode('utf8'))