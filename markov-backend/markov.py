#!/usr/bin/env python
"""This is a simple Markov chainer library."""

import random
from collections import defaultdict

PUNCTUATION = "\n" + ".?!\""
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"

def change(character):
    """Introduce spaces between PUNCTUATION."""
    if character in LETTERS + DIGITS + " ":
        return character

    if character == "\n":
        return " " + character + " "

    return " " + character

class Markov(object):
    """ Simple Markov chainer implementation. The optional max_words parameter
        limits the size of the input to 40K words by default."""
    def __init__(self, data, max_words=40000):
        valid_characters = LETTERS + DIGITS + " " + PUNCTUATION
        data = ''.join(change(ch) for ch in data if ch in valid_characters)
        self.words = data.split(' ')
        if self.words > max_words:
            self.words = self.words[0:max_words]

        self.word_size = len(self.words)
        self.cache = defaultdict(list)
        for word1, word2, word3 in self.triples():
            key = (word1, word2)
            self.cache[key].append(word3)

    def triples(self):
        """Divide text into triples, which we can use for a simple markov chain."""
        if len(self.words) < 3:
            return

        for i in range(len(self.words) - 2):
            yield (self.words[i], self.words[i+1], self.words[i+2])

    def generate(self, length):
        """Use the chainer to generate some text."""
        seed = random.randint(0, self.word_size-3)
        last, current = self.words[seed], self.words[seed+1]
        gen_words = []
        for _ in xrange(length):
            gen_words.append(last)
            maybe_next = self.cache[(last, current)]
            if maybe_next == []:
                sequence = "(" + last + "," + current + ")"
                print "Dictionary size too small, can't find sequence:" + sequence
                print "choosing at random"
                maybe_next = self.cache[random.choice(self.cache.keys())]
            last, current = current, random.choice(maybe_next)
        gen_words.append(current)
        return ' '.join(gen_words)
