import os
import glob
from argparse import ArgumentParser
from typing import Dict, Type
from review_analysis.preprocessing.base_processor import BaseDataProcessor
from review_analysis.preprocessing.metacritic_processor import MetacriticProcessor
from review_analysis.preprocessing.rottentomatoes_processor import RottentomatoesProcessor
from review_analysis.preprocessing.imdb_processor import IMDBProcessor


# 모든 preprocessing 클래스를 예시 형식으로 적어주세요. 
# key는 "reviews_사이트이름"으로, value는 해당 처리를 위한 클래스
PREPROCESS_CLASSES: Dict[str, Type[BaseDataProcessor]] = {
    "reviews_metacritic" : MetacriticProcessor,
    "reviews_rottentomatoes": RottentomatoesProcessor,
    "reviews_imdb": IMDBProcessor
    # key는 크롤링한 csv파일 이름으로 적어주세요! ex. reviews_naver.csv -> reviews_naver
}

# 파일위치 기준 탐색
script_dir = os.path.dirname(os.path.abspath(__file__))
REVIEW_COLLECTIONS = glob.glob(os.path.join(script_dir,"..","..","database", "reviews_*.csv"))

def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-o', '--output_dir', type=str, required=False, default = "../../database", help="Output file dir. Example: ../../database")
    parser.add_argument('-c', '--preprocessor', type=str, required=False, choices=PREPROCESS_CLASSES.keys(),
                        help=f"Which processor to use. Choices: {', '.join(PREPROCESS_CLASSES.keys())}")
    parser.add_argument('-a', '--all', action='store_true',
                        help="Run all data preprocessors. Default to False.")    
    return parser

if __name__ == "__main__":

    parser = create_parser()
    args = parser.parse_args()
    # 파일위치기준 경로설정
    args.output_dir = os.path.join(script_dir,args.output_dir)

    os.makedirs(args.output_dir, exist_ok=True)
    if args.all: 
        for csv_file in REVIEW_COLLECTIONS:
            base_name = os.path.splitext(os.path.basename(csv_file))[0]
            if base_name in PREPROCESS_CLASSES:
                preprocessor_class = PREPROCESS_CLASSES[base_name]
                preprocessor = preprocessor_class(csv_file, args.output_dir)
                preprocessor.preprocess()
                preprocessor.feature_engineering()
                preprocessor.save_to_database()
