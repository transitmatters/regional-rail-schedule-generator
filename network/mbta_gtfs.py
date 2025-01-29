from typing import List, Union
from csv import DictReader
from dataclasses import dataclass
from datetime import date, datetime
from zipfile import BadZipFile, ZipFile
from tqdm import tqdm
import tempfile
import click
import requests

from network.config import GTFS_ARCHIVE_URL, PATH_TO_GTFS_DATA


@dataclass
class GtfsFeed:
    start_date: date
    end_date: date
    url: str
    version: str


def date_from_string(date_str: str, format: str = "%Y%m%d") -> date:
    return datetime.strptime(date_str, format).date()


def validate_date_arg(_, __, date_arg: Union[None, str]) -> Union[None, date]:
    if date_arg == "latest":
        return None
    try:
        parsed = date_from_string(date_arg, "%Y-%m-%d")
        return parsed
    except:
        raise click.BadParameter("Must specify a date as yyyy-mm-dd or 'latest'")


def download_gtfs_feed(feed: GtfsFeed):
    response = requests.get(feed.url, stream=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024
    progress_bar = tqdm(
        total=total_size_in_bytes,
        unit="iB",
        unit_scale=True,
        desc=f"Downloading {feed.url}",
    )
    target_file = tempfile.NamedTemporaryFile(suffix=".zip")
    with open(target_file.name, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    try:
        zf = ZipFile(target_file.name)
        zf.extractall(PATH_TO_GTFS_DATA)
    except BadZipFile:
        print("Corrupt GTFS feed:", feed.url)


def load_feeds_from_archive():
    feeds = []
    req = requests.get(GTFS_ARCHIVE_URL)
    lines = req.text.splitlines()
    reader = DictReader(lines, delimiter=",")
    for entry in reader:
        start_date = date_from_string(entry["feed_start_date"])
        end_date = date_from_string(entry["feed_end_date"])
        version = entry["feed_version"]
        url = entry["archive_url"]
        gtfs_feed = GtfsFeed(
            start_date=start_date,
            end_date=end_date,
            version=version,
            url=url,
        )
        feeds.append(gtfs_feed)
    return list(reversed(sorted(feeds, key=lambda feed: feed.start_date)))


def select_feed(feeds: List[GtfsFeed], date: Union[None, date]) -> GtfsFeed:
    if date is None:
        return feeds[0]
    try:
        return next((feed for feed in feeds if feed.start_date <= date <= feed.end_date))
    except StopIteration:
        print(f"No GTFS feed available for {date}")


@click.command()
@click.option("--date", callback=validate_date_arg)
def load_mbta_gtfs_feed(date: Union[None, date]):
    feeds = load_feeds_from_archive()
    feed = select_feed(feeds, date)
    print(f"Selecting GTFS feed for dates: {feed.start_date} to {feed.end_date}")
    download_gtfs_feed(feed)


if __name__ == "__main__":
    load_mbta_gtfs_feed()
