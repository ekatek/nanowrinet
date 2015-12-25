"""Script to zip up and submit the AWS Lambda using the AWS CLI"""
import json
import sys
import random
import string
import shutil
import os
from subprocess import call

def generate_lambda(settings_file, author):
    """Add the source code and the pre-generated requested author model to a copy of
    the pre-generated zip file containing binary dependencies. Submit to AWS
    Lambda.

    """
    lambda_name = None
    random_id = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
    temporary_zip_dir = "/tmp/lambda-" + random_id + ".zip"
    print "Temporary directory:", temporary_zip_dir

    # Load in the JSON.
    settings = json.loads(open(settings_file).read())

    # Figure out the lambda function name
    for _, mix in settings["net-mixins"].items():
        if mix["author-token"] == author:
            lambda_name = mix["lambda-name"]
            break

    if lambda_name is None:
        print "No author-token by that name in the settings file"
        sys.exit(1)

    def add_to_zip_archive(filename):
        """ Add a file to the zip archive stored at temporary_zip_dir. """
        print "zip", "-r9", temporary_zip_dir, filename
        call(["zip", "-r9", temporary_zip_dir, filename])

    # Copy out the base_lambda.zip file, which contains the binary dependencies.
    shutil.copy("./base_lambda.zip", temporary_zip_dir)

    # Bundle up the source files.
    for filename in ["lambda_function.py", "Predictor.py", "base_rnn.py", "datacleaner.py"]:
        add_to_zip_archive(filename)

    # Bundle up the data
    for filename in [author + ".commons", author + ".model", author + ".vocab"]:
        add_to_zip_archive("models/" + author + "/" + filename)

    # Submit to AWS
    my_env = os.environ.copy()
    my_env["AWS_ACCESS_KEY_ID"] = settings["aws"]["key"]
    my_env["AWS_SECRET_ACCESS_KEY"] = settings["aws"]["secret"]

    zip_command = "--zip-file=fileb://" + temporary_zip_dir

    command = ["aws", "lambda", "update-function-code",
               "--function-name="+lambda_name, zip_command]
    print command
    call(command, env=my_env)

    # Cleanup
    os.remove(temporary_zip_dir)



generate_lambda(sys.argv[1], sys.argv[2])
