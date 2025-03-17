import random

def shuffle(options):
    shuffled_options = options[:]
    random.shuffle(shuffled_options)
    return shuffled_options