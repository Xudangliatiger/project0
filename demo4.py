#coding:utf-8


import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn import preprocessing


# dataprocess
dataframe = pd.read_csv('seq100x.txt',header=None, names = ['y','x'] )


trainingset_x=list(dataframe.x)
trainingset_y=list(dataframe.y)
for i in range(len(trainingset_x)):
    trainingset_x[i] = list(str(trainingset_x[i]))
    temp = []
    for j in range(60):
        if j<len(trainingset_x[i]):
            if trainingset_x[i][j] == 'A':
                temp.append([1,0,0,0])
            elif trainingset_x[i][j] == 'C':
                temp.append([0,1,0,0])
            elif trainingset_x[i][j] == 'G':
                temp.append([0,0,1,0])
            else:
                temp.append([0,0,0,1])
        else:
            temp.append([0,0,0,0])
    trainingset_x[i] = temp
trainingset_x = np.reshape(trainingset_x,(len(trainingset_x),60,4))
trainingset_y = np.array(trainingset_y)

encoder1 = preprocessing.LabelBinarizer()
trainingset_y = encoder1.fit_transform(trainingset_y)

# hyperparameters
lr = 0.0001
training_iters = len(trainingset_x)
batch_size = 100
epoch_num = 100
n_inputs = 4   # equals to embedding dim
n_steps = 60    # time steps, length of single DNA seq
n_hidden_units = len(trainingset_y[0])   # neurons in hidden layer,it equal to output length ,also the n_classes.
n_hidden_layers = 2  # depth of network
n_classes = len(trainingset_y[0])    # number of different y



x = tf.placeholder(tf.float32, [None, n_steps, n_inputs])
y = tf.placeholder(tf.float32, [None, n_classes])

weights = {

    'in': tf.Variable(tf.random_normal([n_inputs, n_hidden_units])),
    'out': tf.Variable(tf.random_normal([n_hidden_units, n_classes]))
}
biases = {

    'in': tf.Variable(tf.constant(0.1, shape=[n_hidden_units, ])),
    'out': tf.Variable(tf.constant(0.1, shape=[n_classes, ]))
}





def LSTMdemo(X, weights, biases):

    X = tf.reshape(X, [-1, n_inputs])
    X_in = tf.matmul(X, weights['in']) + biases['in']
    X_in = tf.reshape(X_in, [-1, n_steps, n_hidden_units])

    lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(n_hidden_units, forget_bias=0.0, state_is_tuple=True)
    cell = tf.nn.rnn_cell.MultiRNNCell([lstm_cell] * n_hidden_layers, state_is_tuple=True)

    init_state = cell.zero_state(batch_size, dtype=tf.float32)

    outputs, final_state = tf.nn.dynamic_rnn(cell, X_in, initial_state=init_state, time_major=False)

    outputs = tf.unstack(tf.transpose(outputs, [1,0,2]))
    results = tf.matmul(outputs[-1], weights['out']) + biases['out']

    return results




pred = LSTMdemo(x, weights, biases)
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
train_op = tf.train.AdamOptimizer(lr).minimize(cost)
correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
saver = tf.train.Saver()


def next(self, batch_size):
    batch_data = (self[step * batch_size:min(step*batch_size +
                                         batch_size, len(self.data))])
    return batch_data


with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)
    for epoch in range(epoch_num):
        lr=10*lr
        step = 0
        while (step+1) * batch_size < training_iters:
            batch_xs = next(trainingset_x,batch_size)
            batch_ys = next(trainingset_y,batch_size)
            batch_xs = batch_xs.reshape([batch_size, n_steps, n_inputs])
            sess.run([train_op], feed_dict={
                x: batch_xs,
                y: batch_ys,
            })
            if step % 20 == 0:
                print(sess.run(accuracy, feed_dict={
                x: batch_xs,
                y: batch_ys,
            }))
            step += 1
        if epoch % 20 == 0: saver.save(sess,'save_path')