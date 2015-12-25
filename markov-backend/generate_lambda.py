"""Script to zip up and submit the AWS Lambda using the AWS CLI."""
import json
import sys
import random
import string
import os
from subprocess import call

def generate_lambda(settings_file):
    """Zip-up the needed parts of the AWS Lambda into a temporary directory; submit
      the directory as a code update for the markov-chainer Lambda
    """
    random_id = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
    temporary_zip_dir = "/tmp/lambda-" + random_id + ".zip"

    # Load in the JSON.
    settings = json.loads(open(settings_file).read())

    def add_to_zip_archive(filename):
        """ Add a file to the zip archive stored at temporary_zip_dir. """
        call(["zip", "-r9", temporary_zip_dir, filename])


    # Bundle up the source files.
    for filename in ["lambda_function.py", "markov.py"]:
        add_to_zip_archive(filename)

    # Bundle up the data
    for _, mixin in settings["markov-mixins"].items():
        if "filename" in mixin:
            add_to_zip_archive("../data/" + mixin["filename"] + ".txt")


    # Submit to AWS
    my_env = os.environ.copy()
    my_env["AWS_ACCESS_KEY_ID"] = settings["aws"]["key"]
    my_env["AWS_SECRET_ACCESS_KEY"] = settings["aws"]["secret"]

    command = ["aws", "lambda", "update-function-code",
               "--function-name=markov-chainer",
               "--zip-file=fileb://" + temporary_zip_dir]
    print command
    call(command, env=my_env)

    # Cleanup
    call(["rm", temporary_zip_dir])


generate_lambda(sys.argv[1])
