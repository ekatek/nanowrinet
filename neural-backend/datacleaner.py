"""Convert between raw text and processed data, and visa-versa. """
from collections import Counter
import string
import re

PUNCTUATION = "\n" + ".?!\""
MAX_WORDS = 30000  # Not counting punctuation.

def clean_input_data(words, common):
    """Clean user input: separate out punctuation, separate out uncommon words,
       etc. Enforce vague length limits.
    """

    letters_and_digits = string.ascii_letters + string.digits
    if len(words) > MAX_WORDS:
        words = words[0:MAX_WORDS]

    unks = Counter()
    clean_words = []
    for word in words:
        # split out the punctuation
        current_word = ""
        sub_words = []
        for char in word:
            # we have already pre-broken on spaces. We only need to filter out
            # invalid characters and break on punctuation
            if char in PUNCTUATION:
                if current_word != "":
                    sub_words.append(current_word)
                    current_word = ""
                sub_words.append(char)
            elif char in letters_and_digits:
                current_word = current_word + char
            # nothing else is valid, so ignore it.
        sub_words.append(current_word)
        for my_word in sub_words:
            if unks[my_word] > 0:
                unks[my_word] = unks[my_word] + 1
                clean_words.append(my_word)
                continue

            low = my_word.lower()
            if low in common:
                clean_words.append(low)
                continue
            if unks[low] > 0:
                unks[low] = unks[low] + 1
                clean_words.append(low)
            else:
                unks[my_word] = 1
                clean_words.append(my_word)


    # Figure out the top unique words; assign them numbers
    sorted_unks = {}
    common_unks = unks.most_common()
    for i in range(0, len(common_unks)):
        sorted_unks[common_unks[i][0]] = i

    def unk_token(word):
        """Construct a token representing a unique word: UNK-<number>"""
        return "UNK-" + str(sorted_unks[word] % 1000)

    # replace a word with an unktoken
    def replace(word):
        """Replace a unique word with a corresponding token"""
        if unks[word]:
            return unk_token(word)
        if word in common:
            return word
        return unk_token(word.lower())

    return [replace(word) for word in clean_words], common_unks


# Clean up the generated sample
def clean_generated_data(sample, unks):
    """Convert generated processed data into an array of strings representing text."""

    def replace_unk_with_word(match):
        """Replace a unique token with a corresponding word"""
        index = match.group(2)
        return unks[int(index) % len(unks)][0]

    sample = re.sub(r"(UNK-)(\d+)", replace_unk_with_word, sample)

    def cap(match):
        """Capitalize letters at the beginning of sentences"""
        return match.group(2) + match.group(3)[0] + match.group(4).upper()
    sample = re.sub(r"( +)(\\.|\?|\!|\"|)( +)(\w)", cap, sample)

    def cap2(match):
        """Capitalize letters following double new lines (paragraph breaks). """
        return match.group(1) + match.group(2).upper()
    regex = re.compile("(\n *\n)( *\w)")
    sample = re.sub(regex, cap2, sample)
    return sample[0].upper() + sample[1:]

#  Read in a raw list of words and add PUNCTUATION.
def read_common_vocab(filename):
    """Read in a list of common words"""
    # Read in the original vocab
    common_vocab = set()
    with open(filename) as wordfile:
        for line in wordfile:
            common_vocab.add(line[:-1])

    for character in PUNCTUATION:
        common_vocab.add(character)
    return common_vocab


# Take an array of words, records them to disk as a common vocab.
def record_common_vocab(data, file_to_write):
    """Record a list of common words"""
    words = set()
    for word in data:
        words.add(word)

    with open(file_to_write, 'w') as commons:
        for word in words:
            commons.write(word + "\n")

def get_dir_for_author(author):
    """Given an author token, get the directory with its model files"""
    return "models/" + author + "/"
