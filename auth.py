# -*- coding: utf-8 -*-
import web
import re
import base64

def _verify(session, users, target, credit):
    """Check if cretitials are valid, redirect to the target if so"""
    allowed = [(u['nick'], u['pass']) for u in users]
    if credit in allowed:
        index = allowed.index(credit)
        # uid will be added as fields to current session
        session.uid = users[index]['uid']
        raise web.seeother(target)

def login_prompt(session, users, target, message):
    """Force the browser to show login prompt and try to authorize the user"""
    auth = web.ctx.env.get('HTTP_AUTHORIZATION')
    if auth is not None:
        auth = re.sub('^Basic ','',auth)
        username,password = base64.decodestring(auth).split(':')
        username = username.lower()
        credit = (username,password)
        _verify(session, users, target, credit)

    web.header('WWW-Authenticate','Basic realm="' + message + '"')
    web.ctx.status = '401 Unauthorized'
    
def login_direct(session, users, target, username, password):
    """Try to authorize the user with given username & password, without showing prompt"""
    credit = (username.lower(), password)
    _verify(session, users, target, credit)

def protected(session, login_page):
    """Decorator - checkes creditials before executing decorated method"""
    def wrap(f):
        def wrap_(*args, **kwargs):
            # check if any user (uid>0) loged in
            if not session.get('uid', 0):
                raise web.seeother(login_page)

            return f(*args, **kwargs)
        return wrap_
    return wrap
