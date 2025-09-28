"""
法律諮詢聊天機器人API服務器
整合FastAPI應用和啟動功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import uuid
import uvicorn
import sys
import os
import time
from legal_consult_agent.agent import graph

# 創建FastAPI應用
app = FastAPI(
    title="法律諮詢聊天機器人API",
    description="基於LangGraph的法律諮詢服務",
    version="1.0.0"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 請求模型
class ChatRequest(BaseModel):
    question: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = None

# 響應模型
class ChatResponse(BaseModel):
    answer: str
    thread_id: str
    user_id: Optional[str] = None
    processing_time: float
    status: str = "success"

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status: str = "error"

# 健康檢查端點
@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "legal-consultation-api"}

# 聊天端點
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    法律諮詢聊天端點
    
    Args:
        request: 包含問題和可選的thread_id、user_id
        
    Returns:
        ChatResponse: 包含回答和相關資訊
    """
    start_time = time.time()
    
    try:
        # 生成thread_id如果沒有提供
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # 準備配置
        config = {"configurable": {"thread_id": thread_id}}
        
        # 調用agent graph
        result = await graph.ainvoke(
            input={"question": request.question},
            config=config,
        )
        
        # 提取回答
        if result and "messages" in result and result["messages"]:
            answer = result["messages"][-1].content
        else:
            answer = "抱歉，我無法處理您的問題。"
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            answer=answer,
            thread_id=thread_id,
            user_id=request.user_id,
            processing_time=round(processing_time, 2),
            status="success"
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"處理請求時發生錯誤: {str(e)}"
        )

# 批量聊天端點
@app.post("/chat/batch", response_model=List[ChatResponse])
async def chat_batch(requests: List[ChatRequest]):
    """
    批量法律諮詢聊天端點
    
    Args:
        requests: 包含多個問題的請求列表
        
    Returns:
        List[ChatResponse]: 包含所有回答的列表
    """
    start_time = time.time()
    
    try:
        results = []
        
        # 並行處理所有請求
        tasks = []
        for request in requests:
            task = process_single_chat(request)
            tasks.append(task)
        
        # 等待所有任務完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理結果
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ChatResponse(
                    answer=f"處理第{i+1}個問題時發生錯誤: {str(result)}",
                    thread_id=requests[i].thread_id or str(uuid.uuid4()),
                    user_id=requests[i].user_id,
                    processing_time=0.0,
                    status="error"
                ))
            else:
                final_results.append(result)
        
        return final_results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量處理請求時發生錯誤: {str(e)}"
        )

async def process_single_chat(request: ChatRequest) -> ChatResponse:
    """處理單個聊天請求的輔助函數"""
    start_time = time.time()
    
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    result = await graph.ainvoke(
        input={"question": request.question},
        config=config,
    )
    
    if result and "messages" in result and result["messages"]:
        answer = result["messages"][-1].content
    else:
        answer = "抱歉，我無法處理您的問題。"
    
    processing_time = time.time() - start_time
    
    return ChatResponse(
        answer=answer,
        thread_id=thread_id,
        user_id=request.user_id,
        processing_time=round(processing_time, 2),
        status="success"
    )

# 獲取對話歷史端點
@app.get("/chat/history/{thread_id}")
async def get_chat_history(thread_id: str, limit: int = 10):
    """
    獲取對話歷史
    
    Args:
        thread_id: 對話線程ID
        limit: 返回的歷史記錄數量限制
        
    Returns:
        dict: 包含對話歷史的字典
    """
    try:
        # 這裡可以實現從記憶中獲取對話歷史的邏輯
        # 目前返回一個示例響應
        return {
            "thread_id": thread_id,
            "history": [],
            "message": "對話歷史功能待實現"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取對話歷史時發生錯誤: {str(e)}"
        )

# 服務器資訊端點
@app.get("/info")
async def server_info():
    """獲取服務器資訊"""
    return {
        "service": "法律諮詢聊天機器人",
        "version": "1.0.0",
        "framework": "FastAPI",
        "agent": "LangGraph",
        "endpoints": {
            "chat": "/chat",
            "batch_chat": "/chat/batch",
            "history": "/chat/history/{thread_id}",
            "health": "/health",
            "info": "/info"
        }
    }

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """啟動FastAPI服務器"""
    
    print("🚀 啟動法律諮詢聊天機器人API服務器...")
    print("=" * 60)
    print(f"🌐 服務器地址: http://{host}:{port}")
    print(f"📚 API文檔: http://{host}:{port}/docs")
    print(f"🔍 健康檢查: http://{host}:{port}/health")
    print(f"ℹ️  服務器資訊: http://{host}:{port}/info")
    print("=" * 60)
    print("💡 提示:")
    print("  - 使用 Ctrl+C 停止服務器")
    print("  - 在另一個終端運行 'uv run python test_client.py' 來測試客戶端")
    print("  - 訪問 /docs 查看完整的API文檔")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "start_server:app",  # 修改為指向當前模組
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服務器已停止")
    except Exception as e:
        print(f"❌ 啟動服務器時發生錯誤: {e}")

if __name__ == "__main__":
    # 解析命令列參數
    host = "0.0.0.0"
    port = 8000
    reload = True
    
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print("用法: python start_server.py [選項]")
            print("選項:")
            print("  --host HOST    服務器主機地址 (預設: 0.0.0.0)")
            print("  --port PORT    服務器端口 (預設: 8000)")
            print("  --no-reload    禁用自動重載")
            print("  --help, -h     顯示此幫助資訊")
            sys.exit(0)
        
        i = 1
        while i < len(sys.argv):
            if sys.argv[i] == "--host" and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--no-reload":
                reload = False
                i += 1
            else:
                i += 1
    
    start_server(host, port, reload)