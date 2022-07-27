import sys

from typing import List

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class SMS:
    def __init__(self, access_key_id: str, access_key_secret: str):
        self.client = SMS.create_client(access_key_id, access_key_secret)

    @staticmethod
    def create_client(access_key_id: str,access_key_secret: str,) -> Dysmsapi20170525Client:
        """使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id=access_key_id,  # 您的 AccessKey ID
            access_key_secret=access_key_secret  # 您的 AccessKey Secret
        )
        config.endpoint = f'dysmsapi.aliyuncs.com'  # 访问的域名
        return Dysmsapi20170525Client(config)

    @staticmethod
    def main(args: List[str],) -> None:
        client = SMS.create_client('', '')
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers='',
            sign_name='',
            template_code='',
            template_param='{"code":"1234"}'
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res = client.send_sms_with_options(send_sms_request, runtime)
            print(res)
        except Exception as error:
            # 如有需要，请打印 error
            UtilClient.assert_as_string(error.message)

    @staticmethod
    async def main_async(args: List[str],) -> None:
        client = SMS.create_client('', '')
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers='',
            sign_name='',
            template_code='',
            template_param=''
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            await client.send_sms_with_options_async(send_sms_request, runtime)
        except Exception as error:
            # 如有需要，请打印 error
            UtilClient.assert_as_string(error.message)


if __name__ == '__main__':
    SMS.main(sys.argv[1:])