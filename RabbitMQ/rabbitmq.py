import pika, sys, os
from multiprocessing import Process


class RabbitMQ:
    def __init__(self, host: str, port: int, username: str, password: str):
        """

        @param host: 主机地址
        @param port: 端口
        @param username: 用户名
        @param password: 密码
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port,
                                      credentials=pika.PlainCredentials(username, password)))

    def __del__(self):
        self.connection.close()

    def send(self, queue, body, queue_declare=True):
        """ 发送消息

        @param queue: 队列
        @param body: 消息
        @param queue_declare: 是否打开队列声明，如果队列被接受方声明独占设置为False
        @return:
        """
        # :TODO: 发布确认、消息过期、队列过期
        #  将消息标记为持久性并不能完全保证消息不会丢失。
        #  虽然它告诉 RabbitMQ 将消息保存到磁盘，但是当 RabbitMQ 接受消息并且还没有保存它时，仍然有很短的时间窗口。
        #  此外，RabbitMQ 不会对每条消息都执行fsync(2) ——它可能只是保存到缓存中而不是真正写入磁盘。
        #  持久性保证并不强，但对于我们简单的任务队列来说已经绰绰有余了。
        #  如果您需要更强的保证，那么您可以使用 发布者确认。
        channel = self.connection.channel()
        if queue_declare:
            # durable= True 将队列标记为持久的
            channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  # 将消息标记为持久的
            ))

    def receive(self, queue, callback, exclusive=False):
        """ 接收消息

        @param queue: 队列
        @param callback: 回调函数
        @param exclusive: 是否独占,如果为真则这个队列只允许当前connection连接，需保证队列未被其他连接提前声明
        @return:
        """
        # :TODO: 队列过期, 可不可以另外起一个进程接收
        channel = self.connection.channel()
        channel.queue_declare(queue=queue, durable=True, exclusive=exclusive)  # durable= True 将队列标记为持久的
        channel.basic_qos(prefetch_count=1)  # 在接收方处理并确认之前的消息之前，不向接收方发送新消息

        def auto_basic_ack_callback(ch, method, properties, body):
            """自动手动确认"""
            callback(ch, method, properties, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        channel.basic_consume(queue=queue, on_message_callback=auto_basic_ack_callback)
        channel.start_consuming()


def main():
    rabbit_mq = RabbitMQ(host='', port=1,
                         username='', password='')

    rabbit_mq.send('hello3', body=b'11111111111')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    rabbit_mq.receive('hello3', callback)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            print('SystemExit')
            os._exit(0)
