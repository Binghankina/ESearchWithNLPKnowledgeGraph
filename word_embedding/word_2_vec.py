import collections
import math
import random
import numpy as np
from six.moves import xrange
import tensorflow as tf
import jieba
import re
import jieba.posseg as pseg
from word_embedding.helpers import optimizer_factory
from tensorflow.python.framework import graph_util
import pickle
import os
from collections import Counter
import random
from time import sleep
import threading
import json
import time

threadLock = threading.Lock()

global data
data = []
dir_path = os.path.dirname(os.path.realpath(__file__))
dic_dir = os.path.join(
    dir_path, '..', 'docker_data', 'elasticsearch_plugins',
    'analysis_ik_plugin', 'config'
)
jieba.load_userdict(os.path.join(dic_dir, './custom_dic'))
jieba.load_userdict(os.path.join(dic_dir, './inserted_features'))

vocabulary_size = 15000  # the number of top words to build embedding graph
num_plot_labels = 15000  # the number of top words to print in the visualization figure
global_data_index = 0
batch_size = 128      # batch size for training
embedding_size = 192  # Dimension of the embedding vector.
skip_window = 8       # How many words to consider left and right.
num_skips = 16         # How many times to reuse an input to generate a label.
num_sampled = 64    # Number of negative examples to sample.
num_training_steps = 2000000  # number of steps to train
learning_rate = 0.0001  # learning rate of the training
random_train = True
continue_train = True

# pick a random validation set to sample nearest neighbors. limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
# valid_size = 64     # Random set of words to evaluate similarity on.
# valid_window = 100  # Only pick dev samples in the head of the distribution.
#valid_examples = np.random.choice(valid_window, valid_size, replace=False)

stop_words = ['漫画区块链', '钛业队', '偷轮胎', '扎轮胎', '轮胎没了', '轮胎被扎', '轮胎被偷', '轮胎杯', '教练机', '车司机', '黄金周', '黄金期', '仓储式', '零售价', '领导专车', '总理专车',
              '总统专车', '主席专车', '专车座驾', '某传媒大学', '一家传媒大学', '奥巴马医改', '奥巴马医保', '医保法案', '人寿命', '人保护', '车炸弹', '车爆炸', '车相撞', '被汽车', '与汽车', '老百姓']
keep_words = ["a股", "gdp", "pmi", "cpi", "美元", "比特币", "tesla", "dna", "alphaGo", "deepMind", "tensorflow", "ai", "spacex", "neuralink", "pvc", "apple pay", "fgd", "docker", "aws", "azure", "oled", "opec", "shibor", "a站", "b站", "acfun", "bilibili", "ipo", "ppp", "ivd", "robot", "iot", "bdi", "st", "分级b", "分级a", "hadoop", "5g", "ldpc码", "polar码", "polar code", "ar眼镜", "智能手表", "智能穿戴", "智能手环", "vr眼镜", "hololens", "oculus",
              "fitbit", "saas", "qi标准", "qi无线", "工业4.0", "scada", "中国制造2025", "iiot", "三湘", "华通", "3d打印", "三维打印", "msci", "uber", "lifi", "li-fi", "led", "ipo加速概念股", "一带一路", "二孩", "二胎", "c919", "双11", "ipo影子股", "lcd", "ofo", "uber", "airbnb", "erp国产化", "h5n1", "h5n2", "h7n3", "h7n2", "h7n9", "h9n2", "h7n7", "h7n1", "h3n2", "h10n8", "gdp", "mdi", "3d成像", "ipo加速", "ipo加速概念股", "r22", "mdi", "pcb", "ppi", "slf", "psl", "mlf", "amc影院", "元/吨度"]
# input file
filename = os.path.join(dir_path, "./article_data.json")
#filename = "/diskz/climt/text_data/news_items20170608.csv"
global Dictionary


def load_keep_list():
    f = open(os.path.join(dic_dir, 'keep_words'), 'r')
    for word in f:
        keep_words.append(word.strip())
    jieba.load_userdict(keep_words)
    f.close()
    return


def load_stop_list():
    f = open(os.path.join(dic_dir, 'stop_words'), 'r')
    for word in f:
        if word != 'UNK' or word != 'linebreak':
            stop_words.append(word.strip())
    jieba.load_userdict(stop_words)
    f.close()
    return


