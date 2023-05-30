from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selectolax.parser import HTMLParser
import re
import json
import time
import subprocess

SLEEP_TIME = 60 * 5


def scrape_streams():
    url = "https://trovo.live/?tags=0:24|Czech"

    options = Options()
    options.add_argument("--headless")

    with webdriver.Chrome(options=options) as driver:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".live-item")))
        html = driver.page_source

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
            stream['stream_url'] = "https://trovo.live" + \
                item.css_first(".live-item").attributes['href']
            stream['user_thumbnail_url'] = item.css_first(
                ".img-face").attributes['src']

            streams.append(stream)

        return streams


def run_cmd(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Command execution failed. ({command})")
            if result.stderr:
                print("Error:")
                print(result.stderr)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


while True:
    start = time.time()

    try:
        streams = scrape_streams()
        data = {"last_updated": int(time.time()),
                "streams": streams}

        with open("streams.json", "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        continue

    run_cmd('git add streams.json')
    run_cmd(f'git commit -m "{time.ctime()}"')
    run_cmd('git push origin')

    time.sleep(SLEEP_TIME - (time.time() - start))
