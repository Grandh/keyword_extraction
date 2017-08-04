# coding:utf-8

# 全局参数
global ENDMARK                                        # 句子结束标记，用于标题检测与TextRank的句子分隔
global COM_WORD_FLAG                                  # 组合词词性过滤
global FILTER_NOUN_FLAG,FILTER_VERB_FLAG,FILTER_FLAG  # 文本分词后的词性筛选

ENDMARK = [u'。',u'.',u',',u',',u'\n']
FILTER_NOUN_FLAG = [u'n',u'l',u'j',u't']
FILTER_VERB_FLAG = [u'v',u'f']
FILTER_FLAG = FILTER_NOUN_FLAG + FILTER_VERB_FLAG
COM_WORD_FLAG = [u'n',u'v',u'a',u'b',u'j',u'l']
blackFlag = [u'ns']               # 限制人名作为关键词输出