"""
测试考试API功能
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:5000"

def test_exam_api():
    """测试考试API"""

    test_data = {
        "paper_id": "test-paper-123",
        "examinee_id": "test-user-456"
    }

    print("🧪 测试考试API...")

    # 测试创建考试
    try:
        response = requests.post(
            f"{BASE_URL}/exam/",
            json=test_data,
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"创建考试 - 状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"请求失败: {e}")

    # 测试获取考试详情
    print("\n2. 测试获取考试详情")
    try:
        response = requests.get(
            f"{BASE_URL}/exam/{response.json().get('exam', {}).get('id')}",
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")

        if response.status_code == 200:
            print("✅ 获取考试详情成功")
        else:
            print("❌ 获取考试详情失败")

    except Exception as e:
        print(f"❌ 获取考试详情请求失败: {e}")

    # 测试更新考试答卷
    print("\n3. 测试更新考试答卷")
    update_data = {
        "answer": {
            "question": [
                {
                    "id": "q1",
                    "subject": "chinese",
                    "type": "choice",
                    "title": "测试题目1（已更新）",
                    "creator_id": "creator-123",
                    "options": "A.选项1,B.选项2,C.选项3,D.选项4"
                }
            ],
            "messages": {
                "q1": [
                    {
                        "id": "msg1",
                        "role": "user",
                        "content": "用户回答（已更新）",
                        "message_type": "text",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            },
            "answer": {
                "q1": "B"
            }
        }
    }

    try:
        response = requests.put(
            f"{BASE_URL}/exam/{response.json().get('exam', {}).get('id')}",
            json=update_data,
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")

        if response.status_code == 200:
            print("✅ 更新考试答卷成功")
        else:
            print("❌ 更新考试答卷失败")

    except Exception as e:
        print(f"❌ 更新考试答卷请求失败: {e}")

    # 测试获取考试列表
    print("\n4. 测试获取考试列表")
    try:
        response = requests.get(
            f"{BASE_URL}/exam/",
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")

        if response.status_code == 200:
            print("✅ 获取考试列表成功")
        else:
            print("❌ 获取考试列表失败")

    except Exception as e:
        print(f"❌ 获取考试列表请求失败: {e}")

    # 测试删除考试
    print("\n5. 测试删除考试")
    try:
        response = requests.delete(
            f"{BASE_URL}/exam/{response.json().get('exam', {}).get('id')}",
            headers={"Authorization": "Bearer test-token"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")

        if response.status_code == 200:
            print("✅ 删除考试成功")
        else:
            print("❌ 删除考试失败")

    except Exception as e:
        print(f"❌ 删除考试请求失败: {e}")

    print("\n🎉 考试API测试完成！")

if __name__ == "__main__":
    test_exam_api()
