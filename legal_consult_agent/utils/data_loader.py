"""
資料載入器 - 讀取JSON資料並寫入Vector Store
"""

import json
import os
import hashlib
from typing import Any
from langchain_core.documents import Document

# 延遲導入以避免循環依賴和環境變數問題
def get_vector_stores():
    from .tools import criminal_vector_store, money_debt_vector_store, marriage_vector_store
    return criminal_vector_store, money_debt_vector_store, marriage_vector_store

def get_embeddings():
    from .embeddings import embeddings
    return embeddings

def calculate_file_hash(file_path: str) -> str:
    """
    計算檔案內容的MD5雜湊值
    
    Args:
        file_path: 檔案路徑
        
    Returns:
        str: MD5雜湊值
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()
    except FileNotFoundError:
        return ""

def get_collection_count(vector_store) -> int:
    """
    獲取collection中的文件數量
    
    Args:
        vector_store: ChromaDB vector store
        
    Returns:
        int: 文件數量
    """
    try:
        # 嘗試獲取collection中的所有文件
        results = vector_store.similarity_search("", k=1000)  # 使用空查詢獲取所有文件
        return len(results)
    except Exception:
        return 0

def is_collection_empty(vector_store) -> bool:
    """
    檢查collection是否為空
    
    Args:
        vector_store: ChromaDB vector store
        
    Returns:
        bool: 是否為空
    """
    return get_collection_count(vector_store) == 0

def save_data_hash(file_path: str, hash_value: str):
    """
    儲存檔案雜湊值到本地檔案
    
    Args:
        file_path: 原始檔案路徑
        hash_value: 雜湊值
    """
    hash_file = file_path + ".hash"
    try:
        with open(hash_file, 'w', encoding='utf-8') as f:
            f.write(hash_value)
    except Exception as e:
        print(f"無法儲存雜湊值: {e}")

def load_data_hash(file_path: str) -> str:
    """
    從本地檔案載入雜湊值
    
    Args:
        file_path: 原始檔案路徑
        
    Returns:
        str: 雜湊值，如果檔案不存在則返回空字串
    """
    hash_file = file_path + ".hash"
    try:
        with open(hash_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"無法載入雜湊值: {e}")
        return ""

def should_reload_data(file_path: str, vector_store, force_reload: bool = False) -> bool:
    """
    判斷是否需要重新載入資料
    
    Args:
        file_path: JSON檔案路徑
        vector_store: ChromaDB vector store
        force_reload: 是否強制重新載入
        
    Returns:
        bool: 是否需要重新載入
    """
    if force_reload:
        print(f"  強制重新載入模式")
        return True
    
    # 檢查collection是否為空
    if is_collection_empty(vector_store):
        print(f"  Collection為空，需要載入資料")
        return True
    
    # 檢查檔案是否已更改
    current_hash = calculate_file_hash(file_path)
    stored_hash = load_data_hash(file_path)
    
    if current_hash != stored_hash:
        print(f"  檔案內容已更改，需要重新載入")
        return True
    
    print(f"  檔案內容未更改，跳過載入")
    return False

def load_json_data(file_path: str) -> list[dict[str, Any]]:
    """
    讀取JSON檔案並返回資料列表
    
    Args:
        file_path: JSON檔案路徑
        
    Returns:
        list[dict]: JSON資料列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功讀取 {file_path}，共 {len(data)} 筆資料")
        return data
    except FileNotFoundError:
        print(f"檔案不存在: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析錯誤: {e}")
        return []

def create_documents_from_data(data: list[dict[str, Any]]) -> list[Document]:
    """
    將JSON資料轉換為LangChain Document格式
    
    Args:
        data: JSON資料列表
        
    Returns:
        list[Document]: Document物件列表
    """
    documents = []
    
    for item in data:
        # 組合內容用於embedding
        content = f"標題: {item.get('title', '')}\n\n內容: {item.get('content', '')}\n\n分類: {item.get('category', '')}\n\n標籤: {', '.join(item.get('tags', []))}"
        
        # 創建metadata (ChromaDB不支援list類型，將tags轉為字串)
        metadata = {
            'id': item.get('id', ''),
            'title': item.get('title', ''),
            'category': item.get('category', ''),
            'tags': ', '.join(item.get('tags', [])),  # 將list轉為字串
            'relevance_score': item.get('relevance_score', 0.0)
        }
        
        # 創建Document
        doc = Document(
            page_content=content,
            metadata=metadata
        )
        documents.append(doc)
    
    return documents

