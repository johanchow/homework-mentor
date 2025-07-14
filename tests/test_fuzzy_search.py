#!/usr/bin/env python3
"""
模糊匹配功能测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from entity.goal import Goal, GoalStatus, Subject, create_goal
from entity.question import Question, QuestionType, Subject as QSubject, create_question
from entity.user import User, create_user
from dao.goal_dao import goal_dao
from dao.question_dao import question_dao
from dao.user_dao import user_dao
from datetime import datetime

def test_goal_fuzzy_search():
    """测试Goal的模糊搜索功能"""
    print("🧪 测试Goal模糊搜索功能...")
    
    # 创建测试数据
    test_goals = [
        create_goal("掌握高中数学导数", Subject.MATH, "导数概念", "user1", GoalStatus.PREPARING),
        create_goal("学习英语语法时态", Subject.ENGLISH, "时态学习", "user1", GoalStatus.DOING),
        create_goal("理解物理力学原理", Subject.PHYSICS, "力学原理", "user2", GoalStatus.PREPARING),
        create_goal("掌握数学函数概念", Subject.MATH, "函数概念", "user2", GoalStatus.PASSED),
        create_goal("学习英语词汇", Subject.ENGLISH, "词汇学习", "user1", GoalStatus.DOING)
    ]
    
    # 保存到数据库
    created_goals = []
    for goal in test_goals:
        created_goal = goal_dao.create(goal)
        created_goals.append(created_goal)
        print(f"   ✅ 创建目标: {created_goal.name}")
    
    print()
    
    # 测试模糊搜索
    print("🔍 测试名称模糊搜索...")
    
    # 搜索包含"数学"的目标
    math_goals = goal_dao.search_by_kwargs({"name": "数学"})
    print(f"   搜索'数学': 找到 {len(math_goals)} 个目标")
    for goal in math_goals:
        print(f"     - {goal.name}")
    
    # 搜索包含"英语"的目标
    english_goals = goal_dao.search_by_kwargs({"name": "英语"})
    print(f"   搜索'英语': 找到 {len(english_goals)} 个目标")
    for goal in english_goals:
        print(f"     - {goal.name}")
    
    # 测试精确匹配
    print("\n🔍 测试精确匹配...")
    
    # 按科目精确匹配
    math_subject_goals = goal_dao.search_by_kwargs({"subject": Subject.MATH})
    print(f"   科目为数学: 找到 {len(math_subject_goals)} 个目标")
    
    # 按状态精确匹配
    preparing_goals = goal_dao.search_by_kwargs({"status": GoalStatus.PREPARING})
    print(f"   状态为准备中: 找到 {len(preparing_goals)} 个目标")
    
    # 测试组合搜索
    print("\n🔍 测试组合搜索...")
    
    # 名称模糊 + 科目精确
    math_name_goals = goal_dao.search_by_kwargs({
        "name": "数学",
        "subject": Subject.MATH
    })
    print(f"   名称包含'数学'且科目为数学: 找到 {len(math_name_goals)} 个目标")
    
    # 清理测试数据
    for goal in created_goals:
        goal_dao.delete(goal)
    print("\n✅ Goal模糊搜索测试完成")

def test_question_fuzzy_search():
    """测试Question的模糊搜索功能"""
    print("\n🧪 测试Question模糊搜索功能...")
    
    # 创建测试数据
    test_questions = [
        create_question(QSubject.MATH, QuestionType.CHOICE, "什么是导数？", "user1"),
        create_question(QSubject.ENGLISH, QuestionType.QA, "英语时态有哪些？", "user1"),
        create_question(QSubject.MATH, QuestionType.CHOICE, "函数的定义是什么？", "user2"),
        create_question(QSubject.PHYSICS, QuestionType.JUDGE, "牛顿第一定律正确吗？", "user2"),
        create_question(QSubject.ENGLISH, QuestionType.CHOICE, "英语语法规则", "user1")
    ]
    
    # 保存到数据库
    created_questions = []
    for question in test_questions:
        created_question = question_dao.create(question)
        created_questions.append(created_question)
        print(f"   ✅ 创建问题: {created_question.title[:20]}...")
    
    print()
    
    # 测试模糊搜索
    print("🔍 测试标题模糊搜索...")
    
    # 搜索包含"导数"的问题
    derivative_questions = question_dao.search_by_kwargs({"title": "导数"})
    print(f"   搜索'导数': 找到 {len(derivative_questions)} 个问题")
    
    # 搜索包含"英语"的问题
    english_questions = question_dao.search_by_kwargs({"title": "英语"})
    print(f"   搜索'英语': 找到 {len(english_questions)} 个问题")
    
    # 测试精确匹配
    print("\n🔍 测试精确匹配...")
    
    # 按科目精确匹配
    math_questions = question_dao.search_by_kwargs({"subject": QSubject.MATH})
    print(f"   科目为数学: 找到 {len(math_questions)} 个问题")
    
    # 按类型精确匹配
    choice_questions = question_dao.search_by_kwargs({"type": QuestionType.CHOICE})
    print(f"   类型为选择题: 找到 {len(choice_questions)} 个问题")
    
    # 清理测试数据
    for question in created_questions:
        question_dao.delete(question)
    print("\n✅ Question模糊搜索测试完成")

def test_user_fuzzy_search():
    """测试User的模糊搜索功能"""
    print("\n🧪 测试User模糊搜索功能...")
    
    # 创建测试数据
    test_users = [
        create_user("张三", "zhangsan@example.com", "password123", "13800138001"),
        create_user("李四", "lisi@example.com", "password123", "13800138002"),
        create_user("王五", "wangwu@example.com", "password123", "13800138003"),
        create_user("张小明", "zhangxiaoming@example.com", "password123", "13800138004"),
        create_user("李小红", "lixiaohong@example.com", "password123", "13800138005")
    ]
    
    # 保存到数据库
    created_users = []
    for user in test_users:
        created_user = user_dao.create(user)
        created_users.append(created_user)
        print(f"   ✅ 创建用户: {created_user.name}")
    
    print()
    
    # 测试模糊搜索
    print("🔍 测试姓名模糊搜索...")
    
    # 搜索包含"张"的用户
    zhang_users = user_dao.search_by_kwargs({"name": "张"})
    print(f"   搜索'张': 找到 {len(zhang_users)} 个用户")
    for user in zhang_users:
        print(f"     - {user.name}")
    
    # 搜索包含"李"的用户
    li_users = user_dao.search_by_kwargs({"name": "李"})
    print(f"   搜索'李': 找到 {len(li_users)} 个用户")
    for user in li_users:
        print(f"     - {user.name}")
    
    # 测试邮箱模糊搜索
    print("\n🔍 测试邮箱模糊搜索...")
    
    # 搜索包含"example"的邮箱
    example_users = user_dao.search_by_kwargs({"email": "example"})
    print(f"   搜索邮箱包含'example': 找到 {len(example_users)} 个用户")
    
    # 测试精确匹配
    print("\n🔍 测试精确匹配...")
    
    # 按手机号精确匹配
    phone_users = user_dao.search_by_kwargs({"phone": "13800138001"})
    print(f"   手机号为13800138001: 找到 {len(phone_users)} 个用户")
    
    # 清理测试数据
    for user in created_users:
        user_dao.delete(user)
    print("\n✅ User模糊搜索测试完成")

def test_count_functions():
    """测试计数功能"""
    print("\n🧪 测试计数功能...")
    
    # 创建测试数据
    test_goals = [
        create_goal("测试目标1", Subject.MATH, "测试", "user1", GoalStatus.PREPARING),
        create_goal("测试目标2", Subject.MATH, "测试", "user1", GoalStatus.DOING),
        create_goal("测试目标3", Subject.ENGLISH, "测试", "user2", GoalStatus.PREPARING)
    ]
    
    created_goals = []
    for goal in test_goals:
        created_goal = goal_dao.create(goal)
        created_goals.append(created_goal)
    
    # 测试计数
    total_count = goal_dao.count_by_kwargs({})
    print(f"   总目标数: {total_count}")
    
    math_count = goal_dao.count_by_kwargs({"subject": Subject.MATH})
    print(f"   数学目标数: {math_count}")
    
    preparing_count = goal_dao.count_by_kwargs({"status": GoalStatus.PREPARING})
    print(f"   准备中目标数: {preparing_count}")
    
    # 清理测试数据
    for goal in created_goals:
        goal_dao.delete(goal)
    print("✅ 计数功能测试完成")

if __name__ == "__main__":
    print("🚀 开始模糊匹配功能测试...\n")
    
    try:
        test_goal_fuzzy_search()
        test_question_fuzzy_search()
        test_user_fuzzy_search()
        test_count_functions()
        
        print("\n✨ 所有模糊匹配功能测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 