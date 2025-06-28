"""
测试Question实体类和QuestionDAO的功能
"""

import json
import logging
from entity.question import Question, QuestionType, Subject, create_question
from dao.question_dao import question_dao
from dao.database import init_database
from entity.user import create_user
from dao.user_dao import user_dao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_question_entity_basic():
    """测试Question实体类的基本功能"""
    print("🧪 测试Question实体类基本功能...")

    question = create_question(
        subject=Subject.CHINESE,
        type=QuestionType.CHOICE,
        title="下列词语中加点字的读音完全正确的一项是",
        creator_id="test_user_123",
        options=["A. 正确", "B. 错误", "C. 不确定", "D. 以上都不是"],
        images=["https://example.com/image1.jpg"],
        audios=["https://example.com/audio1.mp3"],
        videos=["https://example.com/video1.mp4"]
    )

    print(f"问题ID: {question.id}")
    print(f"科目: {question.subject}")
    print(f"类型: {question.type}")
    print(f"标题: {question.title}")
    print(f"选项: {question.options}")
    print(f"图片: {question.images}")

    assert question.subject == Subject.CHINESE
    assert question.type == QuestionType.CHOICE
    assert question.title == "下列词语中加点字的读音完全正确的一项是"
    assert question.options == "A. 正确,B. 错误,C. 不确定,D. 以上都不是"
    assert question.images == "https://example.com/image1.jpg"

    print("✅ Question实体类基本功能测试通过!")


def test_question_entity_methods():
    """测试Question实体类的方法"""
    print("\n🧪 测试Question实体类方法...")

    question = create_question(
        subject=Subject.MATH,
        type=QuestionType.QA,
        title="请计算 2 + 2 = ?",
        creator_id="test_user_456"
    )

    # 测试to_dict方法
    question_dict = question.to_dict()
    print(f"转换为字典: {len(question_dict)} 个字段")
    assert "id" in question_dict
    assert "subject" in question_dict
    assert "type" in question_dict

    # 测试from_dict方法
    new_question = Question.from_dict(question_dict)
    print(f"从字典创建新实例: {new_question.id}")
    assert new_question.id == question.id
    assert new_question.subject == question.subject

    # 测试字符串表示
    question_str = str(question)
    print(f"字符串表示: {question_str}")
    assert "Question" in question_str

    print("✅ Question实体类方法测试通过!")


def test_question_enum_values():
    """测试问题类型和科目枚举"""
    print("\n🧪 测试枚举值...")

    for question_type in QuestionType:
        print(f"问题类型: {question_type.value}")
        assert question_type.value in ["judge", "choice", "qa", "oral", "performance"]

    for subject in Subject:
        print(f"科目: {subject.value}")
        assert subject.value in ["chinese", "english", "math", "physics", "chemistry",
                                "biology", "history", "geography", "politics", "other"]

    print("✅ 枚举值测试通过!")


