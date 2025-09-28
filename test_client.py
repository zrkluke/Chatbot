"""
測試客戶端 - 取代main.py的while迴圈
"""

import asyncio
import aiohttp
import json
import time
from typing import Optional, List

class LegalConsultationClient:
    """法律諮詢客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.thread_id: Optional[str] = None
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def chat(self, question: str, user_id: Optional[str] = None) -> dict:
        """
        發送單個聊天請求
        
        Args:
            question: 用戶問題
            user_id: 可選的用戶ID
            
        Returns:
            dict: 包含回答的響應
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        payload = {
            "question": question,
            "thread_id": self.thread_id,
            "user_id": user_id
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    # 保存thread_id用於後續對話
                    if not self.thread_id:
                        self.thread_id = result.get("thread_id")
                    return result
                else:
                    error_detail = await response.text()
                    return {
                        "error": f"HTTP {response.status}",
                        "detail": error_detail,
                        "status": "error"
                    }
        except Exception as e:
            return {
                "error": "Connection error",
                "detail": str(e),
                "status": "error"
            }
    
    async def batch_chat(self, questions: List[str], user_id: Optional[str] = None) -> List[dict]:
        """
        發送批量聊天請求
        
        Args:
            questions: 問題列表
            user_id: 可選的用戶ID
            
        Returns:
            List[dict]: 包含所有回答的響應列表
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        payload = [
            {
                "question": question,
                "thread_id": self.thread_id,
                "user_id": user_id
            }
            for question in questions
        ]
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/batch",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    # 保存thread_id用於後續對話
                    if not self.thread_id and results:
                        self.thread_id = results[0].get("thread_id")
                    return results
                else:
                    error_detail = await response.text()
                    return [{
                        "error": f"HTTP {response.status}",
                        "detail": error_detail,
                        "status": "error"
                    }]
        except Exception as e:
            return [{
                "error": "Connection error",
                "detail": str(e),
                "status": "error"
            }]
    
    async def health_check(self) -> dict:
        """檢查服務器健康狀態"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "unhealthy", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_server_info(self) -> dict:
        """獲取服務器資訊"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        try:
            async with self.session.get(f"{self.base_url}/info") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}

async def interactive_chat():
    """互動式聊天模式"""
    print("法律諮詢聊天機器人客戶端")
    print("=" * 50)
    print("輸入 'exit', 'q', 'quit', 'bye' 退出")
    print("輸入 'health' 檢查服務器狀態")
    print("輸入 'info' 獲取服務器資訊")
    print("輸入 'batch:' 開始批量模式")
    print("=" * 50)
    
    async with LegalConsultationClient() as client:
        # 檢查服務器健康狀態
        health = await client.health_check()
        if health.get("status") != "healthy":
            print(f"⚠️  服務器狀態異常: {health}")
            return
        
        print("✅ 服務器連接正常")
        print()
        
        batch_mode = False
        batch_questions = []
        
        while True:
            try:
                if batch_mode:
                    user_input = input("Batch> ")
                else:
                    user_input = input("User: ")
                
                if user_input.lower() in ["exit", "q", "quit", "bye"]:
                    print("👋 再見！")
                    break
                
                elif user_input.lower() == "health":
                    health = await client.health_check()
                    print(f"🏥 服務器狀態: {health}")
                    continue
                
                elif user_input.lower() == "info":
                    info = await client.get_server_info()
                    print(f"ℹ️  服務器資訊: {json.dumps(info, indent=2, ensure_ascii=False)}")
                    continue
                
                elif user_input.lower() == "batch:":
                    batch_mode = True
                    batch_questions = []
                    print("📝 進入批量模式，輸入多個問題，輸入 'send' 發送")
                    continue
                
                elif user_input.lower() == "send" and batch_mode:
                    if batch_questions:
                        print(f"📤 發送 {len(batch_questions)} 個問題...")
                        start_time = time.time()
                        results = await client.batch_chat(batch_questions)
                        end_time = time.time()
                        
                        print(f"⏱️  總處理時間: {end_time - start_time:.2f}秒")
                        print()
                        
                        for i, result in enumerate(results):
                            if result.get("status") == "success":
                                print(f"問題 {i+1}: {batch_questions[i]}")
                                print(f"回答: {result['answer']}")
                                print(f"處理時間: {result['processing_time']}秒")
                                print("-" * 30)
                            else:
                                print(f"問題 {i+1} 處理失敗: {result.get('error', 'Unknown error')}")
                                print("-" * 30)
                        
                        batch_mode = False
                        batch_questions = []
                    else:
                        print("❌ 沒有問題要發送")
                    continue
                
                elif user_input.lower() == "cancel" and batch_mode:
                    batch_mode = False
                    batch_questions = []
                    print("❌ 取消批量模式")
                    continue
                
                if batch_mode:
                    batch_questions.append(user_input)
                    print(f"✅ 已添加問題 {len(batch_questions)}: {user_input}")
                    continue
                
                # 正常聊天模式
                print("🤔 思考中...")
                start_time = time.time()
                result = await client.chat(user_input)
                end_time = time.time()
                
                if result.get("status") == "success":
                    print(f"AI: {result['answer']}")
                    print(f"⏱️  處理時間: {result['processing_time']}秒")
                    if result.get("thread_id"):
                        print(f"🧵 對話ID: {result['thread_id']}")
                else:
                    print(f"❌ 錯誤: {result.get('error', 'Unknown error')}")
                    if result.get("detail"):
                        print(f"詳細資訊: {result['detail']}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 再見！")
                break
            except Exception as e:
                print(f"❌ 發生錯誤: {e}")

async def demo_batch_chat():
    """演示批量聊天功能"""
    print("批量聊天演示")
    print("=" * 30)
    
    questions = [
        "竊盜罪的刑責是什麼？",
        "離婚需要什麼條件？",
        "債務不履行如何處理？"
    ]
    
    async with LegalConsultationClient() as client:
        print(f"發送 {len(questions)} 個問題...")
        start_time = time.time()
        results = await client.batch_chat(questions)
        end_time = time.time()
        
        print(f"總處理時間: {end_time - start_time:.2f}秒")
        print()
        
        for i, result in enumerate(results):
            if result.get("status") == "success":
                print(f"問題 {i+1}: {questions[i]}")
                print(f"回答: {result['answer']}")
                print(f"處理時間: {result['processing_time']}秒")
                print("-" * 40)
            else:
                print(f"問題 {i+1} 處理失敗: {result.get('error', 'Unknown error')}")
                print("-" * 40)

async def main():
    """主函數"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            await demo_batch_chat()
        elif sys.argv[1] == "interactive":
            await interactive_chat()
        else:
            print("用法: python test_client.py [demo|interactive]")
            print("  demo: 運行批量聊天演示")
            print("  interactive: 運行互動式聊天 (預設)")
    else:
        await interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())
