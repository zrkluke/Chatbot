'''
Reranker
If Retrieve == Yes then
Rank yt based on IsRelevant, IsSupport, and IsUseful
Return top 1 yt as final consultation answer

else if Retrieve == No then
Return yt as final consultation answer directly
'''
from ..utils.state import LegalConsultState as State
from ..utils.models import llm
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import AIMessage


class Response(BaseModel):
    FinalConsultationAnswer: str = Field(..., description="The final consultation answer")

def calculate_score(
    is_relevant: str,
    is_support: str,
    is_useful: str, 
    weights: dict[str, float] = None
) -> float:
    """
    計算綜合評分
    
    Args:
        is_relevant: "Yes" or "No"
        is_support: "Fully", "Partial", or "No"
        is_useful: "5", "4", "3", "2", or "1"
        weights: 自定義權重字典，預設為 {"relevant": 0.4, "support": 0.35, "useful": 0.25}
    
    Returns:
        float: 綜合評分 (0-10)
    """
    # 預設權重
    if weights is None:
        weights = {"relevant": 0.4, "support": 0.35, "useful": 0.25}
    
    # 相關性評分
    relevant_score = 1.0 if is_relevant == "Yes" else 0.0
    
    # 支持度評分
    support_scores = {"Fully": 1.0, "Partial": 0.5, "No": 0.0}
    support_score = support_scores.get(is_support, 0.0)
    
    # 有用性評分
    useful_scores = {"5": 1.0, "4": 0.8, "3": 0.6, "2": 0.4, "1": 0.2}
    useful_score = useful_scores.get(is_useful, 0.0)
    
    # 加權平均
    total_score = (relevant_score * weights["relevant"] + 
                  support_score * weights["support"] + 
                  useful_score * weights["useful"]) * 10
    
    return total_score

def filter_and_rank_answers(consultation_answers: list[str], 
                          result_isRelevant: list[str], 
                          result_isSupport: list[str], 
                          result_isUseful: list[str],
                          min_score_threshold: float = 3.0,
                          weights: dict[str, float] = None,
                          filter_irrelevant: bool = True) -> list[tuple[str, float, dict]]:
    """
    使用Zip 處理諮詢答案的篩選與排序
    
    Args:
        consultation_answers: 諮詢答案列表
        result_isRelevant: 相關性評分列表
        result_isSupport: 支持度評分列表
        result_isUseful: 有用性評分列表
        min_score_threshold: 最低評分閾值，低於此分數的答案會被過濾
        weights: 自定義權重字典
        filter_irrelevant: 是否過濾不相關的答案
    
    Returns:
        list[tuple[str, float, dict]]: 排序後的(答案, 評分, 詳細評分)列表
    """
    # 使用zip將所有列表打包
    bundled_data = list(zip(consultation_answers, result_isRelevant, result_isSupport, result_isUseful))
    
    # 計算每個答案的綜合評分
    scored_answers = []
    for answer, is_relevant, is_support, is_useful in bundled_data:
        # 如果啟用過濾且答案不相關，跳過
        if filter_irrelevant and is_relevant == "No":
            continue
            
        score = calculate_score(is_relevant, is_support, is_useful, weights)
        
        # 詳細評分資訊
        score_details = {
            "is_relevant": is_relevant,
            "is_support": is_support,
            "is_useful": is_useful,
            "relevant_score": 1.0 if is_relevant == "Yes" else 0.0,
            "support_score": {"Fully": 1.0, "Partial": 0.6, "No": 0.0}.get(is_support, 0.0),
            "useful_score": {"5": 1.0, "4": 0.8, "3": 0.6, "2": 0.4, "1": 0.2}.get(is_useful, 0.0)
        }
        
        scored_answers.append((answer, score, score_details))
    
    # 按評分降序排序
    scored_answers.sort(key=lambda x: x[1], reverse=True)
    
    # 應用最低評分閾值過濾
    filtered_answers = [(answer, score, details) for answer, score, details in scored_answers 
                       if score >= min_score_threshold]
    
    return filtered_answers

async def reranker(state: State):
    consultation_answers = state["ConsultationAnswers"]
    result_isRelevant = state["IsRelevant"]
    result_isSupport = state["IsSupport"]
    result_isUseful = state["IsUseful"]
    
    # 使用Zip bundle進行篩選與排序
    ranked_answers = filter_and_rank_answers(
        consultation_answers, 
        result_isRelevant, 
        result_isSupport, 
        result_isUseful,
        min_score_threshold=2.0,  # 可調整的最低評分閾值
        filter_irrelevant=True    # 過濾不相關的答案
    )
    
    # 選擇評分最高的答案
    if ranked_answers:
        best_answer, best_score, score_details = ranked_answers[0]
        print(f"選擇最佳答案，評分: {best_score:.2f}")
        print(f"詳細評分: 相關性={score_details['is_relevant']}, "
                f"支持度={score_details['is_support']}, "
                f"有用性={score_details['is_useful']}")
        
        # 如果有其他候選答案，也顯示它們的評分
        if len(ranked_answers) > 1:
            print("其他候選答案:")
            for i, (answer, score, details) in enumerate(ranked_answers[1:3], 2):  # 顯示前3個
                print(f"  {i}. 評分: {score:.2f} - {details['is_relevant']}/{details['is_support']}/{details['is_useful']}")
        
        return {"messages": [AIMessage(content=best_answer)]}
    else:
        # 如果沒有有效答案，返回第一個原始答案
        print("警告: 沒有答案通過篩選，返回第一個原始答案")
        return {"messages": [AIMessage(content=consultation_answers[0])]}
    