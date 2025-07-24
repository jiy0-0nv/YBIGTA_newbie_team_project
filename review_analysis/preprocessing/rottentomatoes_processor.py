import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

class RottentomatoesProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = None
        self.tfidf_vectorizer = None

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

        # 1) 기존 파생 변수
        df['text_length'] = df['content'].str.len()
        release_date = datetime(2022, 5, 27)
        df['days_since_release'] = (df['date'] - release_date).dt.days

        # 2) TF‑IDF 벡터화
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        tfidf_mat = self.tfidf_vectorizer.fit_transform(df['content'])
        tfidf_df = pd.DataFrame(
            tfidf_mat.toarray(),
            columns=[f"tfidf_{term}" for term in self.tfidf_vectorizer.get_feature_names_out()]
        )
        tfidf_df.index = df.index
        df = pd.concat([df, tfidf_df], axis=1)

        self.df = df

    def save_to_database(self):
        # 처리된 데이터를 CSV로 저장
        self.df.to_csv(self.output_path, index=False)
