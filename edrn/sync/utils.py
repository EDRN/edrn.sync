# encoding: utf-8

u'''Utilities'''


import random, string


def generatePassword():
    corpus = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.sample(corpus, 16))
