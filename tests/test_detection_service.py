#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 DetectionService 功能
"""

import os
import sys
from service.detection_service import DetectionService, detection_service


def test_local_image():
    """测试本地图像检测"""
    print("=== 测试本地图像检测 ===")
    
    # 测试文件路径
    test_image_path = "11111.png"
    
    if not os.path.exists(test_image_path):
        print(f"测试图像文件不存在: {test_image_path}")
        return
    
    try:
        # 使用全局实例
        result = detection_service.detect_images(test_image_path)
        print(f"检测结果: {result}")
        
        # 绘制检测结果
        output_path = "11111_detection_result.png"
        detection_service.draw_detection_result(test_image_path, output_path)
        
    except Exception as e:
        print(f"本地图像检测失败: {str(e)}")


def test_url_image():
    """测试URL图像检测"""
    print("\n=== 测试URL图像检测 ===")
    
    # 测试URL（这里使用一个示例URL，实际使用时请替换为有效的图像URL）
    test_image_url = "https://example.com/test_image.jpg"  # 请替换为有效的URL
    
    try:
        # 创建新的服务实例
        service = DetectionService(min_area=3000)
        result = service.detect_images(test_image_url)
        print(f"检测结果: {result}")
        
        # 绘制检测结果
        output_path = "url_detection_result.png"
        service.draw_detection_result(test_image_url, output_path)
        
    except Exception as e:
        print(f"URL图像检测失败: {str(e)}")


def test_custom_detection():
    """测试自定义参数检测"""
    print("\n=== 测试自定义参数检测 ===")
    
    test_image_path = "99999.png"
    
    if not os.path.exists(test_image_path):
        print(f"测试图像文件不存在: {test_image_path}")
        return
    
    try:
        # 创建自定义参数的服务实例
        custom_service = DetectionService(min_area=5000)  # 更小的面积阈值
        
        # 检测图像
        result = custom_service.detect_images(test_image_path)
        print(f"自定义参数检测结果: {result}")
        
        # 绘制检测结果
        output_path = "99999_custom_detection.png"
        custom_service.draw_detection_result(test_image_path, output_path)
        
    except Exception as e:
        print(f"自定义参数检测失败: {str(e)}")


def test_coordinate_format():
    """测试坐标格式"""
    print("\n=== 测试坐标格式 ===")
    
    test_image_path = "11111.png"
    
    if not os.path.exists(test_image_path):
        print(f"测试图像文件不存在: {test_image_path}")
        return
    
    try:
        result = detection_service.detect_images(test_image_path)
        coords = result["images"]["coords"]
        
        print(f"检测到 {len(coords)} 个图像区域:")
        for i, coord in enumerate(coords):
            x, y, w, h = coord
            print(f"  区域 {i+1}: x={x}, y={y}, width={w}, height={h}, area={w*h}")
            
    except Exception as e:
        print(f"坐标格式测试失败: {str(e)}")


def main():
    """主测试函数"""
    print("开始测试 DetectionService...")
    
    # 测试本地图像
    test_local_image()
    
    # 测试URL图像（需要有效的URL）
    # test_url_image()
    
    # 测试自定义参数
    test_custom_detection()
    
    # 测试坐标格式
    test_coordinate_format()
    
    print("\n测试完成！")


if __name__ == "__main__":
    main() 