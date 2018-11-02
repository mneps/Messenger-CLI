import readline

# The code in this file was taken and modified from
# https://stackoverflow.com/questions/7821661/how-to-code-autocompletion-in-python

class MyCompleter(object):  # Custom completer

    def __init__(self, options, lower=False):
        self.options = sorted(options)
        if lower:
            self.modify = lambda x: x.lower()
        else:
            self.modify = lambda x: x

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                                    if s and s.startswith(self.modify(text))]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try: 
            if self.matches[state] != text and text[0].isupper():
                return self.matches[state].capitalize()
            return self.matches[state]
        except IndexError:
            return None
