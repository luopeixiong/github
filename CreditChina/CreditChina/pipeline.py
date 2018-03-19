# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
#
import pymssql
import datetime
from decimal import Decimal
import decimal
import logging
from scrapy import log
import time
from pymssql import DatabaseError,ColumnsWithoutNamesError
import sys


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class sqlserver(object):
    # __conn connflag 都为true时 更换数据库连接
    __conn = True
    connflag = False
    def open_spider(self,spider):
        self.infoNums = 0
        self.updates = 0
        self.inserts = 0
        self.donones = 0
        self.errorNums = 0
        self.sql = ""
        self.tableName = ""
        self.tablekeys = []
        self.querykeys = []
        self.item = {}
        self.olditem = {}
        self.sqlFlag = True
        self.__local_account()
        self.conn_db()
        self.starttime=time.time()

    def conn_change(self):
        '''
        用于首次变更数据库,变更完生成一个全局的变量
        conn默认为Fafse,
        变更生成self.__conn变量
        '''
        if self.connflag and self.__conn:
            logger.debug('DB host is modify Begining to Change')
            # 获取conn
            self.__company_account()
            self.conn_db()
            self.__conn = False
            logger.info('%s %s' % (self.conn,self.__conn))
    
    def __local_account(self):
        #  连接本地数据库
        self.host = "10.1.18.35"
        self.db = "Haifeng.CrawlerData"
        self.user = "sa"
        self.passwd = "8927968"


    def __company_account(self):
        #  连接海峰crawler数据库
        self.delConn()
        self.host = "10.1.12.16\HFDATA"
        self.db = "Haifeng.CrawlerData"
        self.user = "luopx"
        self.passwd = "Hf.123"

    def conn_db(self):
        logger.info('START DB SERVER >>> host:%s on database %s' % (self.host,self.db))
        #  生成2个db 用于处理乱码 utf-8用于传输data给数据库
        #  cp936用于向数据库请求数据
        self.conn = pymssql.connect(
            host=self.host, database=self.db, user=self.user, password=self.passwd, charset="utf8")
        self.cursor = self.conn.cursor()
        self.conn.autocommit(True)
        self.conn1 = pymssql.connect(
            host=self.host,
            database=self.db,
            user=self.user,
            password=self.passwd,
            charset="utf8")
        self.cursor1 = self.conn1.cursor()
        self.conn1.autocommit(True)

    def delConn(self):
        self.cursor.close()
        self.conn.close()
        self.cursor1.close()
        self.conn1.close()

    def printsql(func):
        # dbeug sql语句
        def foo(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            try:
                if self.sqlFlag:
                    # logger.debug(self.sql)
                    pass
            except:
                pass
            return result

        return foo

    @printsql
    def getQueryResult(self, item, keys, wherekey, tb, isfetchall=1):
        wherekv = {}
        items = self.changeitem(item)
        for i in wherekey:
            wherekv[i] = items[i]
        wherekey = dict(wherekv)
        for i in wherekey:
            wherekey[i] = str(wherekey[i])
        q1 = ",".join(keys)
        if wherekey:
            q2 = "where " + " and ".join(
                map(lambda x: " = ".join(x) if x[1] != 'Null' else " is ".join(x),
                    wherekey.items()))
        else:
            q2 = ""
        sql = "select %s from %s %s" % (q1, self.tableName, q2)
        self.sql = sql
        try:
            self.cursor1.execute(sql)
        # 排除表名引发的错误
        except DatabaseError as e:
            log.msg(repr(e), level=log.ERROR)
        # 排除列名引发的错误
        except ColumnsWithoutNamesError as e:
            log.msg(repr(e), level=log.ERROR)
        # 重新连接数据库
        except Exception as e:
            self.conn_db()
            log.msg(repr(e), level=log.ERROR)
            # return self.getQueryResult(item, keys, wherekey, tb, isfetchall=1)
        try:
            if isfetchall is True:
                result = self.cursor1.fetchone()
            else:
                result = self.cursor1.fetchall()
            if result:
                return result
            else:
                #            print("that is none result for your query")
                return [None]
        except Exception as e:
            log.msg("sql is:%s/n reason is :%s" % (sql, e), level=log.ERROR)

    #将item 非数值 和非空字段 添加''包衣

    def changeitem2(self, item, changekey=False, changekeyToNull=[]):
        items = dict(item)
        for i in items.keys():
            if item[i] and item[i] in changekeyToNull and changekey:
                item[i] = None
            elif items[i] is False and items[i] != 0:
                items[i] = None
#        print("finshed to change item ready for check")
        return item

    def changeitem(self, item, changekey=False, changekeyToNull=[]):
        items = dict(item)
        for i in items.keys():
            if type(items[i]) is str and items[i] != "Null":
                items[i] = "'%s'" % item[i]
            elif items[i] == None or items[i] == "":
                items[i] = "Null"
            else:
                items[i] = str(items[i])
        return items

    #insert操作
    @printsql
    def insert(self, item):
        items = self.changeitem(item)
        q1 = ",".join([str(x[0])
                       for x in items.items()]) + ",AddTime,Checktime"
        q2 = ",".join(
            [str(x[1]) for x in items.items()]) + ",'" + datetime.datetime.now(
            ).strftime("%Y-%m-%d %H:%M:%S") + "','" + datetime.datetime.now(
            ).strftime("%Y-%m-%d %H:%M:%S") + "'"
        sql = "insert into %s (%s) values (%s)" % (self.tableName, q1, q2)
        self.sql = sql
        try:
            self.cursor.execute(sql)
            try:
                self.conn.commit()
            except:
                logger.debug("commit false")
                self.errorNums += 1
            self.inserts += 1
            # logger.debug("insert sucess")
        except Exception as e:
            #            print("insert fail ,%s" % e)
            log.msg("sql is:%s/n reason is :%s" % (sql, e))
            self.errorNums += 1

    #update操作
    @printsql
    def update(self, item, wherekey):
        items = self.changeitem(item)
        wherekv = {}
        for i in self.tablekeys:
            wherekv[i] = items[i]
        dictlist = list(items.items())
        keysword = ",".join(
            list(
                map(lambda x: " = ".join([str(x[0]), str(x[1])]),
                    dictlist))) + " , updatetime = '%s' , checktime = '%s'" % (
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        wherekv = "where " + " and ".join(
            map(lambda x: " = ".join(x) if x[1] != 'Null' else " is ".join(x),
                wherekv.items()))
        #        sql = "update %s set updatetime = '%s' , checktime = '%s' %s" % (self.tableName, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), wherekey)
        sql = "update %s set %s %s" % (self.tableName, keysword, wherekv)
        self.sql = sql
        try:
            self.cursor.execute(sql)
            try:
                self.conn.commit()
            except:
                logger.debug("commit false")
                self.errorNums += 1
            # logger.debug("update sucess")
            self.updates += 1
        except Exception as e:
            logger.debug("update fail ,%s"%e)
            log.msg("sql is:%s/n reason is :%s" % (sql, e),level=log.ERROR)
            self.errorNums += 1

    #无需任何操作 若需更新checktime执行该方法
    @printsql
    def donone(self, item, wherekey):
        items = self.changeitem(item)
        wherekv = {}
        for i in wherekey:
            wherekv[i] = items[i]
        wherekey = "where " + " and ".join(
            map(lambda x: " = ".join(x) if x[1] != 'Null' else " is ".join(x),
                wherekv.items()))
        sql = "update %s set checktime = '%s' %s" % (
            self.tableName,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), wherekey)
        self.sql = sql
        try:
            self.cursor.execute(sql)
            try:
                self.conn.commit()
            except:
                logger.debug("commit false")
                self.errorNums += 1
            # logger.debug("update stime sucess")
            self.donones += 1
        except Exception as e:
            logger.debug("update stime fail,%s" % e)
            log.msg("sql is:%s/n reason is :%s" % (sql, e),level=log.ERROR)
            self.errorNums += 1
            return sql


    def getid(self, item, wherekey):
        items = self.changeitem(item)
        wherekv = {}
        for i in wherekey:
            wherekv[i] = items[i]
        wherekey = "where " + " and ".join(
            map(lambda x: " = ".join(x) if x[1] != 'Null' else " is ".join(x),
                wherekv.items()))
        sql = "select id from %s %s" % (self.tableName, wherekey)
        self.sql = sql
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result[0]
        except Exception as e:
            log.msg("sql is:%s/n reason is :%s" % (sql, e),level=log.ERROR)

    @printsql
    def saveold(self, items):

        v = self.getid(items, self.tablekeys)

        for k in items.keys():
            if items[k] != self.olditem[k]:
                old = float(self.olditem[k]) if isinstance(
                    self.olditem[k], Decimal) else self.olditem[k]
                new = items[k]
                sql = "insert into AMAC.Change_List (ChangeObjectType,ChangeObjectID,ChangePropertyName,ChangeTime,BeforeContent,AfterContent) values ('%s','%s','%s','%s','%s','%s')" % (
                    self.tableName, v, k,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), old,
                    new)
                self.sql = sql
                try:
                    self.cursor.execute(sql)
                    try:
                        self.conn.commit()
                    except:
                        logger.debug("commit false")
                        self.errorNums += 1
                    logger.debug("saveold sucess")
                except Exception as e:
                    logger.debug("update stime fail,%s" % e)
                    log.msg("sql is:%s/n reason is :%s" % (sql, e),level=log.ERROR)
                    self.errorNums += 1

    def sqlquery(self, item, keys, wherekeys, tb, isfetchall=1):
        def catch(listx, listy):
            for x, y in zip(listx, listy):
                if type(x) is int or type(x) is float or type(
                        y) is float or type(y) is int:
                    try:
                        x = float(x)
                        if x != y:
                            print(x, y)
                            return False

                    except:
                        y = float(y)
                        if x != y:
                            print(x, y)
                            return False

                else:
                    if x != y:
                        try:
                            logger.debug('update %s-->%s' %(x.__str__(),y.__str__()))
                        except:
                            pass
                        return False

            return True

        itemlist = [x[1] for x in item.items()]
        keys = [x[0] for x in item.items()]
        result = self.getQueryResult(
            item, keys, wherekeys, tb, isfetchall=isfetchall)
        result = result[0] if result else None
        queryResult2 = []
        if result:
            for i in result:
                #                    print(type(i))
                if type(i) is decimal.Decimal or type(i) is float:
                    queryResult2.append(float(i))
                elif type(i) is int:
                    queryResult2.append(i)
                elif type(i) is str:
                    queryResult2.append(i)
                elif isinstance(i, datetime.datetime):
                    queryResult2.append(i.strftime("%Y-%m-%d"))
                else:
                    queryResult2.append(i)
                result = queryResult2
            if catch(queryResult2, itemlist):

                return 1  # 无需更新
            else:
                for k, v in zip(keys, queryResult2):
                    self.olditem[k] = float(v) if isinstance(v, Decimal) else v


