import time
import functools
import random

def exponential_backoff(max_retries: int = 3, base_delay: int = 1):
    """
    Decorator: MAS exponential backoffs and retries when connection failed
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries: int = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        print(f"🚨 [MAS] 已達最大重試次數 {max_retries}，放棄通訊。")
                        raise e
                    
                    # calculate waiting time: base_delay * (2 ^ (retries - 1))
                    delay = base_delay * (2 ** (retries - 1))
                    print(f"⚠️  [MAS] 通訊失敗: {e}。第 {retries} 次重試，等待 {delay} 秒...")
                    time.sleep(delay)
        return wrapper
    return decorator

# MAS Agent 
@exponential_backoff(max_retries=4, base_delay=0.5)
def send_message_to_agent(target_id: str, message: str) -> bool:
    """
    Simulate message exchange in between agents
    """
    # simulate 70% failure percentage
    if random.random() < 0.7:
        raise ConnectionError("連線逾時 (Timeout)")
    print(f"📩 [MAS] 訊息已成功送達 Agent {target_id}: {message}")
    return True

def main():
    print("--- 開始執行 MAS Agent 通訊 (含自動重試機制) ---")
    try:
        send_message_to_agent("Product_Agent", "要求同步機台狀態")
    except ConnectionError:
        print("最終處理：通訊徹底失敗，啟動備援路徑。")


if __name__ == "__main__":
    main()
