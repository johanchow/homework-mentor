from typing import List
# import faiss
import numpy as np
from dao.question_dao import question_dao
from utils.llm import Embedding

class VectorService:
    def list_sematic_near_questions(self, subject: str, query: str, top_k = 5):
        # 查询科目里全部的题目，然后计算题目和query的相似度，然后返回相似度最高的k个题目
        # all_questions = question_dao.search_by_kwargs({"subject": subject})
        # all_questions_contents = [q.title for q in all_questions ] 
        # embeddings = Embedding.get_embeddings(all_questions_contents)
        # dimension = len(embeddings[0])
        # faiss_index = faiss.IndexFlatL2(dimension)
        # faiss_index.add(np.array(embeddings))
        # query_vector = Embedding.get_embeddings([query])[0]  # 只有一个查询向量
        # D, I = faiss_index.search(np.array([query_vector]), top_k)
        # return [all_questions[i] for i in I[0]]
        return []

vector_service = VectorService()