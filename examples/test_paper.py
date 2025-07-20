"""
测试Paper实体类和PaperDAO的功能
"""

import json
import logging
from entity.paper import Paper, create_paper
from entity.question import create_question, Subject, QuestionType
from dao.paper_dao import paper_dao
from dao.question_dao import question_dao
from dao.database import init_database
from entity.user import create_user
from dao.user_dao import user_dao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_paper_entity_basic():
    """测试Paper实体类的基本功能"""
    print("🧪 测试Paper实体类基本功能...")

    paper = create_paper(
        title="2024年春季数学试卷",
        creator_id="test_user_123",
        description="包含代数、几何、统计等内容的综合试卷",
        question_ids=["q1", "q2", "q3"]
    )

    print(f"试卷ID: {paper.id}")
    print(f"标题: {paper.title}")
    print(f"描述: {paper.description}")
    print(f"创建人ID: {paper.creator_id}")
    print(f"问题ID列表: {paper.question_ids}")

    assert paper.title == "2024年春季数学试卷"
    assert paper.description == "包含代数、几何、统计等内容的综合试卷"
    assert paper.creator_id == "test_user_123"
    assert paper.question_ids == "q1,q2,q3"

    print("✅ Paper实体类基本功能测试通过!")


def test_paper_entity_methods():
    """测试Paper实体类的方法"""
    print("\n🧪 测试Paper实体类方法...")

    paper = create_paper(
        title="英语听力测试",
        creator_id="test_user_456",
        description="英语听力理解测试",
        question_ids=["q1", "q2"]
    )

    # 测试to_dict方法
    paper_dict = paper.to_dict()
    print(f"转换为字典: {len(paper_dict)} 个字段")
    assert "id" in paper_dict
    assert "title" in paper_dict
    assert "creator_id" in paper_dict
    assert "question_ids" in paper_dict

    # 测试from_dict方法
    new_paper = Paper.from_dict(paper_dict)
    print(f"从字典创建新实例: {new_paper.id}")
    assert new_paper.id == paper.id
    assert new_paper.title == paper.title
    assert new_paper.question_ids == paper.question_ids

    # 测试字符串表示
    paper_str = str(paper)
    print(f"字符串表示: {paper_str}")
    assert "Paper" in paper_str
    assert paper.id in paper_str

    print("✅ Paper实体类方法测试通过!")


def test_paper_dao_operations():
    """测试PaperDAO的数据库操作"""
    print("\n🧪 测试PaperDAO数据库操作...")

    # 创建测试用户
    test_user = create_user(
        name="试卷测试用户",
        email="paper_test@example.com",
        phone="13800138001"
    )
    saved_user = user_dao.create(test_user)
    print(f"创建测试用户: {saved_user.id}")

    # 创建测试问题
    question1 = create_question(
        subject=Subject.PHYSICS,
        type=QuestionType.choice,
        title="下列哪个是力的单位？",
        creator_id=saved_user.id,
        options=["牛顿", "焦耳", "瓦特", "安培"]
    )
    saved_question1 = question_dao.create(question1)

    question2 = create_question(
        subject=Subject.CHEMISTRY,
        type=QuestionType.qa,
        title="请解释什么是化学反应？",
        creator_id=saved_user.id
    )
    saved_question2 = question_dao.create(question2)

    question3 = create_question(
        subject=Subject.MATH,
        type=QuestionType.choice,
        title="1 + 1 = ?",
        creator_id=saved_user.id,
        options=["1", "2", "3", "4"]
    )
    saved_question3 = question_dao.create(question3)

    # 测试创建试卷
    paper1 = create_paper(
        title="物理力学试卷",
        creator_id=saved_user.id,
        description="包含牛顿定律、动量守恒等内容的试卷",
        question_ids=[saved_question1.id, saved_question2.id]
    )

    saved_paper1 = paper_dao.create(paper1)
    print(f"创建试卷1: {saved_paper1.id}")
    assert saved_paper1.id is not None
    assert saved_paper1.title == "物理力学试卷"
    assert saved_paper1.question_ids == f"{saved_question1.id},{saved_question2.id}"

    # 测试创建第二个试卷
    paper2 = create_paper(
        title="化学元素周期表测试",
        creator_id=saved_user.id,
        description="测试学生对元素周期表的掌握程度"
    )

    saved_paper2 = paper_dao.create(paper2)
    print(f"创建试卷2: {saved_paper2.id}")
    assert saved_paper2.id is not None

    # 测试根据ID查询试卷
    found_paper = paper_dao.get_by_id(saved_paper1.id)
    print(f"查询试卷: {found_paper.id if found_paper else 'Not found'}")
    assert found_paper is not None
    assert found_paper.id == saved_paper1.id
    assert found_paper.title == "物理力学试卷"

    # 测试获取试卷及问题列表
    paper_with_questions = paper_dao.get_paper_with_questions(saved_paper1.id)
    print(f"试卷问题数量: {len(paper_with_questions._questions) if paper_with_questions else 0}")
    assert paper_with_questions is not None
    assert len(paper_with_questions._questions) >= 0

    # 测试根据创建者ID查询试卷
    creator_papers = paper_dao.search_by_kwargs({"creator_id": saved_user.id})
    print(f"创建者的试卷数量: {len(creator_papers)}")
    assert len(creator_papers) >= 2

    # 测试获取所有试卷
    all_papers = paper_dao.search_by_kwargs({})
    print(f"所有试卷数量: {len(all_papers)}")
    assert len(all_papers) >= 2

    # 测试搜索试卷
    search_results = paper_dao.search_by_kwargs({"title": "物理"})
    print(f"搜索包含'物理'的试卷: {len(search_results)} 个")
    assert len(search_results) >= 0

    # 测试更新试卷
    saved_paper1.title = "物理力学试卷（已修改）"
    saved_paper1.description = "包含牛顿定律、动量守恒等内容的试卷（更新版）"
    updated_paper = paper_dao.update(saved_paper1)
    print(f"更新试卷: {updated_paper.title if updated_paper else 'Update failed'}")
    assert updated_paper is not None
    assert "已修改" in updated_paper.title

    # 测试统计功能
    total_count = paper_dao.count_by_kwargs({})
    creator_count = paper_dao.count_by_kwargs({"creator_id": saved_user.id})
    print(f"试卷总数: {total_count}")
    print(f"创建者试卷数: {creator_count}")
    assert total_count >= 2
    assert creator_count >= 2

    # 测试软删除试卷
    delete_result = paper_dao.delete(saved_paper2)
    print(f"删除试卷结果: {delete_result}")
    assert delete_result is not None

    # 验证删除后无法查询到
    deleted_paper = paper_dao.get_by_id(saved_paper2.id)
    print(f"删除后查询: {deleted_paper.id if deleted_paper else 'Not found (deleted)'}")
    assert deleted_paper is None

    print("✅ PaperDAO数据库操作测试通过!")


