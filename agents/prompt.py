import json
from typing import List
from operator import itemgetter
from entity.message import create_message, Message, MessageRole
from entity.question import Question, QuestionType

def get_import_prompt(question: Question) -> List[Message]:
    images, audios, videos, attachments = itemgetter('images', 'audios', 'videos', 'attachments')(question.to_dict())
    prompts = [create_message(role=MessageRole.SYSTEM, content=f"你是一位{question.subject}老师，擅长根据题目基础信息，进行完善题目。")]
    question_prompt = f"""
    题目基础信息如下：
    subject(学科): {question.subject}
    type(类型):{question.type}
    title(题目):{question.title}
    tip(提示或要求): {question.tip}
    {question.type == QuestionType.CHOICE and f"options(选项): {question.options.join(' | ')}" or ""}
    """
    if question.type == QuestionType.READING:
        if len(images) > 0 or len(audios) > 0 or len(videos) > 0 or len(attachments) > 0:
            question_prompt += f"阅读材料在上传文件里，请把文件中需要阅读的{question.subject}全部提取出来"
        else:
            question_prompt += f"阅读材料可能在题目里，请把题目中需要阅读的内容分割提取出来"
    elif question.type == QuestionType.SUMMARY:
        question_prompt += f"请根据上传的材料，题目和要求，总结出答案"
    elif question.type == QuestionType.CHOICE:
        question_prompt += f"选项可能在题目里，也可能在提示里"

    example = {
        "title": "阅读材料中的句子",
        "tip": "看材料",
        "options": ["morning", 'noon', 'night'],
        "material": "hello everyone"
    }
    question_prompt += f'''请根据以上信息，修正和完善题目title、tip、options、material信息，并按如下json格式返回题目信息，不要有任何其他内容。举例：{json.dumps(example)}'''
    content = []
    for image_url in images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        })
    for file_url in attachments:
        content.append({
            "type": "file_url",
            "file_url": {
                "url": file_url
            }
        })
    prompts.append(create_message(MessageRole.USER, content))
    return prompts
