# -*- coding: utf-8 -*-

def _session_init(session, page_name, page_data):
    """Resets data of current page if the user came from a different one
    """
    if page_name != session.get('page_name', ''): # page has been changed
        session.page_name = page_name # name of current page
        session.page_data = page_data # initial data of current page

def session_init(session, page_data):
    """This is a wrapper for each GET method which needs to preserve
       some data in sesson.
       page_data - an initial value of dictionary to be maintained
    """
    def wrap(f):
        def wrap_(*args, **kwargs):
            page_name = args[0].__class__.__name__
            _session_init(session, page_name, page_data)
            return f(*args, **kwargs)
        return wrap_
    return wrap