def load_data_to_vector_store(force_reload: bool = False):
    """
    讀取所有JSON檔案並寫入對應的vector store collection
    
    Args:
        force_reload: 是否強制重新載入所有資料
    """
    # 獲取vector stores
    criminal_vector_store, money_debt_vector_store, marriage_vector_store = get_vector_stores()
    
    # 定義檔案路徑和對應的vector store
    data_configs = [
        {
            'file_path': './vectorDB/data/criminal.json',
            'vector_store': criminal_vector_store,
            'collection_name': 'criminal_collection'
        },
        {
            'file_path': './vectorDB/data/money_debt.json', 
            'vector_store': money_debt_vector_store,
            'collection_name': 'money_debt_collection'
        },
        {
            'file_path': './vectorDB/data/marriage.json',
            'vector_store': marriage_vector_store,
            'collection_name': 'marriage_collection'
        }
    ]
    
    total_loaded = 0
    total_skipped = 0
    
    for config in data_configs:
        print(f"\n處理 {config['collection_name']}...")
        
        # 檢查是否需要重新載入
        if not should_reload_data(config['file_path'], config['vector_store'], force_reload):
            total_skipped += 1
            continue
        
        # 讀取JSON資料
        json_data = load_json_data(config['file_path'])
        
        if not json_data:
            print(f"跳過 {config['collection_name']} - 無有效資料")
            continue
            
        # 轉換為Document格式
        documents = create_documents_from_data(json_data)
        
        # 寫入vector store
        try:
            # 如果是強制重新載入，先清空collection
            if force_reload:
                try:
                    # 直接重置collection
                    config['vector_store'].reset_collection()
                    print(f"  已重置 {config['collection_name']}")
                except Exception as e:
                    print(f"  重置collection時發生錯誤: {e}")
            
            # 添加文件到collection
            config['vector_store'].add_documents(documents)
            print(f"成功將 {len(documents)} 筆資料寫入 {config['collection_name']}")
            
            # 儲存檔案雜湊值
            current_hash = calculate_file_hash(config['file_path'])
            save_data_hash(config['file_path'], current_hash)
            
            total_loaded += 1
            
        except Exception as e:
            print(f"寫入 {config['collection_name']} 時發生錯誤: {e}")
    
    print(f"\n載入完成！共載入 {total_loaded} 個collection，跳過 {total_skipped} 個collection")

def clear_all_hash_files():
    """
    清理所有雜湊檔案
    """
    hash_files = [
        './vectorDB/data/criminal.json.hash',
        './vectorDB/data/money_debt.json.hash',
        './vectorDB/data/marriage.json.hash'
    ]
    
    cleared_count = 0
    for hash_file in hash_files:
        try:
            if os.path.exists(hash_file):
                os.remove(hash_file)
                print(f"已刪除雜湊檔案: {hash_file}")
                cleared_count += 1
        except Exception as e:
            print(f"刪除雜湊檔案時發生錯誤: {e}")
    
    print(f"共清理了 {cleared_count} 個雜湊檔案")

def get_collection_status():
    """
    獲取所有collection的狀態資訊
    """
    criminal_vector_store, money_debt_vector_store, marriage_vector_store = get_vector_stores()
    
    collections = [
        (criminal_vector_store, "criminal_collection", "./vectorDB/data/criminal.json"),
        (money_debt_vector_store, "money_debt_collection", "./vectorDB/data/money_debt.json"),
        (marriage_vector_store, "marriage_collection", "./vectorDB/data/marriage.json")
    ]
    
    print("\nCollection狀態:")
    print("-" * 60)
    
    for vector_store, name, file_path in collections:
        count = get_collection_count(vector_store)
        current_hash = calculate_file_hash(file_path)
        stored_hash = load_data_hash(file_path)
        hash_match = current_hash == stored_hash if stored_hash else False
        
        status = "✅ 已載入且檔案未更改" if count > 0 and hash_match else \
                "⚠️  已載入但檔案已更改" if count > 0 and not hash_match else \
                "❌ 未載入"
        
        print(f"{name:20} | 文件數: {count:3} | 狀態: {status}")
    
    print("-" * 60)

def test_vector_stores():
    """
    測試vector store是否正常運作
    """
    print("\n測試vector store檢索功能...")
    
    # 獲取vector stores
    criminal_vector_store, money_debt_vector_store, marriage_vector_store = get_vector_stores()
    
    test_queries = [
        "竊盜罪的刑責是什麼？",
        "離婚需要什麼條件？", 
        "債務不履行如何處理？"
    ]
    
    vector_stores = [
        (criminal_vector_store, "刑法"),
        (marriage_vector_store, "婚姻法"),
        (money_debt_vector_store, "債務法")
    ]
    
    for query in test_queries:
        print(f"\n查詢: {query}")
        for vector_store, name in vector_stores:
            try:
                results = vector_store.similarity_search(query, k=2)
                if results:
                    print(f"  {name}: 找到 {len(results)} 筆相關資料")
                    for i, doc in enumerate(results):
                        print(f"    {i+1}. {doc.metadata.get('title', '無標題')}")
                else:
                    print(f"  {name}: 無相關資料")
            except Exception as e:
                print(f"  {name}: 查詢錯誤 - {e}")

if __name__ == "__main__":
    # 載入資料到vector store
    load_data_to_vector_store()
    
    # 測試檢索功能
    test_vector_stores()
