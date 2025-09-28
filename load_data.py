"""
主要資料載入腳本
執行此腳本將讀取JSON資料並寫入Vector Store

使用方法:
uv run python load_data.py [選項]

選項:
--force: 強制重新載入所有資料，即使檔案未更改
--status: 顯示所有collection的狀態資訊
--clear-hash: 清理所有雜湊檔案（下次執行會重新載入所有資料）

範例:
uv run python load_data.py          # 正常載入（跳過未更改的檔案）
uv run python load_data.py --force  # 強制重新載入所有資料
uv run python load_data.py --status # 檢查collection狀態
uv run python load_data.py --clear-hash # 清理雜湊檔案
"""

import sys
from legal_consult_agent.utils.data_loader import (
    load_data_to_vector_store, 
    test_vector_stores, 
    get_collection_status,
    clear_all_hash_files
)

def main():
    """
    主執行函數
    """
    # 檢查命令列參數
    force_reload = "--force" in sys.argv
    show_status = "--status" in sys.argv
    clear_hash = "--clear-hash" in sys.argv
    
    if clear_hash:
        print("清理雜湊檔案...")
        clear_all_hash_files()
        return 0
    
    if show_status:
        print("檢查Collection狀態...")
        get_collection_status()
        return 0
    
    if force_reload:
        print("開始強制重新載入法律資料到Vector Store...")
    else:
        print("開始載入法律資料到Vector Store...")
    print("=" * 50)
    
    try:
        # 載入資料
        load_data_to_vector_store(force_reload=force_reload)
        
        # 測試檢索
        test_vector_stores()
        
        print("\n" + "=" * 50)
        if force_reload:
            print("強制重新載入完成！Vector Store已準備就緒。")
        else:
            print("資料載入完成！Vector Store已準備就緒。")
        
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
