# -*- coding: utf-8 -*-
import colorsys
from datetime import datetime
from Crypto.Cipher import AES
from markdown import Markdown
from HTMLParser import HTMLParser

import config

crypt_iv = '625a5a63f8e96553e8885913ddd214d1'
crypt_key = 'b77d676b624a48d3464e9c3cb2af85c0'

_md_ex = ['markdown.extensions.' + ex for ex in config.md_extensions]
md = Markdown(extensions=_md_ex)

def markdown_to_html(text):
    """Converts markdown syntax to HTML syntax"""
    return md.convert(text)

def hex_to_str(h):
    """Converts hex representation of chars to string which consists of them
       e.g.
       >>> hex_to_str('414243')
       'ABC'
    """
    return ''.join([chr(int(''.join(x), 16)) for x in zip(h[::2], h[1::2])])
    
def str_to_hex(b):
    """Converts string to hex representation of chars which the string consists of
       e.g.
       >>> str_to_hex('ABC')
       '414243'
    """
    return ''.join(['%02x' % ord(x) for x in b])

def enc_tid(num):
    """Encrypt tid (or any other number, up to 16 digits in decimal representation)
       e.g.
       >>> enc_tid(123)
       'c364803f98ba351669b33aa4f6ce41a9'
    """
    if config.crypt_enabled:
        aes = AES.new(hex_to_str(crypt_key), AES.MODE_CBC, hex_to_str(crypt_iv))
        enc = str_to_hex(aes.encrypt('%016d' % num))
        enc = ('0'*32 + enc)[-32:] # prepend '0' chars if string is shorter than 32 chars
        return enc
    else:
        # for debugging purposes
        return str(num)

def dec_tid(msg):
    """Decrypt tid (or any other number, up to 16 digits in decimal representation)
       e.g.
       >>> dec_tid('c364803f98ba351669b33aa4f6ce41a9')
       123
    """
    if config.crypt_enabled:
        aes = AES.new(hex_to_str(crypt_key), AES.MODE_CBC, hex_to_str(crypt_iv))
        if len(msg) != 32:
            # we expect exactly 32 chars, otherwise sth is wrong
            # (e.g. sb is trying to guess URL)
            return 0
        else:
            dmsg = aes.decrypt(hex_to_str(msg))
            try:
                return int(dmsg)
            except ValueError:
                # msg is 32 chars, but still sth is wrong
                # (e.g. sb is trying to guess URL)
                return 0;
    else:
        # for debugging purposes
        return int(msg)

def hue_to_color(hue):
    """Converts HSV to RGB, H can be given, S and V are predefined in config
       so that the users keep the same style
    """
    if hue == None:
        color = '' # default color (defined in CSS, most probably gray)
    else:
        rgb = colorsys.hsv_to_rgb(hue,
                                  config.user_color_saturation,
                                  config.user_color_value)
        # (r,g,b) -> RRGGBB
        # r,g,b - 0 to 1 each
        # R,G,B - 0 to F each
        color = ''.join([('0' + hex(int(round(255*c)))[2:])[-2:] for c in rgb])

    return color
    
def ts_to_date(ts):
    """Timestamp to human-readable date"""
    if ts == None:
        date = ''
    else:
        dt = datetime.fromtimestamp(float(ts))
        date = dt.strftime(config.date_format)

    return date

def now_to_ts():
    """Current timestamp"""
    ts =  datetime.now() - datetime.fromtimestamp(0)
    return int(ts.total_seconds())

class _HTMLParser(HTMLParser):
    """Helper class to be used by html_to_text function"""
    def handle_data(self, data):
        self.text.append(data)

def html_to_text(html):
    """Decodes HTML to human-readable text"""
    parser = _HTMLParser()
    parser.text = []
    parser.feed(html)
    return ' '.join(parser.text)

def shorten_msg(msg):
    """Turns multiline HTML content into a short, human-readable text representation"""
    short = markdown_to_html(msg)
    short = html_to_text(short)

    if len(short) > config.short_msg_max_len:
        short = short[:config.short_msg_max_len-3] + '...'

    return short