def test_jieba(line):
    for word, flag in pseg.cut(line):
        print(str(word))
        if str(word) in keep_words:
            print(str(word))
            continue
        if re.findall('[\u4e00-\u9fff]{2,}', str(word)):
            if flag.startswith('n'):
                if str(word) not in stop_words:
                    print(str(word))


def thread_read(id, filename, offset, num_lines):
    data = []
    counter = 0
    f = open(filename, 'r')
    for i in range(int(offset)):
        f.readline()
    while True:
        line = f.readline()

        counter = counter + 1
        if counter % 100 == 0:
            print("thread " + str(id) + " processing entry: " + str(counter))

        for word, flag in pseg.cut(line):
            if str(word) in keep_words:
                data.append(str(word))
                continue
            if re.findall('[\u4e00-\u9fff]{2,}', str(word)):
                if flag.startswith('n'):
                    if str(word) not in stop_words:
                        data.append(str(word))
        for i in range(skip_window):
            data.append("linebreak")

        if counter == num_lines:
            break

    return data


def multi_thread_read(filename, thread_num=10):

    global data

    pickle_file = 'data_current.pickle'
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as fd:
            data = pickle.loads(fd.read())
            return data

    with open(filename) as f:
        num_lines = len(f.readlines())
        print(num_lines)

    threads = []
    for i in range(thread_num):
        thread = myThread(i, filename, (num_lines / thread_num)
                          * i, num_lines / thread_num)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    pickle_file = 'data.pickle'
    with open(pickle_file, 'wb') as fd:
        fd.write(pickle.dumps(data))

    return data


class myThread(threading.Thread):
    def __init__(self, threadID, filename, offset, num_lines):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.filename = filename
        self.offset = offset
        self.num_lines = num_lines

    def run(self):
        local_data = thread_read(
            self.threadID, self.filename, self.offset, self.num_lines)
        global data
        threadLock.acquire()
        data = data + local_data
        threadLock.release()


def subsampling(int_words):
    threshold = 1e-4
    word_counts = Counter(int_words)
    total_count = len(int_words)
    freqs = {word: count / total_count for word, count in word_counts.items()}
    p_drop = {
        word: 1 - np.sqrt(threshold / freqs[word]) for word in word_counts}
    train_words = [word for word in int_words if word ==
                   "linebreak" or random.random() < (1 - p_drop[word])]
    return train_words


def jieba_noun_tokenizer(text):
    cuts = pseg.cut(text)
    tokenized_strings = []
    for word, flag in cuts:
        if re.findall('[\u4e00-\u9fff]{2,}', str(word)):
            if flag.startswith('n'):
                tokenized_strings.append(str(word))
    return tokenized_strings


def jieba_tokenizer(text):
    cuts = jieba.cut_for_search(text)
    tokenized_strings = []
    for word in cuts:
        if re.findall('[\u4e00-\u9fff]{2,}', str(word)):
            tokenized_strings.append(str(word))
    return tokenized_strings

# def read_my_file(filename):
#     pickle_file = 'data.pickle'
#     if os.path.exists(pickle_file):
#         with open(pickle_file, 'rb') as fd:
#             return pickle.loads(fd.read())
#
#     f = open(filename, 'r')
#     data = []
#     counter = 0
#     for entry in f:
#         data = data + jieba_noun_tokenizer(entry)
#         counter = counter + 1
#         if counter % 1000 == 0:
#             print("processing entry: "+str(counter))
#
#             with open(pickle_file, 'wb') as fd:
#                 fd.write(pickle.dumps(data))
#
#     return data


def read_my_file(filename):
    pickle_file = 'data_current.pickle'
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as fd:
            return pickle.loads(fd.read())

    data = []
    counter = 0
    with open(filename) as fd:
        for line in fd:
            counter = counter + 1
            if counter % 1000 == 0:
                print("processing entry: " + str(counter))
            for word, flag in pseg.cut(line):
                if str(word) in keep_words:
                    data.append(str(word))
                    continue
                if re.findall('[\u4e00-\u9fff]{2,}', str(word)):
                    if flag.startswith('n'):
                        if str(word) not in stop_words:
                            data.append(str(word))

            # seperate lines since they are seperate news
            for i in range(skip_window):
                data.append("linebreak")

    pickle_file = 'data.pickle'
    with open(pickle_file, 'wb') as fd:
        fd.write(pickle.dumps(data))

    return data


