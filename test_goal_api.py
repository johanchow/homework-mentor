#!/usr/bin/env python3
"""
Goal API测试
"""

import requests
import json

def test_goal_api():
    """测试Goal API接口"""
    base_url = "http://localhost:5000/goal"
    
    print("🚀 开始Goal API测试...\n")
    
    # 测试创建目标
    print("🔍 测试创建目标...")
    create_data = {
        "name": "掌握高中数学导数",
        "subject": "math",
        "ai_prompt": "请帮助我理解高中数学中的导数概念，包括定义、求导法则和应用",
        "creator_id": "user123",
        "status": "preparing"
    }
    
    try:
        response = requests.post(f"{base_url}/create", json=create_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 201:
            goal_data = response.json()
            goal_id = goal_data['goal']['id']
            print(f"✅ 目标创建成功，ID: {goal_id}")
            
            # 测试获取目标详情
            print("\n🔍 测试获取目标详情...")
            response = requests.get(f"{base_url}/{goal_id}")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            
            # 测试更新目标
            print("\n🔍 测试更新目标...")
            update_data = {
                "status": "doing",
                "ai_prompt": "请帮助我深入理解高中数学中的导数概念，包括定义、求导法则、几何意义和实际应用"
            }
            response = requests.put(f"{base_url}/{goal_id}", json=update_data)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            
            # 测试获取目标列表
            print("\n🔍 测试获取目标列表...")
            response = requests.get(f"{base_url}/list?page=1&size=10")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            
            # 测试名称过滤（模糊匹配）
            print("\n🔍 测试名称过滤（模糊匹配）...")
            response = requests.get(f"{base_url}/list?name=导数&page=1&size=10")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            
            # 测试科目过滤
            print("\n🔍 测试科目过滤...")
            response = requests.get(f"{base_url}/list?subject=math&page=1&size=10")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            
            # 测试删除目标
            print("\n🔍 测试删除目标...")
            response = requests.delete(f"{base_url}/{goal_id}")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            
        else:
            print("❌ 目标创建失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_goal_api_validation():
    """测试Goal API验证"""
    base_url = "http://localhost:5000/goal"
    
    print("\n🧪 测试API验证...")
    
    # 测试缺少必需字段
    print("🔍 测试缺少必需字段...")
    invalid_data = {
        "name": "测试目标",
        # 缺少subject
        "creator_id": "user123"
    }
    
    try:
        response = requests.post(f"{base_url}/create", json=invalid_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 400:
            print("✅ 验证失败处理正确")
        else:
            print("❌ 验证失败处理不正确")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试不存在的创建人
    print("\n🔍 测试不存在的创建人...")
    invalid_creator_data = {
        "name": "测试目标",
        "subject": "math",
        "ai_prompt": "测试提示词",
        "creator_id": "nonexistent_user"
    }
    
    try:
        response = requests.post(f"{base_url}/create", json=invalid_creator_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 400:
            print("✅ 创建人验证正确")
        else:
            print("❌ 创建人验证不正确")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_goal_api()
    test_goal_api_validation()
    print("\n✨ Goal API测试完成！") 