
import pickle
import os
from ask_question import *


class Address_Book:

	def __init__(self):
		abspath = (os.path.abspath(__file__))
		dname = os.path.dirname(os.path.dirname(abspath))
		os.chdir(dname)

		if os.path.isfile(".address_book.p"):
			self.uids = pickle.load(open(".address_book.p", "rb"))
		else:
			self.uids = dict()
			pickle.dump(self.uids, open(".address_book.p", "wb"))


	def add_contact(self, recipient):
		message = "Would you like to add this contact to your address book? (Y/n) "
		fail_message = "Please enter a valid response: "
		ok_response = lambda x, _: x not in ["Y", "n"]

		if ask_question(message, fail_message, ok_response) == "Y":
			message = "Please enter the name by which you will refer to your friend: "
			fail_message = "Name is already in address book.  Please enter a different one: "
			ok_response = lambda x, _: x.lower() in self.uids
			contact = ask_question(message, fail_message, ok_response)

			self.uids[contact.lower()] = recipient.uid
			pickle.dump(self.uids, open(".address_book.p", "wb"))
			print ("Contact added")
			recipient.name = contact


	def contact_exists(self, friend):
		return friend.lower() in self.uids


	def get_uid(self, friend):
		return (self.uids[friend.lower()] if friend.lower() in self.uids else None)

	def get_contacts(self):
		friend_list = []

		for key in self.uids:
			friend_list.append(key)

		return friend_list


	def view_contacts(self):
		for key in sorted(self.uids):
			print (key.capitalize())


	def remove_contact(self, contact):
		if contact.lower() in self.uids:
			del self.uids[contact.lower()]
			pickle.dump(self.uids, open(".address_book.p", "wb"))
			print ("Contact removed")
		else:
			print ("Contact not found")




