
import sys
from ask_question import *


class Address_Book:

	def __init__(self):
		self.uids = dict()


	def add_contact(self, recipient):
		message = "Would you like to add this contact to your address book? (Y/n) "
		fail_message = "Please enter valid response: "
		ok_response = lambda x: x not in ["Y", "n"]

		if ask_question(message, fail_message, ok_response) == "Y":
			message = "Please enter the name by which you will refer to your friend: "
			fail_message = "Name is already in address book.  Please enter different one: "
			ok_response = lambda x: x.lower() in self.uids
			contact = ask_question(message, fail_message, ok_response)

			self.uids[contact.lower()] = recipient.uid
			print ("Contact added")
			recipient.name = contact


	def contact_exists(self, friend):
		return friend.lower() in self.uids


	def get_uid(self, friend):
		return (self.uids[friend] if friend in self.uids else None)