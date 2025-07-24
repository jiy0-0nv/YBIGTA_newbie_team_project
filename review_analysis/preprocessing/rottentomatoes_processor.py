import os
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from review_analysis.preprocessing.base_processor import BaseDataProcessor


class RottentomatoesProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = None
        self.tfidf_vectorizer = None
        self.output_path = output_path

    def preprocess(self):
        # 1) 데이터 로드 및 결측치 처리
        df = pd.read_csv(self.input_path, parse_dates=['date'])
        df = df.dropna(subset=['rating', 'date', 'content'])
        df['user'] = df['user'].fillna('unknown')

        # 2) 스케일 변경 및 컬럼명 수정
        df['rating'] = df['rating'] * 2
        df = df.rename(columns={'rating': 'score', 'user': 'author'})

        # 3) 길이 기준 필터링
        df['text_length'] = df['content'].str.len()
        df = df[(df['text_length'] >= 10) & (df['text_length'] <= 1000)]

        self.df = df.reset_index(drop=True)

    def feature_engineering(self):
        df = self.df.copy()

        # 1) 파생 변수 추가
        # - 리뷰 텍스트 길이
        df['text_length'] = df['content'].str.len()
        # - 영화 개봉일 대비 작성일 차이
        release_date = datetime(2022, 5, 27)
        df['days_since_release'] = (df['date'] - release_date).dt.days

        # 2) TF‑IDF 벡터화
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000,
                                                ngram_range=(1, 2),
                                                stop_words='english')
        tfidf_mat = self.tfidf_vectorizer.fit_transform(df['content'])

        # 3) 파생 변수로 요약 지표 추가
        # - tfidf_mean: 각 문서의 평균 TF‑IDF 스코어
        # - tfidf_max : 각 문서의 최대 TF‑IDF 스코어
        # - tfidf_nnz : 각 문서의 비제로 TF‑IDF 피처 개수
        df['tfidf_mean'] = tfidf_mat.mean(axis=1).A1
        df['tfidf_max']  = tfidf_mat.max(axis=1).toarray().ravel()
        df['tfidf_nnz']  = (tfidf_mat > 0).sum(axis=1).A1

        self.df = df

    def save_to_database(self):
        os.makedirs(self.output_path, exist_ok=True)
        file_path = os.path.join(
            self.output_path,
            "preprocessed_reviews_rottentomatoes.csv"
        )
        self.df.to_csv(file_path, index=False)
