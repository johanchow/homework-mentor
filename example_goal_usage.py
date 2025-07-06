#!/usr/bin/env python3
"""
Goal使用示例
"""

import requests
import json

def example_goal_workflow():
    """Goal完整工作流程示例"""
    base_url = "http://localhost:5000/goal"
    
    print("🎯 Goal完整工作流程示例\n")
    
    # 1. 创建学习目标
    print("1️⃣ 创建学习目标")
    goals_data = [
        {
            "name": "掌握初中数学函数概念",
            "subject": "math",
            "ai_prompt": "请帮助我理解初中数学中的函数概念，包括定义、性质和应用场景",
            "creator_id": "user123",
            "status": "preparing"
        },
        {
            "name": "学习英语语法时态",
            "subject": "english",
            "ai_prompt": "请帮助我学习英语语法中的各种时态，包括现在时、过去时、将来时等",
            "creator_id": "user123",
            "status": "preparing"
        },
        {
            "name": "理解物理力学原理",
            "subject": "physics",
            "ai_prompt": "请帮助我理解物理力学的基本原理，包括牛顿定律、能量守恒等",
            "creator_id": "user123",
            "status": "preparing"
        }
    ]
    
    created_goals = []
    for goal_data in goals_data:
        try:
            response = requests.post(f"{base_url}/create", json=goal_data)
            if response.status_code == 201:
                goal = response.json()['goal']
                created_goals.append(goal)
                print(f"   ✅ 创建目标: {goal['name']} (ID: {goal['id']})")
            else:
                print(f"   ❌ 创建目标失败: {goal_data['name']}")
        except Exception as e:
            print(f"   ❌ 创建目标异常: {e}")
    
    print()
    
    # 2. 查看所有目标
    print("2️⃣ 查看所有目标")
    try:
        response = requests.get(f"{base_url}/list?page=1&size=20")
        if response.status_code == 200:
            data = response.json()['data']
            print(f"   总目标数: {data['total']}")
            print(f"   当前页: {data['page']}/{data['pages']}")
            for goal in data['goals']:
                print(f"   📋 {goal['name']} - {goal['subject']} - {goal['status']}")
        else:
            print("   ❌ 获取目标列表失败")
    except Exception as e:
        print(f"   ❌ 获取目标列表异常: {e}")
    
    print()
    
    # 3. 更新目标状态
    print("3️⃣ 更新目标状态")
    if created_goals:
        goal_to_update = created_goals[0]
        update_data = {
            "status": "doing",
            "ai_prompt": "请帮助我深入理解初中数学中的函数概念，包括定义、性质、图像和应用场景，并提供练习题"
        }
        
        try:
            response = requests.put(f"{base_url}/{goal_to_update['id']}", json=update_data)
            if response.status_code == 200:
                updated_goal = response.json()['goal']
                print(f"   ✅ 更新目标: {updated_goal['name']} -> {updated_goal['status']}")
            else:
                print("   ❌ 更新目标失败")
        except Exception as e:
            print(f"   ❌ 更新目标异常: {e}")
    
    print()
    
    # 4. 按科目筛选目标
    print("4️⃣ 按科目筛选目标")
    subjects = ["math", "english", "physics"]
    for subject in subjects:
        try:
            response = requests.get(f"{base_url}/list?subject={subject}&page=1&size=10")
            if response.status_code == 200:
                data = response.json()['data']
                print(f"   📚 {subject.upper()}: {data['total']} 个目标")
                for goal in data['goals'][:3]:  # 只显示前3个
                    print(f"      - {goal['name']} ({goal['status']})")
            else:
                print(f"   ❌ 获取{subject}目标失败")
        except Exception as e:
            print(f"   ❌ 获取{subject}目标异常: {e}")
    
    print()
    
    # 5. 按名称搜索目标（模糊匹配）
    print("5️⃣ 按名称搜索目标（模糊匹配）")
    search_terms = ["函数", "语法", "物理"]
    for term in search_terms:
        try:
            response = requests.get(f"{base_url}/list?name={term}&page=1&size=10")
            if response.status_code == 200:
                data = response.json()['data']
                print(f"   🔍 搜索 '{term}': 找到 {data['total']} 个目标")
                for goal in data['goals']:
                    print(f"      - {goal['name']} ({goal['subject']})")
            else:
                print(f"   ❌ 搜索 '{term}' 失败")
        except Exception as e:
            print(f"   ❌ 搜索 '{term}' 异常: {e}")
    
    print()
    
    # 6. 完成一个目标
    print("6️⃣ 完成一个目标")
    if created_goals:
        goal_to_complete = created_goals[1]  # 选择第二个目标
        complete_data = {"status": "passed"}
        
        try:
            response = requests.put(f"{base_url}/{goal_to_complete['id']}", json=complete_data)
            if response.status_code == 200:
                completed_goal = response.json()['goal']
                print(f"   ✅ 完成目标: {completed_goal['name']} -> {completed_goal['status']}")
            else:
                print("   ❌ 完成目标失败")
        except Exception as e:
            print(f"   ❌ 完成目标异常: {e}")
    
    print()
    
    # 7. 查看不同状态的目标
    print("7️⃣ 查看不同状态的目标")
    statuses = ["preparing", "doing", "passed"]
    for status in statuses:
        try:
            response = requests.get(f"{base_url}/list?status={status}&page=1&size=10")
            if response.status_code == 200:
                data = response.json()['data']
                print(f"   📊 {status.upper()}: {data['total']} 个目标")
                for goal in data['goals']:
                    print(f"      - {goal['name']} ({goal['subject']})")
            else:
                print(f"   ❌ 获取{status}状态目标失败")
        except Exception as e:
            print(f"   ❌ 获取{status}状态目标异常: {e}")
    
    print()
    
    # 8. 删除一个目标
    print("8️⃣ 删除一个目标")
    if created_goals:
        goal_to_delete = created_goals[2]  # 选择第三个目标
        
        try:
            response = requests.delete(f"{base_url}/{goal_to_delete['id']}")
            if response.status_code == 200:
                print(f"   ✅ 删除目标: {goal_to_delete['name']}")
            else:
                print("   ❌ 删除目标失败")
        except Exception as e:
            print(f"   ❌ 删除目标异常: {e}")

def example_api_usage():
    """API使用示例"""
    print("\n📖 API使用示例\n")
    
    print("🔗 创建目标")
    print("POST /goal/create")
    print("Content-Type: application/json")
    print("""
{
    "name": "学习目标名称",
    "subject": "math",
    "ai_prompt": "AI提示词内容",
    "creator_id": "user123",
    "status": "preparing"
}
""")
    
    print("🔗 获取目标详情")
    print("GET /goal/{goal_id}")
    print("")
    
    print("🔗 更新目标")
    print("PUT /goal/{goal_id}")
    print("Content-Type: application/json")
    print("""
{
    "name": "新目标名称",
    "status": "doing",
    "ai_prompt": "新的AI提示词"
}
""")
    
    print("🔗 获取目标列表（支持模糊匹配）")
    print("GET /goal/list?page=1&size=10&subject=math&status=preparing&name=函数")
    print("")
    
    print("🔗 删除目标")
    print("DELETE /goal/{goal_id}")
    print("")

if __name__ == "__main__":
    example_goal_workflow()
    example_api_usage()
    print("✨ Goal使用示例完成！") 