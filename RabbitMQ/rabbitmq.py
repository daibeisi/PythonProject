import os
from typing import Union

import pika
import sys


class RabbitMQ:
    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 virtual_host: str = '/'):
        """

        @param host: 主机地址
        @param port: 端口
        @param username: 用户名
        @param password: 密码
        @param virtual_host: 虚拟主机名称
        """
        self._host = host,
        self._port = port,
        self._username = username
        self._password = password
        self._virtual_host = virtual_host

    @property
    def _connection(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                virtual_host=virtual_host,
                credentials=pika.PlainCredentials(username, password),
                heartbeat=600,
                blocked_connection_timeout=300
            )
        )
        return connection

    @property
    def _channel(self):
        return self._connection.channel()

    def __del__(self):
        pass

    @staticmethod
    def auto_basic_ack_callback(callback):
        """ 回调添加手动确认

        :param callback: 回调函数
        :return:
        """

        def auto_basic_ack_callback(ch, method, properties, body):
            """自动手动确认"""
            try:
                callback(ch, method, properties, body)
            except:
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                # TODO: 先清除后发送到队尾重试，优化消息重试次数，达到了重试上限以后，
                #  手动确认，队列删除此消息，并将消息持久化入MySQL并推送报警，进行人工处理和定时任务做补偿。
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        return auto_basic_ack_callback

    def send(self, queue: str, body: bytes, queue_declare=True):
        """ 发送消息

        @param queue: 队列
        @param body: 消息
        @param queue_declare: 是否打开队列声明，如果队列被接受方声明独占设置为False
        @return:
        """
        # TODO: 发布确认、消息过期、队列过期

        #  将消息标记为持久性并不能完全保证消息不会丢失。
        #  虽然它告诉 RabbitMQ 将消息保存到磁盘，但是当 RabbitMQ 接受消息并且还没有保存它时，仍然有很短的时间窗口。
        #  此外，RabbitMQ 不会对每条消息都执行fsync(2) ——它可能只是保存到缓存中而不是真正写入磁盘。
        #  持久性保证并不强，但对于我们简单的任务队列来说已经绰绰有余了。
        #  如果您需要更强的保证，那么您可以使用 发布者确认。
        if queue_declare:
            # durable= True 将队列标记为持久的
            self.send_channel.queue_declare(queue=queue, durable=True)
        self.send_channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  # NOTE: 将消息标记为持久的
            ))

    def receive(self, queue: str, callback, exclusive=False):
        """ 接收消息

        @param queue: 队列
        @param callback: 回调函数
        @param exclusive: 是否独占,如果为真则这个队列只允许当前connection连接，需保证队列未被其他连接提前声明
        @return:
        """
        # TODO: 队列过期、可不可以另外起一个进程接收
        channel = self.connection.channel()
        channel.queue_declare(queue=queue, durable=True, exclusive=exclusive)  # NOTE: durable= True 将队列标记为持久的
        channel.basic_qos(prefetch_count=1)  # NOTE: 在接收方处理并确认之前的消息之前，不向接收方发送新消息
        auto_basic_ack_callback = self.auto_basic_ack_callback(callback)
        channel.basic_consume(queue=queue,
                              on_message_callback=auto_basic_ack_callback)
        channel.start_consuming()

    def publish(self, exchange: str,
                body: bytes,
                routing_key: Union[str, list] = '',
                exchange_type='fanout'):
        """ 发布消息

        :param exchange: 交换机
        :param routing_key: 路由键列表
        :param body: 消息
        :param exchange_type: 交换机类型，默认为 fanout
        :return:
        """
        if isinstance(routing_key, str):
            routing_key = [routing_key]
        self.send_channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
        for _ in routing_key:
            self.send_channel.basic_publish(exchange=exchange, routing_key=_, body=body,
                                            properties=pika.BasicProperties(
                                                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  # 将消息标记为持久的
                                            ))

    def subscribe(self, exchange, callback, exchange_type='fanout',
                  routing_key: Union[str, list] = None,
                  queue_name: str = None,
                  exclusive: bool = False):
        """ 订阅消息

        :param exchange: 交换机
        :param callback: 回调函数
        :param exchange_type: 交换机类型，默认为 fanout
        :param routing_key: 路由键列表
        :param queue_name: 队列名
        :param exclusive: 是否独占,如果为真则这个队列只允许当前connection连接，需保证队列未被其他连接提前声明
        :return:
        """
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
        result = channel.queue_declare(queue=queue_name, durable=True, exclusive=exclusive)
        if queue_name is None:
            queue_name = result.method.queue
        if routing_key is not None:
            if isinstance(routing_key, str):
                routing_key = [routing_key]
            for _ in routing_key:
                channel.queue_bind(
                    exchange=exchange, queue=queue_name, routing_key=_)
        else:
            channel.queue_bind(exchange=exchange, queue=queue_name)
        auto_basic_ack_callback = self.auto_basic_ack_callback(callback)
        channel.basic_consume(queue=queue_name, on_message_callback=auto_basic_ack_callback)
        channel.start_consuming()


def main():
    rabbit_mq = RabbitMQ(host='', port=5672,
                         username='root', password='')
    while True:
        a = input('请输入消息：')
        rabbit_mq.send('hello3', body=a.encode())

    # def callback(ch, method, properties, body):
    #     print(" [x] Received %r" % ch)
    #     print(" [x] Received %r" % method)
    #     print(" [x] Received %r" % properties)
    #     print(" [x] Received %r" % body)
    #
    # rabbit_mq.receive('hello3', callback)


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
