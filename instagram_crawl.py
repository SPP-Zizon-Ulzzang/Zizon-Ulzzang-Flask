from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

import time

import chromedriver_autoinstaller


# 크롬 자동 다운로드, 옵션 설정, 창 생성
def create_chrome():
    chromedriver_autoinstaller.install("./")

    chrome_options = Options()

    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--no-sandbox")

    return WebDriver(options=chrome_options)


def openInstagram(name: str):
    rst = ""

    # 크롬 창 생성
    driver = create_chrome()
    driver.implicitly_wait(10)

    # 인스타 URL로 이동
    driver.get("https://www.instagram.com/" + name)

    # 게시물 전부 수집
    posts = driver.find_elements(By.XPATH, "//a[contains(@href,'/p/')]")
    post_num = 30 if len(posts) > 30 else len(posts)

    urls = []

    for i in range(post_num):
        urls.append(posts[i].get_attribute('href'))

    text = ''
    for url in urls:
        # 인스타 TEXT 추출
        driver.get(url)
        text += driver.find_elements(By.XPATH, "//*[@class='_a9zr']")[0].text + '\n'

    # 태그 추출
    tags = [i for i in text.split() if i.startswith("#")]

    # 태그 위치 추출
    indexList = []

    for tag in tags:
        indexList.append(text.index(tag))

    # 유니코드 범위 (이 범위를 벗어나면 이모티콘같은 특수 문자)
    SUPPORTED_RANGE_START = 0x0000
    SUPPORTED_RANGE_END = 0xFFFF

    # 태그 위치를 기반으로 추출한 텍스트에서 태그를 제거해 rst에 저장
    i = 0

    while i <= len(text):
        try:
            s = text[i]

            # 태그 위치를 기반으로 추출한 텍스트에서 태그 제거
            for index in indexList:
                if i == index:
                    tag = tags[indexList.index(index)]
                    i += len(tag)

            if s != "#":

                # 유니코드 범위를 기반으로 이모티콘 제거
                code_point = ord(s)
                if SUPPORTED_RANGE_START <= code_point <= SUPPORTED_RANGE_END:
                    rst += s
                else:
                    pass

            i += 1
        except:
            i += 1
            pass
    rst = rst.replace(name, '')
    driver.quit()
    return [rst]
