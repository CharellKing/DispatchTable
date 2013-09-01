#!/usr/bin/python
#-*-coding:utf-8-*-

import MySQLdb
import time
import os
from DispatchConfig import *
from DispatchLog    import *
from SearchSql      import *

"""
    DispatchTable：派发sql语句到各个数据库
            使用DispatchConfig来解析dbconfig.xml,读取派发到数据库的信息
            使用DispatchLog来记录派发表过程中的情况
            使用SearchSql来搜寻当前目录下面的sql文件
"""
class DispatchTable(object):
    """
    Description:
                    初始化类
    Argument:
        xmlname: 派发目的地个个数据库的信息xml配置文件
        logname: 派发过程中日志记录的配置文件名称
        sqldir:  搜寻的sql的目录
    Return:
                    空
    """
    def __init__(self, xmlname, logname, sqldir):
        self.logname = logname
        self.dispatch_config = DispatchConfig(xmlname)
        self.dispatch_log = DispatchLog(logname)
        self.search_sql = SearchSql(sqldir)
        
        self.HOST_ERROR    = 2003
        self.PASS_ERROR    = 1045
        self.DB_ERROR      = 1049
        self.CHARSET_ERROR = 2019
    
    """
    Description:
                    解释信息
    Argument:
                    空
    Return:
                    空
    """    
    def __repr__(self):
        str = "dispatch_config:\n"
        str += self.dispatch_config.__str__()
        str += "dispatch_log:\n"
        str += self.dispatch_log.__str__()
        str += "search_sql:\n"
        str += self.search_sql.__str__()
        return str;
    
    __str__ = __repr__
    
    """
    Description:
                        加载数据:加载数据库信息、加载之前生成的派发生成日志、寻找当前目录下的sql文件
    Argument:
                        空
    Return:
                        空
    """
    def load(self):
        self.dispatch_config.read_connconfig()
        self.dispatch_log.read_log()
        self.search_sql.search_sql()
    
    """
    Description:
                        判断当前的sqlfile是否需要派发，比较上次派发日志的派发时间和当前文件最后修改时间的大小，如果大了，就表示不需要派发，小了，需要派发
    Argument:
        host:    主机IP
        dbname:  数据库名称
        sqlfile: 文件名称
    Return:
        True-need to dispatch, Fasle-need't to dispatch
    """     
    def file_is_dispatch(self, host, dbname, sqlfile):
        try:
            if (self.dispatch_log[host][dbname][sqlfile.filename].timestamp < sqlfile.last_modify_time):
                return True
            else:
                return False
        except KeyError:
                return True
    
    def sql_is_dispatch(self, host, dbname, filename, sql):
        try:
            if sql in self.dispatch_log[host][dbname][filename].keys():
                return False
            else:
                return True
        except KeyError:
                return True
    """
    Description:
                        派发表到各个数据库
    Argument:
                        空
    Return:
        
    """  
    
    def dispatch(self):
        #新建DispatchLog用来记录当前产生的日志
        dispatchlog = DispatchLog(self.logname)
        
        for (host, connconfig) in self.dispatch_config.items():                                 #遍历HOST
            hostlogconfig = HostLogConfig(host, "SUCCESS", "")                                  #初始化HOST日志
            for dbconfig in connconfig.dbconfigs:                                               #遍历HOST里面的DB
                dblogconfig = DbLogConfig(dbconfig.dbname, "SUCCESS", "")                       #初始化DB日志
                if (self.is_connect(host, dbconfig.dbname)):                                    #是否需要连接数据库
                    result = self.connect(connconfig, dbconfig)                                 #连接数据库
                    if ("SUCCESS" == result[1]):                                                #如果连接成功
                        cur = result[0].cursor()                                                #获取数据库游标
                        cur.connection.autocommit(True)                                         #设置游标为主动提交
                        for (filename, sqlfile) in self.search_sql.items():                     #遍历文件
                            filelogconfig = FileLogConfig(filename, time.time(), "SUCCESS", "") #初始化文件日志
                            if (self.file_is_dispatch(host, dbconfig.dbname, sqlfile)):              #该文件是否需要派发
                                for sql in sqlfile.sqls:
                                    sqllogconfig = SqlLogConfig(sql, "SUCCESS", "")
                                    if (self.sql_is_dispatch(host, dbconfig.dbname, filename, sql)):
                                        res = self.executesql(cur, sql);
                                        if ("ERROR" == res[0]):                                         #执行SQL语句失败
                                            #修改文件日志信息
                                            sqllogconfig.error_tag = "ERROR"
                                            sqllogconfig.error_msg = ("Mysql Error: %d %s" %(res[1], res[2]))
                                    else:
                                        #不需要派发的错误sql，需要保存到新的日志中
                                        sqllogconfig = self.dispatch_log[host][dbconfig.dbname][sqlfile.filename][sql]
                                        #即使不需要派发sql，如果文件有误，还是需要显示的
                                    if (sqllogconfig.error_tag == "ERROR"):
                                        filelogconfig.error_tag = sqllogconfig.error_tag
                                        filelogconfig.error_msg = sqllogconfig.error_msg
                                        print "host:%s dbname:%s filename:%s [%s] %s\n" %(host, dbconfig.dbname, filename, sqllogconfig.error_tag, sqllogconfig.error_msg)
                                    filelogconfig[sql] = sqllogconfig
                                if (filelogconfig.error_tag == "SUCCESS"):
                                    print "host:%s dbname:%s filename:%s [%s] %s\n" %(host, dbconfig.dbname, filename, filelogconfig.error_tag, filelogconfig.error_msg)
                            else:
                                #不需要派发的错误文件，需要保存到新的日志中
                                filelogconfig = self.dispatch_log[host][dbconfig.dbname][filename]        
                                if ("ERROR" == filelogconfig.error_tag):
                                    print "host:%s dbname:%s %s\n" %(host, dbconfig.dbname, filelogconfig.__str__())
                            #保存FILE日志到上一级DB日志
                            dblogconfig[filelogconfig.filename] = filelogconfig
                        cur.close()             #关闭游标     
                        result[0].close()       #关闭数据库连接
                    else:
                        if (result[2] == self.HOST_ERROR or result[2] == self.PASS_ERROR):              #连接错误
                            hostlogconfig.error_tag = "ERROR"
                            hostlogconfig.error_msg = "Mysql Error: (%d) %s" %(result[2], result[3])
                            print hostlogconfig
                            break;
                        elif (result[2] == self.DB_ERROR or result[2] == self.CHARSET_ERROR):           #DB错误
                            dblogconfig.error_tag = "ERROR"
                            dblogconfig.error_msg = "Mysql Error: (%d) %s" %(result[2], result[3])
                            print "host:%s %s\n" %(host, dblogconfig.__str__())
                else:
                    #原有日志中的连接有错误，需要更新到最新的日志中来
                    if ("ERROR" == self.dispatch_log[host].error_tag):                              
                        hostlogconfig.error_tag = self.dispatch_log[host].error_tag
                        hostlogconfig.error_msg = self.dispatch_log[host].error_msg
                        print hostlogconfig
                        break;
                    #原有数据库信息有错误，需要更新到最新的日志中来
                    elif ("ERROR" == self.dispatch_log[host][dbconfig.dbname].error_tag):
                        dblogconfig.error_tag = self.dispatch_log[host][dbconfig.dbname].error_tag
                        dblogconfig.error_msg = self.dispatch_log[host][dbconfig.dbname].error_msg
                        print "host:%s %s\n" %(host, dblogconfig.__str__())
                #保存DB日志到上一级的HOST日志
                hostlogconfig[dbconfig.dbname] = dblogconfig
            #保存HOST日志到上一级的Dispatch日志
            dispatchlog[host] = hostlogconfig
        #写日志
        dispatchlog.write_log()   
       
    """
    Description:
        current connection is needed; if last time's log appear error, return True, or return False
    Agument:
        host:主机名称
        dbname:数据库名称
    Return:
        if last time's log appear error, return True, or return False
    """
    def is_connect(self, host, dbname):
        try:
            if ("ERROR" == self.dispatch_log[host].error_tag or "ERROR" == self.dispatch_log[host][dbname].error_tag):
                return False
            else:
                return True
        except KeyError:
                return True
    
    """
    """
    def connect(self, connconfig, dbconfig):
        try:
            conn=MySQLdb.connect(host   =   connconfig.host,
                                 user   =   connconfig.user,
                                 passwd =   connconfig.passwd,
                                 db     =   dbconfig.dbname,
                                 port   =   connconfig.port,
                                 charset=   dbconfig.charset)
            return [conn, "SUCCESS", 0, ""]
        except MySQLdb.Error,e:
            return [None, "ERROR", e.args[0], e.args[1]]
            
    def executesql(self, cur, sql):
        try:
            cur.execute(sql);
            return ["SUCCESS", 0, ""]
        except MySQLdb.Error,e:
            return ["ERROR", e.args[0], e.args[1]]                 

