import argparse
import json
import os
import sys

from hn_saved_stories import HNSession

def get_options():
    parser = argparse.ArgumentParser(description="""
        Download saved stories from HackerNews and dump the resultant data into
        a .json file.
        """)

    parser.add_argument('-u', '--username', help="HackerNews username")
    parser.add_argument('-p', '--password', help="HackerNews password")
    parser.add_argument('-f', '--file', help="File to download to. (default: hnss.json)", default="hnss.json")

    return parser.parse_args()

def main():
    options = get_options()

    session = HNSession()
    session.login(options.username, options.password)
    stories = session.get_saved_stories(max_pages=1)

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
