# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 18:20:08 2018

@author: luopx
"""

#%%
print(1)
#%%
print(2)
#%%
print(3)
#%%
from functools import reduce
from operator import mod,mul
print(reduce(mul,range(1,4)))