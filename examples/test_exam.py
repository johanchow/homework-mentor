"""
测试Exam实体类和ExamDAO的功能
"""

import json
from datetime import datetime
from entity.exam import Exam, Answer, create_exam
from entity.question import Question, QuestionType, Subject, create_question
from entity.message import create_message, Message, MessageRole
from entity.user import User, create_user
from entity.paper import Paper
from dao.database import init_database
from dao.exam_dao import exam_dao
from dao.user_dao import user_dao
from dao.paper_dao import paper_dao


def test_answer_entity():
    """测试Answer实体类"""
    print("🧪 测试Answer实体类...")
    
    # 创建测试问题
    question = create_question(
        subject=Subject.CHINESE,
        type=QuestionType.CHOICE,
        title="下列词语中加点字的读音完全正确的一项是",
        options=["A. 憧憬(chōng jǐng)", "B. 憧憬(chōng jìng)", "C. 憧憬(chōng jīng)", "D. 憧憬(chōng jīng)"],
        creator_id='123'
    )
    
    # 创建测试消息
    message = create_message(
        role=MessageRole.USER,
        content="请帮我解答这道题",
    )
    
    # 创建Answer对象
    answer = Answer(
        question=[question],
        messages={
            question.id: [message]
        },
        answer={
            question.id: "A"
        }
    )
    
    print(f"Answer对象创建成功")
    print(f"  问题数量: {len(answer.question)}")
    print(f"  消息数量: {len(answer.messages)}")
    print(f"  答案数量: {len(answer.answer)}")
    
    # 测试序列化
    answer_json = answer.model_dump_json()
    print(f"序列化成功，JSON长度: {len(answer_json)}")
    
    print("✅ Answer实体类测试完成!")


def test_exam_entity():
    """测试Exam实体类"""
    print("\n🧪 测试Exam实体类...")
    
    # 创建测试用户
    examinee = create_user(
        name="张三",
        email="zhangsan@example.com"
    )
    
    # 创建测试试卷
    paper = Paper(
        title="语文期中考试",
        description="包含字音、词语填空等题型",
        creator=examinee,
        questions=[]
    )
    
    # 创建测试问题
    question = create_question(
        subject=Subject.CHINESE,
        type=QuestionType.CHOICE,
        title="下列词语中加点字的读音完全正确的一项是",
        options=["A. 憧憬(chōng jǐng)", "B. 憧憬(chōng jìng)", "C. 憧憬(chōng jīng)", "D. 憧憬(chōng jīng)"],
        creator_id='123'
    )
    
    # 创建Answer对象
    answer = Answer(
        question=[question],
        messages={
            question.id: [create_message(
                role=MessageRole.USER,
                content="请帮我解答这道题"
            )]
        },
        answer={
            question.id: "A"
        }
    )
    
    # 创建Exam对象
    exam = create_exam(
        paper_id=paper.id,
        examinee_id=examinee.id,
        answer=answer
    )
    
    print(f"Exam对象创建成功")
    print(f"  考试ID: {exam.id}")
    print(f"  试卷ID: {exam.paper_id}")
    print(f"  考生ID: {exam.examinee_id}")
    print(f"  创建时间: {exam.created_at}")
    print(f"  是否删除: {exam.is_deleted}")
    
    # 测试get_answer方法
    retrieved_answer = exam.get_answer()
    print(f"获取答卷成功，问题数量: {len(retrieved_answer.question)}")
    
    print("✅ Exam实体类测试完成!")


def test_exam_dao_basic_operations():
    """测试ExamDAO基本操作"""
    print("\n🧪 测试ExamDAO基本操作...")
    
    # 创建测试用户
    examinee = create_user(
        name="李四",
        email="lisi@example.com"
    )
    examinee_id = examinee.id
    user_dao.create(examinee)
    
    # 创建测试试卷
    paper = Paper(
        title="数学期末考试",
        description="包含选择题和填空题",
        creator=examinee,
        questions=[]
    )
    paper_id = paper.id
    paper_dao.create(paper)
    
    # 创建测试问题
    question = create_question(
        subject=Subject.MATH,
        type=QuestionType.CHOICE,
        title="1 + 1 = ?",
        options=["A. 1", "B. 2", "C. 3", "D. 4"],
        creator_id='123'
    )
    
    # 创建Answer对象
    answer = Answer(
        question=[question],
        messages={
            question.id: [
                create_message(role=MessageRole.USER, content="请帮我计算"),
                create_message(role=MessageRole.ASSISTANT, content="1+1=2，答案是B")
            ]
        },
        answer={
            question.id: "B"
        }
    )
    
    # 创建Exam对象
    print(f"examinee: {examinee}")
    exam = create_exam(
        paper_id=paper_id,
        examinee_id=examinee_id,
        answer=answer
    )
    
    # 测试创建
    created_exam = exam_dao.create(exam)
    print(f"创建考试成功: {created_exam.id}")
    
    # 测试查询
    retrieved_exam = exam_dao.get_by_id(created_exam.id)
    print(f"查询考试成功: {retrieved_exam.id}")
    
    # 测试搜索
    exams_by_paper = exam_dao.list_exams_by_paper_id(paper_id)
    print(f"根据试卷ID查询考试数量: {len(exams_by_paper)}")
    
    exams_by_examinee = exam_dao.list_exams_by_examinee_id(examinee_id)
    print(f"根据考生ID查询考试数量: {len(exams_by_examinee)}")
    
    # 测试统计
    count = exam_dao.count_by_kwargs({"paper_id": paper_id})
    print(f"统计考试数量: {count}")
    
    # 测试更新
    new_answer = Answer(
        question=[question],
        messages={
            question.id: [
                create_message(role=MessageRole.USER, content="请重新计算"),
                create_message(role=MessageRole.ASSISTANT, content="重新计算：1+1=2，答案是B")
            ]
        },
        answer={
            question.id: "B"
        }
    )
    
    updated_exam = exam_dao.update_answer(created_exam.id, new_answer)
    print(f"更新考试成功: {updated_exam.id}")
    
    # 测试删除
    exam_dao.delete(created_exam)
    print(f"删除考试成功")
    
    # 验证删除
    deleted_exam = exam_dao.get_by_id(created_exam.id)
    print(f"删除后查询结果: {deleted_exam is None}")
    
    print("✅ ExamDAO基本操作测试完成!")


