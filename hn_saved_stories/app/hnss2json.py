import argparse
import logging
import json
import os
import re
import sys

from hn_saved_stories import HNSession
from hn_saved_stories.logger import logger

def get_options():
    parser = argparse.ArgumentParser(description="""
        Download saved stories from HackerNews and dump the resultant data into
        a .json file.
        """)

    parser.add_argument('-u', '--username', help="HackerNews username")
    parser.add_argument('-p', '--password', help="HackerNews password")
    parser.add_argument('-f', '--file', help="File to download to. '-' can be used to redirect output to stdout. (default: hnss.json)", default="hnss.json")

    parser.add_argument('-d', '--debug', action='store_true', help="Debug mode.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output.")

    return parser.parse_args()

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

    new_stories = session.get_saved_stories(max_pages=2, break_func=break_func)

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
