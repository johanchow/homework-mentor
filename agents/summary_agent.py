"""
总结文本Agent - 专门负责总结文本并提取题目信息
"""

import json
from typing import Dict, Any, List, Optional
from langchain.schema import HumanMessage, SystemMessage
from entity.message import create_message, Message, MessageRole
from entity.question import Question
from utils.transformer import markdown_to_json
from utils.llm import LLM


class SummaryAgent:
    """总结文本Agent - 负责总结文本并提取题目信息"""

    def __init__(self, agent_id: Optional[str] = None, **kwargs):
        self.agent_id = agent_id or "summary_agent"
        self.agent_type = "SummaryAgent"
        
        # 设置系统提示词
        self.system_summary_prompt: Message = create_message(
            role=MessageRole.SYSTEM,
            content="""用户会可能会传入一段文字、或者若干个图片，里面都应该是多个作业题目。也可能会包含一点杂乱无用的信息。

题目的全部类型有： 选择题(choice)、判断题(judge)、阅读题(reading)、口述题(talking)、表演题(show)、其他自查完成题(checking)
题目的全部学科有: chinese、math、english、physics、chemistry、biology、history、geography、politics、other

请你帮我提取出全部文字和全部图片中的所有题目。每道题最多包含以下属性：
- title: 题目文字，必填
- subject: 题目学科，必填
- type: 题目类型，必填
- material: 题目材料，只有type为reading时，才可能存在
- options: 题目选项，只有type为choice时，才需要填写

请返回所有题目的 JSON 列表。
举例1:
[题目] 小明有3个苹果，给了小红1个，下面哪个说法正确？ A. 小明还剩2个 B. 小明还剩1个 C. 小红拥有2个 D. 小红拥有3个
[输出] { "title": "小明有3个苹果，给了小红1个，下面哪个说法正确？", "subject": "math", "type": "choice", "options": ["小明还剩2个", "小明还剩1个", "小红拥有2个","小红拥有3个"] }

举例2:
[题目] 请阅读图片的内容
[输出] { "title": "请阅读图片的内容", "subject": "english", "type": "reading", "material": "The picture shows a cat." }

举例3:
[题目] 讲解课文P53页的诗词含义
[输出] { "title": "讲解课文P53页的诗词含义", "subject": "chinese", "type": "talking" }

举例4:
[题目] 表演课本的狼来了故事
[输出] { "title": "表演课本的狼来了故事", "subject": "chinese", "type": "show" }

说明：
忽略可能有的广告、页眉页脚等无关内容; 尽可能完整识别题干，保留题号、选项等;
可能需要进行修改少量字、格式、单词拼写、去掉中间多余空格等工作
请返回所有题目的 JSON 列表。"""
        )
        
        # 初始化 LLM
        self.llm = LLM.get_text_llm()


    async def process_input(self, text: str) -> List[Question]:
        """处理任务的核心方法"""
        questions = await self.summarize_text(text)
        return questions

    async def summarize_text(self, text: str, max_iterations: int = 3) -> List[Question]:
        """总结文本并提取题目信息 - 使用 ReAct 模式迭代完善"""
        try:
            # 构建初始消息列表
            messages = [
                self.system_summary_prompt,
                create_message(role=MessageRole.USER, content=text)
            ]
            
            # 转换为 LLM 消息格式
            llm_messages = [msg.to_llm_message() for msg in messages]
            
            # 迭代完善题目信息
            for iteration in range(max_iterations):
                print(f'=== 第 {iteration + 1} 次迭代 ===')
                
                # 调用 LLM
                result = self.llm.invoke(llm_messages)
                print(f'LLM 返回结果: {result.content}')
                
                # 解析返回的 JSON
                try:
                    json_str = markdown_to_json(result.content)
                    question_dicts = json.loads(json_str)
                    
                    # 验证和转换题目
                    questions = []
                    incomplete_questions = []
                    
                    for i, question_dict in enumerate(question_dicts):
                        try:
                            # 验证必需字段
                            missing_fields = []
                            for field in ['title', 'subject', 'type']:
                                if field not in question_dict or not question_dict[field]:
                                    missing_fields.append(field)
                            
                            if missing_fields:
                                incomplete_questions.append({
                                    'index': i,
                                    'data': question_dict,
                                    'missing_fields': missing_fields
                                })
                                continue
                            
                            # 处理 images_coords 字段
                            if 'images_coords' in question_dict:
                                if question_dict['images_coords']:
                                    question_dict['images'] = ','.join(['placeholder_image.jpg'] * len(question_dict['images_coords']))
                                del question_dict['images_coords']
                            
                            # 添加默认的 creator_id
                            if 'creator_id' not in question_dict:
                                question_dict['creator_id'] = 'system'
                            
                            # 创建 Question 对象
                            question = Question.from_dict(question_dict)
                            questions.append(question)
                            
                        except Exception as e:
                            print(f"转换题目失败: {e}, 题目数据: {question_dict}")
                            incomplete_questions.append({
                                'index': i,
                                'data': question_dict,
                                'error': str(e)
                            })
                    
                    # 如果没有不完整的题目，返回结果
                    if not incomplete_questions:
                        print(f'✓ 所有题目解析成功，共 {len(questions)} 道题目')
                        return questions
                    
                    # 构建改进提示
                    improvement_prompt = self._build_improvement_prompt(incomplete_questions, iteration + 1)
                    
                    # 添加改进提示到消息列表
                    messages.append(create_message(role=MessageRole.ASSISTANT, content=result.content))
                    messages.append(create_message(role=MessageRole.USER, content=improvement_prompt))
                    
                    # 更新 LLM 消息
                    llm_messages = [msg.to_llm_message() for msg in messages]
                    
                    print(f'发现 {len(incomplete_questions)} 道不完整题目，发送改进提示...')
                    
                except json.JSONDecodeError as e:
                    print(f'JSON 解析失败: {e}')
                    # 发送格式错误提示
                    format_error_prompt = f"""返回的内容不是有效的 JSON 格式。请重新返回有效的 JSON 数组，每个题目包含以下必需字段：
- title: 题目文字
- subject: 题目学科 (chinese, math, english, physics, chemistry, biology, history, geography, politics, other)
- type: 题目类型 (choice, judge, reading, talking, show, checking)

原始内容: {result.content}"""
                    
                    messages.append(create_message(role=MessageRole.ASSISTANT, content=result.content))
                    messages.append(create_message(role=MessageRole.USER, content=format_error_prompt))
                    llm_messages = [msg.to_llm_message() for msg in messages]
                    continue
            
            # 如果达到最大迭代次数，返回已解析的题目
            print(f'达到最大迭代次数 {max_iterations}，返回已解析的题目')
            return questions if 'questions' in locals() else []
                
        except Exception as e:
            print(f'总结文本时发生错误: {e}')
            return []
    
    def _build_improvement_prompt(self, incomplete_questions: List[Dict], iteration: int) -> str:
        """构建改进提示"""
        prompt = f"""请完善以下不完整的题目信息（第 {iteration} 次提醒）：

"""
        
        for item in incomplete_questions:
            prompt += f"题目 {item['index'] + 1}:\n"
            prompt += f"当前数据: {json.dumps(item['data'], ensure_ascii=False, indent=2)}\n"
            
            if 'missing_fields' in item:
                prompt += f"缺少字段: {', '.join(item['missing_fields'])}\n"
                prompt += "请补充完整这些字段。\n"
            elif 'error' in item:
                prompt += f"解析错误: {item['error']}\n"
                prompt += "请修正数据格式。\n"
            
            prompt += "\n"
        
        prompt += """请确保每个题目都包含以下必需字段：
- title: 题目文字（必填）
- subject: 题目学科（必填，从以下选择：chinese, math, english, physics, chemistry, biology, history, geography, politics, other）
- type: 题目类型（必填，从以下选择：choice, judge, reading, talking, show, checking）
- options: 题目选项（仅当 type 为 choice 时必填）

请返回完整的 JSON 数组。"""
        
        return prompt

    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态信息"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type
        }
