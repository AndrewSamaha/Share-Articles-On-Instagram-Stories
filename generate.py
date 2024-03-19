import os
import argparse
import time
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL import Image
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def get_article_data(article: str) -> tuple[str, str]:
    url = urlparse(article)
    assert all([url.scheme, url.netloc]), 'Article is not a valid URL :('

    resp = requests.get(article)
    assert 199 < resp.status_code < 300, f'Received a status code of {resp.status_code} :('

    tree = html.fromstring(resp.text)

    url = tree.xpath('//head/meta[@property="og:image"]/@content')
    if not url: raise Exception('No og:image found :(')

    title = tree.xpath('//head/title/text()')
    if not title: raise Exception('No title tag found :(')

    return url[0], title[0]

def get_img_brightness(img):
    img_gray = img.convert('L')
    pixels = list(img_gray.getdata())
    return sum(pixels) / len(pixels)

def get_color_from_brightness(brightness):
    if brightness < 127:
        return "snow"
    return "black"

def choose_font_color_web(image_url: str) -> str:
    resp = requests.get(image_url)
    assert 199 < resp.status_code < 300, f'Received a status code of {resp.status_code} :('

    img = Image.open(BytesIO(resp.content))
    avg_brightness = get_img_brightness(img)
    return get_color_from_brightness(avg_brightness)    

def choose_font_color_local(image_path: str) -> str:
    img = Image.open(image_path)
    avg_brightness = get_img_brightness(img)
    return get_color_from_brightness(avg_brightness)

def get_font_color_from_img_url(url):
    if url[:1] == "/":
        print(f"File URL: {url}")
        return choose_font_color_local(url)
    print(f"Web URL: {url}")
    return choose_font_color_web(url)

def get_template(template_type):
    path = "templates/"
    extension = ".html"
    accepted_types = ["story","post"]
    if template_type in accepted_types:
        return path + template_type + extension
    throw("Unknown template_type:", template_type)

def set_window_size(template, driver):
    sizes = {
        "post": [1080, 1080],
        "story": [1080, 1920]  # 7.7/2 = 3.85
    }
    width = sizes[template][0]
    height = sizes[template][1]
    print(f"Setting window size to {width}x{height}  aspect-ratio: {width/height}")
    driver.set_window_size(width, height)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('template_type', choices=["post","story"])
    args = parser.parse_args()

    template = args.template_type
    print("template:",template)
    
    background_path = "/home/andrew/Development/Share-Articles-On-Instagram-Stories/backgrounds/"
    background_img = "Firefly20240315182503.png"
    og_image = background_path + background_img
    title = "this is a test title"
    
    print(f'{og_image = }\n{title = }\nGenerating image...')

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    # driver.set_window_size(2500, 3500)
    set_window_size(template, driver)

    driver.get(f"file://{os.path.join(os.getcwd(), get_template(template))}")

    font_color = get_font_color_from_img_url(og_image)
    # Instantiate stuff
    driver.execute_script(f'setImages("{og_image}")')
    #driver.execute_script(f'setFigCaption("{title.strip()}")')
    driver.execute_script(f'setFontColor("{font_color}")')

    time.sleep(1)

    # Take screenshot
    container = driver.find_element(By.ID, 'story-container')
    container.screenshot(f"output/{template}-[{'-'.join(title.lower().split())}].png")

    driver.quit()


if __name__ == '__main__':
    main()
