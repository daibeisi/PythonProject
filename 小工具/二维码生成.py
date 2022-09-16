# -*- coding: utf-8 -*-
import qrcode
import base64
from io import BytesIO


class QRcode:
    @staticmethod
    def generate_qr_code(url):
        """url生成二维码 Data URLs

        :param url:
        :return:
        """
        qr = qrcode.QRCode(
            version=1,  # 二维码大小，用1~40之间的整数来设置。
            # 最小的version=1，是一个21x21的矩阵。如果你想自动生成，将值设置为 None 并使用 fit=True 参数即可。
            error_correction=qrcode.ERROR_CORRECT_H,  # 用于控制二维码的错误纠正程度
            box_size=10,  # 控制二维码中每个格子的像素数，默认为10
            border=4,  # 二维码四周留白，包含的格子数，默认为4
            # image_factory=None,  选择生成图片的形式，默认为 PIL 图像
            # mask_pattern=None  选择生成图片的的掩模
        )
        qr.add_data(url)  # QRCode.add_data(data)函数添加数据
        qr.make(fit=True)  # QRCode.make(fit=True)函数生成图片
        img = qr.make_image()
        buffer = BytesIO()
        img.save(buffer)
        data_bytes = buffer.getvalue()
        base64_data = base64.b64encode(data_bytes)
        buffer.close()
        return "data:image/jpeg;base64," + str(base64_data)


def main():
    qr_code = QRcode()
    url_iterator = ("https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs" for _ in range(1000))
    qr_code_data_url_iterator = map(qr_code.generate_qr_code, url_iterator)
    for qr_code_data_url in qr_code_data_url_iterator:
        print(qr_code_data_url)


if __name__ == '__main__':
    main()
