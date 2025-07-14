import easyocr
import requests
import tempfile
import os
from typing import List, Dict, Union
from dataclasses import dataclass


@dataclass
class OCRResult:
    """OCR识别结果的数据类"""
    text: str
    bbox: List[List[int]]  # 边界框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    confidence: float


class OCRService:
    """OCR服务类，支持本地文件和URL图片识别"""
    
    def __init__(self, languages: List[str] = None):
        """
        初始化OCR服务
        
        Args:
            languages: 支持的语言列表，默认为中文简体和英文
        """
        if languages is None:
            languages = ['ch_sim', 'en']
        self.reader = easyocr.Reader(languages)
    
    def read_from_file(self, file_path: str) -> List[OCRResult]:
        """
        从本地文件读取图片进行OCR识别
        
        Args:
            file_path: 本地图片文件路径
            
        Returns:
            OCRResult对象列表
            
        Raises:
            FileNotFoundError: 文件不存在
            Exception: OCR识别失败
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            results = self.reader.readtext(file_path)
            return self._convert_to_ocr_results(results)
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}")
    
    def read_from_url(self, url: str) -> List[OCRResult]:
        """
        从URL读取图片进行OCR识别
        
        Args:
            url: 图片URL地址
            
        Returns:
            OCRResult对象列表
            
        Raises:
            Exception: 下载图片或OCR识别失败
        """
        try:
            # 下载图片到临时文件
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            try:
                # 进行OCR识别
                results = self.reader.readtext(temp_file_path)
                return self._convert_to_ocr_results(results)
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except requests.RequestException as e:
            raise Exception(f"下载图片失败: {str(e)}")
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}")
    
    def read_image(self, image_source: Union[str, bytes]) -> List[OCRResult]:
        """
        通用的图片OCR识别方法，自动判断输入类型
        
        Args:
            image_source: 图片源，可以是文件路径、URL或图片字节数据
            
        Returns:
            OCRResult对象列表
        """
        if isinstance(image_source, str):
            # 判断是URL还是文件路径
            if image_source.startswith(('http://', 'https://')):
                return self.read_from_url(image_source)
            else:
                return self.read_from_file(image_source)
        elif isinstance(image_source, bytes):
            # 处理字节数据
            return self.read_from_bytes(image_source)
        else:
            raise ValueError("不支持的图片源类型，请提供文件路径、URL或字节数据")
    
    def read_from_bytes(self, image_bytes: bytes) -> List[OCRResult]:
        """
        从字节数据读取图片进行OCR识别
        
        Args:
            image_bytes: 图片字节数据
            
        Returns:
            OCRResult对象列表
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_bytes)
                temp_file_path = temp_file.name
            
            try:
                results = self.reader.readtext(temp_file_path)
                return self._convert_to_ocr_results(results)
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}")
    
    def _convert_to_ocr_results(self, easyocr_results: List) -> List[OCRResult]:
        """
        将EasyOCR的结果转换为OCRResult对象列表
        
        Args:
            easyocr_results: EasyOCR的原始结果
            
        Returns:
            OCRResult对象列表
        """
        ocr_results = []
        for result in easyocr_results:
            bbox, text, confidence = result
            # 将numpy数组转换为普通Python列表，确保边界框格式清晰
            bbox_list = [[int(point[0]), int(point[1])] for point in bbox]
            ocr_result = OCRResult(
                text=text,
                bbox=bbox_list,
                confidence=float(confidence)
            )
            ocr_results.append(ocr_result)
        return ocr_results


# 创建默认的OCR服务实例
default_ocr_service = OCRService()


def read_text_from_image(image_source: Union[str, bytes]) -> List[OCRResult]:
    """
    便捷函数：从图片中读取文本
    
    Args:
        image_source: 图片源（文件路径、URL或字节数据）
        
    Returns:
        OCRResult对象列表
    """
    return default_ocr_service.read_image(image_source)


# 示例用法
if __name__ == "__main__":
    # 创建OCR服务实例
    ocr_service = OCRService()
    
    # 从本地文件读取
    try:
        results = ocr_service.read_from_file('99999.png')
        print("本地文件识别结果:")
        for result in results:
            print(f"文本: {result.text}")
            print(f"置信度: {result.confidence:.2f}")
            print(f"边界框: {result.bbox}")
            print("---")
    except Exception as e:
        print(f"本地文件识别失败: {e}")
    
    # 从URL读取（示例）
    # try:
    #     results = ocr_service.read_from_url('https://example.com/image.png')
    #     print("URL图片识别结果:")
    #     for result in results:
    #         print(f"文本: {result.text}")
    #         print(f"置信度: {result.confidence:.2f}")
    #         print(f"边界框: {result.bbox}")
    #         print("---")
    # except Exception as e:
    #     print(f"URL图片识别失败: {e}")
