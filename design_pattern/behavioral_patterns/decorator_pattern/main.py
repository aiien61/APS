import functools
import polars as pl
from collections import namedtuple
from typing import Iterable
from abc import ABC, abstractmethod
from icecream import ic

def validate_capacity(max_capacity: int):
    """
    Decorator: validate the schedule does not exceed 
    machine capacity limit
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # execute scheduling algorithm to get the result
            schedule_result = func(*args, **kwargs)

            # constraint check
            total_load: int = sum(item['hours'] for item in schedule_result)

            print(f"📊 [APS 驗證] 目前排程總負荷: {total_load} 小時 (上限: {max_capacity} 小時)")

            if total_load > max_capacity:
                print("❌ [警告] 排程無效：超出產能上限！將回傳空值或觸發警報。")
                return []
            
            print("✅ [驗證通過] 排程結果符合產能約束。")
            return schedule_result
        return wrapper
    return decorator


# core scheduling algorithm
@validate_capacity(max_capacity=50)
def generate_weekly_schedule(repo: "JobRepository"):
    """
    simulate APS scheduling result
    """
    jobs: list[dict] = repo.to_dicts()
    return jobs

class JobRepository(ABC):
    @abstractmethod
    def to_dicts(self): raise NotImplementedError

class PolarsJobRepository(JobRepository):
    def __init__(self, df: pl.DataFrame):
        self._df = df
    
    def to_dicts(self) -> list[dict]:
        return self._df.to_dicts()

def main():
    Job = namedtuple("Job", ['job_id', 'hours'])
    
    print("--- 測試 1：正常排程 ---")
    df = pl.DataFrame([Job("j1001", 10), Job("j1002", 20)])
    repo = PolarsJobRepository(df)
    generate_weekly_schedule(repo)

    print("\n--- 測試 2：超載排程 ---")
    df = pl.DataFrame([Job('j1003', 30), Job('j1004', 25)])
    repo = PolarsJobRepository(df)
    generate_weekly_schedule(repo)

if __name__ == "__main__":
    main()
