
import os
import json
import re
import sys
import requests
import lxml.html

from datetime import datetime, timedelta
from pprint import pprint as PP
from time import sleep
from urlparse import urljoin

from .utils import hn_relatime_to_datetime, get_story_id
from .logger import logger

class HNSession(object):
    max_retries = 2
    retry_delay = 2

    def __init__(self, *args, **kwargs):
        self.session = requests.Session(*args, **kwargs)
        self.last_response = None

    def last_response_time(self):
        """ Return the time of the last response """
        if 'last_response' in self.__dict__ and self.last_response.headers.get('date'):
            return datetime.strptime(self.last_response.headers.get('date'), "%a, %d %B %Y %H:%M:%S %Z")
        else:
            return None

    def last_response_url(self):
        """ Return the url of the last response """
        if 'last_response' in self.__dict__:
            return self.last_response.url
        else:
            return None

    def get(self, *args, **kwargs):
        """ requests.get() within the session

        Wraps requests.get() within the session (so it has access to session
        cookies), and also retries on failures, because timeouts seem to
        happen randomly.
        """
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 10
        retries = 0
        while True:
            try:
                request = self.session.get(*args, **kwargs)
                request.raise_for_status()
                return request
            except requests.exceptions.RequestException as e:
                if retries < self.max_retries:
                    retries += 1
                    sleep(self.retry_delay)
                else:
                    raise

    def resolve_url(self, url):
        """ Resolve :url: using the most appropriate base url """
        base_url = self.last_response_url() or 'https://news.ycombinator.com'
        return urljoin(base_url, url)

    def login(self, username, password):
        """ Log into the session using provided credentials """
        try:
            response = self.get('https://news.ycombinator.com/newslogin')
        except requests.exceptions.HTTPError:
            raise Exception("Error: Unable to retrieve login page")

        doc = lxml.html.fromstring(response.text)

        fields = doc.xpath('.//input')
        form_data = { x.get('name'): x.get('value') for x in fields }
        form_data['u'] = username
        form_data['p'] = password

        response = self.session.post('https://news.ycombinator.com/y', data=form_data, timeout=10)
        if response.status_code != requests.codes.ok:
            raise Exception("Error: Unable to successfully login.")

        self.username = username
        self.last_response = response

    def get_saved_stories(self, max_pages=None, break_func=None):
        """ Fetch the list of 'saved stories' from a profile

        Fetch the list of saved stories for a Hacker News user account. The
        session needs to be logged into an account for this to work.

        break_func - A function that takes the current page's story list, and
                     returns True if we should break out of the loop.

        max_pages - The maximum number of pages that we should go through
                    before aborting. A value of None goes through all pages.
        """

        def parse_story(title, subtext):
            """ Parse a story from title + subtext """
            url_keys = ['url', 'comments', 'submitter_link']
            story = {}
            title_anchor = title.xpath('./a')[0]
            comments_anchor = subtext.xpath('.//a')[-1] # See Footnote [1]

            story['url'] = title_anchor.get('href')
            story['title'] = title_anchor.text
            story['comments'] = comments_anchor.get('href')
            story['submitter'] = subtext.xpath('.//a[1]//text()')[0] # See Footnote [4]
            story['submitter_link'] = subtext.xpath('.//a[1]/@href')[0]
            story['submitted_at'] = str( hn_relatime_to_datetime(self.last_response_time(), subtext.xpath('./text()')[1]) )

            # Resolve all relative URLs
            for key in story.keys():
                if key in url_keys and story.get(key):
                    story[key] = self.resolve_url(story[key])

            return get_story_id(story), story

        page = 1
        stories = {}
        url = 'https://news.ycombinator.com/saved?id=%s' % self.username

        while max_pages is None or page <= max_pages:
            try:
                logger.info("Page %d:" % page)
                logger.debug("  url = %s" % url)
                logger.info("  Fetching...")

                try:
                    response = self.get(url)
                except requests.exceptions.HTTPError as e:
                    raise Exception("Error: Failed to retrieve page %d, error:'%s', rurl: %s" % (page, str(e), url))

                logger.info("  Parsing...")
                html = lxml.html.fromstring(response.text)
                basetime = datetime.strptime(response.headers['date'], "%a, %d %B %Y %H:%M:%S %Z")

                title = html.cssselect('td.title') # See Footnote [3]
                subtext = html.cssselect('td.subtext')

                page_stories = dict([ parse_story(*s) for s in zip(title[1::2], subtext) ])
                next_link = title[-1].xpath('.//a[text() = "More"]/@href')
                next_link = next_link[0] if next_link else None

                stories.update(page_stories)

                should_break = (break_func and break_func(page_stories)) or next_link is None
                if should_break:
                    break

                url = self.resolve_url(next_link)
                page += 1

                logger.info("  Sleeping (1s)...")
                sleep(1)
            except Exception as e:
                logger.debug("Caught exception. Dumping page...")
                logger.debug("______________")
                logger.debug(lxml.html.tostring(html, pretty_print=True))
                logger.debug("______________")
                raise

        logger.info("Done.")
        return stories

# Footnotes
# ~~~~~~~~~
# [1] Can't use xpath './/a[3]' because if you have submitted a story, the
#     'flag' link is excluded, making only 2 anchors, so use python arrays to
#     look for the last element in the list.
#
# [2] '[Dead]' links remove the 'href' attribute from the anchor, so you end up
#     with None as a URL.
#
# [3] 'td.title' selects 3 different things:
#         1) the number of the story (in reverse, story #1 is
#            the most recently saved)
#         2) the title + link of the story
#         3) the 'More' link at the bottom of the page, which
#            goes to the next page in the series.
#     The series should look something like [1,2,1,2,1,2,1,2,3], #1 and #2
#     alternating with #3 being the last in the list. #3 will be missing on the
#     final page.
#
# [4] The '//text()' part is needed because sometimes the submitter has a
#     <font> element colouring it, so text() is not a direct child of the
#     anchor. E.g.:
#
#       <a href="user?id=foofoobar"><font color="#3c963c">foofoobar</font></a>
