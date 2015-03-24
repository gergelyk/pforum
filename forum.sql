DROP TABLE IF EXISTS POSTS;
DROP TABLE IF EXISTS THREADS;
DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS HISTORY;

CREATE TABLE POSTS (
        pid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, /* post ID > 0 */
        uid INTEGER,                                  /* user ID */
        tid INTEGER,                                  /* thread ID */
        msg TEXT,                                     /* message, anything */
        ts INTEGER                                    /* timestamp */
);

CREATE TABLE THREADS (
        tid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, /* thread ID > 0 */
        title TEXT,                                   /* title, anything */
        uids TEXT,                                    /* comma separated uids of the users (if empty, then everyone is the user) */
        uid INTEGER                                   /* uid of the creator, just for tracking purposes*/
);

CREATE TABLE USERS (
        uid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, /* user ID > 0 */
        nick TEXT UNIQUE,                             /* [a-z0-9.]+ */
        pass TEXT,                                    /* password, anything */
        name TEXT,                                    /* full name, anything */
        hue REAL,                                     /* 0 <= hue <= 1 */
        lang TEXT,                                    /* language */
        isadm INTEGER                                 /* 1 if he/she is an admin, 0 therwise */
);

CREATE TABLE HISTORY (
        uid INTEGER,                                  /* who has read*/
        tid INTEGER,                                  /* which thread*/
        pid INTEGER                                   /* what was the last post in it*/
);

INSERT INTO USERS (nick, pass, name, hue, lang, isadm) VALUES ('admin', '', 'Administrator', 0.0, 'en', 1);
INSERT INTO THREADS (title, uids, uid) VALUES ('Welcome to PForum', '', 1);
INSERT INTO POSTS (uid, tid, msg, ts) VALUES (1, 1, 'Please hover your cursor over "User" field on the main page to understand who can read your posts. Have fun! ![](/static/em/smile.png)', 0);
INSERT INTO POSTS (uid, tid, msg, ts) VALUES (1, 1, 'PForum supports a subset of Markdown syntax. Visit [this](http://www.markitdown.net/markdown) page to check out some examples.', 0);


