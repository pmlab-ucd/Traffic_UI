__author__ = 'hao'
import csv
import numpy
from statistics import *
import re
import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import json

def stat_fea_cal(x):
    return [min(x), max(x), mean(x), median(x), s_dev(x), skewness(x), kurtosis(x)]

def weka_header(stat_num):
    stat_name = ['min', 'max', 'mean', 'median', 'sdev', 'skewness', 'kurtosis']
    train_file.write('@RELATION ' + 'pcap' + '\n')
    #train_file.write('@ATTRIBUTE pcapname STRING\n')
    train_file.write('@ATTRIBUTE frameNum NUMERIC\n')
    for i in range(stat_num):
        train_file.write('@ATTRIBUTE frameStat_' + stat_name[i] + ' NUMERIC\n')
    for i in range(stat_num):
        train_file.write('@ATTRIBUTE epoStat_' + stat_name[i] + ' NUMERIC\n')
    for i in range(stat_num):
        train_file.write('@ATTRIBUTE upStat_' + stat_name[i] + ' NUMERIC\n')
    train_file.write('@ATTRIBUTE non_httpFrameNum NUMERIC\n')
    train_file.write('@ATTRIBUTE upCounter NUMERIC\n')
    train_file.write('@ATTRIBUTE class {1}\n')
    train_file.write('\n@DATA\n')

def get_sta_data(txt):
    appdict = json.load(open(txt, 'r'))
    #appdict = eval(ui_label_txt)
    for appdir in appdict.keys():
        os.path.walk(appdir, visit, appdict[appdir][1])
    weka_header(7)
    for fea_val in fea_val_list:
        if len(fea_val) < 7:
            continue
        weka_data(fea_val)


def weka_data(fea_val):
    #train_file.write(str(fea_val['pcap']) + ',')
    train_file.write(str(fea_val['frameNum']) + ',')
    for i in fea_val['frameStat']:
        train_file.write(str(i) + ',')
    for i in fea_val['epoStat']:
        train_file.write(str(i) + ',')
    for i in fea_val['upStat']:
        train_file.write(str(i) + ',')
    train_file.write(str(fea_val['non_httpFrameNum']) + ',')
    train_file.write(str(fea_val['upCounter']) + ',')
    train_file.write(str(fea_val['class']) + '\n')


def sta_fea_cal(dirname, filename, fea_val, ui_label):
    if ui_label == '1' or ui_label == 1:
        return
    ui_label = '1'
    pcapreader = csv.reader(open(dirname + '/' + filename, 'rb'), delimiter='\t')
    result = list(pcapreader)
    result = numpy.array(result)
    # print result
    fea_val['pcap'] = dirname + '/' + filename
    fea_val['frameNum'] = len(result)
    print fea_val['frameNum']
    try:
        frame_len = map(int, result[:, 1].tolist())
    except:
        print dirname
        return
    fea_val['frameStat'] = stat_fea_cal(frame_len)
    print fea_val['frameStat']

    epoch = map(float, result[:, 63].tolist())
    interval = []
    for i in range(1, len(epoch)):
        interval.append(epoch[i] - epoch[i - 1])
    # print interval
    fea_val['epoStat'] = stat_fea_cal(interval)
    print fea_val['epoStat']

    protos = map(str, result[:, 2].tolist())
    http_counter = 0
    for prot in protos:
        if re.search('http', prot):
            http_counter += 1
    fea_val['non_httpFrameNum'] = fea_val['frameNum'] - http_counter
    print fea_val['non_httpFrameNum']

    # uplink and downlink
    try:
        s_ports = map(int, result[:, 6].tolist())
    except:
        fea_val = {}
        return
    d_ports = map(int, result[:, 7].tolist())
    port_s = s_ports[0]
    # port_d = d_ports[0]
    up_frames = []
    for i in range(len(s_ports)):
        if s_ports[i] == port_s:
            up_frames.append(frame_len[i])
    fea_val['upCounter'] = len(up_frames)
    print fea_val['upCounter']
    fea_val['upStat'] = stat_fea_cal(up_frames)
    # print s_ports
    # if re.search('/1', dirname):
    #     fea_val['class'] = 1
    # elif re.search('/0', dirname):
    #     fea_val['class'] = 0
    # else:
    #     fea_val['class'] = 2
    fea_val['class'] = ui_label
    #weka_data(fea_val)
    #fea_val_list.append(fea_val)

def get_data(txt):
    titles = []
    titles_label = []
    #fea_val = {}
    appdict = json.load(open(txt, 'r'))
    #appdict = eval(ui_label_txt)
    for appdir in appdict.keys():
        os.path.walk(appdir, visit, [titles, titles_label, appdict[appdir][1]])
    # Initialize the "CountVectorizer" object, which is scikit-learn's bag of words tool.


    if len(titles_label) != len(titles):
        print 'ERROR: number of titles and titles not consistent'
        exit(1)
    weka(titles, titles_label)

