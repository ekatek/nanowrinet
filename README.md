NaNoWriMo Autocompleter
=======

A small proof-of-concept joke project: given some user-generated text, use a Markov chain, or a
Recurrent Neural Net to intermix it with pre-existing data, and generate some new text.

This repository contains a small Meteor webapp (UI), and two backends (`markov-backend`) and (`neural-backend`).
We use AWS Lambda for computation (it is practically free, but suboptimal, since it doesn't have GPU support).
The backend directories contain code to generate the text, model (if applicable), and then to tar up and upload
the code + model into AWS Lambda.

For control, we use the settings file -- there is a sample `sample-settings.json` in the root directory.

To make AWS Lambda calls, fill in the `key` and `secret` keys with a key & secret for an
AWS IAM user authorized to run/change AWS Lambda code on your AWS account.

## Neural Net

The `neural-backend` directory contains some python/chainer code that runs a neural net
to, first, generate a model based on an author, use that model to generate samples, and remix the
results with the user's input. The net logic itself is based off: [[https://github.com/yusuketomoto/chainer-char-rnn]]
The zipped `base_lambda.zip` file contains the project's binary dependencies, as compiled and zipped from
an AWS machine.

To add a new source:

- Choose an author-token (ex: "tolkien") and lamnda-name (ex: "tolkien-net"). The token is what
  we will use as a base filename for plaintext, model, etc. The lambda-name should be the name of the
  AWS Lambda function that you should define using the AWS API. Add these to the settings.json file, in the
  `net-mixins` stanza, as approporiate.

- Add a plaintext file of the author's work to `data/<token>.txt`.

- In the `neural-backend` directory, run `generate_model.py <token>` to generate a new model.
  The script will also use that model to generate a small sample, just to give some visibility in what that
  model produces.

- Once you are satisfied with the model, in the `neural-backend` directory, run
  `generate_lambda.py <path to settings.json> <token>` to publish the AWS Lambda.

To run the webapp with the neural net backend, set the `mode` in `settings.json` to `net`.

## Markov Chain

The `markov-backend` directory contains some python to run a simple markov chainer autocompleter. By default, it runs/updates in an AWS Lambda function called "markov-chainer", but the name could be changed in `webapp/server/markov.js` and `markov-backend/generate_lambda.py`.

To add a new source:

- Add a file called `<token>.txt` to the data directory. Add it to the `markov-mixins` in the settings file, as
  approporiate.

- In the `markov-backend` directory, run `generate_lambda.py <path to settings.json>`

To run the webapp with the markov backend, set the `mode` in `settings.json` to `markov`.

## Running the webapp

The webapp is a small UI that calls up the AWS Lambda functions on the server. You can run it with:

`meteor --settings <settings.json>`

You can deploy it for free with:

`meteor deploy --settings <settings.json> <domain-name>.meteor.com`
>>>>>>> init