"""
Description:
            派发表
Agument:
    dbconfigxml:        数据库配置表
    dispatchlogxml:    派发SQL语句的配置
    sqldir:            sql目录
Return:
    None
"""
def SendTable(dbconfigxml, dispatchlogxml, sqldir):
    dispatch_table  = DispatchTable(dbconfigxml, dispatchlogxml, sqldir)
    dispatch_table.load()
    dispatch_table.dispatch()

"""
Description:
            删除当前目录下面的sql文件
Agument:
    sqldir:            sql目录
Return:
    None
"""
def RemoveSql(sqldir):
    filenames = os.listdir(sqldir)
    for filename in filenames:
        if fnmatch.fnmatch(filename, '*.sql'):
            filepath = os.path.join(sqldir, filename)
            os.remove(filepath)
            print "remove %s success!\n" %filename
        
def Cmd(type, dbconfigxml, dispatchlogxml, sqldir):
    try:
        cmds = {'d':lambda:SendTable(dbconfigxml, dispatchlogxml, sqldir),
                'r':lambda:RemoveSql(sqldir),}
        cmds[type]()
    except KeyError:
        return 
    
def InputCmd():
    print """=============help============
d-dispatch sql
r-remove current directory's sql file
e-exit
============================"""
    return raw_input().strip().lower()

def main(script, *args):
    dbconfigxml     =       "dbconfig.xml"
    dispatchlogxml  =       "dispatchlog.xml"
    sqldir          =       "."
    str = InputCmd()
    while ("e" != str):
        Cmd(str, dbconfigxml, dispatchlogxml, sqldir)
        str = InputCmd()
    
if __name__ == '__main__':
    import sys
    main(*sys.argv) 