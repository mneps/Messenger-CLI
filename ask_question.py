import sys

def ask_question(message, fail_message, response_test):
	sys.stdout.write(message)

	response = input()
	while response_test(response):
		sys.stdout.write(fail_message)
		response = input()
	return response