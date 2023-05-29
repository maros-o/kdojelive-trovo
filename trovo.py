from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
import requests
import re
import json
import time
import subprocess


SLEEP_TIME = 60 * 5


def scrape_streams():
    url = "https://trovo.live/?tags=0:24|Czech"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        html = page.content()

        items = HTMLParser(html).css(".live-item")
        streams = []
        url_pattern = r'url\("([^"]+)"\)'

        for item in items:
            stream = {}

            stream['user_name'] = item.css_first(".nickname").text()
            stream['title'] = item.css_first(".main-desc").text()
            stream['viewer_count'] = int(item.css_first(".watch-num").text())

            style = item.css_first(".cover").attributes['style']
            match = re.search(url_pattern, style)
            if match:
                stream['stream_thumbnail_url'] = match.group(1)

            stream['platform'] = 'trovo'
            stream['category'] = item.css_first(".sub-desc").text().strip()
            stream['stream_url'] = "https://trovo.live" + item.css_first(
                ".live-item").attributes['href']
            stream['user_thumbnail_url'] = item.css_first(
                ".img-face").attributes['src']

            streams.append(stream)

        browser.close()

        return streams


def run_cmd(command):
    try:
        result = subprocess.run(command, shell=True,
                                capture_output=True, text=True)

        if result.returncode == 0:
            if result.stdout:
                print(" Output:", result.stdout)
        else:
            if result.stderr:
                print("Error:", result.stderr)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


count = 0

while True:
    start = time.time()

    streams = scrape_streams()
    print(f'streams updated {count}, {time.ctime()}')

    with open("streams.json", "w", encoding='utf-8') as f:
        json.dump(streams, f, indent=4)

    run_cmd('git add streams.json')
    run_cmd(f'git commit -m "auto commit {count}"')
    run_cmd('git push origin')
    count += 1

    elapsed = time.time() - start
    time.sleep(SLEEP_TIME)