#                    print("old",self.olditem,"new",item)
#                    print("对比",itemlist,queryResult2)

                return 2  # 需要跟新

        else:
            return 0  # 需要插入

    def dbclose(self):
        try:
            self.cursor.close()
        except:
            pass
        try:
            self.conn.close()
        except:
            pass

    def process_item(self, item, spider):
        self.infoNums += 1
        self.olditem = {}

        def main(item):

            items = self.changeitem2(item)
            error = self.sqlquery(items)
            # logger.debug("flag is :%s" %error)
            if error == 0:
                self.insert(items)
            elif error == 1:
                self.update2(items)
            elif error == 2:
                self.donone(items)

    def close_spider(self, spider):
        try:
            self.conn.commit()
        except Exception as e:
            print(e)
        self.conn.close()
        self.cursor.close()
        self.conn1.close()
        self.cursor1.close()
        logger.debug('DB is closed')

        logger.debug("爬虫结束,结束时间为%s,\n本次共采集%s条,插入%s,更新%s条,无需操作%s条,其中有%s条错误信息" %
              (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               self.infoNums, self.inserts, self.updates, self.donones,
               self.errorNums))



class Pipeline(sqlserver):
    def __init__(self):
        sqlserver.__init__(self)
        self.tb = ""
        self.tablekeys = ["manager_id"]
        self.schema = "dbo"
        self.tableName = "dbo.howbuy_manager"

    def process_item(self, item, spider):
        self.infoNums += 1
        self.olditem = {}

        def main(item):
            try:
                self.tableName = item['db']
            except KeyError as e:
                pass
            try:
                self.tablekeys = item['keys']
            except KeyError as e:
                pass
            self.connflag = item.get('conn',False)
            self.conn_change()
            item = item['result']

            items = self.changeitem2(item)
            error = self.sqlquery(item, item.keys(), self.tablekeys,
                                  self.tableName)
            # logger.debug('error %s' %error)
            # print(error)
            if error == 0:
                self.insert(items)
            elif error == 2:
                # logger.info("old:%s\nnew:%s" %(self.olditem,items))
                self.update(items, self.tablekeys)
#                self.saveold(items)
            elif error == 1:
                self.donone(items, self.tablekeys)

        main(item)

        return item


if __name__ == '__main__':
    pass
    string = 'GetItem:{:^7},SucessInto{:^7},SucessUpdate{:^7},SucessOther{:^7},Faile{:^7},Speed{:^7.1f} per sencond'.format(self.infoNums,self.inserts,self.updates,self.donones,self.errorNums,self.infoNums/(time.time()-self.starttime))
    sys.stdout.write(string + "\r")
    sys.stdout.flush()