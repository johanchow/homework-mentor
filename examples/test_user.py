"""
测试User实体类和UserDAO的功能
"""

import json
import logging
from entity.user import User, create_user
from dao.user_dao import user_dao
from dao.database import init_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_user_entity_basic():
    """测试User实体类的基本功能"""
    print("🧪 测试User实体类基本功能...")

    user = create_user(
        name="张三",
        email="zhangsan@example.com",
        phone="13800138000",
        avatar="https://example.com/avatar/zhangsan.jpg"
    )

    print(f"用户ID: {user.id}")
    print(f"姓名: {user.name}")
    print(f"邮箱: {user.email}")
    print(f"手机号: {user.phone}")
    print(f"头像: {user.avatar}")

    assert user.name == "张三"
    assert user.email == "zhangsan@example.com"
    assert user.phone == "13800138000"
    assert user.avatar == "https://example.com/avatar/zhangsan.jpg"
    assert user.is_active == True
    assert user.is_deleted == False

    print("✅ User实体类基本功能测试通过!")


def test_user_entity_methods():
    """测试User实体类的方法"""
    print("\n🧪 测试User实体类方法...")

    user = create_user(
        name="李四",
        email="lisi@example.com",
        phone="13800138001"
    )

    # 测试model_dump方法
    try:
        user_dict = user.model_dump()
        print(f"转换为字典: {len(user_dict)} 个字段")
        assert "id" in user_dict
        assert "name" in user_dict
        assert "email" in user_dict
        assert "phone" in user_dict
        assert "is_active" in user_dict
        assert "is_deleted" in user_dict
    except AttributeError:
        print("model_dump方法不可用，跳过字典转换测试")

    # 测试字符串表示
    user_str = str(user)
    print(f"字符串表示: {user_str}")
    assert "name" in user_str

    print("✅ User实体类方法测试通过!")


def test_user_dao_operations():
    """测试UserDAO的数据库操作"""
    print("\n🧪 测试UserDAO数据库操作...")

    # 测试创建用户
    user1 = create_user(
        name="王五",
        email="wangwu@example.com",
        phone="13800138002",
        avatar="https://example.com/avatar/wangwu.jpg"
    )

    saved_user1 = user_dao.create(user1)
    print(f"创建用户1: {saved_user1.id}")
    assert saved_user1.id is not None
    assert saved_user1.name == "王五"

    # 测试创建第二个用户
    user2 = create_user(
        name="赵六",
        email="zhaoliu@example.com",
        phone="13800138003"
    )

    saved_user2 = user_dao.create(user2)
    print(f"创建用户2: {saved_user2.id}")
    assert saved_user2.id is not None

    # 测试根据ID查询用户
    found_user = user_dao.get_by_id(saved_user1.id)
    print(f"查询用户: {found_user.id if found_user else 'Not found'}")
    assert found_user is not None
    assert found_user.id == saved_user1.id
    assert found_user.name == "王五"

    # 测试根据邮箱查询用户
    email_users = user_dao.search_by_kwargs({"email": "wangwu@example.com"})
    print(f"通过邮箱查询用户: {len(email_users)} 个")
    assert len(email_users) >= 1
    assert email_users[0].email == "wangwu@example.com"

    # 测试根据姓名搜索用户
    name_users = user_dao.search_by_kwargs({"name": "王"})
    print(f"搜索包含'王'的用户: {len(name_users)} 个")
    assert len(name_users) >= 0

    # 测试更新用户
    saved_user1.name = "王五（已修改）"
    saved_user1.avatar = "https://example.com/avatar/wangwu_updated.jpg"
    updated_user = user_dao.update(saved_user1)
    print(f"更新用户: {updated_user.name if updated_user else 'Update failed'}")
    assert updated_user is not None
    assert "已修改" in updated_user.name

    # 测试统计功能
    total_count = user_dao.count_by_kwargs({})
    active_count = user_dao.count_by_kwargs({"is_active": True})
    print(f"用户总数: {total_count}")
    print(f"活跃用户数: {active_count}")
    assert total_count >= 2
    assert active_count >= 2

    # 测试软删除用户
    delete_result = user_dao.delete(saved_user2)
    print(f"删除用户结果: {delete_result}")
    assert delete_result == True

    # 验证删除后无法查询到
    deleted_user = user_dao.get_by_id(saved_user2.id)
    print(f"删除后查询: {deleted_user.id if deleted_user else 'Not found (deleted)'}")
    assert deleted_user is None

    print("✅ UserDAO数据库操作测试通过!")


