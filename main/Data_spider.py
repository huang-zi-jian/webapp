import requests
import re
import random
import jieba
from jieba import analyse
import csv
import wordcloud
from PIL import Image

# import a as b的意思是给引入的包a取一个别名为b
import numpy as np
from bs4 import BeautifulSoup

find_link = re.compile(r'<a data-promid=".*?" href="(https://www.liepin.com/job/.*?shtml)" target="_blank">', re.S)
# (?:内容部分)，表示括号中的内容部分充当匹配条件，但是不作为匹配的输出
finddata = re.compile(r'<div class="content content-word">.*(?:任职|岗位)?(?:要求|资格|基本需求)(.*?)</div>', re.S)


# 提取待爬取数据链接
def getData_link(city, keyword):
    dict_city = {'1': '010', '2': '020', '3': '050020', '4': '050090', '5': '070020', '6': '170020'}
    city_number = dict_city[city]

    linklist_all = []
    # 发起访问请求

    user_Agent = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)'
    ]

    for temp in range(0, 10):

        url = "https://www.liepin.com/zhaopin/?compkind=&dqs=" + city_number + "&key=" + keyword + "&cuPage=" + str(temp)

        reponse = ''
        try:
            reponse = requests.get(url, headers={"User-Agent": random.choice(user_Agent)}, timeout=2)
            # reponse.text是str字符串类型的数据
            # print(reponse.text)

        except requests.ConnectionError as e:
            if hasattr(e, "code"):
                print(e.code)

        soup = BeautifulSoup(reponse.text, "html.parser")
        data_list = soup.find_all("h3")


        linklist = []
        for temp in data_list:

            temp = str(temp)
            # print(temp)
            link = re.findall(find_link, temp)
            if len(link) != 0:
                link = link[0]
                linklist.append(link)

        linklist_all.append(linklist)

    return linklist_all


# 获取任职需求文字信息，传入城市和关键字作为参数
def getData(city, keyword):
    linklist_all = getData_link(city, keyword)

    user_Agent = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)'
    ]

    require_data = []
    for linklist in linklist_all:

        for address in linklist:
            print(address)  #打印网址

            reponse = ''
            try:
                reponse = requests.get(address, headers={"User-Agent": random.choice(user_Agent)}, timeout=2)
                # time.sleep(0.1)

            except requests.ConnectionError as e:
                if hasattr(e, "code"):
                    print(e.code)

            soup = BeautifulSoup(reponse.text, "html.parser")

            datalist = soup.find_all("div", class_="content content-word")

            for temp in datalist:

                temp = str(temp)
                data = re.findall(finddata, temp)
                if len(data) != 0:
                    data = re.findall(finddata, temp)[0]
                    require_data.append(data)

    return require_data


# 存储文字信息数据
def saveData(datapath, datalist):
    # print(datalist)
    # print(len(datalist))

    with open(datapath, "w", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        for temp in datalist:
            inform = []
            inform.append(temp)
            writer.writerow(inform)


def analyse_data(datapath, pic_name):
    """
    this is the analyse function which can help to divide the sentences
    :param datapath: the path of .csv  means the data file
    :param tag: the pic created name
    :return: none
    """
    file = open(datapath, encoding="UTF-8")
    jieba.set_dictionary('../addwords.txt')
    analyse.set_stop_words('../stopwords.txt')

    txt = file.read()
    tfidf = analyse.extract_tags

    txt_list1 = jieba.lcut(txt, cut_all=False, HMM=True)
    txt_list2 = tfidf(txt, topK=100, allowPOS=('n', 'vn', 'v', 'a', 'd', 'vd', 'un'))
    file.close()
    txt_list = list(set(txt_list1).intersection(txt_list2))

    return generate_word_cloud(txt_list, pic_name)


def generate_word_cloud(txt_list, pic_name):
    w_number = len(txt_list)
    # 为词云图设置形状
    if w_number < 60:
        path = '../static/word_cloud_pic/star.png'
    elif w_number < 100:
        path = r'../static/word_cloud_pic/cloud.png'
    else:
        path = r'../static/word_cloud_pic/heart_1.png'

    background = Image.open(path)
    graph = np.array(background)

    word_cloud = wordcloud.WordCloud(
        width=1000,
        height=700,
        background_color="white",
        font_path='msyh.ttc',  # attention, this path is changeable
        scale=15,
        mask=graph,
        stopwords=set(wordcloud.STOPWORDS)
    )
    string = " ".join(txt_list)
    word_cloud.generate(string)
    filename = 'wordclouds_res/' + pic_name + ".png"
    word_cloud.to_file(filename)
    return filename


if __name__ == '__main__':
    saveData("require_data.csv", getData('1','数据分析'))
    analyse_data("require_data.csv",'1_数据分析')