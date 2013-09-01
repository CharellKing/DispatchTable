from xml.etree import ElementTree

class ConnConfig(object):
    def __init__(self, host = "", port = 3306, user = "webgame", passwd = "wg1q2w3e", dbnames = []):
        self.host   = host
        self.port   = int(port)
        self.user   = user
        self.passwd = passwd
        self.dbconfigs = []
        for dbname in dbnames:
            self.dbnames.append(dbname);
        
    def __repr__(self):
         str = ("host = %s port = %s user = %s passwd = %s\n" %(self.host, self.port, self.user, self.passwd))
         for dbconfig in self.dbconfigs:
             str += ('%s %s\n' %(dbconfig.dbname, dbconfig.charset))
         return str
        
    __str__ = __repr__;
    
class DbConfig(object):
    def __init__(self, dbname, charset):
        self.dbname = dbname
        self.charset = charset
        
class DispatchConfig(dict):
    def __init__(self, xml_name):
        self.xml_name = xml_name;
        
    def read_connconfig(self):
         dbconfig = ElementTree.parse(self.xml_name)
         conns = dbconfig.getiterator("connect")
         for conn in conns:
            conn_config = ConnConfig(conn.attrib["host"],
                                     conn.attrib["port"],
                                     conn.attrib["user"],
                                     conn.attrib["passwd"])
            self[conn.attrib["host"]] = conn_config
            dbs = conn.getiterator("db")

            for db in dbs:
                dbconfig = DbConfig(db.attrib["dbname"],
                                    db.attrib["charset"])
                self[conn.attrib["host"]].dbconfigs.append(dbconfig)
    
    def __repr__(self):
        str = ""
        for (ip, conn) in self.items():
            str += conn.__str__()
        return str
    
    __str__ = __repr__
    

def main(script, *args):
    dispatch_config  = DispatchConfig("dbconfig.xml")
    dispatch_config.read_connconfig()
    print dispatch_config;
    


if __name__ == '__main__':
    import sys
    main(*sys.argv)    
        
    