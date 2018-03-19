import sys
import os
_pathadd = os.getcwd()
pathadd=_pathadd.split('\\')

path1 = '\\'.join(pathadd[:-1])
path2 = '\\'.join(pathadd[:-2])
sys.path.extend((path1,path2,_pathadd,'./','../'))