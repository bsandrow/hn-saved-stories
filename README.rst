================
hn-saved-stories
================

hn-saved-stores is a script for archiving all of the saved stories in your
Hacker News profile (i.e. all of the stories that you have upvoted).

::

    $ hn-saved-stories -f hnss.json -u username -p password --max-pages 1
    $ json_pp < hnss.json
    { "STORY_ID" : {
         "submitted_at" : "STORY_DATE",
         "url" : "STORY_URL",
         "title" : "STORY_TITLE",
         "submitter_link" : "SUBMITTER_USER_URL",
         "comments" : "COMMENTS_URL",
         "submitter" : "SUBMITTER_USER_ID"
      }
    }

**Note:** This script hits the '/x?' URL pattern, which is specifically
disallowed by robots.txt. I've made attempts to make this as low-impact as
possible:

(1) It's meant to scrape the 'saved stories' of only a single user.
(2) There is a delay between requests.
(3) Subsequent runs using the same output file, will only scrape as far as the most recent story in the output file.
(4) A delay of 30 seconds between requests is obeyed (with the exception of the login requests) as per the robots.txt.

That said, use this script responsibly.

Usage
-----

::

    usage: hn-saved-stories [-h] [-u USERNAME] [-p PASSWORD] [-a AUTH_FILE]
                            [-f FILE] [-m MAX_PAGES] [-d] [-v]

    Download saved stories from HackerNews and dump the resultant data into a
    .json file.

    optional arguments:
      -h, --help            show this help message and exit
      -u USERNAME, --username USERNAME
                            HackerNews username
      -p PASSWORD, --password PASSWORD
                            HackerNews password
      -a AUTH_FILE, --auth-file AUTH_FILE
                            Auth file (JSON format). (default:
                            ~/.config/hnss/auth.json)
      -f FILE, --file FILE  File to download to. '-' can be used to redirect
                            output to stdout. (default:
                            ~/.local/share/hnss/data.json)
      -m MAX_PAGES, --max-pages MAX_PAGES
                            The maximum number of pages to go into the past. 0
                            goes back all the way to the beginning of time.
                            (default: 1)
      -d, --debug           Debug mode.
      -v, --verbose         Verbose output.


Credits
-------

Copyright 2013 Brandon Sandrowicz <brandon@sandrowicz.org>

License
-------

MIT License. See LICENSE.
