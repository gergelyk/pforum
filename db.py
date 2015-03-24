# -*- coding: utf-8 -*-
import web
import re

import translations as tr
import utils

webdb = web.database(dbn='sqlite', db='forum.db')

def get_posts(uid, tid):
    """Gives list of details necessary to render posts in selected thread
       uid - uid of the user currently logged in
    """
    result = []
    posts = webdb.select('POSTS', where='tid = ' + str(tid), order='pid')
    history_pid = get_history_pid(uid, tid)
    
    for post in posts:
        user = get_user(post['uid'])
        unread = post['pid'] > history_pid

        result.append({'msg': utils.markdown_to_html(post['msg']),
                       'date': utils.ts_to_date(post['ts']),
                       'nick': user['nick'],
                       'name': user['name'],
                       'font_weight': ['normal', 'bold'][unread],
                       'color': utils.hue_to_color(get_user(post['uid'])['hue'])})
    return result
    
def is_thread(tid):
    """Checks if thread of given tid exists in database"""
    threads = [t for t in webdb.select('THREADS', where='tid = ' + str(tid), limit=1)]
    return bool(threads)
    
def add_post(uid, tid, msg):
    """Add post specified by msg to the thread specified by tid
       uid - uid of the user currently logged in
    """
    ts = utils.now_to_ts()
    try:
        webdb.insert('POSTS', uid=uid, tid=tid, msg=msg, ts=ts)
        succ = True
    except: # e.g. database file can be read-only
        succ = False
        
    return succ
    
def get_threads(uid):
    """Gives list of details necessary to render headers of all the
       threads accessible to the user given by uid
    """
    result = []
    threads = webdb.select('THREADS', order='tid')
    
    # filter out threads which the user doesn't have access to'
    threads = [thread for thread in threads if str(uid) in thread['uids'].split(',') or not thread['uids']]
        
    for thread in threads:
        # the last post in this thread
        last_post = [lp for lp in webdb.select('POSTS', where='tid = ' + str(thread['tid']), order='pid DESC', limit=1)]
        if (last_post):
            last_post = last_post[0]
            last_user = webdb.select('USERS', where='uid = ' + str(last_post['uid']))[0]
        else: # no posts in this thread
            last_post = {'ts': None, 'msg': '', 'pid': 0}
            last_user = {'name': '', 'hue': None}

        unread = last_post['pid'] > get_history_pid(uid, thread['tid'])
        
        result.append({'tid': utils.enc_tid(thread['tid']),
                       'title': thread['title'],
                       'font_weight': ['normal', 'bold'][unread],
                       'is_public': not bool(thread['uids']),
                       'last_date': utils.ts_to_date(last_post['ts']),
                       'last_name': last_user['name'],
                       'last_color': utils.hue_to_color(last_user['hue']),
                       'last_msg': utils.shorten_msg(last_post['msg'])})
    return result

def get_thread_title(tid):
    """Returns title of the thread given by tid"""
    return webdb.select('THREADS', where='tid = ' + str(tid))[0]['title']

def get_thread_users(lang, tid):
    """Returns human-readable text which say who can access thread given by tid"""
    uids_str = webdb.select('THREADS', where='tid = ' + str(tid))[0]['uids']
    if uids_str:
        uids = [int(uid_str) for uid_str in uids_str.split(',')]
        where = ' or '.join(['uid = ' + str(uid) for uid in uids])
        nicks = [user['nick'] for user in webdb.select('USERS', what='nick', where=where)]
        nicks.sort()
        nicks = ', '.join(nicks)
    else: # empty list means everyone (including these who will register in the future)
        uids = []
        nicks = tr.text[lang]['everyone']

    return (nicks, uids)

