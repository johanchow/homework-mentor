"""
UserDAO 使用示例
"""

from entity.user import User, create_user
from dao.user_dao import user_dao
from dao.database import init_database
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """主函数 - 演示UserDAO的使用"""

    # 初始化数据库
    logger.info("初始化数据库...")
    init_database()

    # 示例1: 创建用户
    logger.info("=== 创建用户示例 ===")
    user1 = create_user(
        name="张三",
        email="zhangsan@example.com",
        phone="13800138000"
    )

    user2 = create_user(
        name="李四",
        email="lisi@example.com",
        phone="13800138001"
    )

    # 保存到数据库
    saved_user1 = user_dao.create_user(user1)
    saved_user2 = user_dao.create_user(user2)

    print(f"创建用户1: {saved_user1}")
    print(f"创建用户2: {saved_user2}")

    # 示例2: 根据ID查询用户
    logger.info("=== 根据ID查询用户示例 ===")
    found_user = user_dao.get_user_by_id(saved_user1.id)
    if found_user:
        print(f"找到用户: {found_user}")
    else:
        print("用户不存在")

    # 示例3: 根据邮箱查询用户
    logger.info("=== 根据邮箱查询用户示例 ===")
    email_user = user_dao.get_user_by_email("zhangsan@example.com")
    if email_user:
        print(f"通过邮箱找到用户: {email_user}")

    # 示例5: 搜索用户
    logger.info("=== 搜索用户示例 ===")
    search_results = user_dao.search_users(name="张")
    print(f"搜索包含'张'的用户: {len(search_results)} 个")
    for user in search_results:
        print(f"  - {user}")

    # 示例6: 更新用户
    logger.info("=== 更新用户示例 ===")
    update_data = {
        "name": "张三丰",
        "avatar": "https://example.com/avatar/zhangsan.jpg"
    }
    updated_user = user_dao.update_user(saved_user1.id, update_data)
    if updated_user:
        print(f"更新后的用户: {updated_user}")

    # 示例7: 停用用户
    logger.info("=== 停用用户示例 ===")
    deactivated_user = user_dao.deactivate_user(saved_user2.id)
    if deactivated_user:
        print(f"停用后的用户: {deactivated_user}")

    # 示例10: 软删除用户
    logger.info("=== 软删除用户示例 ===")
    deleted = user_dao.delete_user(saved_user2.id)
    if deleted:
        print("用户软删除成功")

        # 验证用户已被软删除
        deleted_user = user_dao.get_user_by_id(saved_user2.id)
        if deleted_user is None:
            print("用户已被软删除，无法通过get_user_by_id查询到")

    logger.info("示例演示完成！")


if __name__ == "__main__":
    main()
