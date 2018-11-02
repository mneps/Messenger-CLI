
from fb_user import *
from getpass import getpass
from extend_reactions import *
from retrieve_messages import *


def main():
    client = fbchat.Client("matthew.n.epstein", getpass())
    receive = Receive(client)

    instance = Messenger_CLI(client, receive)
    instance.run()


if __name__ == "__main__":
    main()