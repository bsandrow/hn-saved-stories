import argparse
import logging
import json
import os
import re
import sys

from xdg.BaseDirectory import load_first_config, save_data_path
from hn_saved_stories import HNSession
from hn_saved_stories.logger import logger

def get_options():
    config_dir = load_first_config('hnss')
    data_dir = save_data_path('hnss')
    auth_file_default = os.path.join(config_dir, 'auth.json')
    data_file_default = os.path.join(data_dir, 'data.json')

    if os.path.exists('auth.json'):
        with open('auth.json', 'rb') as fh:
            auth = json.loads(fh.read())


    parser = argparse.ArgumentParser(description="""
        Download saved stories from HackerNews and dump the resultant data into
        a .json file. Subsequent runs using a previous data file will only
        scrape the newest saved stories. (Note: There is a 30 second delay
        between requests.)
        """)

    parser.add_argument('-u', '--username', default=None, help="HackerNews username")
    parser.add_argument('-p', '--password', default=None, help="HackerNews password")
    parser.add_argument('-a', '--auth-file', default=None, help="Auth file (JSON format). (default: %s)" % auth_file_default)
    parser.add_argument('-f', '--file', help="File to download to. '-' can be used to redirect output to stdout. (default: %s)" % data_file_default, default=data_file_default)
    parser.add_argument('-m', '--max-pages', type=int, default=1, help="The maximum number of pages to go into the past. 0 goes back all the way to the beginning of time. (default: 1)")
    parser.add_argument('-d', '--debug', action='store_true', help="Debug mode.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output.")

    options = parser.parse_args()

    if options.auth_file:
        with open(options.auth_file, 'rb') as fh:
            auth_info = json.loads(fh.read())
            options.username = options.username or auth_info['username']
            options.password = options.password or auth_info['password']
    else:
        if os.path.exists(auth_file_default):
            with open(auth_file_default, 'rb') as fh:
                auth_info = json.loads(fh.read())
                options.username = options.username or auth_info['username']
                options.password = options.password or auth_info['password']

    if not options.username:
        sys.exit("Error: No username given.")
    if not options.password:
        sys.exit("Error: No password given.")

    return options

def main():
    options = get_options()

    if options.debug:
        logger.setLevel(logging.DEBUG)
    elif options.verbose:
        logger.setLevel(logging.INFO)

    if options.file != '-' and os.path.exists(options.file):
        with open(options.file, 'rb') as fh:
            stories = json.loads(fh.read())
    else:
        stories = {}

    most_recent_story = max(map(int, stories.keys())) if stories.keys() else 0
    break_func = lambda stories: most_recent_story and str(most_recent_story) in stories

    session = HNSession()
    session.login(options.username, options.password)

    new_stories = session.get_saved_stories(max_pages=(options.max_pages or None), break_func=break_func)

    stories_to_add = set(new_stories.keys()) - set(stories.keys())
    stories.update({ story_id: new_stories[story_id] for story_id in stories_to_add })

    if options.file == '-':
        sys.stdout.write(json.dumps(stories))
    else:
        with open(options.file, 'wb') as fh:
            fh.write(json.dumps(stories))

def run():
    try:
        # Turn off buffering for stdout
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

        main()
    except KeyboardInterrupt:
        sys.exit(">> Caught user interrupt. Exiting...")

if __name__ == '__main__':
    run()