def weka(titles, titles_label):
    weka_header(7)
    # For each, print the vocabulary word and the number of times it appears in the training set
    if numeric_flag:
        for word in vocabulary:
            #print '@ATTRIBUTE word_freq_' + tag + ' NUMERIC'
            train_file.write('@ATTRIBUTE word_freq_' + word + ' NUMERIC\n')
    else:
        for word in vocabulary:
            #print '@ATTRIBUTE word_freq_' + tag + ' NUMERIC'
            train_file.write('@ATTRIBUTE word_freq_' + word + ' {0, 1}\n')
            #print count
    train_file.write('@ATTRIBUTE word_freq_unknown_word {0, 1}\n')

    train_file.write('@ATTRIBUTE class {1}\n')
    #print '\n@DATA'
    train_file.write('\n@DATA\n')

    if len(titles_label) != len(fea_val_list):
        print len(fea_val_list), len(titles_label)
        print 'ERROR: number of titles and fea_val not consistent'
        exit(1)
    counter = 0
    for title in titles:
        if len(fea_val_list[counter]) < 7:
            counter += 1
            continue
        weka_data(fea_val_list[counter])
        # print title_counts
        #word_freq_list = []
        for word_count in title:
              # calculate freq of words = percentage of words in front page that match WORD
            # i.e. 100 * (number of times the WORD appears in the front_page) /  total number of words in front page

            #word_freq_list.append(word_freq)
            #sys.stdout.write(str(word_freq) + ',')
                if int(word_count) > 0:
                    train_file.write('1,')
                else:
                    train_file.write('0,')
        #sys.stdout.write(str(titles_lable[counter]) + '\n')
        train_file.write(str(titles_label[counter]) + '\n')
        counter += 1

def str2words(str, title):
    #print 'English Detected!'
    str = re.sub('(http|com|net|org|/|\?|=|_|:|&|\.)', ' ', str)  # if English only
    words = str.lower().split()
    #words = [w for w in words if not w in stopwords.words("english")]
    #print words

    # print '/'.join(words) #  do not use print if you want to return
    for word in words:
        if len(word) < 11:
            for i in range(len(vocabulary)):
                if word.encode('utf-8') == vocabulary[i]:
                    title[i] += 1
                    break
            if word not in vocabulary:
                title[len(vocabulary)] = 1
    return ' '.join(words)

# read from txt and get url
def struct_fea_cal(dirname, filename, titles, titles_label, ui_label):
    if ui_label == '1' or ui_label == 1:
        return
    ui_label = '1'
    #print 'label:' + str(ui_label)
    pcapreader = csv.reader(open(dirname + '/' + filename, 'rb'), delimiter='\t')
    result = list(pcapreader)
    result = np.array(result)
    title = [0] * (len(vocabulary) + 1)
    try:
        uris = result[:, 26]
    except IndexError as e:
        print e.args
        print e.message
        return False
    host = None
    for uri in uris:
        if uri:
            urilist.append(uri)
            if uri not in distinct_uri:
                distinct_uri.append(uri)
            print uri
            host = uri.split('/')[2]

            host_pcap[dirname + '/' + filename] = host
            if host not in domain_list:
                domain_list.append(host)
            # ignore the parameter part of URI
            #uri = uri.split['?'][0]
            str2words(uri, title)
            break
    if filter_ad and host:
        for ad in adlist:
            if re.search(ad, host):
                return False
                ui_label = 1
                break
    titles.append(title)
    titles_label.append(ui_label)
    return True

def visit(arg, dirname, files):
    #titles = arg[0]
    #titles_label = arg[1]
    #ui_label = arg[2]
    ui_label = arg
    for filename in files:
        if re.search('\.csv', filename) or (re.search('\.c1sv', filename) and re.search('/0', dirname)):
            #if struct_fea_cal(dirname, filename, titles, titles_label, ui_label):
                fea_val = {}
                sta_fea_cal(dirname, filename, fea_val, ui_label)
                fea_val_list.append(fea_val)


#dir = '/home/hao/Dropbox/Descrption-to-traffic/pcap'
#dir = '/home/hao/Documents/pcap'
#dir = '/home/hao/Documents/Ground'
ui_label_txt = 'ui_pcap_label.json' # to see whether loc or not
adlist = ['talkingdata', 'easemob', 'appx.91', 'ads', 'share.mob', 'flurry', 'umeng', 'chinacloud',
          'domob', 'scorecard', 'mobvoi', 'bmob', 'igeak', 'wirelessdeve', 'apps123', 'ixingji.com'
          ,'analytics', 'lizhi', 'ynuf.alipay.com', 'kiip', 'appspot', 'openspeech', 'tuisong', 'igexin'
          ,'wapx', 'push']
filter_ad = True
host_pcap = {}
fea_val_list = []
numeric_flag = False
vocabulary = json.load(open('train_ocsvm_vocab.json', 'r'))
#train_file = open('train_pcap.arff', 'w')
#train_file = open('train_pcap_allFeature.arff', 'w')
train_file = open('test_ui_pcap_ocsvm_all.arff', 'w')
urilist = []
distinct_uri = []
domain_list = []
get_sta_data(ui_label_txt)
train_file.close()
json.dump(host_pcap, open('pcap_host_ocsvm_test.json', 'w'))


print domain_list
print len(domain_list)

#os.popen('java weka.core.converters.CSVSaver -i test_ui_pcap_ocsvm_all.arff -o test_ui_pcap_ocsvm_all.csv')


