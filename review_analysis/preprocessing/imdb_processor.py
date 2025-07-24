import os
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from review_analysis.preprocessing.base_processor import BaseDataProcessor


class IMDBProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = None
        self.tfidf_vectorizer = None
        self.output_path = output_path

    def preprocess(self):
        df = pd.read_csv(self.input_path, parse_dates=['date'])
        df = df.dropna(subset=['score', 'date', 'content'])
        df = df[['score', 'author', 'date', 'content']]
        df['text_length'] = df['content'].astype(str).str.len()
        df = df[df['text_length'] <= 3000]
        self.df = df.reset_index(drop=True)

    def feature_engineering(self):
        df = self.df.copy()
        df['text_length'] = df['content'].astype(str).str.len()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        release_date = datetime(2022, 5, 27)
        df['days_since_release'] = (df['date'] - release_date).dt.days

        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        tfidf_mat = self.tfidf_vectorizer.fit_transform(df['content'])

        df['tfidf_mean'] = tfidf_mat.mean(axis=1).A1
        df['tfidf_max'] = tfidf_mat.max(axis=1).toarray().ravel()
        df['tfidf_nnz'] = (tfidf_mat > 0).sum(axis=1).A1

        self.df = df

    def save_to_database(self):
        os.makedirs(self.output_path, exist_ok=True)
        file_path = os.path.join(
            self.output_path,
            "preprocessed_reviews_imdb.csv"
        )
        self.df.to_csv(file_path, index=False)
