import os
import asyncio
import time
from math import floor
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

place = "Alun Alun Rembang"

async def extract_google_reviews(query):
    options = Options()
    options.headless = True
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    
    
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options=options)
    driver.get("https://www.google.com/?hl=id")
    driver.find_element(By.NAME, "q").send_keys(query)
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.NAME, "btnK"))
    ).click()

    reviews_header = driver.find_element(By.CSS_SELECTOR, "div.kp-header")
    reviews_link = reviews_header.find_element(By.PARTIAL_LINK_TEXT, "ulasan Google")
    number_of_reviews = int(reviews_link.text.replace(".", "").split()[0])
    reviews_link.click()

    all_reviews = WebDriverWait(driver, 3).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.gws-localreviews__google-review")
        )
    )
    start = time.time()
    last = 0
    while len(all_reviews) < number_of_reviews:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", all_reviews[-1])
            WebDriverWait(driver, 5, 0.25).until_not(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[class$="activityIndicator"]')
                )
            )
            all_reviews = driver.find_elements(
                By.CSS_SELECTOR, "div.gws-localreviews__google-review"
            )
            now = time.time()
            print(
                f"loading {len ( all_reviews )} reviews of {number_of_reviews} running for {floor ( now - start )} seconds "
            )
            print(len(all_reviews), " from ", number_of_reviews)
            if len(all_reviews) != last:
                writetocsv(all_reviews)
                last = len(all_reviews)
        except Exception as e:
            print(e)
            driver.implicitly_wait(3)
            pass
    
    
    # quit driver here
    driver.quit()


def writetocsv(all_reviews):
    f = open("reviews.csv", "a", encoding="utf-8")
    wr = csv.writer(f)
    if len(all_reviews) <= 20:
        stop = 0
    else:
        stop = len(all_reviews) - 11
    for i in range(len(all_reviews) - 1, stop, -1):
        try:
            wr.writerow(
                [
                    all_reviews[i]
                    .find_element(By.CSS_SELECTOR, "span.review-full-text")
                    .get_attribute("textContent")
                ]
            )
        except NoSuchElementException:
            try:
                wr.writerow(
                    [
                        all_reviews[i]
                        .find_element(By.CSS_SELECTOR, "span[data-expandable-section]")
                        .get_attribute("textContent")
                    ]
                )
            except NoSuchElementException:
                print("Review has no comment")
                pass
    f.close()


if __name__ == "__main__":
    # binary = "C:\\Users\\loren\\AppData\\Local\\Mozilla Firefox\\firefox.exe"
    asyncio.run(extract_google_reviews(place))