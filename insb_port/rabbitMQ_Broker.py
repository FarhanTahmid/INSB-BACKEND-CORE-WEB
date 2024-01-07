# # rabbitMQ_Broker.py
# import pika
# from django_q.brokers import Broker

# class RabbitMQBroker(Broker):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # CloudAMQP connection parameters
#         self.rabbitmq_host = 'puffin.rmq2.cloudamqp.com'       # Replace with your CloudAMQP server host
#         self.rabbitmq_port = 1883                        # Replace with your CloudAMQP server port
#         self.rabbitmq_user = 'rnchgmqb:rnchgmqb'   # Replace with your CloudAMQP server username
#         self.rabbitmq_password = '9MJ-CtXDdA9ph20hpf6azM1-vPl-oes9'  # Replace with your CloudAMQP server password

#         # Establish connection to CloudAMQP
#         self.connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host=self.rabbitmq_host,
#                 port=self.rabbitmq_port,
#                 credentials=pika.PlainCredentials(
#                     username=self.rabbitmq_user,
#                     password=self.rabbitmq_password
#                 )
#             )
#         )

#         # Create a channel
#         self.channel = self.connection.channel()
#         self.channel.queue_declare(queue='my_queue')

#     def enqueue(self, task):
#         # Implement the logic to enqueue the task in CloudAMQP
#         self.channel.basic_publish(exchange='', routing_key='my_queue', body=task)

#     def dequeue(self):
#         # Implement the logic to dequeue a task from CloudAMQP
#         method_frame, header_frame, body = self.channel.basic_get(queue='my_queue')
#         if method_frame:
#             return body.decode('utf-8')
#         return None

#     def info(self):
#         return 'RabbitMQ Broker'

# rabbitMQ_Broker.py

import pika

class RabbitMQBroker:
    def __init__(self, list_key='my_queue'):
        cloudamqp_params = {
            'host': 'puffin.rmq2.cloudamqp.com',
            'port': 5672,  # CloudAMQP typically uses port 5672
            'virtual_host': 'rnchgmqb',
            'credentials': pika.PlainCredentials('rnchgmqb', '9MJ-CtXDdA9ph20hpf6azM1-vPl-oes9'),
            'heartbeat': 600,
        }

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(**cloudamqp_params))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=list_key, durable=True)

    def enqueue(self, task):
        # Implement your enqueue logic here
        pass

    def dequeue(self):
        # Implement your dequeue logic here
        pass

    # Add other methods as needed

# Example usage:
# broker = RabbitMQBroker()
# broker.enqueue("Your task data")
# task = broker.dequeue()
