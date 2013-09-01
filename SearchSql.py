#!/usr/bin/python
#-*-coding:utf-8-*-
import os
import fnmatch
import time
import re

"""
    SqlFile-sql          查询SQL语句
    filename:            文件名称
    last_modify_time:    文件最后修改时间
    sqls:                文件里面包含的SQL语句
"""   
class SqlFile(object):
    def __init__(self, filename, last_modify_time, sqls = []):
        self.filename = filename;
        self.last_modify_time = float(last_modify_time);
        self.sqls = []
        for sql in sqls:
            sql = str.strip(sql)
            if (len(sql) > 0):
                sql =sql.replace('\n',' ')
                self.sqls.append(sql)
    
    def __repr__(self):
        str = 'filename = %s last_modify_time = %f size = %d\n' %(self.filename, self.last_modify_time, self.sqls.__len__())
        for sql in self.sqls:
            str += sql + "\n"
        return str
    
    __str__ = __repr__
    

        
class SearchSql(dict):
    def __init__(self, dir):
        self.dir = dir
    
    def search_sql(self):
        filenames = os.listdir(self.dir)
        for filename in filenames:
            if fnmatch.fnmatch(filename, '*.sql'):
                filepath = os.path.join(self.dir, filename)
                filemt = os.stat(filepath).st_mtime
                file = open(filepath, "r");
                line = file.read()
                line = self.remove_comment(line)
                sqls = line.split(';')
                self[filename] = SqlFile(filename, filemt, sqls)
    
    def __repr__(self):
        str = ""
        for (filename, sqlfile) in self.items():
            str += sqlfile.__str__()
        return str
    
    __str__ = __repr__
    
    def remove_comment(self, str):
        #删除/*...*/, #....., --.....
        rule = "(\/\*(\s|.)*?\*\/)|(\#.*)|(\-\-.*)"
        regex = re.compile(rule)
        return regex.sub("",str)
        
    
def main(script, *args):
    search_sql = SearchSql('.')
    search_sql.search_sql()
    print search_sql;


if __name__ == '__main__':
    import sys
    main(*sys.argv) 
                