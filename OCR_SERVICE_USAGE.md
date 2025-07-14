# OCR服务使用说明

## 概述

重构后的OCR服务提供了更好的封装和更灵活的输入支持，支持本地文件路径、URL地址和字节数据作为输入，返回结构化的OCR结果对象。

## 主要特性

- ✅ 支持本地文件路径
- ✅ 支持图片URL地址
- ✅ 支持图片字节数据
- ✅ 返回结构化的OCRResult对象数组
- ✅ 包含文本内容、边界框坐标和置信度
- ✅ 完善的错误处理
- ✅ 自动清理临时文件

## 安装依赖

确保已安装以下依赖：
```bash
pip install easyocr requests
```

## 基本用法

### 1. 创建OCR服务实例

```python
from service.ocr_service import OCRService

# 使用默认语言（中文简体和英文）
ocr_service = OCRService()

# 自定义语言
ocr_service = OCRService(languages=['ch_sim', 'en', 'ja'])
```

### 2. 从本地文件读取

```python
# 方法1：使用专门的方法
results = ocr_service.read_from_file('path/to/image.png')

# 方法2：使用通用方法（自动判断）
results = ocr_service.read_image('path/to/image.png')
```

### 3. 从URL读取

```python
# 方法1：使用专门的方法
results = ocr_service.read_from_url('https://example.com/image.png')

# 方法2：使用通用方法（自动判断）
results = ocr_service.read_image('https://example.com/image.png')
```

### 4. 从字节数据读取

```python
# 读取图片字节数据
with open('image.png', 'rb') as f:
    image_bytes = f.read()

results = ocr_service.read_from_bytes(image_bytes)
# 或者使用通用方法
results = ocr_service.read_image(image_bytes)
```

### 5. 使用便捷函数

```python
from service.ocr_service import read_text_from_image

# 自动判断输入类型
results = read_text_from_image('path/to/image.png')
results = read_text_from_image('https://example.com/image.png')
results = read_text_from_image(image_bytes)
```

## 结果格式

每个OCR结果都是一个`OCRResult`对象，包含以下属性：

```python
@dataclass
class OCRResult:
    text: str                    # 识别的文本内容
    bbox: List[List[int]]        # 边界框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    confidence: float            # 识别置信度 (0.0-1.0)
```

### 示例结果

```python
[
    OCRResult(
        text="1.用一个水盆向浴缸中倒水",
        bbox=[[68, 19], [1339, 19], [1339, 72], [68, 72]],
        confidence=0.460
    ),
    OCRResult(
        text="容量是(",
        bbox=[[68, 116], [204, 116], [204, 166], [68, 166]],
        confidence=0.992
    )
]
```

## 完整示例

```python
from service.ocr_service import OCRService

def process_image_example():
    # 创建OCR服务
    ocr_service = OCRService()
    
    try:
        # 处理本地文件
        local_results = ocr_service.read_from_file('99999.png')
        print(f"本地文件识别到 {len(local_results)} 个文本区域")
        
        # 处理URL图片（示例）
        # url_results = ocr_service.read_from_url('https://example.com/image.png')
        # print(f"URL图片识别到 {len(url_results)} 个文本区域")
        
        # 显示结果
        for i, result in enumerate(local_results, 1):
            print(f"\n文本区域 {i}:")
            print(f"  文本: {result.text}")
            print(f"  置信度: {result.confidence:.3f}")
            print(f"  边界框: {result.bbox}")
            
    except FileNotFoundError as e:
        print(f"文件不存在: {e}")
    except Exception as e:
        print(f"OCR识别失败: {e}")

if __name__ == "__main__":
    process_image_example()
```

## 错误处理

服务提供了完善的错误处理：

- `FileNotFoundError`: 文件不存在
- `requests.RequestException`: URL下载失败
- `Exception`: OCR识别失败

```python
try:
    results = ocr_service.read_from_file('image.png')
except FileNotFoundError as e:
    print(f"文件不存在: {e}")
except Exception as e:
    print(f"OCR识别失败: {e}")
```

## 性能优化建议

1. **重用OCR服务实例**: 避免重复创建`OCRService`实例，因为初始化需要加载模型
2. **批量处理**: 对于多个图片，可以重用同一个服务实例
3. **语言优化**: 只加载需要的语言模型以减少内存使用

```python
# 推荐：重用实例
ocr_service = OCRService()
for image_path in image_list:
    results = ocr_service.read_from_file(image_path)
    # 处理结果...

# 不推荐：重复创建实例
for image_path in image_list:
    ocr_service = OCRService()  # 每次都重新加载模型
    results = ocr_service.read_from_file(image_path)
```

## 注意事项

1. **临时文件**: URL和字节数据处理时会创建临时文件，但会自动清理
2. **网络超时**: URL下载默认30秒超时，可根据需要调整
3. **内存使用**: 大图片处理时注意内存使用情况
4. **模型加载**: 首次使用时会下载语言模型，需要网络连接

## 测试

运行测试文件验证功能：

```bash
python test_ocr_service.py
```

测试包括：
- OCRResult结构测试
- 本地文件识别测试
- 通用方法测试
- 错误处理测试 