def add_thread(uid, title, nicks):
    """Adds a thread
       uid - uid of the author
       title - title of the thread
       nicks - text which specifies who can access the thread
    """
    succ = True
    
    if nicks == ['']:
        # everyone currently registered
        uids = [u['uid'] for u in webdb.select('USERS', order='uid')]
    elif nicks == ['*']:
        # everyone who is currently registered or will be registered in the future
        uids = [];
    else:
        try:
            uids = [get_uid(nick) for nick in nicks if nick]
            uids.append(uid)
        except IndexError: # given nick doesn't correspond to any user
            succ = False

    if succ:
        uids = list(set(uids)) # unique
        uids_str = str(uids)[1:-1].replace(' ','')
        try:
            webdb.insert('THREADS', title=title, uids=uids_str, uid=uid)
        except: # e.g. database file can be read-only
            succ = False
    
    return succ
    
def del_thread(uid, tid):
    """Removes requestor from the thread and removes the thread if there are no more users left
       uid - requestor
       tid - thread to be removed
    """

    thread = webdb.select('THREADS', where='tid = ' + str(tid))

    # if user manages to click for the second time before webpage is refreshed thread may be already removed
    if not thread:
        return

    uids_str = webdb.select('THREADS', where='tid = ' + str(tid))[0]['uids']
    # public threads cannot be removed
    if uids_str:
        uids = [int(uid_str) for uid_str in uids_str.split(',')]

        # if user manages to click for the second time before webpage is refreshed he can be already
        # removed from the list of users
        if uid not in uids:
            return

        uids.remove(uid)
        where='tid = ' + str(tid)
        try:
            if uids:
                uids_str = str(uids)[1:-1].replace(' ','')
                # update list of users
                webdb.update('THREADS', where=where, uids=uids_str)
            else:
                # remove whole thread
                webdb.delete('THREADS', where=where)
        except: # e.g. database file can be read-only
            pass

def get_user(uid):
    """Returns details of the user specified by uid"""
    return webdb.select('USERS', where='uid = ' + str(uid), limit=1)[0]
    
def set_user(uid, **kwargs):
    """Updates details of the user specified by uid"""
    where = 'uid = ' + str(uid)
    try:    
        webdb.update('USERS', where=where, **kwargs)
    except: # e.g. database file can be read-only
        pass

def get_users():
    """Returns list of all users in database"""
    return [u for u in webdb.select('USERS', order='uid')]

def get_user_list():
    """Returns list of all users prepared for being displayed in html table"""
    users = [u for u in webdb.select('USERS', order='uid')]
    indices = range(1, len(users) + 1)
    user_list = [{'index': index,
                  'nick': u['nick'],
                  'name': u['name'],
                  'color': utils.hue_to_color(u['hue']),
                  } for (u, index) in zip(users, indices)]

    return user_list
    
def get_uid(nick):
    """Returns uid of the user with given nick"""
    return webdb.select('USERS', where='nick = "' + nick + '"', limit=1)[0]['uid']
    
def get_lang(uid):
    """Returns lang of the user with given uid"""
    return webdb.select('USERS', where='uid = "' + str(uid) + '"', limit=1)[0]['lang']
    
def mark_read(uid, tid):
    """Appends an entry to the history which say what was the last post
       in the thread specified by tid, when the user specified by uid read
       the thread for the last time
    """
    # last post in the thread
    last_post = [p for p in webdb.select('POSTS', where='tid = ' + str(tid), order='pid DESC', limit=1)]
    if last_post:
        pid = last_post[0]['pid']
        # check if an entry for this uid & tid already exists
        where = 'uid = ' + str(uid) + ' and tid = ' + str(tid)
        history = [p for p in webdb.select('HISTORY', where=where)]
        try:    
            if history:
                # no need to update history if there are no new posts
                if history[0]['pid'] < pid:
                    webdb.update('HISTORY', where=where, pid=pid)
            else:
                # there is no entry for this uid & tid yet
                webdb.insert('HISTORY', uid=uid, tid=tid, pid=pid)
        except: # e.g. database file can be read-only
            pass

def get_history_pid(uid, tid):
    """Returns pid of the last post in the thread specified by tid,
       when the user specified by uid read the thread for the last time
    """
    where = 'uid = ' + str(uid) + ' and tid = ' + str(tid)
    history = [p for p in webdb.select('HISTORY', where=where)]

    if history:
        history_pid = history[0]['pid']
    else:
        # there is no entry for this uid & tid yet
        history_pid = 0

    return history_pid

