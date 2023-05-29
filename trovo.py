from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
import requests
import re
import json
import time
import subprocess


SLEEP_TIME = 10


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


def create_commit(repository, commit_message, access_token):
    url = f"https://api.github.com/repos/{repository}/git/commits"
    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "message": commit_message,
        "tree": "<commit SHA>",
        "parents": ["<parent commit SHA>"]
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("Commit created successfully.")
    else:
        print(f"Failed to create commit. Error: {response.text}")


def run_cmd(command):
    try:
        result = subprocess.run(command, shell=True,
                                capture_output=True, text=True)

        if result.returncode == 0:
            print(f"cmd OK ({command})")
            if result.stdout:
                print(" Output:")
                print(' ' + result.stdout)
        else:
            print(f"cmd FAIL ({command})")
            if result.stderr:
                print(" Error:")
                print(' ' + result.stderr)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


count = 0

while True:
    start = time.time()

    streams = scrape_streams()
    print(f'streams updated {count}')

    with open("streams.json", "w", encoding='utf-8') as f:
        json.dump(streams, f, indent=4)

    run_cmd('git add .')
    run_cmd(f'git commit -m "auto commit {count}"')
    run_cmd('git push origin')
    count += 1

    elapsed = time.time() - start
    time.sleep(SLEEP_TIME)
