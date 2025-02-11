from PIL import Image
import base64
import io
import re


img_target_width = 250
img_target_height = 140


# 从Base64字符串调整图片大小并返回Base64
def resize_image_base64(input_base64):
    # 解码 Base64 字符串为字节数据
    image_data = base64.b64decode(re.sub(r"^data:image/[^;]+;base64,", "", input_base64))

    # 使用 PIL 从字节流中打开图片
    with Image.open(io.BytesIO(image_data)) as img:
        original_width, original_height = img.size
        scale = min(img_target_width / original_width, img_target_height / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        resized_img = img.resize((new_width, new_height))

        # 将调整后的图片保存到字节流中
        buffer = io.BytesIO()
        resized_img.save(buffer, format="PNG")  # 可以指定格式为 PNG 或其他格式

        # 将调整后的图片编码为 Base64
        resized_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return f"data:image/png;base64,{resized_base64}"



if __name__ == '__main__':
    base64_str = "data:image/jpeg;base64,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"
    resized_base64 = resize_image_base64(base64_str)
    print(resized_base64)