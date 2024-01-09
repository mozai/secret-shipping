Secret Shipping Signup Sheet
================
Did it in Python and sqlite3 out of stubborness.

Setup
-----
- Gotta create the sqlite3 file
  TODO: autogenerate by index.cgi if missing
  ```
  sqlite3 ss2024.db "CREATE TABLE IF NOT EXISTS signups
      (tstamp DATETIME, remote_addr, name, email, address, country,
      intro, foreignokay, moon);"
  chmod 666 ss2024.db
  ```
  and to do writes you gotta make the folder writable by the webserver
  ```
  chmod g+rwx .; sudo chgrp www-data .
  ```

- Gotta set the start/end times. remember these will use the server
  clock, which may not be the your clock nor every participant's clock.
  ```
  OPEN_TIME = "2024-01-02 17:00"
  CLOSED_TIME = "2024-01-08 17:00"
  ```

- the html output, especially forms, are all written into the index.cgi
  which is not great for customizing but it did the job for this event

- Gotta tell nginx to launch .cgi programs, and not allow sqlite3 db downloads
  ```
  index index.html index.htm index.cgi ;
  location ~ \.cgi$ {
    include      snippets/fastcgi.conf ;
  }
  location ~ .*\.db {
    return 403;
  }
  ```
  I ain't gonna write fastcgi.conf here, you can figure it out.


Use
---
It's index.cgi, people just sign-up.  They can sign up more than
once but I have a limit of no more than 32 signups from the same
IP address.

After the CLOSED\_TIME pases, launch `./show_results.py` and
copy-paste into email messages to each person.  Don't automate
this part because it needs a human to verify each link in the chain.


TODO
----
- What if someone signs up faking another person's name?
- How to correctly merge multiple sign-ups by (legit) the same person?
- How can a participant drop-out? I used `delete from signups where 
  name = 'Mozai';` for now.
- Refine protection of the sqlite3 database, currently done in nginx config.


Image credits
-------------
- check-em by Cpt.Nameless
- nepeta-with-her-tablet by Zethrina
- equius-at-attention by Luzerna