def test_question_dao_operations():
    """测试QuestionDAO的数据库操作"""
    print("\n🧪 测试QuestionDAO数据库操作...")

    # 创建测试用户
    test_user = create_user(
        name="测试用户",
        email="test@example.com",
        phone="13800138000"
    )
    saved_user = user_dao.create_user(test_user)
    print(f"创建测试用户: {saved_user.id}")

    # 测试创建问题
    question1 = create_question(
        subject=Subject.PHYSICS,
        type=QuestionType.CHOICE,
        title="下列哪个是力的单位？",
        creator_id=saved_user.id,
        options=["牛顿", "焦耳", "瓦特", "安培"],
        images=["https://example.com/physics.jpg"]
    )

    saved_question1 = question_dao.create_question(question1)
    print(f"创建问题1: {saved_question1.id}")
    assert saved_question1.id is not None

    # 测试创建第二个问题
    question2 = create_question(
        subject=Subject.CHEMISTRY,
        type=QuestionType.QA,
        title="请解释什么是化学反应？",
        creator_id=saved_user.id,
        videos=["https://example.com/chemistry.mp4"]
    )

    saved_question2 = question_dao.create_question(question2)
    print(f"创建问题2: {saved_question2.id}")
    assert saved_question2.id is not None

    # 测试根据ID查询问题
    found_question = question_dao.get_question_by_id(saved_question1.id)
    print(f"查询问题: {found_question.id if found_question else 'Not found'}")
    assert found_question is not None
    assert found_question.id == saved_question1.id

    # 测试根据创建者ID查询问题
    creator_questions = question_dao.search_questions_by_creator_id(saved_user.id)
    print(f"创建者的问题数量: {len(creator_questions)}")
    assert len(creator_questions) >= 2

    # 测试更新问题
    update_data = {
        "title": "下列哪个是力的单位？（已修改）",
        "options": "牛顿,焦耳,瓦特,安培,帕斯卡"
    }
    updated_question = question_dao.update_question(saved_question1.id, update_data)
    print(f"更新问题: {updated_question.title if updated_question else 'Update failed'}")
    assert updated_question is not None
    assert "已修改" in updated_question.title

    # 测试软删除问题
    delete_result = question_dao.delete_question(saved_question2.id)
    print(f"删除问题结果: {delete_result}")
    assert delete_result == True

    # 验证删除后无法查询到
    deleted_question = question_dao.get_question_by_id(saved_question2.id)
    print(f"删除后查询: {deleted_question.id if deleted_question else 'Not found (deleted)'}")
    assert deleted_question is None

    print("✅ QuestionDAO数据库操作测试通过!")


def test_question_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况...")

    # 测试空选项和媒体文件
    empty_question = create_question(
        subject=Subject.ENGLISH,
        type=QuestionType.JUDGE,
        title="这是一个判断题",
        creator_id="test_user_edge"
    )

    print(f"空选项问题: {empty_question.options}")
    print(f"空图片问题: {empty_question.images}")
    assert empty_question.options is None
    assert empty_question.images is None

    # 测试长标题
    long_title = "这是一个非常长的标题哦" * 10
    long_question = create_question(
        subject=Subject.HISTORY,
        type=QuestionType.ORAL,
        title=long_title,
        creator_id="test_user_long"
    )

    print(f"长标题长度: {len(long_question.title)}")
    assert len(long_question.title) > 100

    print("✅ 边界情况测试通过!")


def test_question_serialization():
    """测试序列化功能"""
    print("\n🧪 测试序列化功能...")

    question = create_question(
        subject=Subject.BIOLOGY,
        type=QuestionType.CHOICE,
        title="下列哪个是细胞的基本结构？",
        creator_id="test_user_serial",
        options=["细胞膜", "细胞核", "细胞质", "以上都是"],
        images=["https://example.com/cell.jpg"]
    )

    # 测试JSON序列化
    question_json = question.model_dump_json()
    print(f"JSON序列化长度: {len(question_json)} 字符")
    assert len(question_json) > 0
    assert "细胞" in question_json

    # 测试从JSON反序列化
    parsed_dict = json.loads(question_json)
    restored_question = Question.from_dict(parsed_dict)
    print(f"反序列化问题ID: {restored_question.id}")
    assert restored_question.title == question.title

    print("✅ 序列化功能测试通过!")


def main():
    """主测试函数"""
    print("🚀 开始测试Question实体类和QuestionDAO...")

    try:
        test_question_entity_basic()
        test_question_entity_methods()
        test_question_enum_values()
        test_question_edge_cases()
        test_question_serialization()
        test_question_dao_operations()

        print("\n🎉 所有测试通过!")
        print("\n📊 测试总结:")
        print("- ✅ Question实体类基本功能")
        print("- ✅ Question实体类方法")
        print("- ✅ 枚举值验证")
        print("- ✅ 边界情况处理")
        print("- ✅ 序列化功能")
        print("- ✅ QuestionDAO数据库操作")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    init_database()
    main()
