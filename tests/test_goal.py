#!/usr/bin/env python3
"""
Goal实体测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dao.goal_dao import goal_dao
from datetime import datetime
from entity.goal import Goal, GoalStatus, Subject, create_goal
from dao.database import init_database

def test_goal_entity():
    """测试Goal实体"""
    print("🧪 测试Goal实体...")
    
    # 创建目标实例
    goal = create_goal(
        name="掌握初中数学函数概念",
        subject=Subject.MATH,
        ai_prompt="请帮助我理解初中数学中的函数概念，包括定义、性质和应用",
        creator_id="user123",
        status=GoalStatus.PREPARING
    )
    
    print(f"✅ 目标创建成功: {goal.id}")
    print(f"   名称: {goal.name}")
    print(f"   科目: {goal.subject}")
    print(f"   状态: {goal.status}")
    print(f"   AI提示词: {goal.ai_prompt}")
    print(f"   创建人: {goal.creator_id}")
    print(f"   创建时间: {goal.created_at}")
    print(f"   更新时间: {goal.updated_at}")
    
    return goal

def test_goal_dao():
    """测试Goal DAO"""
    print("\n🧪 测试Goal DAO...")
    
    # 创建测试目标
    goal = create_goal(
        name="学习英语语法",
        subject=Subject.ENGLISH,
        ai_prompt="请帮助我学习英语语法，特别是时态和语态",
        creator_id="user456",
        status=GoalStatus.DOING
    )
    
    # 保存到数据库
    created_goal = goal_dao.create(goal)
    print(f"✅ 目标保存成功: {created_goal.id}")
    
    # 根据ID查询
    found_goal = goal_dao.get_by_id(created_goal.id)
    if found_goal:
        print(f"✅ 根据ID查询成功: {found_goal.name}")
    else:
        print("❌ 根据ID查询失败")
    
    # 根据名称搜索（模糊匹配）
    goals = goal_dao.search_by_kwargs({"name": "英语"})
    print(f"✅ 名称模糊搜索成功，找到 {len(goals)} 个目标")
    
    # 根据条件搜索
    filters = {"subject": Subject.ENGLISH, "status": GoalStatus.DOING}
    goals = goal_dao.search_by_kwargs(filters, skip=0, limit=10)
    print(f"✅ 条件搜索成功，找到 {len(goals)} 个目标")
    
    # 更新目标
    found_goal.status = GoalStatus.PASSED
    found_goal.updated_at = datetime.now()
    updated_goal = goal_dao.update(found_goal)
    print(f"✅ 目标更新成功: {updated_goal.status}")
    
    # 删除目标
    goal_dao.delete(updated_goal)
    print("✅ 目标删除成功")
    
    # 验证删除
    deleted_goal = goal_dao.get_by_id(updated_goal.id)
    if deleted_goal and deleted_goal.is_deleted:
        print("✅ 软删除验证成功")
    else:
        print("❌ 软删除验证失败")

def test_goal_status_enum():
    """测试Goal状态枚举"""
    print("\n🧪 测试Goal状态枚举...")
    
    statuses = [GoalStatus.PREPARING, GoalStatus.DOING, GoalStatus.PASSED, GoalStatus.cancelled]
    for status in statuses:
        print(f"   状态: {status}")

def test_subject_enum():
    """测试科目枚举"""
    print("\n🧪 测试科目枚举...")
    
    subjects = [Subject.CHINESE, Subject.ENGLISH, Subject.MATH, Subject.PHYSICS, Subject.CHEMISTRY, 
                Subject.BIOLOGY, Subject.HISTORY, Subject.GEOGRAPHY, Subject.POLITICS, Subject.OTHER]
    for subject in subjects:
        print(f"   科目: {subject}")

if __name__ == "__main__":
    init_database()
    print("🚀 开始Goal实体测试...\n")
    
    try:
        test_goal_entity()
        test_goal_status_enum()
        test_subject_enum()
        test_goal_dao()
        
        print("\n✨ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 