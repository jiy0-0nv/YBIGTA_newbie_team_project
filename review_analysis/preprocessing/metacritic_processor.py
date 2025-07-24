from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd
import re
import emoji
from sklearn.feature_extraction.text import TfidfVectorizer
import os

class MetacriticProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)

    def preprocess(self):
        '''
            결측치 제거, 이상치 처리, 텍스트데이터 전처리
        '''
        # CSV 파일 불러오기
        self.df = pd.read_csv(self.input_path)
        
        # 1. 결측치 제거
        self.df = self.df.dropna()
        
        # 2. 이상치 처리 (예: 점수가 0-10 범위를 벗어나는 경우)
        self.df = self.df[(self.df['score'] >= 0) & (self.df['score'] <= 10)]
        
        # 3. 텍스트 데이터에서 이모지 제거
        if 'review' in self.df.columns:
            self.df['review'] = self.df['review'].apply(self._remove_emoji)

    def _remove_emoji(self, text):
        '''
        텍스트에서 이모지 제거
        '''
        if pd.isna(text):
            return text
        # emoji 라이브러리 사용
        return emoji.replace_emojis(text, replace='')

    def feature_engineering(self):
        '''
        새로운 피처 생성
        '''
        # 1. hatescore: 3점 이하 리뷰의 길이에 루트 씌운 값
        low_score_mask = self.df['score'] <= 3
        self.df['hatescore'] = 0  # 기본값 0으로 초기화
        
        # 3점 이하 리뷰에 대해서만 hatescore 계산
        self.df.loc[low_score_mask, 'hatescore'] = np.sqrt(
            self.df.loc[low_score_mask, 'review'].str.len()
        )
        
        # 2. 리뷰 텍스트 벡터화 (TF-IDF)
        vectorizer = TfidfVectorizer(
            max_features=100,  # 최대 100개 단어
            stop_words='english',  # 영어 불용어 제거
            ngram_range=(1, 2)  # 1-gram과 2-gram 사용
        )
        
        # 리뷰 텍스트 벡터화
        review_vectors = vectorizer.fit_transform(self.df['review'])
        
        # 벡터화된 결과를 데이터프레임으로 변환
        vector_df = pd.DataFrame(
            review_vectors.toarray(),
            columns=[f'vector_{i}' for i in range(review_vectors.shape[1])]
        )
        
        # 원본 데이터프레임에 벡터 컬럼들 추가
        self.df = pd.concat([self.df, vector_df], axis=1)
        
        print("피처 엔지니어링 완료!")
        print(f"새로 생성된 컬럼 수: {len(vector_df.columns) + 1}")  # hatescore + 벡터 컬럼들        

    def save_to_database(self):
        output_filename = "preprocessed_reviews_metacritic.csv"
        output_path = os.path.join(self.output_dir, output_filename)
        self.df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print("저장 완료!")

