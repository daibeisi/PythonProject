#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import datetime
import zipfile
import subprocess

import oss2
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo


class Backup:
    def __init__(self, access_key_id, access_key_secret, endpoint='http://oss-cn-hangzhou-internal.aliyuncs.com'):
        """初始化

        阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。

        endpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
        :param access_key_id:
        :param access_key_secret:
        :param endpoint:
        :return:
        """
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        try:
            import crcmod._crcfunext
        except (ModuleNotFoundError, ImportError) as e:
            raise RuntimeError("crcmod模块没有正确安装，上传效率将大大降低")

    @staticmethod
    def backup_db(store_path):
        """备份数据库

        :param store_path: 备份数据库存储路径
        :return:
        """
        cmd = "docker exec -t hefei_save_db_1 pg_dump -U odoo -c hefei_save  > " + store_path
        res = subprocess.call(cmd, shell=True)
        assert res == 0, '备份数据库失败'

    @staticmethod
    def zip_file(file_path, zip_name):
        """压缩文件

        :param file_path: 需要压缩的文件的绝对路径
        :param zip_name: 压缩后保存的文件名（文件会保存在需压缩文件同目录下）
        :return:
        """
        with zipfile.ZipFile(os.path.join(os.path.dirname(file_path), zip_name), 'w',
                             zipfile.ZIP_DEFLATED, allowZip64=True) as z:
            z.write(file_path)

    def multipart_upload(self, bucket_name, key, file_path):
        """分片上传

        :param bucket_name: 填写Bucket名称，例如examplebucket
        :param key: 填写不能包含Bucket名称在内的Object完整路径，例如exampledir/exampleobject.txt
        :param file_path: 填写本地文件的完整路径，例如D:\\localpath\\examplefile.txt
        :return:
        """
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, bucket_name)
        total_size = os.path.getsize(file_path)
        # percentage = functools.partial(self.percentage, total_bytes=total_size)
        part_size = determine_part_size(total_size, preferred_size=500 * 1024 * 1024)  # determine_part_size方法用于确定分片大小
        headers = dict()  # 如需在初始化分片时设置文件存储类型，请在init_multipart_upload中设置相关Headers
        # headers['Content-Disposition'] = 'oss_MultipartUpload.txt'  # 指定该Object被下载时的名称。
        headers['Content-Encoding'] = 'utf-8'  # 指定该Object的内容编码格式。
        headers['Expires'] = '1000'  # 指定过期时间，单位为毫秒。
        # headers['x-oss-forbid-overwrite'] = 'true'  # 指定初始化分片上传时是否覆盖同名Object。此处设置为true，表示禁止覆盖同名Object
        upload_id = bucket.init_multipart_upload(key, headers=headers).upload_id
        parts = []
        # 逐个上传分片
        with open(file_path, 'rb') as file_obj:
            part_number = 1
            offset = 0

            def percentage(consumed_bytes, total_bytes):
                """进度条回调函数，计算当前完成的百分比

                :param consumed_bytes: 已经上传/下载的数据量
                :param total_bytes: 总数据量
                """
                rate = int(100 * (float(consumed_bytes + offset) / float(total_size)))
                print('\r{0}% '.format(rate), end='')
                sys.stdout.flush()

            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                result = bucket.upload_part(key, upload_id, part_number,
                                            SizedFileAdapter(file_obj, num_to_upload),
                                            progress_callback=percentage)
                parts.append(PartInfo(part_number, result.etag))
                offset += num_to_upload
                part_number += 1
        # 完成分片上传
        result = bucket.complete_multipart_upload(key, upload_id, parts)
        # 验证分片上传
        # with open(file_path, 'rb') as file_obj:
        #     assert bucket.get_object(key).read() == file_obj.read()
        return result


def main():
    print('{0} backup start'.format(datetime.datetime.now()).center(50, '='))
    backup = Backup(access_key_id='', access_key_secret='')
    # backup.backup_db('/home/workspace/hefei_save.sql')
    # print('{0} database dump end'.format(datetime.datetime.now()).center(50, '='))
    backup.zip_file('/home/workspace/hefei_save.sql', 'hefei_save.zip')
    print('{0} file zip end'.format(datetime.datetime.now()).center(50, '='))
    backup.multipart_upload(bucket_name='ttwb-db', key='/example/hefei_save.zip',
                            file_path='/home/workspace/hefei_save.zip')
    print('{0} backup end'.format(datetime.datetime.now()).center(50, '='))


if __name__ == '__main__':
    main()
