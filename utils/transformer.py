import re

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
