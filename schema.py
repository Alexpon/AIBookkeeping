from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class TransactionRecord(BaseModel):
    date: str = Field(..., description="消費日期 (YYYY-MM-DD)，如辨識出三位數年份為中華民國年，需要轉成西元年")
    description: str = Field(..., description="消費明細")
    amount: float = Field(..., description="消費金額，支出為正，收入為負")
    type: Literal['消費', '轉帳'] = Field(..., description="紀錄類型 (單選)")
    category: Optional[Literal['飲食', '日常用品', '交通', '旅遊', '儲值', '其他']] = Field(None, description="消費分類 (單選)")

class TransactionRecords(BaseModel):
    records: List[TransactionRecord]