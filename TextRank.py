# coding:utf8

import networkx as nx
import numpy as np
import chardet

from commonFunction import *
from improvedFunction import *
import parameter

# ================ 封装关键词提取接口 =================
# 输入：
# JSON形式的python字典查询
# 'text':      输入的文本
# 'keywordNum':输入的关键词数量
# 'weight':    是否输出权重
def KeywordExtraction(input):
    
    keywordResult = ""
    if not input['text']: return False
    keywordResult = ImproveTextRank(text = input['text'],\
                                    keywordNum = input['keywordNum'],\
                                    weight = input['weight'])
    return keywordResult

# ================ 辅助句段间的词语列表生成 ==================
def combine(word_list,windows = 2):
    
    if windows < 2: windows = 2
    for x in xrange(1,windows):
        if x >= len(word_list):break
        word_list2 = word_list[x:]
        res = zip(word_list,word_list2)
        for r in res: yield r
# ======================= 改进的TextRank算法接口 ============================
# 输入:
# text:文本（必须输入）
# keywordNum : 返回的关键词个数 （默认为5）
# windows : TextRank分析的词共现窗口数量 （默认为2）
# keyword_black_list ： 加载的停用词表文件 （路径，默认为执行路径下的dictionary文件夹中的keyword_black_list.txt）
def ImproveTextRank(text,keywordNum = 5,weight = False,windows = 2,keyword_black_list = r"./Dictionary/keyword_black_list.txt"):

    segResult = SegText(text)

    vertex_source = []
    wordlist = []

    # 加载过滤词典与过滤词性列表，并对分词结果进行过滤
    stopWordList = LoadWordListFromFile(keyword_black_list)
    global ENDMARK,FILTER_FLAG
    
    # 将文本以句的形式分隔
    for word,flag in segResult:
        if word in ENDMARK:
            vertex_source.append(wordlist)
            wordlist = []
        if flag[0] not in FILTER_FLAG: continue
        elif word in stopWordList: continue
        wordlist.append(word)
    
    # 通过词语间的窗口共现建立文本的词汇链
    word_index = {}
    index_word = {}
    words_number = 0
    for word_list in vertex_source:
        for word in word_list:
            if word not in word_index:
                word_index[word] = words_number
                index_word[words_number] = word
                words_number += 1
                
    # 创建一个行列大小为文本总词语数的零矩阵
    graph = np.zeros((words_number,words_number)) 
    # 通过窗口共现关系，建立词共现矩阵
    for word_list in vertex_source:
        for w1,w2 in combine(word_list, windows):
            if w1 in word_list and w2 in word_list:
                index1 = word_index[w1]
                index2 = word_index[w2]
                graph[index1][index2] = 1.0
                graph[index2][index2] = 1.0
                
    # 运用pagerank 的图计算进行收敛
    nx_graph = nx.from_numpy_matrix(graph) #图计算
    
    # 得到文本中词语的分布权重
    scores = nx.pagerank(nx_graph, **{'alpha': 0.85,}) # set the para is 0.85
    # 得到文本中词语的词频与位置权重
    TF_Value = GetWordPara(segResult).copy() 
    
    # 计算文本中词语的总权重
    wordDict = {}
    for index in scores.keys():
        word = index_word[index]  
        if word in TF_Value.keys():
            wordDict[word]=scores[index]*TF_Value[word]

    # 得到权重最高的keywordNum个关键词,以列表形式返回
    resultList = ArrangeKeyword(wordDict,keywordNum,weight)
    return resultList
    