def read_my_file_touyantong(filename):
    pickle_file = 'data_current.pickle'
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as fd:
            return pickle.loads(fd.read())

    data = []
    counter = 0
    with open(filename) as fd:
        d = json.load(fd)
        for line in d:
            counter = counter + 1
            if counter % 1000 == 0:
                print("processing entry: " + str(counter))
            if 'article' in line.keys():
                for word, flag in pseg.cut(line['article']):
                    if str(word) in keep_words:
                        data.append(str(word))
                        continue
                    if re.findall('[\u4e00-\u9fff]{2,}', str(word)):
                        if flag.startswith('n'):
                            if str(word) not in stop_words:
                                data.append(str(word))
            else:
                for word, flag in pseg.cut(line['content']):
                    if str(word) in keep_words:
                        data.append(str(word))
                        continue
                    if re.findall('[\u4e00-\u9fff]{2,}', str(word)):
                        if flag.startswith('n'):
                            if str(word) not in stop_words:
                                data.append(str(word))

            # seperate lines since they are seperate news
            for i in range(skip_window):
                data.append("linebreak")

    pickle_file = 'data.pickle'
    with open(pickle_file, 'wb') as fd:
        fd.write(pickle.dumps(data))

    return data


def build_dataset(words, n_words):
    count = [['UNK', -1]]
    count.extend(collections.Counter(words).most_common(n_words - 1))
    dictionary = dict()
    for word, _ in count:
        dictionary[word] = len(dictionary)
    data = list()
    unk_count = 0
    for word in words:

        if word in dictionary:
            index = dictionary[word]
        else:
            index = 0  # dictionary['UNK']
            unk_count += 1

        # seperate lines
        if word == "linebreak":
            index = 0  # dictionary['UNK']

        data.append(index)
    count[0][1] = unk_count
    reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
    global Dictionary
    Dictionary = reversed_dictionary

    '''
    for i in range(len(data)):
        print(check(data[i]))
        sleep(0.1)
    '''

    return data, count, dictionary, reversed_dictionary


def check(index):
    return Dictionary[int(index)]


