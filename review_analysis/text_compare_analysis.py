import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
import numpy as np
import os
from typing import Dict, List, Tuple

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'  # macOS용
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

class ReviewSentimentAnalyzer:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.database_path = os.path.join(script_dir,"..","database")
        self.results = {}
        
    def load_preprocessed_files(self) -> Dict[str, pd.DataFrame]:
        """전처리된 파일들을 로드합니다."""
        files = {
            'IMDB': 'preprocessed_reviews_imdb.csv',
            'Metacritic': 'preprocessed_reviews_metacritic.csv', 
            'Rotten Tomatoes': 'preprocessed_reviews_rottentomatoes.csv'
        }
        
        dataframes = {}
        for site_name, filename in files.items():
            file_path = os.path.join(self.database_path, filename)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                dataframes[site_name] = df
                print(f"✅ {site_name}: {len(df)} 리뷰 로드됨")
            else:
                print(f"❌ {filename} 파일을 찾을 수 없습니다.")
                
        return dataframes
    
    def analyze_sentiment(self, text: str) -> float:
        """TextBlob을 사용하여 텍스트의 감정 점수를 계산합니다."""
        if pd.isna(text) or text == '':
            return 0.0
        try:
            blob = TextBlob(str(text))
            return blob.sentiment.polarity
        except:
            return 0.0
    
    def categorize_sentiment(self, polarity: float) -> str:
        """감정 점수를 긍정/부정/중립으로 분류합니다."""
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    
    def analyze_site_sentiments(self, df: pd.DataFrame, site_name: str) -> Dict:
        """특정 사이트의 감정분석을 수행합니다."""
        print(f"\n📊 {site_name} 감정분석 중...")
        
        # content 컬럼이 있는지 확인
        if 'content' not in df.columns:
            print(f"❌ {site_name}: 'content' 컬럼을 찾을 수 없습니다.")
            return {}
        
        # 감정분석 수행
        df['sentiment_polarity'] = df['content'].apply(self.analyze_sentiment)
        df['sentiment_category'] = df['sentiment_polarity'].apply(self.categorize_sentiment)
        
        # 결과 계산
        total_reviews = len(df)
        sentiment_counts = df['sentiment_category'].value_counts()
        
        results = {
            'total_reviews': total_reviews,
            'positive_count': sentiment_counts.get('Positive', 0),
            'negative_count': sentiment_counts.get('Negative', 0),
            'neutral_count': sentiment_counts.get('Neutral', 0),
            'positive_ratio': sentiment_counts.get('Positive', 0) / total_reviews * 100,
            'negative_ratio': sentiment_counts.get('Negative', 0) / total_reviews * 100,
            'neutral_ratio': sentiment_counts.get('Neutral', 0) / total_reviews * 100,
            'avg_polarity': df['sentiment_polarity'].mean()
        }
        
        print(f"✅ {site_name} 분석 완료:")
        print(f"   - 총 리뷰: {total_reviews:,}개")
        print(f"   - 긍정: {results['positive_count']:,}개 ({results['positive_ratio']:.1f}%)")
        print(f"   - 부정: {results['negative_count']:,}개 ({results['negative_ratio']:.1f}%)")
        print(f"   - 중립: {results['neutral_count']:,}개 ({results['neutral_ratio']:.1f}%)")
        print(f"   - 평균 감정점수: {results['avg_polarity']:.3f}")
        
        return results
    
    def create_comparison_plot(self, results: Dict[str, Dict]):
        """사이트별 긍정/부정 비율을 비교하는 막대그래프를 생성합니다."""
        if not results:
            print("❌ 분석할 데이터가 없습니다.")
            return
        
        # 데이터 준비
        sites = list(results.keys())
        positive_ratios = [results[site]['positive_ratio'] for site in sites]
        negative_ratios = [results[site]['negative_ratio'] for site in sites]
        neutral_ratios = [results[site]['neutral_ratio'] for site in sites]
        
        # 그래프 설정
        plt.figure(figsize=(12, 8))
        
        # 막대 그래프 생성
        x = np.arange(len(sites))
        width = 0.25
        
        plt.bar(x - width, positive_ratios, width, label='긍정', color='#2E8B57', alpha=0.8)
        plt.bar(x, negative_ratios, width, label='부정', color='#DC143C', alpha=0.8)
        plt.bar(x + width, neutral_ratios, width, label='중립', color='#808080', alpha=0.8)
        
        # 그래프 꾸미기
        plt.xlabel('리뷰 사이트', fontsize=12, fontweight='bold')
        plt.ylabel('비율 (%)', fontsize=12, fontweight='bold')
        plt.title('사이트별 리뷰 감정분석 결과 비교', fontsize=14, fontweight='bold', pad=20)
        plt.xticks(x, sites, fontsize=11)
        plt.legend(fontsize=11)
        plt.grid(axis='y', alpha=0.3)
        
        # 값 표시
        for i, site in enumerate(sites):
            plt.text(i - width, positive_ratios[i] + 1, f'{positive_ratios[i]:.1f}%', 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
            plt.text(i, negative_ratios[i] + 1, f'{negative_ratios[i]:.1f}%', 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
            plt.text(i + width, neutral_ratios[i] + 1, f'{neutral_ratios[i]:.1f}%', 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def run_analysis(self):
        """전체 분석을 실행합니다."""
        print("🔍 리뷰 감정분석 시작...\n")
        
        # 파일 로드
        dataframes = self.load_preprocessed_files()
        
        if not dataframes:
            print("❌ 분석할 파일이 없습니다.")
            return
        
        # 각 사이트별 감정분석
        for site_name, df in dataframes.items():
            results = self.analyze_site_sentiments(df, site_name)
            if results:
                self.results[site_name] = results
        
        # 비교 그래프 생성
        if self.results:
            print("\n📈 비교 그래프 생성 중...")
            self.create_comparison_plot(self.results)
        else:
            print("❌ 분석 결과가 없습니다.")

def main():
    """메인 실행 함수"""
    analyzer = ReviewSentimentAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
