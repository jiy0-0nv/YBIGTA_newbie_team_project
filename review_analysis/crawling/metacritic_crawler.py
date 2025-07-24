import os
from .base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd 

class MetacriticCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://www.metacritic.com/movie/top-gun-maverick/'
        self.driver = None
        self.reviews_data = None
        
    def start_browser(self):
        # Chrome 옵션 설정
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 필요시 주석 해제

        # 새로운 방식으로 드라이버 생성
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        # options.add_argument('--headless')

        service = Service()
        self.driver = webdriver.Chrome(service=service, options=options)

        url = "https://www.metacritic.com/movie/top-gun-maverick/user-reviews/"
        self.driver.get(url)  # headers 파라미터 제거
    
    def scrape_reviews(self):
        '''
        별점, 날짜, 리뷰 크롤링
        '''
        self.start_browser()
        # 끝까지 스크롤
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # 페이지 끝까지 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 새 내용 로딩 대기
            time.sleep(2)
            # 새로운 높이 계산
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 높이가 같으면 더 이상 로드할 내용이 없음
            if new_height == last_height:
                break
            
            last_height = new_height

        print("모든 내용 로드 완료!")

        # 이제 전체 HTML 가져오기
        html = self.driver.page_source

        # print(html)
        from bs4 import BeautifulSoup

        # ... (Selenium으로 html 받아오는 부분은 동일)

        soup = BeautifulSoup(html, "html.parser")

        # 리뷰 블록 전체 선택
        review_blocks = soup.select("div.c-pageProductReviews_row.g-outer-spacing-bottom-xxlarge > div")
        
        # 데이터를 저장할 리스트 생성
        self.reviews_data = []

        for block in review_blocks:
            # 1. 점수 추출
            score = block.select_one("div.c-siteReviewHeader_reviewScore span")
            score_text = score.get_text(strip=True) if score else "점수 없음"
            
            # 2. 작성자 추출
            author = block.select_one("a.c-siteReviewHeader_username")
            author_text = author.get_text(strip=True) if author else "작성자 없음"
            
            # 3. 작성일 추출
            date = block.select_one("div.c-siteReviewHeader_reviewDate.g-color-gray80.u-text-uppercase")
            date_text = date.get_text(strip=True) if date else "날짜 없음"
            
            # 4. 리뷰 내용 추출
            review_content = block.select_one("div:nth-child(2) > div > span")
            content_text = review_content.get_text(strip=True) if review_content else "내용 없음"
            
            # 결과 출력
            print(f"점수: {score_text}")
            print(f"작성자: {author_text}")
            print(f"작성일: {date_text}")
            print(f"리뷰: {content_text}")
            print("-" * 50)

                # 데이터 딕셔너리로 저장
            self.reviews_data.append({
                'score': score_text,
                'author': author_text,
                'date': date_text,
                'review': content_text
            })

        self.driver.quit()
            
    def save_to_database(self):
        # DataFrame 생성 및 CSV 저장
        csv_path = os.path.join(self.output_dir, 'reviews_metacritic.csv')
        df = pd.DataFrame(self.reviews_data)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print("CSV 파일 저장 완료!")

