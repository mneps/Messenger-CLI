import emoji


def ask_question(message, fail_message, response_test, extra=None):
	response = input(message)
	while response_test(response, extra):
		response = input(fail_message)
	return response


def check_response(x, limit):
	try:
		return int(x) < 0 or int(x) >= limit
	except:
		return x != "q"


def check_reaction(x, limit):
	try:
		return int(x) < 0 or int(x) >= limit
	except:
		return False