def generate_batch(data, batch_size, num_skips, skip_window):
    global global_data_index
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    span = 2 * skip_window + 1
    buffer = collections.deque(maxlen=span)
    for _ in range(span):
        buffer.append(data[global_data_index])
        global_data_index = (global_data_index + 1) % len(data)
    for i in range(batch_size // num_skips):
        target = skip_window
        targets_to_avoid = [skip_window]
        for j in range(num_skips):
            while target in targets_to_avoid:
                target = random.randint(0, span - 1)
            targets_to_avoid.append(target)
            # remove influence of UNK and linebreaks
            if buffer[skip_window] == 0 or buffer[target] == 0:
                batch[i * num_skips + j] = 0
                labels[i * num_skips + j, 0] = 0
            else:
                batch[i * num_skips + j] = buffer[skip_window]
                labels[i * num_skips + j, 0] = buffer[target]
        buffer.append(data[global_data_index])
        global_data_index = (global_data_index + 1) % len(data)
    global_data_index = (global_data_index + len(data) - span) % len(data)

    '''
    for i in range(len(batch)):
        print(check(batch[i]))
        print(check(labels[i][0]))
        print("------------")
        sleep(0.1)
    '''

    return batch, labels


def generate_batch_random(data, batch_size, num_skips, skip_window):
    global global_data_index
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    span = 2 * skip_window + 1
    buffer = collections.deque(maxlen=span)
    for _ in range(span):
        buffer.append(data[global_data_index])
        global_data_index = (global_data_index + 1) % len(data)
    for i in range(batch_size // num_skips):
        target = skip_window
        targets_to_avoid = [skip_window]
        for j in range(num_skips):
            while target in targets_to_avoid:
                target = random.randint(0, span - 1)
            targets_to_avoid.append(target)
            # remove influence of UNK and linebreaks
            if buffer[skip_window] == 0 or buffer[target] == 0:
                batch[i * num_skips + j] = 0
                labels[i * num_skips + j, 0] = 0
            else:
                batch[i * num_skips + j] = buffer[skip_window]
                labels[i * num_skips + j, 0] = buffer[target]
        buffer.append(data[global_data_index])
        global_data_index = (global_data_index + 1) % len(data)
    global_data_index = random.randint(0, len(data) - 1)

    '''
    for i in range(len(batch)):
        print(check(batch[i]))
        print(check(labels[i][0]))
        print("------------")
        sleep(0.1)
    '''

    return batch, labels


def save_embedding(final_embeddings, reverse_dictionary, filename_embedding, filename_dictionary):
    data = pickle.dumps(final_embeddings)
    with open(filename_embedding, 'wb') as outfile:
        outfile.write(data)

    data = pickle.dumps(reverse_dictionary)
    with open(filename_dictionary, 'wb') as outfile:
        outfile.write(data)


def load_embedding(filename_embedding, filename_dictionary):

    with open(filename_embedding, 'rb') as embeddings:
        final_embeddings = pickle.loads(embeddings.read())

    with open(filename_dictionary, 'rb') as dictionary:
        final_dictionary = pickle.loads(dictionary.read())

    return final_embeddings, final_dictionary


def train(data, reverse_dictionary, checkpoint=False):

    graph = tf.Graph()
    with graph.as_default():

        train_inputs = tf.placeholder(
            tf.int32, shape=[batch_size], name="input_node")
        train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])

        with tf.device('/cpu:0'):
            '''
            if checkpoint == True:
                loaded_embeddings, _ = load_embedding('./embedding/embedding', './embedding/dictionary')
                embeddings = tf.Variable(loaded_embeddings, name="embeddings")
                print(embeddings)
            else:
            '''
            embeddings = tf.Variable(tf.random_uniform(
                [vocabulary_size, embedding_size], -1.0, 1.0), name="embeddings")

            embed = tf.nn.embedding_lookup(embeddings, train_inputs)

            nce_weights = tf.Variable(
                tf.truncated_normal([vocabulary_size, embedding_size],
                                    stddev=1.0 / math.sqrt(embedding_size)))
            nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

        loss = tf.reduce_mean(
            tf.nn.nce_loss(weights=nce_weights,
                           biases=nce_biases,
                           labels=train_labels,
                           inputs=embed,
                           num_sampled=num_sampled,
                           num_classes=vocabulary_size))

        optimizer = optimizer_factory['adam'](learning_rate).minimize(loss)

        norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
        normalized_embeddings = embeddings / norm

        saver = tf.train.Saver()

        init = tf.global_variables_initializer()

    with tf.Session(graph=graph) as session:

        init.run()

        if checkpoint == True:
            saver.restore(session, "./embedding/model.ckpt")

        average_loss = 0

        try:
            for step in xrange(num_training_steps):
                if random_train:
                    batch_inputs, batch_labels = generate_batch_random(data,
                                                                       batch_size, num_skips, skip_window)
                else:
                    batch_inputs, batch_labels = generate_batch(data,
                                                                batch_size, num_skips, skip_window)

                feed_dict = {train_inputs: batch_inputs,
                             train_labels: batch_labels}

                _, loss_val = session.run(
                    [optimizer, loss], feed_dict=feed_dict)
                average_loss += loss_val

                if step % 2000 == 0:
                    if step > 0:
                        average_loss /= 2000

                    print('Average loss at step ', step, ': ', average_loss)
                    average_loss = 0

                if step % 20000 == 0:
                    print("saving embeddings")
                    saver.save(session, "./embedding/model.ckpt")
                    final_embeddings = normalized_embeddings.eval()
                    save_embedding(final_embeddings, reverse_dictionary,
                                   './embedding/embedding', './embedding/dictionary')
                    print("finished saving embeddings")

        except KeyboardInterrupt:
            # Introduce a line break after ^C is displayed so save message
            # is on its own line.
            print()
        finally:
            print("saving embeddings")
            saver.save(session, "./embedding/model.ckpt")
            final_embeddings = normalized_embeddings.eval()
            save_embedding(final_embeddings, reverse_dictionary,
                           './embedding/embedding', './embedding/dictionary')
            print("finished saving embeddings")


def serve(word, final_embeddings, reverse_dictionary):

    with tf.Session():
        word_index = -1
        for key in reverse_dictionary.keys():
            if word == reverse_dictionary[key]:
                word_index = key

        if word_index == -1:
            print("word not found in top words, please try another word")
            return

        valid_embeddings = tf.nn.embedding_lookup(
            final_embeddings, [word_index])
        similarity = tf.matmul(
            valid_embeddings, final_embeddings, transpose_b=True)

        sim = similarity.eval()

        top_k = 10
        nearest = (-sim[0, :]).argsort()[1:top_k + 1]
        log_str = '和 \"%s\" 语义相近的是: ' % word
        for k in xrange(top_k):
            close_word = reverse_dictionary[nearest[k]]
            log_str = '%s %s,' % (log_str, close_word)
        print(log_str)

