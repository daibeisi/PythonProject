import logging

f = None
try:
    f = open('/path/to/file', 'r')
    print(f.read())
except Exception as e:
    logging.exception(e)
finally:
    if f:
        f.close()


with open('/Users/michael/gbk.txt', 'rw', encoding='gbk', errors='ignore') as f:
    print(f.read())
    f.write('Hello, world!')