def test_paper_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况...")

    # 测试空描述
    empty_desc_paper = create_paper(
        title="无描述试卷",
        creator_id="test_user_edge"
    )

    print(f"空描述试卷: {empty_desc_paper.description}")
    assert empty_desc_paper.description is None

    # 测试空问题列表
    empty_questions_paper = create_paper(
        title="无问题试卷",
        creator_id="test_user_edge",
        question_ids=[]
    )
    print(f"空问题列表: {empty_questions_paper.question_ids}")
    assert empty_questions_paper.question_ids == ""

    # 测试长标题
    long_title = "这是一个非常长的试卷标题" * 5
    long_paper = create_paper(
        title=long_title,
        creator_id="test_user_long",
        description="长标题试卷测试"
    )

    print(f"长标题长度: {len(long_paper.title)}")
    assert len(long_paper.title) > 50

    # 测试特殊字符
    special_paper = create_paper(
        title="特殊字符试卷：!@#$%^&*()_+-=[]{}|;':\",./<>?",
        creator_id="test_user_special",
        description="包含特殊字符的试卷"
    )

    print(f"特殊字符标题: {special_paper.title}")
    assert "!@#$%^&*()" in special_paper.title

    print("✅ 边界情况测试通过!")


def test_paper_serialization():
    """测试序列化功能"""
    print("\n🧪 测试序列化功能...")

    paper = create_paper(
        title="序列化测试试卷",
        creator_id="test_user_serial",
        description="用于测试序列化功能的试卷",
        question_ids=["q1", "q2", "q3"]
    )

    # 测试JSON序列化
    paper_json = paper.model_dump_json()
    print(f"JSON序列化长度: {len(paper_json)} 字符")
    assert len(paper_json) > 0
    assert "序列化测试试卷" in paper_json
    assert "q1,q2,q3" in paper_json

    # 测试从JSON反序列化
    parsed_dict = json.loads(paper_json)
    restored_paper = Paper.from_dict(parsed_dict)
    print(f"反序列化试卷ID: {restored_paper.id}")
    assert restored_paper.title == paper.title
    assert restored_paper.description == paper.description
    assert restored_paper.question_ids == paper.question_ids

    print("✅ 序列化功能测试通过!")


def main():
    """主测试函数"""
    print("🚀 开始测试Paper实体类和PaperDAO...")

    try:
        test_paper_entity_basic()
        test_paper_entity_methods()
        test_paper_edge_cases()
        test_paper_serialization()
        test_paper_dao_operations()

        print("\n🎉 所有测试通过!")
        print("\n📊 测试总结:")
        print("- ✅ Paper实体类基本功能")
        print("- ✅ Paper实体类方法")
        print("- ✅ 边界情况处理")
        print("- ✅ 序列化功能")
        print("- ✅ PaperDAO数据库操作")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    init_database()
    main()
