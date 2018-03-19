# -*- coding:utf-8 -*-

'''
Models
'''

from datetime import datetime
import re
import numbers
from decimal import Decimal
from hashlib import md5
import time
import logging 
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

NUMBER_COMP = re.compile('[^0-9\.]').sub

class _BaseField(object):
    default = None

    def __call__(self, func:callable):
        return func(self.value)

    def __bool__(self):
        return str(self) != 'null'

    def __str__(self):
        return '%r' % self

    @property
    def con_str(self):
        return ' = ' if bool(self) else ' is '

    def sql_equal(self, name):
        if self.key:
            return '%s %s %s' % (name,self.con_str,self)
        else:
            return ''

    def set_columns(self, name):
        return '%s = %s' % (name, self)

    def length_str(self):
        return ''

    @property
    def default_set(self):
        if self.default is None:
            return 'NULL'
        else:
            return 'NULL DEFAULT %r' % self.default 

    def create_str(self, name):
        return '\n[%s] %s%s %s' % (name, self.cloumn_str(), self.length_str(),self.default_set)


class _VarCharField(_BaseField):
    def __init__(self, value:str or None, max_length:int=255,key=False,NullList=[],default:str or None=None):
        self.value = value
        self.max_length = max_length
        self.key=key
        self.default = default

    def __repr__(self):
        if self.value is None:
            return 'null'
        else:
            return '%r' % str(self.value).replace('\'','"')[:self.max_length]

    def cloumn_str(self):
        return 'nvarchar'

    def length_str(self):
        return '(%s)' % self.max_length

class _DecimalField(_BaseField):
    
    def __init__(self, value:str or None, max_length:int=25,float_length=3,key=False,NullList=(),default:numbers.Integral=None):
        self.value = value
        self.max_length = max_length
        self.float_length = float_length
        self.key=key
        self.default = default

    def cloumn_str(self):
        return 'decimal'

    def length_str(self):
        return '(%s,%s)' % (self.max_length,self.float_length)

    def __repr__(self):
        if self.value is 'null':
            return 'null'
        else:
            return '%s' % self.re_compile

    @property
    def re_compile(self):
        if self.value:
            result =  NUMBER_COMP('',self.value)
            return Decimal(result) if re.compile('^\d+(?:.\d+)\d$').match(result) else None

class _Float(_DecimalField):
    def __init__(self, value:str or None, float_length=53, key=False, NullList=(),default=None):
        self.value = '%s' % value if value is not None else 'null'
        self.float_length = float_length
        self.key=key
        self.default = default

    def cloumn_str(self):
        return 'float'

    def length_str(self):
        return '(%s)' % self.float_length

    def __repr__(self):
        if self.value is 'null':
            return 'null'
        else:
            return '%.3f'.format(self.float_length) % self.re_compile

class _DateTime(_BaseField):
    def __init__(self, value:str or None, key=False, NullList=()):
        self.vaule=value

    def cloumn_str(self):
        return 'datetime'

class BaseFiled(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self,value):
        return self.cls(value,*self.args,**self.kwargs)


class VarCharField(BaseFiled):
    cls = _VarCharField

class DecimalField(BaseFiled):
    cls = _DecimalField

class Float(BaseFiled):
    cls = _Float

class DateTime(BaseFiled):
    cls = _DateTime


