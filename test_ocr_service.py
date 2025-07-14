#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OCR服务的功能
"""

from service.ocr_service import OCRService, read_text_from_image, OCRResult


def test_local_file():
    """测试本地文件OCR识别"""
    print("=== 测试本地文件OCR识别 ===")
    
    ocr_service = OCRService()
    
    try:
        # 测试本地文件
        results = ocr_service.read_from_file('99999.png')
        print(f"识别到 {len(results)} 个文本区域:")
        
        for i, result in enumerate(results, 1):
            print(f"\n文本区域 {i}:")
            print(f"  文本内容: {result.text}")
            print(f"  置信度: {result.confidence:.3f}")
            print(f"  边界框: {result.bbox}")
            
    except Exception as e:
        print(f"本地文件识别失败: {e}")


def test_generic_method():
    """测试通用方法"""
    print("\n=== 测试通用方法 ===")
    
    try:
        # 使用便捷函数
        results = read_text_from_image('99999.png')
        print(f"使用便捷函数识别到 {len(results)} 个文本区域:")
        
        for i, result in enumerate(results, 1):
            print(f"\n文本区域 {i}:")
            print(f"  文本内容: {result.text}")
            print(f"  置信度: {result.confidence:.3f}")
            print(f"  边界框: {result.bbox}")
            
    except Exception as e:
        print(f"通用方法识别失败: {e}")


def test_ocr_result_structure():
    """测试OCRResult结构"""
    print("\n=== 测试OCRResult结构 ===")
    
    # 创建一个示例OCRResult对象
    sample_result = OCRResult(
        text="示例文本",
        bbox=[[100, 100], [200, 100], [200, 150], [100, 150]],
        confidence=0.95
    )
    
    print(f"示例OCRResult对象:")
    print(f"  文本: {sample_result.text}")
    print(f"  置信度: {sample_result.confidence}")
    print(f"  边界框: {sample_result.bbox}")
    print(f"  边界框类型: {type(sample_result.bbox)}")
    print(f"  置信度类型: {type(sample_result.confidence)}")


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    ocr_service = OCRService()
    
    # 测试不存在的文件
    try:
        results = ocr_service.read_from_file('不存在的文件.png')
    except FileNotFoundError as e:
        print(f"预期的文件不存在错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")


if __name__ == "__main__":
    print("开始测试OCR服务...\n")
    
    test_ocr_result_structure()
    test_local_file()
    test_generic_method()
    test_error_handling()
    
    print("\n测试完成！") 