# -*- coding: utf-8 -*-
import web

# required for 'session_store' to work
web.config.debug = False

# encryption of tid, it can be disabled for debugging purposes
# it is implemented so that the user has no clue how many threads are
# potentially hidden in front of him
crypt_enabled = True

# S and V components of user color expressed in HSV format
user_color_saturation = 0.4
user_color_value = 1.0

# Date format to be tisplayed for each post
date_format = '%Y-%m-%d %H:%M'

# Max length of the message displayed in the table of threads
short_msg_max_len = 80

# Markdown extensions
# For more info see: https://pythonhosted.org/Markdown/extensions/
md_extensions = ['tables', 'nl2br']