def test_exam_dao_advanced_operations():
    """测试ExamDAO高级操作"""
    print("\n🧪 测试ExamDAO高级操作...")
    
    # 创建测试数据
    examinee = create_user(name="王五", email="wangwu@example.com")
    examinee_id = examinee.id
    user_dao.create(examinee)
    paper = Paper(title="语文测试", description="语文题目", creator=examinee, questions=[])
    paper_id = paper.id
    paper_dao.create(paper)
    
    # 创建测试问题
    question = create_question(
        subject=Subject.CHINESE,
        type=QuestionType.CHOICE,
        title="测试题目",
        options=["A", "B", "C", "D"],
        creator_id='123'
    )
    
    answer = Answer(
        question=[question],
        messages={question.id: [create_message(role=MessageRole.USER, content="测试")]},
        answer={question.id: "A"}
    )
    
    # 创建考试记录
    exam = create_exam(
        paper_id=paper_id,
        examinee_id=examinee_id,
        answer=answer
    )
    created_exam = exam_dao.create(exam)
    
    # 测试获取详细信息
    exam_details = exam_dao.get_exam_with_details(created_exam.id)
    print(f"获取考试详细信息成功")
    print(f"  考试: {exam_details['exam'].id}")
    print(f"  试卷: {exam_details['paper'].title}")
    print(f"  考生: {exam_details['examinee'].name}")
    print(f"  答卷问题数: {len(exam_details['answer'].question)}")
    
    # 清理测试数据
    exam_dao.delete(created_exam)
    
    print("✅ ExamDAO高级操作测试完成!")


def test_exam_dao_search_operations():
    """测试ExamDAO搜索操作"""
    print("\n🧪 测试ExamDAO搜索操作...")
    
    # 创建测试数据
    examinee1 = create_user(name="赵六", email="zhaoliu@example.com")
    examinee2 = create_user(name="钱七", email="qianqi@example.com")
    examinee1_id = examinee1.id
    examinee2_id = examinee2.id
    user_dao.create(examinee1)
    user_dao.create(examinee2)
    
    paper1 = Paper(title="数学测试1", description="数学题目1", creator=examinee1, questions=[])
    paper2 = Paper(title="数学测试2", description="数学题目2", creator=examinee1, questions=[])
    paper1_id = paper1.id
    paper2_id = paper2.id
    paper_dao.create(paper1)
    paper_dao.create(paper2)
    
    # 创建测试问题
    question = create_question(
        subject=Subject.MATH,
        type=QuestionType.CHOICE,
        title="测试数学题",
        options=["A", "B", "C", "D"],
        creator_id='123'
    )
    
    answer = Answer(
        question=[question],
        messages={question.id: [create_message(role=MessageRole.USER, content="测试")]},
        answer={question.id: "A"}
    )
    
    # 创建多个考试记录
    exams = []
    for i in range(3):
        exam = create_exam(
            paper_id=paper1_id if i < 2 else paper2_id,
            examinee_id=examinee1_id if i % 2 == 0 else examinee2_id,
            answer=answer
        )
        created_exam = exam_dao.create(exam)
        exams.append(created_exam)
    
    # 测试根据试卷ID搜索
    exams_paper1 = exam_dao.list_exams_by_paper_id(paper1_id)
    print(f"试卷1的考试数量: {len(exams_paper1)}")
    
    exams_paper2 = exam_dao.list_exams_by_paper_id(paper2_id)
    print(f"试卷2的考试数量: {len(exams_paper2)}")
    
    # 测试根据考生ID搜索
    exams_examinee1 = exam_dao.list_exams_by_examinee_id(examinee1_id)
    print(f"考生1的考试数量: {len(exams_examinee1)}")
    
    exams_examinee2 = exam_dao.list_exams_by_examinee_id(examinee2_id)
    print(f"考生2的考试数量: {len(exams_examinee2)}")
    
    # 测试通用搜索
    search_results = exam_dao.search_by_kwargs({"paper_id": paper1_id}, skip=0, limit=10)
    print(f"通用搜索试卷1的考试数量: {len(search_results)}")
    
    # 测试统计
    count_paper1 = exam_dao.count_by_kwargs({"paper_id": paper1_id})
    print(f"试卷1的考试统计: {count_paper1}")
    
    count_examinee1 = exam_dao.count_by_kwargs({"examinee_id": examinee1_id})
    print(f"考生1的考试统计: {count_examinee1}")
    
    # 清理测试数据
    for exam in exams:
        exam_dao.delete(exam)
    
    print("✅ ExamDAO搜索操作测试完成!")


