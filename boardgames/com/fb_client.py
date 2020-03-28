from fbchat import Client, log
from fbchat.models import Message, ThreadType

from boardgames import utils


# Subclass fbchat.Client and override required methods
class FacebookClient(Client):
    def __init__(self, thread_id, is_group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread_id = int(thread_id)
        self.is_group = is_group
        self.message_received = None

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if self.thread_id != int(thread_id):
            return

        # self.markAsDelivered(thread_id, message_object.uid)
        # self.markAsRead(thread_id)

        self.message_received = message_object

    def getMessage(self):
        message_received = self.message_received
        self.message_received = None
        return message_received

    def waitForMessage(self, format_message=True):
        self.startListening()
        self.onListening()
        while self.listening and self.doOneListen(markAlive=True):
            message = self.getMessage()
            if message is not None:
                break
        self.stopListening()
        if format_message and message.text is not None:
            message.text = utils.format_str(message.text)
        return message

    def processMessages(self, call_fn, end_message="end", format_message=True):
        """
        call_fn, function to call which takes as argument message and user
        """
        end_triggered = False
        while not end_triggered:
            message = self.waitForMessage(format_message)
            user = self.fetchUserInfo(message.author)[message.author]
            end_called = call_fn(message, user)
            end_triggered = end_called or (message.text == end_message)

    def selfSubscription(self, subscription_message, end_message):
        users = []
        thread_type = ThreadType.GROUP if self.is_group else ThreadType.USER

        def filter_add(message, user):
            print(user.name, message.text)
            if message.text == subscription_message:
                users.append(user)
                self.send(
                    Message(text="{} est inscrit.".format(user.name)),
                    thread_id=self.thread_id,
                    thread_type=thread_type,
                )
            return False

        self.processMessages(filter_add, end_message)
        return users
