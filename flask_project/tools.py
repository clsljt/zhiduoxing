from collections import Counter
import jieba
import numpy as np
import pymysql


school_dict = {1:"勤信荣誉学院", 2:"计算机学院", 3:"管理科学与工程学院", 4:"公共管理与传媒学院", 5:"商学院", 6:"自动化学院", 7:"机械学院", 8:"其他学院或部门"}

def get_info_data():
    res_all = {}
    db = pymysql.connect(host='localhost',
                        user='root',
                        password='123456',
                        database='basedata')
    cursor = db.cursor()

    ## 学院饼图数据
    cursor.execute("SELECT school FROM users;")
    res = Counter([i[0] for i in cursor.fetchall()])
    res_school = {}
    for k,v in res.items():
        res_school[school_dict[k]] = v
    res_all["school"] = res_school

    ## 人流量数据
    res_all["num"] = np.random.uniform(50, 600, 10)

    ## 词云
    cursor.execute("SELECT chat FROM chatlist;")
    info = cursor.fetchall()
    text = ''.join([i[0] for i in info])
    with open("./stopwords.txt",encoding='utf-8')as s:
        content1=s.read()
    stop_words=content1.split()

    seg_list = jieba.cut(text)
    filtered_words = [word for word in seg_list if word not in stop_words]
    word_counts = Counter(filtered_words)

    if len(word_counts) < 100:
        res1 = dict(word_counts)
    else:
        a1 = sorted(word_counts.items(),key = lambda x:x[1],reverse = True)
        res1 ={}
        for i in a1[:100]:
            res1[i[0]] = i[1]

    res_all["cloud"] = res1

    return res_all

    
    






