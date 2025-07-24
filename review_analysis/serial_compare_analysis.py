import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'  # macOS용
# plt.rcParams['font.family'] = 'Malgun Gothic' # Windows용
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

class TimeSeriesAnalyzer:
    def __init__(self):
        # 스크립트 실행 위치를 기준으로 경로 설정 (더 안정적)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.database_path = os.path.join(script_dir, "..", "database")
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
                try:
                    df = pd.read_csv(file_path)
                    dataframes[site_name] = df
                    print(f"✅ {site_name}: {len(df)} 리뷰 로드됨")
                except Exception as e:
                    print(f"❌ {site_name}: 파일 로드 중 오류 발생 - {e}")
            else:
                print(f"❌ {filename} 파일을 찾을 수 없습니다. (경로: {file_path})")
                
        return dataframes

    def debug_imdb_data(self, df: pd.DataFrame):
        """IMDB 데이터의 'days_since_release' 컬럼을 심층 분석합니다."""
        if df is None or 'days_since_release' not in df.columns:
            print("IMDB 데이터 또는 'days_since_release' 컬럼이 없습니다.")
            return

        print("\n🕵️‍♂️ IMDB 데이터 심층 분석 시작...")
        print("="*50)
        
        # 1. 데이터 타입 및 기본 정보 확인
        print("\n[1] 데이터프레임 정보 (.info()):")
        df.info()

        # 2. 'days_since_release' 컬럼의 기술 통계
        print("\n[2] 'days_since_release' 기술 통계 (.describe()):")
        print(df['days_since_release'].describe())

        # 3. 'days_since_release' 컬럼의 고유값과 개수 확인 (가장 중요!)
        print("\n[3] 'days_since_release' 고유값 분포 (.value_counts()):")
        value_counts = df['days_since_release'].value_counts().sort_index()
        print(value_counts)
        
        print("="*50)
        print("🕵️‍♂️ 분석 종료. 위 '고유값 분포'를 확인해주세요.\n")

        # 만약 고유값이 2개 뿐이라면, 이것이 원인일 가능성이 매우 높습니다.
        if len(value_counts) < 5:
             print("⚠️ 경고: 'days_since_release'의 고유값이 매우 적습니다.")
             print("   이것이 그래프가 수직/수평선으로 나타나는 원인일 가능성이 큽니다.")


    def process_time_data(self, df: pd.DataFrame, site_name: str) -> pd.DataFrame:
        """시간 데이터를 처리하고 정규화합니다."""
        print(f"\n📊 {site_name} 시간 데이터 처리 중...")
        
        time_columns = ['days_since_release', 'date', 'timestamp', 'time', 'created_at', 'review_date']
        time_col = next((col for col in time_columns if col in df.columns), None)
        
        if time_col is None:
            print(f"❌ {site_name}: 시간 컬럼을 찾을 수 없습니다.")
            return None
        
        try:
            if time_col == 'days_since_release':
                df['relative_time'] = pd.to_numeric(df[time_col], errors='coerce') * 24
                df.dropna(subset=['relative_time'], inplace=True)
                print(f"✅ {site_name}: days_since_release 컬럼을 시간으로 변환 완료")
            else:
                df['datetime'] = pd.to_datetime(df[time_col], errors='coerce')
                df = df.dropna(subset=['datetime'])
                
                if len(df) == 0:
                    print(f"❌ {site_name}: 유효한 시간 데이터가 없습니다.")
                    return None
                
                df = df.sort_values('datetime')
                time_diff = df['datetime'] - df['datetime'].min()
                df['relative_time'] = time_diff.dt.total_seconds() / 3600
            
            if 'relative_time' not in df or df['relative_time'].isnull().all():
                 print(f"❌ {site_name}: 'relative_time' 계산에 실패했습니다.")
                 return None

            total_hours = df['relative_time'].max()
            display_unit = "시간"
            display_total_time = total_hours
            if total_hours > 72:
                display_unit = "일"
                display_total_time = total_hours / 24

            print(f"✅ {site_name}: {len(df)} 개의 유효한 시간 데이터 처리 완료")
            if 'datetime' in df:
                print(f"   - 시간 범위: {df['datetime'].min()} ~ {df['datetime'].max()}")
            print(f"   - 총 시간: {display_total_time:.1f} {display_unit} ({total_hours:.1f} 시간)")
            
            return df
            
        except Exception as e:
            print(f"❌ {site_name}: 시간 데이터 처리 중 오류 발생 - {e}")
            return None
    
    def create_time_distribution_plot(self, dataframes: Dict[str, pd.DataFrame]):
        """정규화된 누적 리뷰 분포를 비교하는 그래프를 생성합니다."""
        if not dataframes:
            print("❌ 분석할 데이터가 없습니다.")
            return
        
        plt.figure(figsize=(15, 10))
        colors = {'IMDB': '#FF6B6B', 'Metacritic': '#4ECDC4', 'Rotten Tomatoes': '#45B7D1'}
        
        for site_name, df in dataframes.items():
            if df is None or len(df) < 2:
                print(f"⚠️ {site_name}: 데이터가 부족하여 그래프를 그릴 수 없습니다.")
                continue
                
            df_sorted = df.sort_values('relative_time')
            
            time_range = df_sorted['relative_time'].max() - df_sorted['relative_time'].min()
            
            if time_range == 0:
                print(f"⚠️ {site_name}: 모든 리뷰의 시간이 동일하여 정규화된 분포를 그릴 수 없습니다.")
                normalized_time = [0, 100]
                cumulative_percent = [100, 100]
            else:
                normalized_time = (df_sorted['relative_time'] - df_sorted['relative_time'].min()) / time_range * 100
                cumulative_percent = np.arange(1, len(df_sorted) + 1) / len(df_sorted) * 100
            
            plt.plot(normalized_time, cumulative_percent,
                    label=f'{site_name} ({len(df)}개)',
                    color=colors.get(site_name, '#000000'),
                    linewidth=2.5,
                    alpha=0.8)
    
        plt.xlabel('정규화된 시간 (%)', fontsize=12, fontweight='bold')
        plt.ylabel('누적 리뷰 비율 (%)', fontsize=12, fontweight='bold')
        plt.title('사이트별 정규화된 누적 리뷰 분포 비교', fontsize=14, fontweight='bold', pad=20)
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        
        plt.tight_layout()
        plt.show()
    
    def analyze_time_patterns(self, dataframes: Dict[str, pd.DataFrame]):
        """시간 패턴을 분석하고 통계를 출력합니다."""
        print("\n📈 시간 패턴 분석 결과:")
        print("=" * 60)
        
        for site_name, df in dataframes.items():
            if df is None or len(df) == 0:
                continue
                
            print(f"\n🎯 {site_name}:")
            
            total_time = df['relative_time'].max()
            total_reviews = len(df)
            
            if total_time <= 0:
                print("   - 전체 리뷰 기간이 0 또는 음수이므로 패턴 분석을 생략합니다.")
                continue

            avg_reviews_per_hour = total_reviews / total_time
            
            print(f"   - 총 리뷰 수: {total_reviews:,}개")
            print(f"   - 총 시간: {total_time:.1f}시간")
            print(f"   - 시간당 평균 리뷰: {avg_reviews_per_hour:.2f}개")
            
            time_bins = np.arange(0, total_time + 1, 1)
            hist, bin_edges = np.histogram(df['relative_time'], bins=time_bins)
            
            if len(hist) > 0:
                peak_hour = bin_edges[np.argmax(hist)]
                peak_reviews = np.max(hist)
                print(f"   - 피크 시간: {peak_hour:.1f}시간 (리뷰 {peak_reviews}개)")
            
            first_quarter_count = len(df[df['relative_time'] <= total_time * 0.25])
            last_quarter_count = len(df[df['relative_time'] >= total_time * 0.75])
            
            print(f"   - 첫 25% 시간: {first_quarter_count}개 리뷰 ({first_quarter_count/total_reviews*100:.1f}%)")
            print(f"   - 마지막 25% 시간: {last_quarter_count}개 리뷰 ({last_quarter_count/total_reviews*100:.1f}%)")
    
    def run_analysis(self):
        """전체 분석을 실행합니다."""
        print("🔍 시계열 리뷰 분석 시작...\n")
        
        dataframes = self.load_preprocessed_files()
        
        if not dataframes:
            print("❌ 분석할 파일이 없습니다.")
            return

        # IMDB 데이터가 있다면, 디버깅 함수를 먼저 호출
        if 'IMDB' in dataframes:
            self.debug_imdb_data(dataframes['IMDB'])
        
        processed_dataframes = {}
        for site_name, df in dataframes.items():
            processed_df = self.process_time_data(df, site_name)
            if processed_df is not None and not processed_df.empty:
                processed_dataframes[site_name] = processed_df
        
        if not processed_dataframes:
            print("❌ 처리할 수 있는 시간 데이터가 없습니다.")
            return
        
        self.analyze_time_patterns(processed_dataframes)
        
        print("\n📊 시각화 생성 중...")
        self.create_time_distribution_plot(processed_dataframes)

def main():
    """메인 실행 함수"""
    analyzer = TimeSeriesAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
