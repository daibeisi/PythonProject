import os
import pika
import sys


class RabbitMQ:
    def __init__(self, host: str, port: int, username: str, password: str, virtual_host: str = '/'):
        """

        @param host: 主机地址
        @param port: 端口
        @param username: 用户名
        @param password: 密码
        @param virtual_host: 虚拟主机名称
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, virtual_host=virtual_host,
                                      credentials=pika.PlainCredentials(username, password)))

    def __del__(self):
        self.connection.close()

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
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        return auto_basic_ack_callback

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
        auto_basic_ack_callback = self.auto_basic_ack_callback(callback)
        channel.basic_consume(queue=queue, on_message_callback=auto_basic_ack_callback)
        channel.start_consuming()

    def publish(self, exchange: str, body: bytes):
        """ 发布消息

        :param exchange: 交换机
        :param body: 消息
        :return:
        """
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='fanout')
        channel.basic_publish(exchange='logs', routing_key='', body=body)

    def subscribe(self, exchange, callback):
        """ 订阅消息

        :param exchange: 交换机
        :param callback: 回调函数
        :return:
        """
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=exchange, queue=queue_name)
        auto_basic_ack_callback = self.auto_basic_ack_callback(callback)
        channel.basic_consume(queue=queue_name, on_message_callback=auto_basic_ack_callback)
        channel.start_consuming()

    def routing_publish(self, exchange, routing_key_list, body):
        """ 路由推送消息

        :param exchange: 交换机
        :param routing_key_list: 路由键列表
        :param body: 消息
        :return:
        """
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='direct')
        for routing_key in routing_key_list:
            channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)

    def routing_subscribe(self, exchange, routing_key_list, callback):
        """ 路由订阅消息

        :param exchange:
        :param routing_key_list:
        :param callback:
        :return:
        """
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='direct')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        for routing_key in routing_key_list:
            channel.queue_bind(
                exchange=exchange, queue=queue_name, routing_key=routing_key)
        auto_basic_ack_callback = self.auto_basic_ack_callback(callback)
        channel.basic_consume(queue=queue_name, on_message_callback=auto_basic_ack_callback)
        channel.start_consuming()

    def topics_publish(self, exchange, routing_key_list, body):
        """

        :param exchange:
        :param routing_key_list:
        :param body:
        :return:
        """
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='topic')
        for routing_key in routing_key_list:
            channel.basic_publish(
                exchange='topic_logs', routing_key=routing_key, body=body)

    def topics_subscribe(self, exchange, routing_key_list, callback, queue_name=None):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='topic')
        result = channel.queue_declare('', exclusive=True)
        if queue_name is None:
            queue_name = result.method.queue
        for routing_key in routing_key_list:
            channel.queue_bind(
                exchange='topic_logs', queue=queue_name, routing_key=routing_key)
        auto_basic_ack_callback = self.auto_basic_ack_callback(callback)
        channel.basic_consume(queue=queue_name, on_message_callback=auto_basic_ack_callback)
        channel.start_consuming()


def main():
    rabbit_mq = RabbitMQ(host='', port=5672,
                         username='', password='')

    rabbit_mq.send('hello3', body=b'2222222')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % ch)
        print(" [x] Received %r" % method)
        print(" [x] Received %r" % properties)
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
