import os
import sys
import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from review_analysis.crawling.base_crawler import BaseCrawler
from utils.logger import setup_logger


class IMDBCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = "https://www.imdb.com/title/tt1745960/reviews?ref_=tt_ql_3"
        self.driver = None
        self.reviews = []
        log_path = os.path.join(self.output_dir, "crawler_imdb.log")
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = setup_logger(log_path)

    def start_browser(self):
        options = Options()
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=options)
        self.logger.info("Chrome 브라우저 실행 성공")

    def scroll_reviews(self, limit=500):
        last_count = 0
        for _ in range(30):
            review_elements = self.driver.find_elements(By.CSS_SELECTOR, "article")
            current_count = len(review_elements)
            self.logger.info(f"{current_count}개의 리뷰 블록 발견")
            if current_count >= limit or current_count == last_count:
                break
            try:
                more_btn = self.driver.find_element(By.XPATH, "//span[text()='25 more']")
                self.driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(2.5)
                last_count = current_count
            except:
                break

    def scrape_reviews(self):
        self.start_browser()
        self.driver.get(self.base_url)
        time.sleep(2)
        self.scroll_reviews(limit=500)

        review_elements = self.driver.find_elements(By.CSS_SELECTOR, "article")
        self.logger.info(f"리뷰 블럭 {len(review_elements)}개 발견")

        for i, elem in enumerate(review_elements):
            try:
                # 스포일러 해제
                try:
                    spoiler = elem.find_element(By.XPATH, ".//span[text()='Spoiler']/..")
                    self.driver.execute_script("arguments[0].click();", spoiler)
                    time.sleep(0.3)
                except NoSuchElementException:
                    pass

                # 작성자
                try:
                    author = elem.find_element(
                        By.CSS_SELECTOR, "div[data-testid='reviews-author'] a[data-testid='author-link']"
                    ).text.strip()
                except NoSuchElementException:
                    author = "작성자 정보 없음"

                # 날짜
                try:
                    date = elem.find_element(
                        By.CSS_SELECTOR, "div[data-testid='reviews-author'] li.review-date"
                    ).text.strip()
                except NoSuchElementException:
                    date = "날짜 정보 없음"

                # 별점
                try:
                    score = elem.find_element(
                        By.CSS_SELECTOR, "span.review-rating span.ipc-rating-star--rating"
                    ).text.strip()
                except NoSuchElementException:
                    score = "별점 없음"

                # 제목 + 내용
                try:
                    title = elem.find_element(
                        By.CSS_SELECTOR, "div[data-testid='review-summary'] h3"
                    ).text.strip()
                except NoSuchElementException:
                    title = ""

                try:
                    content = elem.find_element(
                        By.CSS_SELECTOR, "div.ipc-html-content-inner-div"
                    ).text.strip()
                except NoSuchElementException:
                    content = ""

                full_content = f"{title}\n{content}".strip()

                self.reviews.append({
                    "author": author,
                    "date": date,
                    "score": score,
                    "content": full_content
                })

            except Exception as e:
                self.logger.warning(f"{i+1}번 리뷰 처리 실패: {e}")

        self.logger.info(f"총 수집 리뷰 수: {len(self.reviews)}")
        self.driver.quit()

    def save_to_database(self):
        csv_path = os.path.join(self.output_dir, 'reviews_imdb.csv')
        pd.DataFrame(self.reviews).to_csv(csv_path, index=False, encoding='utf-8-sig')
        self.logger.info(f"리뷰 CSV 저장 완료: {csv_path}")
