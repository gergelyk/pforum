Description
===========

PForum is a private forum. It is intended to be used for your domestic
pourposes - communication with friends, organizing events, working on projects.

PForum doesn't assume presenting posts in public. Users can be registered only
by administrator. It has been developed as an extension of a Smart TV. The goal
was to provide basic functionality to the users who are less experienced with
using state of the art tools offered by the internet.


Requirements
============

Python2, and following packages are required:
* pycrypto
* Markdown
* web.py

Additionally you may wont to use uwsgi. This is optional though.


Starting
========

Reset database by invoking ./commands/resetdb

To start the server simply run ./commands/start script. This is preferred method
for development. If you want to use uwsgi, feel free to use ./commands/uwsgi_*
scripts. Please also edit relevant script if you would like to change port.

Log in as 'admin', without password.


Usage
=====

1. Logging in

   There are three options to log in:
   * Include your creditials in URL: http://user:password@domain:port
     This is a dangerous method and it's not recommended (especially in public
     networks).

   * Go to http://domain:port/login and enter your username and password.

   * Go to http://domain:port/login/username and enter your password.
     This is a method which allows you to bookmark the forum together with
     username, so that it is even faster for the user to access it.

2. Creating a thread

   Just give a title and press 'create' button. Optionally you can specify who
   will have an access to your thread. For that you need to provide comma
   separated nick names. Alternatively you can leave 'users' field empty, which
   means that everyone who is currently registered will get the access. The last
   option is to put asterix (*) to the user field. This means that the thread
   will be public which means that it will be open for everyone who is already
   registered or who will be registered in the future. Author is always added to
   the list of users.

3. Removing a thread

   Press red x button next to the title of the thread which you would like to
   remove. The thread will disappear from you view, but it will remain visible
   to the other users until they remove it from their views too. Public threads
   cannot be removed.

4. Creating a post

   Just write something and press 'post' button. You can use Markdown syntax.
   PForum supports it's subset. There are many tutorials and examples on the
   internet where you can learn about Markdown.

5. Administration

   All the administrative tasks can be performed either by editing forum.db
   file, or by using web interface. For the first option you need an SQLite
   editor, for instance 'sqlitebrowser' from http://sqlitebrowser.org
   For the second option you need to log in to the forum as a privileged user
   and then go to the admin panel: http://domain:port/admin
   Please read the hints in the admin panel before making any changes.

6. Advanced editing

   It is possible to use plain HTML in your posts. Please check 'examples'
   directory to learn more.


Release Notes
=============

v1.1.0
* Removable threads
* List of users
* Editable profile
* Reduced number of emot icons

v1.0.0
* Initial version


Development
===========

   Ideas for further development:

1. Forum can be turned into the one which can be accessible anonymously. For
   example double asterix (**) in 'user' field would mean read access for
   anonymous users.

2. There may be a need of giving rights for reading and writing separately.

3. Empty 'user' field could rather mean that the user want to grant the rights
   to the guests from his 'preffered users' list. If his 'preffered users' list
   is empty then all registered users would have the rights granted (as it
   works now).

4. USERS table could be expanded by 'email' and 'notes' fields for
   administrative pourposes.





