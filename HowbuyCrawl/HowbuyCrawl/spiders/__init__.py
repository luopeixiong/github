# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import sys
#from myselector1
import os
_pathadd = os.getcwd()
pathadd=_pathadd.split('\\')

path1 = '\\'.join(pathadd[:-1])
path2 = '\\'.join(pathadd[:-2])
sys.path.extend((path1,path2,_pathadd,'./','../'))

print(sys.path)