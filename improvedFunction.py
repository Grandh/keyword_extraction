# coding:utf-8

from commonFunction import *

# ================================= special function =================================

# ================= 封装分词功能  ====================
# input：文本 output: 分词后的词语列表
def SegText(text):
    
    # 先分词之后，寻找组合词
    textList = []
    result = pseg.cut(text)
    for word,flag in result: textList.append((word,flag)) # 获取第一次分词结果
    compoundUserdict = CompoundWord(textList) # 获取组合词后的 临时词典(后期要与专业词典结合)
    jieba.load_userdict(compoundUserdict) # 调用 临时词典
    
    # 利用jieba分词，结果带词性
    segTextList = []
    result = pseg.cut(text)
    for word,flag in result:segTextList.append((word,flag))

    return segTextList

# ================= 组合词  ====================
# 基于文本共现图的组合词算法实现
def CompoundWord(segTextList,compoundT=3):
    
    global COM_WORD_FLAG  # 全局变量：允许组合词的词性
    stopWordList = LoadWordListFromFile(r"./dictionary/compound_black_list.txt") # "./xx 的形式限于windows
    
    length = len(segTextList)
    wordDigraph = {}
    counter = 0-1
    while 1:
        
        counter += 1
        if counter >= length: break
               
        word,flag = segTextList[counter]
        if flag[0] not in COM_WORD_FLAG: continue
        if word in stopWordList: continue
        
        ## 统计组合词出现的次数
        tmp_compoundword = [word]
        while 1:
            counter += 1
            if counter >= length: break
            
            next_word,next_flag = segTextList[counter]
            if next_flag[0] not in COM_WORD_FLAG: break
            
            tmp_compoundword.append(next_word)
            
        if len(tmp_compoundword) >= 2: # 超过两个词的组合，考虑为组合词
            com = ""
            for word in tmp_compoundword: com += word
            
            if com not in wordDigraph.keys(): wordDigraph[com] = 1
            else: wordDigraph[com] += 1
            
    output = ""
    for word in wordDigraph.keys():
        if wordDigraph[word] < compoundT:  continue  # 小于组合的频率阈值则过滤
        else: output += "%s n\n" % word  # 输出到文件，服务器cenos系统中考虑\r\n结束符 
            
    output += u"%s n\n" % word
    output = output[:-1]
    
    tmp_userdict = r"./Dictionary/tmp_compoundword_dictionary.txt"
    openDictFile = open(tmp_userdict,"w")
    openDictFile.write(output.encode('utf8'))
    openDictFile.close()
    
    return tmp_userdict  # 返回词典形式，用于jieba加载（jieba.addusrdict()会覆盖原有词典文件）

# ================= 计算词语间的余弦相似度  ====================
def CosWord(word1,word2,T=0.7):
    
    # 将词语以字为单位转化为向量，进行余弦计算
    wordlist = []
    for i in range(0,len(word1)):
        if word1[i] not in wordlist:
            wordlist.append(word1[i])
    for i in range(0,len(word2)):
        if word2[i] not in wordlist:
            wordlist.append(word2[i])
            
    _vector_list = [[0]*len(wordlist),[0]*len(wordlist)]
    for i in range(0,len(word1)):
        index = wordlist.index(word1[i])
        _vector_list[0][index] = 1
    for i in range(0,len(word2)):
        index = wordlist.index(word2[i])
        _vector_list[1][index] = 1

    # 计算两词的余弦相似度
    numerator = 0
    denominator = [0,0]
    for i in range(0,len(wordlist)):
        numerator += _vector_list[0][i] * _vector_list[1][i]
        denominator[0] += _vector_list[0][i] ** 2
        denominator[1] += _vector_list[1][i] ** 2
    denominator[0] = math.sqrt(float(denominator[0]))
    denominator[1] = math.sqrt(float(denominator[1]))
        
    result = float(numerator)/(denominator[0] * denominator[1])
    
    if result>T:return True
    else:return False


# ================= 将提取的关键词以权重排序  ====================
# 输入：wordDict : 所有文本中各个词语的权重结果
# keywordNum : 输入的关键词个数
# weight ： 是否带权重输出
def ArrangeKeyword(wordDict,keywordNum,weight):
    
    # 排序
    dict = sorted(wordDict.items(),key = lambda item:item[1],reverse = True)
    
    #for word,weight in dict:
    #    print word,weight
        
    resultList = []
    for word,score in dict:
        print word,score
        # 在已有的关键词列表中，计算两个关键词的余弦相似度
        # 相似程度超过阈值则合并
        there_have_simword = False
        for old_word in resultList:
            if CosWord(word,old_word):
                there_have_simword = True
                if len(word) >= len(old_word):
                    i = resultList.index(old_word)
                    resultList[i] = word
                    break
        # there_have_simword 关键词列表中是否存在相似的词语
        if there_have_simword: continue
        resultList.append(word)
        if len(resultList) > keywordNum: break
    
    # 输出最后的结果，以list形式返回
    outputResult = ""
    for keyword in resultList:
        if not weight: outputResult += keyword + "\n"
        else:          outputResult += "%s %.5f\n" % (keyword,wordDict[keyword])
    outputResult = outputResult[:-1]
    
    return outputResult
