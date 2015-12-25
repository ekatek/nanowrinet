""" Entrypoint for AWS Lambda. Generate text using a Markov chainer """

from __future__ import print_function
from markov import Markov

def load_mixin(mixin_token):
    """Load text from the specified author mixin"""
    if mixin_token == "":
        return ""
    mixin_text = open("data/" + mixin_token + ".txt", 'r').read()
    mixin_words = mixin_text.split(' ')
    if len(mixin_words) > 20000:
        return ' '.join(mixin_words[0:20000])
    return ' '.join(mixin_words)

def lambda_handler(event, context):
    """Entrypoint for AWS Lambda. Event contains the payload from the AWS Lambda
       call."""
    user_text = event['userText']
    mixin = event['mixin']
    length = int(event['length'])

    full_text = user_text + load_mixin(mixin)
    markover = Markov(full_text)
    return markover.generate(length)
