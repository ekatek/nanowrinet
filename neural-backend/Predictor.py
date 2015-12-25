"""The Predictor class keeps trains and samples models. """
import cPickle as pickle
import copy
import time

import numpy as np
from chainer import cuda, Variable, FunctionSet, optimizers
from base_rnn import BaseRNN, make_initial_state

class Settings(object):
    """ Base settings for BaseRNN. """
    def __init__(self,
                 seed=None,
                 decay_rate=0.95,
                 dropout=0,
                 learning_rate=2*10**-3,
                 learning_rate_decay=0.95,
                 learning_rate_decay_after=100,
                 grad_clip=15):
        self.seed = seed
        self.decay_rate = decay_rate
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.learning_rate_decay = learning_rate_decay
        self.learning_rate_decay_after = learning_rate_decay_after
        self.grad_clip = grad_clip

## Create and run the net in BaseRNN
class Predictor(object):
    """Use base_rnn and chainer to create models. Sample models, train models, save
       models, etc."""

    def __init__(self, n_units, gpu=-1, model=None, vocab=None):
        """ Constructor. Initialize some basic constants, like size of the RNN """
        self.units = n_units  # RNN size
        self.gpu = gpu        # GPU usage (-1 to not use the GPU)
        self.settings = Settings()

        self.model = None    # Existing model, if any
        self.vocab = None    # Existing vocab, if any
        if not model is None:
            self.model = pickle.load(open(model, 'rb'))
        if not vocab is None:
            self.vocab = pickle.load(open(vocab, 'rb'))


    ### Save model & vocab to disk.
    def save(self, model_file, vocab_file):
        """ Write the model and vocab to disk """
        model = self.model
        vocab = self.vocab
        pickle.dump(copy.deepcopy(model).to_cpu(), open(model_file, 'wb'))
        pickle.dump(vocab, open(vocab_file, 'wb'))


    ### Sample from a given model.
    def sample(self, length):
        """ Sample from the Predictor's model for length tokens."""

        result = []

        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()
            self.model.to_gpu()

        np.random.seed(self.settings.seed)

        # initialize generator
        state = make_initial_state(self.units, batchsize=1, train=False)
        if self.gpu >= 0:
            for _, value in state.items():
                value.data = cuda.to_gpu(value.data)

        prev_item = np.array([0], dtype=np.int32)
        if self.gpu >= 0:
            prev_item = cuda.to_gpu(prev_item)

         # optimize vocab for easy by-the-number-retrieval
        ivocab = {}
        for c, i in self.vocab.items():
            ivocab[i] = c

        # perform the actual sampling
        for i in xrange(length):
            state, prob = self.model.predict(prev_item, state)

            probability = cuda.to_cpu(prob.data)[0].astype(np.float64)
            probability /= np.sum(probability)
            index = np.random.choice(range(len(probability)), p=probability)

            result.append(ivocab[index])

            prev_item = np.array([index], dtype=np.int32)
            if self.gpu >= 0:
                prev_item = cuda.to_gpu(prev_item)

        return result

    ### Train the net on a given dataset, for a given number of jumps
    def train(self, words, steps, batchsize=100, sequence_length=10):
        """ Train the Predictor's model on words for steps number of steps. """

        whole_len = len(words)
        train_data = np.ndarray(whole_len, dtype=np.int32)
        jumps = steps * sequence_length

        # Initialize training data and maybe vocab.
        if self.vocab is None:
            vocab_initializing = True
            self.vocab = {}
        for i, word in enumerate(words):
            if vocab_initializing:
                if word not in self.vocab:
                    self.vocab[word] = len(self.vocab)
            train_data[i] = self.vocab[word]
        vocab_initializing = False


        print 'corpus length:', len(words)
        print 'self.vocab size:', len(self.vocab)

        # Initialize base model (if we need to)
        if self.model is None:
            self.model = BaseRNN(len(self.vocab), self.units)

        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()
            self.model.to_self.gpu()

        optimizer = optimizers.RMSprop(lr=self.settings.learning_rate,
                                       alpha=self.settings.decay_rate,
                                       eps=1e-8)
        optimizer.setup(self.model)

        jumpsPerEpoch = whole_len / batchsize
        epoch = 0
        start_at = time.time()
        cur_at = start_at
        state = make_initial_state(self.units, batchsize=batchsize)

        if self.gpu >= 0:
            accum_loss = Variable(cuda.zeros(()))
            for _, value in state.items():
                value.data = cuda.to_self.gpu(value.data)
        else:
            accum_loss = Variable(np.zeros((), dtype=np.float32))

        print 'going to train {} iterations'.format(steps)
        for i in xrange(jumps):
            x_batch = np.array([train_data[(jumpsPerEpoch * j + i) % whole_len]
                                for j in xrange(batchsize)])
            y_batch = np.array([train_data[(jumpsPerEpoch * j + i + 1) % whole_len]
                                for j in xrange(batchsize)])

            if self.gpu >= 0:
                x_batch = cuda.to_self.gpu(x_batch)
                y_batch = cuda.to_self.gpu(y_batch)


            state, loss_i = self.model.forward_one_step(x_batch,
                                                        y_batch,
                                                        state,
                                                        dropout_ratio=self.settings.dropout)
            accum_loss += loss_i

            if (i + 1) % sequence_length == 0:
                now = time.time()
                print '{}/{}, train_loss = {}, time = {:.2f}'.format((i+1)/sequence_length, steps, accum_loss.data / sequence_length, now-cur_at)
                cur_at = now

                optimizer.zero_grads()
                accum_loss.backward()
                accum_loss.unchain_backward()  # truncate
                if self.gpu >= 0:
                    accum_loss = Variable(cuda.zeros(()))
                else:
                    accum_loss = Variable(np.zeros((), dtype=np.float32))


                optimizer.clip_grads(self.settings.grad_clip)
                optimizer.update()

            if (i + 1) % jumpsPerEpoch == 0:
                epoch += 1

                if epoch >= self.settings.learning_rate_decay_after:
                    optimizer.lr *= self.settings.learning_rate_decay
                    print 'decayed self.settings.learning rate by a factor {} to {}'.format(self.settings.learning_rate_decay, optimizer.lr)