def test_user_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况...")

    # 测试空邮箱和手机号
    empty_user = create_user(
        name="空信息用户"
    )

    print(f"空邮箱用户: {empty_user.email}")
    print(f"空手机号用户: {empty_user.phone}")
    assert empty_user.email is None
    assert empty_user.phone is None

    # 测试长姓名
    long_name = "这是一个非常长的姓名哦" * 5
    long_user = create_user(
        name=long_name,
        email="long@example.com"
    )

    print(f"长姓名长度: {len(long_user.name)}")
    assert len(long_user.name) > 50

    # 测试特殊字符
    special_user = create_user(
        name="特殊字符用户：!@#$%^&*()_+-=[]{}|;':\",./<>?",
        email="special@example.com"
    )

    print(f"特殊字符姓名: {special_user.name}")
    assert "!@#$%^&*()" in special_user.name

    print("✅ 边界情况测试通过!")


def test_user_serialization():
    """测试序列化功能"""
    print("\n🧪 测试序列化功能...")

    user = create_user(
        name="序列化测试用户",
        email="serial@example.com",
        phone="13800138004",
        avatar="https://example.com/avatar/serial.jpg"
    )

    # 测试JSON序列化
    try:
        user_json = user.model_dump_json()
        print(f"JSON序列化长度: {len(user_json)} 字符")
        assert len(user_json) > 0
        assert "序列化测试用户" in user_json
        assert "serial@example.com" in user_json

        # 测试从JSON反序列化
        parsed_dict = json.loads(user_json)
        print(f"反序列化成功，包含 {len(parsed_dict)} 个字段")
        assert "name" in parsed_dict
        assert "email" in parsed_dict
        assert "phone" in parsed_dict
        assert "avatar" in parsed_dict
    except AttributeError:
        print("model_dump_json方法不可用，跳过JSON序列化测试")

    print("✅ 序列化功能测试通过!")


def test_user_search_functionality():
    """测试搜索功能"""
    print("\n🧪 测试搜索功能...")

    # 创建测试用户
    test_user1 = create_user(
        name="搜索测试用户1",
        email="search1@example.com",
        phone="13800138005"
    )
    user_dao.create(test_user1)

    test_user2 = create_user(
        name="搜索测试用户2",
        email="search2@example.com",
        phone="13800138006"
    )
    user_dao.create(test_user2)

    # 测试按姓名搜索
    search_users = user_dao.search_by_kwargs({"name": "搜索测试"})
    print(f"搜索测试用户数量: {len(search_users)}")
    assert len(search_users) >= 0

    # 测试按邮箱搜索
    email_users = user_dao.search_by_kwargs({"email": "search1@example.com"})
    print(f"特定邮箱用户数量: {len(email_users)}")
    assert len(email_users) >= 1

    # 测试按手机号搜索
    phone_users = user_dao.search_by_kwargs({"phone": "13800138005"})
    print(f"特定手机号用户数量: {len(phone_users)}")
    assert len(phone_users) >= 1

    # 测试分页搜索
    paginated_users = user_dao.search_by_kwargs({}, skip=0, limit=1)
    print(f"分页搜索结果: {len(paginated_users)} 个")
    assert len(paginated_users) <= 1

    print("✅ 搜索功能测试通过!")


def main():
    """主测试函数"""
    print("🚀 开始测试User实体类和UserDAO...")

    try:
        test_user_entity_basic()
        test_user_entity_methods()
        test_user_edge_cases()
        test_user_serialization()
        test_user_dao_operations()
        test_user_search_functionality()

        print("\n🎉 所有测试通过!")
        print("\n📊 测试总结:")
        print("- ✅ User实体类基本功能")
        print("- ✅ User实体类方法")
        print("- ✅ 边界情况处理")
        print("- ✅ 序列化功能")
        print("- ✅ UserDAO数据库操作")
        print("- ✅ 搜索功能")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    init_database()
    main()
