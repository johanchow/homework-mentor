"""
用户API测试脚本
"""

import requests
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# API基础URL
BASE_URL = "http://localhost:5000/user"

def test_register():
    """测试用户注册"""
    print("🧪 测试用户注册...")

    data = {
        "name": "测试用户",
        "password": "123456",
        "email": "test@example.com",
        "phone": "13800138000"
    }

    response = requests.post(f"{BASE_URL}/register", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 201:
        print("✅ 注册成功")
        return response.json().get('token')
    else:
        print("❌ 注册失败")
        return None

def test_login():
    """测试用户登录"""
    print("\n🧪 测试用户登录...")

    data = {
        "email": "test@example.com",
        "password": "123456"
    }

    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        print("✅ 登录成功")
        return response.json().get('token')
    else:
        print("❌ 登录失败")
        return None

def test_get_profile(token):
    """测试获取用户信息"""
    print("\n🧪 测试获取用户信息...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        print("✅ 获取用户信息成功")
    else:
        print("❌ 获取用户信息失败")

def test_update_profile(token):
    """测试更新用户信息"""
    print("\n🧪 测试更新用户信息...")

    data = {
        "name": "测试用户（已更新）",
        "phone": "13800138001"
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/profile", json=data, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        print("✅ 更新用户信息成功")
    else:
        print("❌ 更新用户信息失败")

def test_change_password(token):
    """测试修改密码"""
    print("\n🧪 测试修改密码...")

    data = {
        "old_password": "123456",
        "new_password": "654321"
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/password", json=data, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        print("✅ 修改密码成功")
    else:
        print("❌ 修改密码失败")

def test_check_email():
    """测试检查邮箱是否存在"""
    print("\n🧪 测试检查邮箱是否存在...")

    data = {"email": "test@example.com"}
    response = requests.post(f"{BASE_URL}/check-email", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        print("✅ 检查邮箱成功")
    else:
        print("❌ 检查邮箱失败")

def main():
    """主测试函数"""
    print("🚀 开始测试用户API...")

    # 测试注册
    token = test_register()

    if token:
        # 测试登录
        login_token = test_login()

        if login_token:
            # 测试获取用户信息
            test_get_profile(login_token)

            # 测试更新用户信息
            test_update_profile(login_token)

            # 测试修改密码
            test_change_password(login_token)

    # 测试检查邮箱
    test_check_email()

    print("\n🎉 API测试完成!")

if __name__ == "__main__":
    main()
