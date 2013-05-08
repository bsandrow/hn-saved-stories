import re

from datetime import datetime, timedelta

def hn_relatime_to_datetime(basetime, hn_relatime):
    """ Convert the HN relative time to a datetime (or date) object. """
    match = re.search(r'(\d+) minutes? ago', hn_relatime, re.I)
    if match:
        minutes = int(match.group(1))
        return basetime - timedelta(minutes=minutes)

    match = re.search(r'(\d+) hours? ago', hn_relatime, re.I)
    if match:
        hours = int(match.group(1))
        return basetime - timedelta(hours=hours)

    match = re.search(r'(\d+) days? ago', hn_relatime, re.I)
    if match:
        days = int(match.group(1))
        return basetime.date() - timedelta(days=days)

    return None
