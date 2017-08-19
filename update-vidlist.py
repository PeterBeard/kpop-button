#!/usr/bin/env python
"""
Get a list of the top videos on /r/kpop and export the list to JSON.

Copyright Peter Beard, licensed under the GPLv3. See LICENSE for details.
"""
from time import sleep
from collections import namedtuple
import json

import requests
import mechanicalsoup as ms


# Each video is identified by a title and a video id
Video = namedtuple("Video", "title id")


class KPopBrowser(ms.StatefulBrowser):
    """Wraps StatefulBrowser so we can set the user-agent"""
    def __init__(self, *args, **kwargs):
        BOT_USER_AGENT = "Kpopbot/0.1"

        headers = requests.utils.default_headers()
        headers.update({"User-Agent": BOT_USER_AGENT})
        self.headers = headers
        super().__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        """Open a page using the correct user-agent"""
        return super().open(headers=self.headers, *args, **kwargs)


def link_to_id(link):
    """Convert a YouTube link to a video ID"""
    return link.split("v=")[1][:11]


def get_flair(soup):
    """Get the link flair from a thing.
    
    Returns the flair or None if there isn't one.
    """
    f = soup.select(".linkflairlabel")
    if len(f) == 0:
        return None
    else:
        return f[0].get_text()


def get_score(thing):
    """Get the score of a thing.
    
    Returns the score of the thing as an int or 0 if no score is found.
    """
    s = thing.select(".midcol .score.unvoted")
    if len(s) > 0:
        return int(s[0].get_text())
    else:
        return 0


def get_music_videos(things, threshold):
    """Extract the music video links from a page of /r/kpop submissions.
    
    Returns a list of Video tuples.
    """
    # Music videos have this link flair
    MV_FLAIR = "[MV]"

    videos = []
    for thing in things:
        score = get_score(thing)
        link = thing.select(".entry .title a.title")[0]
        title = link.get_text()
        url = link.get("href")
        if score > threshold and "youtube" in url and get_flair(thing) == MV_FLAIR:
            videos.append(Video(title, link_to_id(url)))

    return videos


def get_top_videos(time="week"):
    """Get all of the top videos over a certain period of time.

    Default is one week but any of the values reddit supports can be used.
    Unsupported time spans will raise a ValueError.
    """
    CRAWL_RATE_LIMIT = 2
    SCORE_THRESHOLD = 5

    if time not in set(["all", "year", "month", "week", "day", "hour"]):
        raise ValueError("Invalid time span")

    videos = []

    browser = KPopBrowser(
            soup_config={'features': 'html.parser'},
    )
    browser.open("https://www.reddit.com/r/kpop/top/?sort=top&t={}".format(time))
    curr_page = browser.get_current_page()
    things = curr_page.select(".thing")
    videos += get_music_videos(things, SCORE_THRESHOLD)
    last_score = SCORE_THRESHOLD + 1

    while curr_page.select("a[rel~=next]") and last_score > SCORE_THRESHOLD:
        sleep(CRAWL_RATE_LIMIT)
        next_link = curr_page.select("a[rel~=next]")[0].get("href")
        response = browser.open(next_link)
        curr_page = browser.get_current_page()
        things = curr_page.select(".thing")
        if len(things) > 0:
            last_score = get_score(things[-1])
            videos += get_music_videos(things, SCORE_THRESHOLD)
        else:
            last_score = 0
        print("Found {} videos so far".format(len(videos)))

    # Deduplicate and return list of videos
    return list(set(videos))


def load_json(list_file):
    """Load an existing video list from a JSON file.
    
    Returns a list of Video tuples or an empty list if the file failed to open
    """
    videos = []
    try:
        with open(list_file, "r") as fh:
            data = json.load(fh)
            videos = [Video(v["title"], v["id"]) for v in data]
    except FileNotFoundError:
        videos = []
    return videos


def main():
    JSON_FILE = "website/top-all-time.json"

    # Load existing videos
    videos = load_json(JSON_FILE)
    old_count = len(videos)
    print("Loaded {} existing videos.".format(old_count))
    
    # Load new videos and remove duplicates
    videos += get_top_videos("all")
    videos = list(set(videos))
    new_count = len(videos)
    print("Found {} new videos ({} total).".format(
        (new_count - old_count),
        len(videos)
    ))

    # Write list to JSON
    with open(JSON_FILE, "w") as fh:
        # Convert tuples to dicts so we get keys in the JSON
        fh.write(json.dumps([v._asdict() for v in videos]))
    print("Saved JSON to {}".format(JSON_FILE))


if __name__ == "__main__":
    main()
