
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
		self.send = lambda msg, uid: self.client.send(Message(text=msg), uid)
		self.args = [None, None]


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


	def __empty_check(self, text):
		if text == "":
			if self.locked:
				print("Message cannot be empty")
				self.__get_message()
				return self.message
			else:
				self.__reset()
				self.run()

		return text

	def __iterations(self, text):
		pattern = re.compile("^-i ([0-9]*[1-9][0-9]*) ([^\s].*)$") #-i [positive integer] [some_text]
		if pattern.match(text):
			self.iterations = int(pattern.search(text).group(1))
			text = pattern.search(text).group(2)

		return text


	def __spaces(self, text):
		pattern = re.compile("^-s ([^\s].*)$") #-s [some text]
		if pattern.match(text):
			as_list = list(pattern.search(text).group(1))
			no_spaces = filter(lambda x: x != " ", as_list)
			text = reduce(lambda acc,x: acc+x+" ", no_spaces, "")

		return text


	def __oboi(self, text):
		if text == "oboi":
			self.send = lambda img, uid: self.client.sendLocalImage(img, thread_id=uid)
			self.args = ['images/oboi.jpg', self.uid]
			return True

		return False

	def __contains_word(self, s, w):
		if s.startswith(w + ' ') or s == w:
			return len(w)
		elif s.find(' ' + w + ' ') != -1:
			return s.find(' ' + w + ' ') + len(w) + 1
		elif s.endswith(' ' + w):
			return s.find(' ' + w) + len(w) + 1
		else:
			return -1

	def __replace_word(self, text, find, replace):
		match = self.__contains_word(text, find)
		while match != -1:
			text = text[:match].replace(find, replace, 1) + text[match:]
			match = self.__contains_word(text, find)

		return text


	def __get_message(self):
		sys.stdout.write("Message text: ")
		text = input()

		text = self.__empty_check(text)
		text = emoji.emojize(text, use_aliases=True)
		text = self.__iterations(text)
		text = self.__spaces(text)
		text = self.__replace_word(text, "shru.gg", "¯\_(ツ)_/¯")
		if not self.__oboi(text):
			self.args = [text, self.uid]

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
				self.send(self.args[0], self.args[1])
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
		self.send = lambda msg, uid: self.client.send(Message(text=msg), uid)		


		