def serve_touyantong(word, final_embeddings, reverse_dictionary):

    with tf.Session():
        word_index = -1
        for key in reverse_dictionary.keys():
            if word == reverse_dictionary[key]:
                word_index = key

        if word_index == -1:
            print("word not found in top words, please try another word")
            return

        valid_embeddings = tf.nn.embedding_lookup(
            final_embeddings, [word_index])
        similarity = tf.matmul(
            valid_embeddings, final_embeddings, transpose_b=True)

        sim = similarity.eval()

        top_k = 10
        nearest = (-sim[0, :]).argsort()[1:top_k + 1]


        close_word = []
        similarity_score = []
        #log_str = '和 \"%s\" 语义相近的是: ' % word
        for k in xrange(top_k):
            if reverse_dictionary[nearest[k]] == 'UNK':
                continue
            similarity_score.append(nearest[k])
            close_word.append(reverse_dictionary[nearest[k]])
        #    log_str = '%s %s,' % (log_str, reverse_dictionary[nearest[k]])
        #print(log_str)
        #print(sim[0, similarity_score])

        return close_word, sim[0, similarity_score]

# tensorflow way of preserving models, this piece of code does not work yet
# TODO: load model using fronzen graph
def save_model(sess, logdir):
    input_node = sess.graph.get_tensor_by_name("input_node:0")
    tf.identity(input_node, name="input_node")

    name_empty_graph_file = 'graph-frozen-{}.pb'.format("net")

    # Store empty graph file
    print('Saving const graph def to {}'.format(name_empty_graph_file))
    # graph_def = sess.graph_def
    # graph_def = sess.graph.as_graph_def()
    graph_def = tf.get_default_graph().as_graph_def()

    # fix batch norm nodes
    # https://github.com/tensorflow/tensorflow/issues/3628
    for node in graph_def.node:
        if node.op == 'RefSwitch':
            node.op = 'Switch'
            for index in range(len(node.input)):
                if 'moving_' in node.input[index]:
                    node.input[index] = node.input[index] + '/read'
        elif node.op == 'AssignSub':
            node.op = 'Sub'
            if 'use_locking' in node.attr:
                del node.attr['use_locking']
        elif node.op == 'AssignAdd':
            node.op = 'Add'
            if 'use_locking' in node.attr:
                del node.attr['use_locking']

    converted_graph_def = graph_util.convert_variables_to_constants(sess, graph_def,
                                                                    ["embeddings"])

    tf.train.write_graph(converted_graph_def, logdir,
                         name_empty_graph_file, as_text=False)


def main():
    global data
    load_stop_list()
    jieba.load_userdict(keep_words)
    jieba.enable_parallel(8)
    #test_jieba("polar码a股市场中国企业经济资金行业基金数据银行产品项目UNK linebreak业务方面集团公司情况月份时间方式部分水平人士全面重点部门原因基本中心整体空间比例关系过程比特币漫画区块链a股")

    # load data from the csv file
    vocabulary = read_my_file_touyantong(filename)
    # multi_thread_read(filename)
    #vocabulary = data
    # build dataset from the read file
    # print(vocabulary)
    sub_vocabulary = subsampling(vocabulary)
    data, count, dictionary, reverse_dictionary = build_dataset(
        sub_vocabulary, vocabulary_size)
    # release some memory
    del vocabulary
    # train embeddings

    train(data, reverse_dictionary, continue_train)

    # load from trained embeddings
    final_embeddings, reverse_dictionary = load_embedding(
        './embedding/embedding', './embedding/dictionary')
    # generate figures to visualize embeddings
    #plot_embeddings(final_embeddings, reverse_dictionary)
    # find closest word to a given word
    serve("公债", final_embeddings, reverse_dictionary)
    # if you want to build a service, just load embeddings in two variables "final_embeddings, reverse_dictionary",
    # and then call serve("公债",final_embeddings,reverse_dictionary) for each request


if __name__ == '__main__':
    #main()
    final_embeddings, reverse_dictionary = load_embedding('./embedding/embedding', './embedding/dictionary')
    close_words, similarity = serve_touyantong("假新闻", final_embeddings, reverse_dictionary)
