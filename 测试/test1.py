import time
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
from PIL import Image
from io import BytesIO
import pytesseract
import ddddocr

# Windows 下指定 tesseract.exe 路径（如果没配置环境变量）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def setup_driver():
    """设置并返回 WebDriver 实例"""
    service = EdgeService(executable_path="C:\\Users\\admin\\Downloads\\msedgedriver.exe")
    options = webdriver.EdgeOptions()
    return webdriver.Edge(service=service, options=options)


def get_captcha_code(driver):
    """获取并识别验证码"""
    # 定位验证码 canvas 元素
    captcha_element = driver.find_element(By.CSS_SELECTOR, "canvas#s-canvas")

    # 使用 JavaScript 获取 canvas 内容
    canvas_base64 = driver.execute_script("""
        var canvas = arguments[0];
        return canvas.toDataURL('image/png').substring(22);
    """, captcha_element)

    # 将 base64 编码的字符串转换为图像数据
    canvas_png = base64.b64decode(canvas_base64)

    # 将图像数据转换为 PIL Image 对象
    captcha_image = Image.open(BytesIO(canvas_png))

    # 使用 ddddocr 进行验证码识别
    ocr = ddddocr.DdddOcr()
    captcha_code = ocr.classification(captcha_image)
    print("识别出的验证码是：", captcha_code)
    return captcha_code


def login(driver, username, password, captcha_code):
    """执行登录操作"""
    # 填写用户名/邮箱
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入用户名/邮箱']").send_keys(username)

    # 填写密码
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入密码']").send_keys(password)

    # 填写验证码
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入验证码']").send_keys(captcha_code)

    # 点击登录按钮
    driver.find_element(By.CSS_SELECTOR, "button").click()


def create_project(driver, project_name):
    """创建项目"""
    # 点击“创建项目”按钮
    create_project_button = driver.find_element(By.XPATH, "//div[class='add-item']")
    create_project_button.click()

    # 等待弹出框出现
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='创建项目']/following-sibling::div"))
    )

    # 输入项目名称
    project_name_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入项目名称']")
    project_name_input.send_keys(project_name)

    # 点击“确认”按钮
    confirm_button = driver.find_element(By.XPATH, "//button[text()='确认']")
    confirm_button.click()


def main():
    # 设置 WebDriver
    driver = setup_driver()

    try:
        # 打开登录页面
        driver.get("http://172.18.18.201:8777")

        # 等待页面加载（使用显式等待）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas#s-canvas"))
        )

        # 获取验证码
        captcha_code = get_captcha_code(driver)

        # 执行登录
        login(driver, "admin", "admin", captcha_code)

        # 等待几秒观察效果
        time.sleep(5)

        # 创建项目
        create_project(driver, f"Test Project{uuid.uuid1()}")

        # 等待几秒观察效果
        time.sleep(5)
    finally:
        # 可选：关闭浏览器
        driver.quit()


if __name__ == "__main__":
    main()
