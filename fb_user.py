
import emoji
import fbchat
import re
from address_book import *
from ask_question import *
from getpass import getpass
from fbchat.models import *
from functools import reduce


class Messenger_CLI:

	def __init__(self, client):
		self.client = client
		self.address_book = Address_Book()
		self.locked = False
		self.friend = None
		self.uid = None
		self.message = None
		self.iterations = 1


	def run(self):
		while True:
			if not self.locked:
				self.__get_friend(True)
			self.__get_message()
			self.__send_message()
			self.__reset()


	def __get_friend(self, first_time, friend=None):
		if first_time:
			sys.stdout.write("Friend: ")
			friend = input()
		if friend == "quit":
			self.client.logout()
			exit(0)

		if self.address_book.contact_exists(friend):
			self.friend = friend
			self.uid = self.address_book.get_uid(friend)
		else:
			recipient = self.__get_recipient(friend)
			if recipient == None:
				return

			message = "Name not in address book. Do you want to send a message to " \
					+ recipient.name +"? (Y/n) "
			fail_message = "Please enter valid response: "
			ok_response = lambda x: x not in ["Y", "n"]

			if ask_question(message, fail_message, ok_response) == "Y":
				self.address_book.add_contact(recipient)
			else:
				return self.__get_friend(True)

			self.friend = recipient.name
			self.uid = recipient.uid


	def __get_recipient(self, friend):
		try:
			return self.client.searchForUsers(friend)[0]
		except:
			sys.stdout.write("Could not find friend.  Please enter different name: ")
			new_friend = input()
			self.__get_friend(False, new_friend)


	def __get_message(self):
		sys.stdout.write("Message text: ")
		text = input()
		text = emoji.emojize(text, use_aliases=True)

		pattern = re.compile("^-i ([0-9]*[1-9][0-9]*) ([^\s].*)$") #-i [positive integer] [some_text]
		if pattern.match(text):
			self.iterations = int(pattern.search(text).group(1))
			text = pattern.search(text).group(2)

		pattern = re.compile("^-s ([^\s].*)$") #-s [some text]
		if pattern.match(text):
			as_list = list(pattern.search(text).group(1))
			no_spaces = filter(lambda x: x != " ", as_list)
			text = reduce(lambda acc,x: acc+x+" ", no_spaces, "")

		if text == "":
			print("Message cannot be empty")
			return self.__get_message()

		if not self.locked and text == "--lock":
			self.locked = True
			print("Locked on " + self.friend)
			return self.__get_message()
		if self.locked and text == "--unlock":
			self.locked = False
			print("Unlocked from " + self.friend)
			self.__reset()
			self.run()

		self.message = text.rstrip()



	def __send_message(self):
		sent = False
		try:
			for i in range(self.iterations):
				self.client.send(Message(text=self.message), self.uid)
				sent = True
		except:
			if sent:
				print("Not all messages sent")
			else:
				print("Message not sent")
			return

		if not self.locked:
			if self.iterations == 1:
				print ("Message sent")
			else:
				print ("Messages sent")


	def __reset(self):
		if not self.locked:
			self.friend = None
			self.uid = None
		self.message = None
		self.iterations = 1


		


