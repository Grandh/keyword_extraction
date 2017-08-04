# coding:utf-8

import os,re,math,chardet,jieba
import jieba.posseg as pseg

from parameter import *
from MySQLInterface import *

# ================================= common function =================================

# 从文件中读取词语列表，存于数组中返回
# 文件中的数据格式： 每词一行 (适用该格式的有：主题词停用表、关键词黑名单等)
def LoadWordListFromFile(file_path):
    
    if not os.path.exists(file_path): 
        print "commonFunction erro : no such file"
        return []

    # 读取文件数据
    stopFile = open(file_path,"r")
    List = stopFile.read()
    stopFile.close()

    # 对文件数据进行编码检测，并转为unicode编码
    tmpList = List
    try:
        cc = chardet.detect(List)['encoding']
        try: List = unicode(List,cc)
        except Exception,e:  List = tmpList
    except Exception,e: pass
    
    # 将文件数据以回车分隔，读出存于WordList列表中
    WordList = []
    stopwordList = List.split(u"\n")
    for stopword in stopwordList:
        if stopword not in WordList:
            WordList.append(stopword)
            
    return WordList

# 从MySQL数据中读取词语列表，存于数组中返回
def LoadWordListFromMySQL(host="127.0.0.1",\
                          user="root",password="huang",\
                          databaseName="dictionary",tableName="black_keyword"):
    
    mysql = MySQLInterface(host,user,password,databaseName)
    WordList = mysql.GetWordFromMySQL(tableName)
    mysql.close()
    
    return WordList

# 计算词语的特征参数
def GetWordPara(segTextList,titleValue = 3.00,nounValue = 1.200,verbValue = 0.800):

    TF_Dict = {}

    # 文本形式是首句标题，其下正文，进行位置与词性判断
    cc = True
    value_Dict = {}
    global COMWORDFLAG,FILTER_NOUN_FLAG,FILTER_VERB_FLA
    for word,flag in segTextList:

        if cc:
            if word == u"\n": cc = False
            else: value_Dict[word] = titleValue
                
        if flag[0] in FILTER_NOUN_FLAG: 
            if word in value_Dict.keys():
                if value_Dict[word] < nounValue:
                    value_Dict[word] = nounValue
            else: value_Dict[word] = nounValue

        elif flag[0] in FILTER_VERB_FLAG: 
            if word not in value_Dict.keys():
                value_Dict[word]=float(1.0)
        else:continue
        
        if word not in TF_Dict.keys():TF_Dict[word] = 1
        else:TF_Dict[word] += 1
    
    # 计算词频参数
    for word in TF_Dict.keys():
        value = TF_Dict[word]
        TF_Dict[word] = float(value)/(value+1)
        
    # 相乘得到最后的权重结果
    wordValue = {}
    for word in TF_Dict.keys():
        wordValue[word] = TF_Dict[word] * value_Dict[word]
    return wordValue

    