"""
测试Question实体类的功能
"""

from entity.question import Question, QuestionType, Subject, MediaFile, create_question
import json


def test_basic_question_creation():
    """测试基本问题创建"""
    print("🧪 测试基本问题创建...")
    
    # 创建选择题
    question = create_question(
        subject=Subject.CHINESE,
        question_type=QuestionType.MULTIPLE_CHOICE,
        title="下列词语中加点字的读音完全正确的一项是",
        content="A. 憧憬(chōng jǐng) B. 憧憬(chōng jìng) C. 憧憬(chōng jīng) D. 憧憬(chōng jīng)",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty=3,
        points=5,
        tags=["语文", "字音", "选择题"]
    )
    
    print(f"问题ID: {question.id}")
    print(f"科目: {question.subject}")
    print(f"类型: {question.question_type}")
    print(f"标题: {question.title}")
    print(f"难度: {question.difficulty}")
    print(f"分值: {question.points}")
    print(f"标签: {question.tags}")
    
    assert question.subject == Subject.CHINESE
    assert question.question_type == QuestionType.MULTIPLE_CHOICE
    assert question.is_multiple_choice() == True
    print("✅ 基本问题创建测试通过!")


def test_media_operations():
    """测试媒体文件操作"""
    print("\n🧪 测试媒体文件操作...")
    
    question = create_question(
        subject=Subject.ENGLISH,
        question_type=QuestionType.ORAL,
        title="请朗读下面的英语句子",
        content="Hello, how are you today?",
        difficulty=2,
        points=3
    )
    
    # 添加图片
    image_id = question.add_image("题目图片.jpg", "https://example.com/image1.jpg", 1024000)
    print(f"添加图片，ID: {image_id}")
    
    # 添加音频
    audio_id = question.add_audio("朗读音频.mp3", "https://example.com/audio1.mp3", 30.5, 2048000)
    print(f"添加音频，ID: {audio_id}")
    
    # 添加视频
    video_id = question.add_video("示范视频.mp4", "https://example.com/video1.mp4", 120.0, 10485760, "https://example.com/thumbnail.jpg")
    print(f"添加视频，ID: {video_id}")
    
    # 检查媒体文件统计
    media_count = question.get_media_count()
    print(f"媒体文件统计: {media_count}")
    
    assert media_count["images"] == 1
    assert media_count["audios"] == 1
    assert media_count["videos"] == 1
    assert media_count["total"] == 3
    assert question.has_media() == True
    
    # 移除媒体文件
    removed = question.remove_media(image_id)
    print(f"移除图片: {removed}")
    
    media_count = question.get_media_count()
    print(f"移除后媒体文件统计: {media_count}")
    
    assert media_count["images"] == 0
    assert media_count["total"] == 2
    
    print("✅ 媒体文件操作测试通过!")


def test_different_question_types():
    """测试不同的问题类型"""
    print("\n🧪 测试不同的问题类型...")
    
    # 填空题
    fill_blank = create_question(
        subject=Subject.MATH,
        question_type=QuestionType.FILL_BLANK,
        title="计算：2 + 3 = ___",
        correct_answer="5",
        difficulty=1,
        points=2
    )
    
    # 口述题
    oral = create_question(
        subject=Subject.CHINESE,
        question_type=QuestionType.ORAL,
        title="请背诵《静夜思》",
        content="床前明月光，疑是地上霜。举头望明月，低头思故乡。",
        difficulty=2,
        points=5
    )
    
    # 表演题
    performance = create_question(
        subject=Subject.ENGLISH,
        question_type=QuestionType.PERFORMANCE,
        title="请表演一个英语对话",
        content="角色A: Hello, nice to meet you!\n角色B: Nice to meet you too!",
        difficulty=4,
        points=10
    )
    
    print(f"填空题类型: {fill_blank.question_type}")
    print(f"口述题类型: {oral.question_type}")
    print(f"表演题类型: {performance.question_type}")
    
    assert fill_blank.question_type == QuestionType.FILL_BLANK
    assert oral.question_type == QuestionType.ORAL
    assert performance.question_type == QuestionType.PERFORMANCE
    
    print("✅ 不同问题类型测试通过!")


def test_serialization():
    """测试序列化和反序列化"""
    print("\n🧪 测试序列化和反序列化...")
    
    question = create_question(
        subject=Subject.PHYSICS,
        question_type=QuestionType.MULTIPLE_CHOICE,
        title="下列哪个是力的单位？",
        options=["牛顿", "焦耳", "瓦特", "安培"],
        correct_answer="牛顿",
        difficulty=2,
        points=3
    )
    
    # 添加媒体文件
    question.add_image("物理图.jpg", "https://example.com/physics.jpg")
    question.add_audio("题目朗读.mp3", "https://example.com/audio.mp3", 15.0)
    
    # 转换为字典
    question_dict = question.to_dict()
    print(f"转换为字典成功，包含 {len(question_dict)} 个字段")
    
    # 从字典创建新实例
    new_question = Question.from_dict(question_dict)
    print(f"从字典创建新实例成功，ID: {new_question.id}")
    
    # 转换为JSON
    question_json = json.dumps(question_dict, ensure_ascii=False, indent=2)
    print(f"转换为JSON成功，长度: {len(question_json)} 字符")
    
    assert new_question.id == question.id
    assert new_question.subject == question.subject
    assert new_question.question_type == question.question_type
    
    print("✅ 序列化和反序列化测试通过!")


def test_subject_enum():
    """测试科目枚举"""
    print("\n🧪 测试科目枚举...")
    
    subjects = [
        Subject.CHINESE,
        Subject.ENGLISH,
        Subject.MATH,
        Subject.PHYSICS,
        Subject.CHEMISTRY,
        Subject.BIOLOGY,
        Subject.HISTORY,
        Subject.GEOGRAPHY,
        Subject.POLITICS,
        Subject.OTHER
    ]
    
    for subject in subjects:
        question = create_question(
            subject=subject,
            question_type=QuestionType.MULTIPLE_CHOICE,
            title=f"这是一个{subject.value}题目",
            difficulty=1,
            points=1
        )
        print(f"创建{subject.value}科目题目成功")
    
    print("✅ 科目枚举测试通过!")


def main():
    """主测试函数"""
    print("🚀 开始测试Question实体类...")
    
    try:
        test_basic_question_creation()
        test_media_operations()
        test_different_question_types()
        test_serialization()
        test_subject_enum()
        
        print("\n🎉 所有测试通过!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 