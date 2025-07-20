import re
from datetime import datetime
from typing import Union

def markdown_to_json(text: str) -> str:
  """
  提取并解析可能被 markdown 包裹的 JSON 字符串。

  参数:
      text (str): 可能是 ```json 包裹的 JSON 字符串，或纯 JSON。

  返回:
      object: 被 json.loads 解析后的 Python 对象。

  异常:
      如果 JSON 格式不合法，将抛出 json.JSONDecodeError。
  """
  text = text.strip()

  # 尝试提取被 ```json 或 ``` 包裹的部分
  match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
  if match:
      json_str = match.group(1).strip()
  else:
      json_str = text  # 认为它本身就是 JSON 字符串
  return json_str


def iso_to_mysql_datetime(date_str: Union[str, None]) -> Union[datetime, None]:
    """
    将 ISO 8601 或 MySQL datetime 格式字符串转换为 datetime 对象
    """
    if date_str is None:
        return None
    try:
        # 尝试 ISO 8601 格式
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        pass

    try:
        # 尝试 MySQL datetime 格式
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass

    raise ValueError(f"无法解析的时间格式: {date_str}")


def mysql_datetime_to_iso(dt: Union[datetime, None]) -> Union[str, None]:
    """
    将 datetime 对象转换为 ISO 8601 格式字符串（带毫秒和Z时区标识）
    """
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'