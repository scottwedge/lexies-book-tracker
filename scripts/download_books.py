#!/usr/bin/env python

import csv
import datetime
import hashlib
import os
import pathlib
import re
from urllib.request import urlretrieve

import hyperlink
from unidecode import unidecode


def sha256(path):
    h = hashlib.sha256()
    h.update(open(path, "rb").read())
    return h.hexdigest()


def slugify(u):
    """Convert Unicode string into blog slug."""
    # https://leancrew.com/all-this/2014/10/asciifying/
    u = re.sub("[–—/:;,.]", "-", u)  # replace separating punctuation
    a = unidecode(u).lower()  # best ASCII substitutions, lowercased
    a = re.sub(r"[^a-z0-9 -]", "", a)  # delete any other characters
    a = a.replace(" ", "-")  # spaces to hyphens
    a = re.sub(r"-+", "-", a)  # condense repeated hyphens
    return a


def download_cover_image(row, *, backup_root):
    cover_images_dir = backup_root / "cover_images"
    cover_images_dir.mkdir(exist_ok=True)

    url = row["image_url"]
    title = slugify(row["title"])

    if (cover_images_dir / f"{title}.jpg").exists() or (
        cover_images_dir / f"{title}.png"
    ).exists():
        return

    if url == "":
        return

    url = hyperlink.URL.from_text(url)

    # This ensures we get the full-sized image, not the thumbnail
    # returned by default from the API.
    url = url.remove("zoom")

    local_filename, headers = urlretrieve(str(url))

    # Check it's not a "image not available" URL.
    if (
        sha256(local_filename)
        == "3efa8c43e5b4348f303a528c81adf435f0111ea752fe9f0f6241478b60987fa6"
    ):
        url = row["image_url"]
        local_filename, headers = urlretrieve(str(url))

    content_type = headers["Content-Type"]
    if content_type == "image/jpeg":
        ext = ".jpg"
    elif content_type == "image/png":
        ext = ".png"
    else:
        raise ValueError("Unrecognised Content-Type header: {content_type}")

    out_path = cover_images_dir / f"{title}{ext}"
    os.rename(local_filename, out_path)


def main():
    backup_root = pathlib.Path.home() / "Documents" / "backups" / "lexies-book-tracker"
    backup_root.mkdir(exist_ok=True)

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    downloads = {
        "https://books.alexwlchan.net/export/reading": f"reading.{today}.csv",
        "https://books.alexwlchan.net/export/reviews": f"reviews.{today}.csv",
        "https://books.alexwlchan.net/export/plans": f"plans.{today}.csv",
    }

    for url, filename in downloads.items():
        local_filename, _ = urlretrieve(url)
        os.rename(local_filename, backup_root / filename)

    for filename in downloads.values():
        csv_path = backup_root / filename

        for row in csv.DictReader(open(csv_path)):
            download_cover_image(row, backup_root=backup_root)


if __name__ == "__main__":
    main()
