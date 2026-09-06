"""Refresh the existing latest-post block without altering the rest of index.html."""
import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

FEED = 'https://jeremedotxyz.substack.com/feed'
BLOCK = re.compile(r'<article class="latest-post">[\s\S]*?</article>')


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag in ('p', 'br', 'div', 'li'):
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden:
            self.hidden -= 1
        if tag in ('p', 'div', 'li'):
            self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain(value):
    parser = PlainText()
    parser.feed(value)
    return ' '.join(''.join(parser.parts).split())


def latest(xml):
    root = ET.fromstring(xml)
    candidates = []
    for item in root.findall('./channel/item'):
        title = (item.findtext('title') or '').strip()
        url = (item.findtext('link') or '').strip()
        parsed = urlparse(url)
        if not title or parsed.scheme != 'https' or parsed.netloc != 'jeremedotxyz.substack.com' or not parsed.path.startswith('/p/'):
            continue
        try:
            date = parsedate_to_datetime(item.findtext('pubDate') or '')
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError, OverflowError):
            continue
        if date > datetime.now(timezone.utc):
            continue
        description = item.findtext('description') or item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') or ''
        excerpt = plain(description)
        if len(excerpt) > 240:
            excerpt = excerpt[:237].rsplit(' ', 1)[0] + '...'
        # Keep the site's lowercase body style while preserving LiDAR.
        excerpt = re.sub(r'\blidar\b', 'LiDAR', excerpt.lower())
        candidates.append((date, title, url, excerpt))
    if not candidates:
        raise ValueError('No valid published articles found; existing homepage retained')
    return max(candidates, key=lambda entry: entry[0])


def update(source, xml):
    if len(BLOCK.findall(source)) != 1:
        raise ValueError('Expected exactly one latest-post block; refusing to modify homepage')
    date, title, url, excerpt = latest(xml)
    label = date.strftime('%b').lower() + f' {date.day}, {date.year}'
    block = ('<article class="latest-post"><p class="post-meta">latest on substack '
             f'<time datetime="{date.isoformat()}">{label}</time></p>'
             f'<h3><a href="{escape(url, quote=True)}">{escape(title)} '
             '<span aria-hidden="true">↗</span></a></h3>'
             f'<p>{escape(excerpt)}</p></article>')
    return BLOCK.sub(lambda _: block, source)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('homepage', type=Path)
    parser.add_argument('--feed-file', type=Path, help='Use a local RSS fixture for testing')
    args = parser.parse_args()
    if args.feed_file:
        xml = args.feed_file.read_bytes()
    else:
        request = urllib.request.Request(FEED, headers={'User-Agent': 'jereme.xyz RSS reader/1.0', 'Accept': 'application/rss+xml, application/xml, text/xml'})
        with urllib.request.urlopen(request, timeout=30) as response:
            xml = response.read(4_000_001)
        if len(xml) > 4_000_000:
            raise ValueError('RSS response exceeded size limit')
    source = args.homepage.read_text(encoding='utf-8')
    updated = update(source, xml)
    if updated != source:
        temporary = args.homepage.with_suffix('.html.tmp')
        temporary.write_text(updated, encoding='utf-8')
        temporary.replace(args.homepage)
    print('Latest Substack article:', latest(xml)[1])


if __name__ == '__main__':
    main()
