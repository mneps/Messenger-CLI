
from fb_user import *
from getpass import getpass


def main():
	client = fbchat.Client("matthew.n.epstein", getpass())

	instance = Messenger_CLI(client)
	instance.run()


if __name__ == "__main__":
	main()
