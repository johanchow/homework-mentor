import requests
from config.settings import settings


def read_text_from_file(file_url: str) -> str:
    """
    使用 Landing AI ADE API 从图片 URL 中提取文本
    
    Args:
        image_url: 图片的 URL 地址
        
    Returns:
        提取的文本内容
        
    Raises:
        ValueError: 当 API key 未配置时
        requests.RequestException: 当 API 请求失败时
    """
    # 检查 API key 是否配置
    api_key = settings.VISION_AGENT_API_KEY
    if not api_key:
        raise ValueError("VISION_AGENT_API_KEY 未在配置中设置")
    
    # Landing AI ADE API 端点
    url = "https://api.va.landing.ai/v1/ade/parse"
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 请求体
    data = {
        "document_url": file_url
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取文本内容
        if 'text' in result:
            return result['text']
        elif 'content' in result:
            return result['content']
        elif 'result' in result and 'text' in result['result']:
            return result['result']['text']
        else:
            return str(result)
            
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"API 请求失败: {str(e)}")
    except Exception as e:
        raise Exception(f"处理图片 URL 时出错: {str(e)}")

