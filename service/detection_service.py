
import cv2
import numpy as np
import requests
from typing import List, Dict, Union
from urllib.parse import urlparse
import os


class DetectionService:
    """图像检测服务，用于检测图片中的图像区域"""
    
    def __init__(self, min_area: int = 5000):
        """
        初始化检测服务
        
        Args:
            min_area: 最小区域面积阈值，用于过滤噪声
        """
        self.min_area = min_area
    
    def _load_image(self, image_source: str) -> np.ndarray:
        """
        加载图像，支持本地文件路径和URL
        
        Args:
            image_source: 图像源，可以是本地文件路径或URL
            
        Returns:
            加载的图像数组
            
        Raises:
            ValueError: 当图像源无效时
            Exception: 当图像加载失败时
        """
        # 检查是否为URL
        parsed_url = urlparse(image_source)
        if parsed_url.scheme and parsed_url.netloc:
            # 从URL加载图像
            try:
                response = requests.get(image_source, timeout=10)
                response.raise_for_status()
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if image is None:
                    raise ValueError(f"无法从URL加载图像: {image_source}")
                return image
            except Exception as e:
                raise Exception(f"从URL加载图像失败: {str(e)}")
        else:
            # 从本地文件加载图像
            if not os.path.exists(image_source):
                raise ValueError(f"本地文件不存在: {image_source}")
            
            image = cv2.imread(image_source)
            if image is None:
                raise ValueError(f"无法加载本地图像: {image_source}")
            return image
    
    def _detect_image_regions(self, image: np.ndarray) -> List[List[int]]:
        """
        检测图像中的图像区域
        
        Args:
            image: 输入图像
            
        Returns:
            检测到的区域坐标列表，每个坐标是 [x, y, w, h]
        """
        # 灰度化
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 自适应阈值二值化
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=15,
            C=8
        )
        
        # 轮廓检测
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # 过滤较小区域（通常为噪声）
        image_regions = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w * h > self.min_area:
                image_regions.append([x, y, w, h])
        
        # 按 y 坐标排序（从上到下）
        image_regions.sort(key=lambda b: b[1])
        
        return image_regions
    
    def detect_images(self, image_source: str) -> Dict[str, List[List[int]]]:
        """
        检测图像中的图像区域
        
        Args:
            image_source: 图像源，可以是本地文件路径或URL
            
        Returns:
            包含检测结果的字典，格式为 {"images": {"coords": List[List[int]]}}
            其中每个坐标是 [x, y, w, h]
        """
        # 加载图像
        image = self._load_image(image_source)
        
        # 检测图像区域
        coords = self._detect_image_regions(image)
        
        return {
            "images": [
                {
                    "coords": item
                } for item in coords
            ]
        }
    
    def draw_detection_result(self, image_source: str, output_path: str) -> None:
        """
        在图像上绘制检测结果并保存
        
        Args:
            image_source: 输入图像源
            output_path: 输出图像路径
        """
        # 加载图像
        image = self._load_image(image_source)
        
        # 检测图像区域
        coords = self._detect_image_regions(image)
        
        # 绘制检测结果
        for i, (x, y, w, h) in enumerate(coords):
            # 绘制矩形框
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 添加序号标签
            cv2.putText(image, str(i + 1), (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # 保存结果图像
        cv2.imwrite(output_path, image)
        print(f"检测结果已保存到: {output_path}")
        print(f"检测到 {len(coords)} 个图像区域")


# 创建全局实例
detection_service = DetectionService()