# 法律資料載入指南

## 功能說明
此腳本會讀取 `legal_consult_agent/vectorDB/data/` 目錄下的三個JSON檔案：
- `criminal.json` - 刑法相關資料
- `marriage.json` - 婚姻法相關資料  
- `money_debt.json` - 金錢債務法相關資料

並使用OpenAI的embedding模型將這些資料寫入對應的ChromaDB collection。

## 執行方式

### 方法1: 直接執行主腳本
```bash
python load_data.py
```

### 方法2: 在Python中執行
```python
from legal_consult_agent.utils.data_loader import load_data_to_vector_store, test_vector_stores

# 載入資料
load_data_to_vector_store()

# 測試檢索功能
test_vector_stores()
```

## 資料結構
每個JSON檔案包含以下欄位的法律條文：
- `id`: 唯一識別碼
- `title`: 法律條文標題
- `content`: 具體法律內容
- `category`: 法律分類
- `tags`: 相關標籤陣列
- `relevance_score`: 相關性分數

## Vector Store Collections
資料會被寫入以下三個collection：
- `criminal_collection` - 刑法資料
- `marriage_collection` - 婚姻法資料
- `money_debt_collection` - 債務法資料

## 注意事項
1. 確保已設定 `.env` 檔案並包含 `OPENAI_API_KEY`
2. 確保網路連線正常以使用OpenAI API
3. 首次執行會建立ChromaDB資料庫檔案
4. 重複執行會添加新資料到現有collection

## 測試功能
腳本執行後會自動測試檢索功能，使用以下測試查詢：
- "竊盜罪的刑責是什麼？"
- "離婚需要什麼條件？"
- "債務不履行如何處理？"
