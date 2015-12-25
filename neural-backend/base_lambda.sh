# On an AWS machine, inside a virtual environment,
# install numpy, cython, h5py and chainer.

# These commands will create a base lambda. You can
# add new models to it.

zip -r9 BaseRNN.py base_lambda.zip
zip -r9 Predictor.py base_lambda.zip
zip -r9 datacleaner.py base_lambda.zip
zip -r9 lambda_function.py base_lambda.zip

pushd $VIRTUAL_ENV/lib/python2.7/site-packages
zip -r9 ~/pancakes/base_lambda.zip *
popd

pushd $VIRTUAL_ENV/lib64/python2.7/site-packages
zip -r9 ~/pancakes/base_lambda.zip *
popd