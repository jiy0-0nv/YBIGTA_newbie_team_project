import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__)))))))
from utils.logger import setup_logger
from typing import List, Dict, Any

class RottentomatoesCrawler(BaseCrawler):
    reviews: List[Dict[str, Any]]
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.reviews = []  # type: List[Dict[str, Any]]
        self.base_url = 'https://www.rottentomatoes.com/m/top_gun_maverick/reviews?type=user'
        self.driver = None
        self.reviews = []
        log_path = os.path.join(self.output_dir, 'crawler.log')
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = setup_logger(log_path)

    def start_browser(self):
        self.logger.info('브라우저 시작')
        chrome_opts = Options()
        # chrome_opts.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_opts)

    def scrape_reviews(self):
        self.logger.info('로튼토마토 리뷰 크롤링 시작')
        self.start_browser()
        self.driver.get(self.base_url)
        time.sleep(2)

        page = 1
        while True:
            self.logger.debug(f'{page}페이지 소스 로드 완료')
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            blocks = soup.select('div.audience-review-row')
            self.logger.debug(f'{len(blocks)}개의 리뷰 블록을 발견했습니다.')
            
            for block in soup.select('div.audience-review-row'):
                # 유저명
                name_el = block.select_one('span.audience-reviews__name')
                if not name_el:
                    name_el = block.select_one('a.audience-reviews__name')
                user = name_el.text.strip() if name_el else None

                # 평점 (5 stars)
                star_tag = block.select_one('rating-stars-group')
                if star_tag and star_tag.has_attr('score'):
                    rating = float(star_tag['score'])
                else:
                    rating = None

                # 작성일
                date_el = block.select_one('span.audience-reviews__duration')
                date = date_el.text.strip() if date_el else None

                # 리뷰
                content_el = block.select_one('p.audience-reviews__review')
                content = content_el.text.strip() if content_el else None

                self.reviews.append({
                    'user': user,
                    'rating': rating,
                    'date': date,
                    'content': content
                })
                
            # Load More 버튼
            load_more = self.driver.find_elements(
                By.CSS_SELECTOR,
                'rt-button[data-qa="load-more-btn"]'
            )
            
            if page > 25:
                self.logger.warning('25페이지에 도달해 루프를 종료합니다.')
                break
            if load_more:
                page += 1
                self.logger.info(f'{page}페이지 추가 로드')
                self.driver.execute_script("arguments[0].click();", load_more[0])
                time.sleep(1)
            else:
                self.logger.info('더 불러올 리뷰가 없어 크롤링을 종료합니다.')
                break

        self.driver.quit()

    def save_to_database(self):
        self.logger.info('CSV 저장 시작')
        os.makedirs(self.output_dir, exist_ok=True)
        csv_path = os.path.join(self.output_dir, 'reviews_Rottentomatoes.csv')

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['user', 'rating', 'date', 'content'])
            writer.writeheader()
            for review in self.reviews:
                writer.writerow(review)

        self.logger.info(f'CSV 파일을 {csv_path}에 저장했습니다.')
