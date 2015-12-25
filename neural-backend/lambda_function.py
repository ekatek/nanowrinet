""" The lambda_handler function is the entryway for AWS Lambda """
from Predictor import Predictor
from datacleaner import clean_input_data, read_common_vocab, clean_generated_data, get_dir_for_author

def lambda_handler(event, context):
    """Use a model for an existing author to generate length words, interleaved
       with user text input."""
    author = event["author"]
    user_text = event["userText"]
    length = event["length"]

    # Load in the predictor
    model_file = get_dir_for_author(author) + author + ".model"
    vocab_file = get_dir_for_author(author) + author + ".vocab"
    predictor = Predictor(128, model=model_file, vocab=vocab_file)

    # Clean the user data and separate out unknown words.
    common_vocab = read_common_cocab(get_dir_for_author(author) + author + ".commons")
    data, unique_user_words = clean_input_data(user_text, common_vocab)

    generated_sample = predictor.sample(length)
    return clean_generated_data(' '.join(generated_sample), unique_user_words)