def test_exam_dao_error_handling():
    """测试ExamDAO错误处理"""
    print("\n🧪 测试ExamDAO错误处理...")
    
    # 测试查询不存在的考试
    non_existent_exam = exam_dao.get_by_id("non-existent-id")
    print(f"查询不存在的考试: {non_existent_exam is None}")
    
    # 测试更新不存在的考试
    try:
        question = create_question(
            subject=Subject.CHINESE,
            type=QuestionType.CHOICE,
            title="测试题目",
            options=["A", "B", "C", "D"],
            creator_id='123'
        )
        
        answer = Answer(
            question=[question],
            messages={question.id: [create_message(role=MessageRole.USER, content="测试")]},
            answer={question.id: "A"}
        )
        
        exam_dao.update_answer("non-existent-id", answer)
        print("❌ 应该抛出异常但没有")
    except ValueError as e:
        print(f"✅ 正确捕获异常: {e}")
    
    # 测试搜索不存在的试卷
    non_existent_exams = exam_dao.list_exams_by_paper_id("non-existent-paper-id")
    print(f"搜索不存在试卷的考试: {len(non_existent_exams)}")
    
    # 测试搜索不存在的考生
    non_existent_exams = exam_dao.list_exams_by_examinee_id("non-existent-examinee-id")
    print(f"搜索不存在考生的考试: {len(non_existent_exams)}")
    
    print("✅ ExamDAO错误处理测试完成!")


def test_exam_dao_pagination():
    """测试ExamDAO分页功能"""
    print("\n🧪 测试ExamDAO分页功能...")
    
    # 创建测试数据
    examinee = create_user(name="孙八", email="sunba@example.com")
    examinee_id = examinee.id
    user_dao.create(examinee)
    
    paper = Paper(title="分页测试试卷", description="测试分页", creator=examinee, questions=[])
    paper_id = paper.id
    paper_dao.create(paper)
    
    # 创建测试问题
    question = create_question(
        subject=Subject.CHINESE,
        type=QuestionType.CHOICE,
        title="分页测试题",
        options=["A", "B", "C", "D"],
        creator_id='123'
    )
    
    answer = Answer(
        question=[question],
        messages={question.id: [create_message(role=MessageRole.USER, content="测试")]},
        answer={question.id: "A"}
    )
    
    # 创建多个考试记录
    exams = []
    for i in range(5):
        exam = create_exam(
            paper_id=paper_id,
            examinee_id=examinee_id,
            answer=answer
        )
        created_exam = exam_dao.create(exam)
        exams.append(created_exam)
    
    # 测试分页查询
    page1 = exam_dao.list_exams_by_paper_id(paper_id, skip=0, limit=2)
    print(f"第一页考试数量: {len(page1)}")
    
    page2 = exam_dao.list_exams_by_paper_id(paper_id, skip=2, limit=2)
    print(f"第二页考试数量: {len(page2)}")
    
    page3 = exam_dao.list_exams_by_paper_id(paper_id, skip=4, limit=2)
    print(f"第三页考试数量: {len(page3)}")
    
    # 测试通用搜索分页
    search_page1 = exam_dao.search_by_kwargs({"paper_id": paper_id}, skip=0, limit=3)
    print(f"通用搜索第一页数量: {len(search_page1)}")
    
    search_page2 = exam_dao.search_by_kwargs({"paper_id": paper_id}, skip=3, limit=3)
    print(f"通用搜索第二页数量: {len(search_page2)}")
    
    # 清理测试数据
    for exam in exams:
        exam_dao.delete(exam)
    
    print("✅ ExamDAO分页功能测试完成!")


def main():
    """主测试函数"""
    print("🚀 开始测试Exam实体类和ExamDAO...")
    print("=" * 60)
    
    try:
        # 测试实体类
        test_answer_entity()
        test_exam_entity()
        
        # 测试DAO基本操作
        test_exam_dao_basic_operations()
        
        # 测试DAO高级操作
        test_exam_dao_advanced_operations()
        
        # 测试搜索操作
        test_exam_dao_search_operations()
        
        # 测试分页功能
        test_exam_dao_pagination()
        
        # 测试错误处理
        test_exam_dao_error_handling()
        
        print("\n🎉 所有测试通过!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    init_database()
    main()
