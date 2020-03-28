from fbchat.models import Message, ThreadType


class FacebookSender:
    def __init__(self, client):
        self.client = client
        self.users_id = []
        self.groups_id = []

    def add_user_id(self, user_id):
        # if not user.is_friend:
        #     raise ValueError("Trying to add a user which is not your friend!")
        self.users_id.append(user_id)

    def add_group_id(self, group_id):
        self.groups_id.append(group_id)

    def send_message(self, msg):
        for user_id in self.users_id:
            self.client.send(
                Message(text=msg), thread_id=user_id, thread_type=ThreadType.USER
            )
        for group_id in self.groups_id:
            self.client.send(
                Message(text=msg), thread_id=group_id, thread_type=ThreadType.GROUP
            )

    def send_image(self, image_path, caption=""):
        for user_id in self.users_id:
            self.client.sendLocalImage(
                image_path,
                message=Message(text=caption),
                thread_id=user_id,
                thread_type=ThreadType.USER,
            )
        for group_id in self.groups_id:
            self.client.sendLocalImage(
                image_path,
                message=Message(text=caption),
                thread_id=group_id,
                thread_type=ThreadType.GROUP,
            )
