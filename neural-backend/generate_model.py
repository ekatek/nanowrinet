""" Usage: generate_model.py <author token> [<steps>]
For a given author token, iterate steps (or 5000) steps to generate a model.
Save the model and other files in "models/<author token>/". Display a small
sample text generated from the model.
"""
import os
import sys
from Predictor import Predictor
from datacleaner import clean_input_data, read_common_vocab, record_common_vocab, get_dir_for_author

def generate_model(author, steps):
    """Given an author name, processes the data/<author>.txt input for steps number
    of iterations into the model input to be used by the lambda_handler
    function.
    """
    predictor = Predictor(128)

    # Filenames.
    author_models_dir = get_dir_for_author(author)
    if not os.path.exists(author_models_dir):
        os.mkdir(author_models_dir)
    model_file = author_models_dir + author + ".model"
    vocab_file = author_models_dir +  author + ".vocab"
    commons_file = author_models_dir +  author + ".commons"
    raw_text_file = "../data/" + author + ".txt"

    # Read in the 'frequently used words' as common vocab.
    frequent = read_common_vocab("../data/20k_most_common.txt")

    # Clean the content.
    with open(raw_text_file, 'r') as raw:
        raw_words = raw.read().split(' ')
        data, _ = clean_input_data(raw_words, frequent)

    # Write out the words that occur in the clean data to the commons file.
    record_common_vocab(data, commons_file)

    # Train the model. This step takes the longest.
    predictor.train(data, steps)

    # Save the model that we have trained to disk.
    predictor.save(model_file, vocab_file)

    return predictor


def process_input():
    """ Process the sys.argv input, generate a model, and print a small sample """
    author = sys.argv[1]
    steps = 5000
    print len(sys.argv)
    if len(sys.argv) > 2:
        steps = int(sys.argv[2])

    predictor = generate_model(author, steps)
    print predictor.sample(100)


process_input()
