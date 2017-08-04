# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import MySQLdb

class MySQLInterface:
    
    # ======================================================== 初始化函数
    # host: 目标数据库的ip user/password 用户名/密码
    # dbName: 选择的数据库（）
    def __init__(self,host,user,password,dbName):
        
        self.myDatabase = MySQLdb.Connect(db=dbName,\
                        host=host,user=user,passwd=password)
        self.myDatabase.set_character_set("utf8")
        self.cusor = self.myDatabase.cursor()
    
    ## 封装执行数据库insert/update指令功能函数
    def executeCommand(self,command):
        try:
            self.cusor.execute(command)
            self.myDatabase.commit()
        except Exception,e:
            print e
            self.myDatabase.rollback()
            return False
        return True
    
    ## ==================================================
    ## 封装执行数据库select等功能操作
    def queryCommand(self,command):
        try:
            self.cusor.execute(command)
            result = self.cusor.fetchall()
        except Exception,e:
            print e
            return False
        return result
    
    # ================= 将词语插入数据库 ==============
    # input:
    # datasTableName : 要操作的表名
    # word : 要插入的词语
    def InsertWordToMySQL(self,dataTableName,word):
        
        command = u'insert into %s(word) value("%s");' % (dataTableName,word)
        return self.executeCommand(command)
    
    # ================= 获取数据库的词语  ==============
    # input:
    # datasTableName : 要操作的表名
    def GetWordFromMySQL(self,dataTableName):
        
        command = u'select word from %s;' % (dataTableName)
        result = self.queryCommand(command)
        if not result : return False
        output = []
        for tup in result: 
            for id,w in tup: 
                output.append(w.encode("utf-8")) #此处可能存在编码问题？
        return output
                
    # ================= 将词语从数据库删除 ==============
    # input:
    # datasTableName : 要操作的表名
    # word : 要删除的词语
    def DelWordFromMySQL(self,dataTableName,word):
        
        command = u'delete from %s where word="%s";' % (dataTableName,word)
        return self.executeCommand(command)
    
    # ================= 清空数据库中的表 ==============
    # input:
    # datasTableName : 要操作的表名
    # word : 要删除的词语
    def DropTable(self,dataTableName):
        
        command = u'drop table %s' % (dataTableName)
        return self.executeCommand(command)
    
    # ================= 关闭数据库 ==============
    def close(self):
        self.cusor.close()
        self.myDatabase.close()
        