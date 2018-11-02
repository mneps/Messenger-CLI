import emoji
import re


def ask_question(message, fail_message, response_test, extra=None):
    response = input(message)
    while response_test(response, extra):
        response = input(fail_message)
    return response


def check_response(x, extras):
    (limit, num_messages) = extras

    try:
        return int(x) < 0 or int(x) >= limit
    except:
        pattern = re.compile("--open ([0-9][0-9]*)") #--open [positive integer]
        if pattern.match(x):
            msg_num = pattern.search(x).group(1)
            return int(msg_num) >= num_messages

        return x != "q"


def check_reaction(x, limit):
    try:
        return int(x) < 0 or int(x) >= limit
    except:
        return False