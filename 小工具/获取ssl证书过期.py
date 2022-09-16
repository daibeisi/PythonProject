import re
import subprocess
from datetime import datetime
from io import StringIO


def main(domain):
    f = StringIO()
    comm = f"curl -Ivs https://{domain} --connect-timeout 10"
    result = subprocess.getstatusoutput(comm)
    f.write(result[1])
    try:
        m = re.search('start date: (.*?)\n.*?expire date: (.*?)\n', f.getvalue(), re.S)
        # start_date = m.group(1)
        expire_date = m.group(2)
    except Exception as e:
        raise RuntimeError("没找到开始和过期时间")
    # time 字符串转时间数组
    # start_date = time.strptime(start_date, "%b %d %H:%M:%S %Y GMT")
    # datetime 字符串转时间数组
    expire_date = datetime.strptime(expire_date, "%b %d %H:%M:%S %Y GMT")
    # 剩余天数
    remaining = (expire_date - datetime.now()).days
    return remaining


if __name__ == "__main__":
    domain = "www.baidu.com"
    remaining_days = main(domain)
    print(remaining_days)
