
import cv2

# 1. 读取图像
image = cv2.imread("11111.png")

# 2. 灰度化
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 3. 自适应阈值二值化
thresh = cv2.adaptiveThreshold(
    gray, 255,
    cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY_INV,
    blockSize=15,
    C=8
)

# 4. 轮廓检测
contours, _ = cv2.findContours(
    thresh, cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

# 5. 过滤较小区域（通常为噪声）
min_area = 5000  # 面积阈值
question_blocks = []
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if w * h > min_area:
        question_blocks.append((x, y, w, h))

# 6. 按 y 坐标排序（从上到下）
question_blocks.sort(key=lambda b: b[1])

print(f'question_blocks: {len(question_blocks)}')
for i, (x, y, w, h) in enumerate(question_blocks):
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(image, str(i + 1), (x, y - 10),
    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    # 保存

cv2.imwrite("11111_detection.png", image)