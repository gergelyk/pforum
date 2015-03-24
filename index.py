# -*- coding: utf-8 -*-
import web
import tempfile
import re
import os

import translations as tr
import auth
import utils
import form
import config
import db

urls = (
    '(.+)/', 'Slash',
    '/', 'LoginPrompt',
    '/login','Login',
    '/login/(.+)','Login',
    '/forum', 'Forum',
    '/thread/([a-fA-F0-9]+)', 'Thread',
    '/preview/([a-fA-F0-9]+)', 'Thread',
    '/admin', 'Admin'
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
app = web.application(urls, globals())
session_store = tempfile.mkdtemp()
session = web.session.Session(app, web.session.DiskStore(session_store))
render = web.template.render('html', base='base')
render_empty = web.template.render('html')

class Slash:
    """Truncates slash if the user put it at the end of URL"""

    def GET(self, url):
        raise web.seeother(url)
        
class LoginPrompt:
    """Shows browser-specific login prompt"""
    
    def GET(self):
        users = db.get_users()
        auth.login_prompt(session, users, '/forum#top', 'Please log in.')
        return 'Authorization failed'

class Login:
    """Shows html-based login page"""
    
    def GET(self, nick=''):
        html = render_empty.login(nick.lower())
        return html

    def POST(self, nick=''):
        data = web.input()
        users = db.get_users()
        nick = data.nick.lower()
        if nick:
            auth.login_direct(session, users, '/forum#top', nick, data.password)

        raise web.seeother('/login' + ['', '/'][bool(nick)] + nick)

class Forum:
    """Main page with the list of threads"""
    
    @auth.protected(session, '/')
    @form.session_init(session, {'title': '', 'nicks': ''})
    def GET(self):
        threads = db.get_threads(session.uid)
        html = render.forum(tr.text[session.lang],
                            db.get_user_list(),
                            threads[::-1],
                            session.page_data)
        return html

    def POST(self):
        data = web.input()
        session.page_data = {'title': data.title, 'nicks': data.nicks}
        title = data.title.strip()
        
        # officialy only comma is allowed as a separator, in practice more
        # characters are alowed
        nicks = re.split('[ |,|;|\|]+', data.nicks.lower())

        if title:
            if db.add_thread(session.uid, title, nicks):
                session.page_data = {'title': '', 'nicks': ''}

        raise web.seeother(web.ctx.path) # stay here, only refresh

class Thread:
    """View of one thread including editing tools"""
    
    @auth.protected(session, '/')
    @form.session_init(session, {'preview': False, 'message': ''})
    def GET(self, tid):        
        tid = utils.dec_tid(tid)
        
        # tid can be entered in URL, so we need to verify if it is valid
        if not db.is_thread(tid):
            return 'Access denied' # page doesn't exist

        # check if current user is on the list of users of this thread
        user = db.get_user(session.uid)
        (guests, uids) = db.get_thread_users(session.lang, tid)
        if uids and session.uid not in uids:
            return 'Access denied' # tid is out of the list of users

        # if page is refreshed or the user switches between edit and
        # preview mode, we want to preserve the text in textarea
        message = session.page_data['message']
        if session.page_data['preview']:
            message = utils.markdown_to_html(message)
        
        # emoticons come from http://www.veryicon.com/icons/emoticon/the-black/
        # read names of emot icons and split the list into 2 rows
        emots = os.listdir('static' + os.sep + 'em')
        emots = zip(*[iter(emots)]*(len(emots)//2))

        html = render.thread(tr.text[session.lang],
                             db.get_posts(session.uid, tid),
                             user['nick'],
                             user['name'],
                             utils.hue_to_color(user['hue']),
                             guests,
                             db.get_thread_title(tid),
                             session.page_data['preview'],
                             message,
                             emots)
                             
        # save the fact of visiting this thread in history
        db.mark_read(session.uid, tid)
        return html
        
    def POST(self, tid):
        tid = utils.dec_tid(tid)
        data = web.input()

        if data.has_key('button'):
            if data.button == 'back':
                raise web.seeother('/forum#top')

            elif data.button == 'help':
                raise web.seeother('http://www.markitdown.net/markdown#top')

            elif data.button == 'post':
                if session.page_data['preview']:
                    message = session.page_data['message']
                else:
                    message = data.message

                if message:
                    if db.add_post(session.uid, tid, message):
                        db.mark_read(session.uid, tid)
                        session.page_data['preview'] = False
                        session.page_data['message'] = ''
                
            elif data.button == 'preview':
                if data.message:
                    session.page_data['preview'] = True
                    session.page_data['message'] = data.message

            elif data.button == 'edit':
                session.page_data['preview'] = False

        elif data.has_key('nbsp.x'):
            session.page_data['message'] = data.message + '&#160;'

        else:
            # in the list of keys we shoud find emot_{name}.png.x and
            # emot_name.png.y where {name} is variable
            keys = '\n'.join(data.keys())
            emot = re.search('^emot_(.*)\.x', keys, re.M).groups()[0]
            
            # append markdown tag at the end of message
            session.page_data['message'] = data.message + '![](/static/em/%s)' % emot

        raise web.seeother(web.ctx.path + '#bottom') # stay here, only refresh

class Admin:
    """Admin panel"""

    @auth.protected(session, '/')
    @form.session_init(session, {'query': '', 'response': '', 'status': 'S'})
    def GET(self):
        
        if not db.get_user(session.uid)['isadm']:
            return 'Access denied'
        
        shortcuts = [('List all users',      "SELECT * FROM USERS ORDER BY uid"),
                     ('List enabled users',  "SELECT * FROM USERS WHERE pass IS NOT NULL ORDER BY uid"),
                     ('List threads',        "SELECT * FROM THREADS ORDER BY tid"),
                     ('See thread',          "SELECT * FROM POSTS WHERE tid = 0 ORDER BY pid"),
                     ('List user\'s posts',  "SELECT * FROM POSTS WHERE uid = 0 ORDER BY pid"),
                     ('Add user',            "INSERT INTO USERS (nick, pass, name, hue, isadm) VALUES ('john', 'abc123', 'John', 0.0, 0)"),
                     ('Update user',         "UPDATE USERS SET hue = 0.3 WHERE nick = 'john'"),
                     ('Disable user',        "UPDATE USERS SET pass = NULL WHERE nick = 'john'"),
                     ('Delete user',         "DELETE FROM USERS WHERE nick = 'someone'"),
                     ('Delete thread',       "DELETE FROM THREADS WHERE tid = 0"),
                     ('Delete post',         "DELETE FROM POSTS WHERE pid = 0")]
        
        html = render.admin(session.page_data['query'],
                            session.page_data['response'],
                            session.page_data['status'],
                            shortcuts)
        return html

    def POST(self):
        data = web.input()
        query = data.query.strip()
        
        # if page is refreshed or query evaluated we want to preserve the text of query
        session.page_data['query'] = query
        
        if 'shortcut' in data:
            session.page_data['query'] = data.shortcut
        else:
            if query:
                try:
                    resp_webdb = db.webdb.query(query) # evaluate query
                    if resp_webdb.__class__ == int: # exit code returned
                        if resp_webdb < 0:
                            response = 'Error! (code: ' + str(resp_webdb) + ')'
                            status = 'E'
                        elif resp_webdb == 0:
                            response = 'Nothing to do!'
                            status = 'W'
                        else:
                            response = 'Success! (' + str(resp_webdb) + ' items affected)'
                            status = 'S'
                    else: # list of items returned
                        resp_dict = [item for item in resp_webdb]
                        if resp_dict:
                            response = '\n<table class="sql_responce">\n'

                            response += '<tr>'
                            for th in resp_dict[0].keys():
                                response += '<th>' + th + '</th>'
                            response += '</tr>\n'
                            
                            for item in resp_dict:
                                response += '<tr>'
                                for key in item:
                                    if item[key].__class__ == unicode: # TEXT in database
                                        td = item[key].encode('utf8')
                                    elif item[key] is None: # NULL in database
                                        td = '<i>NULL</i>'
                                    else:
                                        td = str(item[key])
                                    response += '<td>' + td + '</td>'
                                response += '</tr>\n'

                            response += '</table>\n'
                            status = 'S'
                        else:
                            response = 'Empty array!'
                            status = 'W'
                            
                except Exception as e:
                    # e.g. database file is read-only
                    response = str(e)
                    status = 'E'
            else: # empty query, nothing to do
                response = ''
                status = 'S'

            session.page_data['response'] = response
            session.page_data['status'] = status

        raise web.seeother(web.ctx.path) # stay here, only refresh


if __name__ == '__main__':
    app.run() # for development
else:
     application = app.wsgifunc() # for running by wsgi

