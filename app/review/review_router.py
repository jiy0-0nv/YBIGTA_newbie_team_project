from fastapi import APIRouter, HTTPException
from pymongo.collection import Collection
from database.mongodb_connection import mongo_db, mongo_client
from review_analysis.preprocessing.main import PREPROCESS_CLASSES

import pandas as pd
import tempfile, os

router = APIRouter()

@router.post("/preprocess/{site_name}")
async def preprocess(site_name: str):
    raw_collection_name = f"reviews_{site_name}"
    raw_coll: Collection = mongo_db[raw_collection_name]
    if raw_coll.count_documents({}) == 0:
        raise HTTPException(status_code=404, detail="원본 데이터가 없습니다")

    # MongoDB → DataFrame
    raw_docs = list(raw_coll.find({}))
    df_raw = pd.DataFrame(raw_docs)

    # 전처리 클래스 매핑
    processor_cls = PREPROCESS_CLASSES.get(raw_collection_name)
    if not processor_cls:
        raise HTTPException(status_code=400, detail="지원하지 않는 사이트입니다")

    # 임시 CSV로 저장
    tmp_dir = tempfile.mkdtemp()
    tmp_csv = os.path.join(tmp_dir, f"{raw_collection_name}.csv")
    df_raw.to_csv(tmp_csv, index=False, encoding="utf-8")

    # 전처리 실행
    processor = processor_cls(tmp_csv, tmp_dir)
    processor.preprocess()
    processor.feature_engineering()

    # pandas 타입을 Python 기본 타입으로 변환
    processed_docs = []
    for rec in processor.df.to_dict(orient="records"):
        norm = {}
        for k, v in rec.items():
            # NaT → None
            if v is pd.NaT:
                norm[k] = None
            # pandas.Timestamp → datetime.datetime
            elif isinstance(v, pd.Timestamp):
                norm[k] = v.to_pydatetime()
            else:
                norm[k] = v
        processed_docs.append(norm)

    # 파일로도 저장하고 싶다면
    # processor.save_to_database()

    # MongoDB에 저장
    pre_db = mongo_client.get_database("preprocessed_reviews")
    target_coll: Collection = pre_db[site_name]
    if processed_docs:
        target_coll.insert_many(processed_docs)

    return {"inserted_count": len(processed_docs)}