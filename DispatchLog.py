from xml.etree import ElementTree
from xml.etree.ElementTree import Element

class SqlLogConfig(object):
    def __init__(self, sql, error_tag, error_msg):
        self.sql = sql
        self.error_tag = error_tag
        self.error_msg = error_msg
    
    def __repr__(self):
        return "%s:[%s]%s" %(self.sql, self.error_tag, self.error_msg)
    
    __str__ = __repr__
    
    def GetTag(self):
        return {"sql":self.sql, "error_tag":self.error_tag, "error_msg":self.error_msg}
        
class FileLogConfig(dict):
    def __init__(self, filename, timestamp, error_tag, error_msg, sqllogconfigs = []):
        self.filename   = filename
        self.timestamp  = float(timestamp)
        self.error_tag  = error_tag
        self.error_msg  = error_msg
        for sqllogconfig in sqllogconfigs:
            self[sqllogconfig.sql] = sqllogconfig
         
    
    def __repr__(self):
        return "%s:[%s]%s" %(self.filename, self.error_tag, self.error_msg)
    
    __str__ = __repr__
    
    def GetTag(self):
        return {"filename":self.filename, "time":str(self.timestamp), "error_tag":self.error_tag, "error_msg":self.error_msg}
    
    
class DbLogConfig(dict):
    def __init__(self, dbname, error_tag, error_msg, filelogconfigs = []):
        self.dbname = dbname
        self.error_tag = error_tag
        self.error_msg = error_msg
        for filelogconfig in filelogconfigs:
            self[filelogconfig[0]] = filelogconfig
    def __repr__(self):
        return ("%s:[%s] %s" %(self.dbname, self.error_tag, self.error_msg))
    
    __str__ = __repr__
    
    def GetTag(self):
        return {"dbname":self.dbname, "error_tag":self.error_tag, "error_msg":self.error_msg}
    
class HostLogConfig(dict):
    def __init__(self, host, error_tag, error_msg, dblogconfigs = []):
        self.host = host
        self.error_tag = error_tag
        self.error_msg = error_msg
        for dblogconfig in dblogconfigs:
            self[dblogconfig.db] = dblogconfig
    
    def __repr__(self):
        return ("%s:[%s] %s" %(self.host, self.error_tag, self.error_msg))
    
    __str__ = __repr__
    
    def GetTag(self):
        return {"host":self.host, "error_tag":self.error_tag, "error_msg":self.error_msg}
    
       
class DispatchLog(dict):
    def __init__(self, log_name):
        self.log_name = log_name
        
    def read_log(self):
        try:
            dispatchlog = ElementTree.parse(self.log_name)
        except Exception, e:
            return 
          
        #hostlog
        hostlogs = dispatchlog.getiterator("hostlog")
        for hostlog in hostlogs:
            hostlogconfig = HostLogConfig(hostlog.attrib["host"],
                                          hostlog.attrib["error_tag"],
                                          hostlog.attrib["error_msg"],)
            self[hostlogconfig.host] = hostlogconfig
            
            #dblog
            dblogs = hostlog.getiterator("dblog")
            for dblog in dblogs:
                dblogconfig = DbLogConfig(dblog.attrib["dbname"],
                                          dblog.attrib["error_tag"],
                                          dblog.attrib["error_msg"],)
                self[hostlogconfig.host][dblogconfig.dbname] = dblogconfig
                
                #filelog
                filelogs = dblog.getiterator("filelog")
                for filelog in filelogs:
                    filelogconfig = FileLogConfig(filelog.attrib["filename"],
                                                  filelog.attrib["time"],
                                                  filelog.attrib["error_tag"],
                                                  filelog.attrib["error_msg"])
                    self[hostlogconfig.host][dblogconfig.dbname][filelogconfig.filename] = filelogconfig
                    sqllogs = filelog.getiterator("sqllog")
                    for sqllog in sqllogs:
                        sqllogconfig = SqlLogConfig(sqllog.attrib["sql"],
                                                    sqllog.attrib["error_tag"],
                                                    sqllog.attrib["error_msg"])
                        self[hostlogconfig.host][dblogconfig.dbname][filelogconfig.filename][sqllogconfig.sql] = sqllogconfig
                    

    def write_log(self):
        root = Element("dispatchlog")
        for (host, hostlogconfig) in self.items():
            firstchild = Element('hostlog', hostlogconfig.GetTag())
            for(db, dblogconfig) in  hostlogconfig.items():
                secondchild = Element('dblog', dblogconfig.GetTag())
                for(file, filelogconfig) in dblogconfig.items():
                    thirdchild = Element('filelog', filelogconfig.GetTag())
                    for (sql, sqllogconfig) in filelogconfig.items():
                        fourthchild = Element('sqllog', sqllogconfig.GetTag())
                        thirdchild.append(fourthchild)
                    secondchild.append(thirdchild)
                firstchild.append(secondchild)
            root.append(firstchild)
        file = open(self.log_name, 'w')
        ElementTree.ElementTree(root).write(file)
        file.close() 
    
    def __repr__(self):
        str = ""
        for (host, host_config) in self.items():
            for (dbname, db_config) in host_config.items():
                for (logname, log_config) in db_config.items():
                    str += (host + "|" + dbname + "|" + logname + "|" + log_config.__str__() + "\n")
        return str
    
    __str__ = __repr__

def main(script, *args):
    log_dispatch = DispatchLog("dispatchlog.xml")
    log_dispatch.read_log();
    print log_dispatch;
    log_dispatch.write_log();


if __name__ == '__main__':
    import sys
    main(*sys.argv)               
                 
        
        
        
        