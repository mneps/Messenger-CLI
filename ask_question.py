
def ask_question(message, fail_message, response_test):
	response = input(message)
	while response_test(response):
		response = input(fail_message)
	return response