class ItemParse(object):
    addtime = 'AddTime'
    checktime = 'CheckTime'
    updatetime = 'UpdateTime'
    def __init__(self, items):
        # 初始化参数
        self.item = items.get('item')
        self.tablename = items.get('tb')
        self.items = self._items()
        self.keys = self.get_keys()
        self.new_items = self._new_items()
        assert self.keys and self.item and self.tablename

    def get_keys(self):
        # 获取主键list
        return {k:v for k,v in self.items if getattr(v,'key')==1}.items()

    def _new_items(self):
        # 去除非主键null字段
        return {k:v for k,v in self.items if str(v) is not 'null' or k in dict(self.keys)}.items()

    def _items(self):
        # 返回元组
        return self.item.items()

    @property
    def ID_Create(self):
        # ID字段
        return '[ID] bigint NOT NULL IDENTITY(1,1)'

    @property
    def get_local_time(self):
        # 获取当前时间string
        return repr(time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime()))

    def CreateTable(self):
        # 建表sql语句
        return 'CREATE TABLE %s (\n%s,\
        %s,\n[MD5] nvarchar(255) NOT NULL,\n[%s] datetime NUll,\n\
[%s] datetime NULL,\n\
[%s] datetime NULL)\nON [PRIMARY]' % (self.tablename,self.ID_Create,self.colums(),self.addtime,self.checktime,self.updatetime)

    def colums(self):
        return ','.join(v.create_str(k) for k,v in self.item.items())

    def set_sql(self):
        # 抛去null字段 --保留原值
        return ','.join((v.set_columns(k) for k,v in self.new_items))+',%s = %s,%s = %s' % (self.checktime,self.get_local_time,self.updatetime,self.get_local_time)

    def where_sql(self):
        return ','.join((v.sql_equal(k) for k,v in self.keys))

    def where_all_sql(self):
        return ','.join((v.sql_equal(k) for k,v in self.new_items))

    @property
    def md5(self):
        # 表字段md5 --排序?
        # print('_'.join(sorted(str(i) for i in self.item.values())))
        _md5 =  md5('_'.join(sorted(str(i[1]) for i in self.items)).encode('utf-8')).hexdigest()
        return repr(_md5)

    def insert(self):
        # 生成sql语句 供course调用
        items = self.items
        insert_sql = 'INSERT INTO %s (%s,MD5,%s,%s) values (%s)' % (self.tablename,','.join(i[0] for i in items),self.addtime,self.checktime,','.join(['%s'] * (len(items)+3)))
        values = tuple([str(i[1]) for i in items] + [self.md5]+[self.get_local_time]*2)
        return insert_sql,values

    def insert_(self):
        # 不安全的sql
        insert_tuple = self.insert()
        return insert_tuple[0] % (insert_tuple[1])

    def update_column(self):
        return 'update %s\nset %s\nwhere %s' % (self.tablename,self.set_sql(),self.where_sql())

    def update_check_time(self):
        return 'update %s\nset %s=%s\nwhere %s' % (self.tablename,self.checktime,self.get_local_time,self.where_sql())

    def query_first(self):
        return 'select top 1 1 from %s where %s' %(self.tablename,self.where_sql())

    def query_second(self):
        return 'select top 1 1 from %s where MD5 = %s' %(self.tablename,self.md5)

    def create_table(self):
        return "if  object_id('%s') is null  \n%s\
        else \
            select 0" % (self.tablename,self.CreateTable())

    def go(self):
        sql = 'if not exists(%s) begin %s end else if not exists(%s) begin %s end else begin %s end' % (self.query_first(), self.insert_(), self.query_second(), self.update_column(),self.update_check_time())
        return sql
if __name__ == '__main__':
    items = {'item':{'c_a':VarCharField(max_length=255,key=1,default=None)('3'),
         'c_b':VarCharField(max_length='max',key=1,default='qqq')(None),
         'c_c':DecimalField(default=111,key=1)("587655"),
         'c_d':Float(key=1)(None)},
         'tb':'Chinawealth.haozu'}
    # Fields = VarCharField(max_length=255,key=1,default=None)
    # item = {'q':'b','c':'d','e':'f'}
    # V = Fields({1111:1111,3333:'q'})
    # print(V.sql_equal('q'))
    # print(V.create_str('q'))
    table = ItemParse(items)
    # print(table.CreateTable())
    # print(table.insert())
    print(table.create_table())
    # print(table.insert_())
    # print(table.update_column())
    # print(table.update_check_time())
    # print(table.query_first())
    # print(table.query_second())
    # print(table.go())
    # number = DecimalField(default=111,key=1)("587655")
    # print(number.re_compile)
    # print(number.create_str('q'))
    # print(number.sql_equal('q'))
