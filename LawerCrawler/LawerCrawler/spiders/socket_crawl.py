# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 13:49:27 2017

@author: luopx
"""

# import socket
# import json
# import requests
# from scrapy import Selector
# #res = requests.get('http://www.zk120.com/ji/book/529')
# #response = Selector(res)
# #csrf =response.xpath('//input[@name="csrfmiddlewaretoken"]/@value').extract_first()
# #cookies = {'csrftoken':csrf}
# #res = requests.get('http://www.zk120.com/common/centrifugo?t=1512976784000&uid=anyone',cookies =cookies)
# #JS = json.loads(res.text)
# CENTRIFUGE_TOKEN = 'q'#JS['CENTRIFUGE_TOKEN']
# #CENTRIFUGE_SOCKJS_ENDPOINT = JS['CENTRIFUGE_SOCKJS_ENDPOINT']
# #CENTRIFUGE_TIMESTAMP = JS['CENTRIFUGE_TIMESTAMP']
# #CENTRIFUGE_WS_ENDPOINT = JS['CENTRIFUGE_WS_ENDPOINT']
# #host = 'centrifugo.zk120.com'
# host = 'centrifugo.zk120.com'
# remote_ip = socket.gethostbyname(host)
# sk =socket.socket()
# ip_port = (remote_ip,80)
# #sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# port = socket.getservbyname("http","tcp")
# #sk.connect((host,8602))
# ###
# sk.connect(ip_port)
# #
# import time
# def send(sk,string):
#     try:
#         string = string % int(time.time())
#     except:
#         pass
#     print(string)
#     sk.sendall(string.encode('utf-8'))
# def recv(sk):
#     data = ''
#     string = True
#     while string:
#         string = sk.recv(1024)
#         if string:
#             data += string.decode('utf-8')
#         else:
#             return data

# def step(sk,string):
#     send(sk,string)
#     data = recv(sk)
#     print(data)

# step(sk,'["[{\"method\":\"connect\",\"params\":{\"user\":\"\",\"info\":\"\",\"timestamp\":\"1512977827\",\"token\":\"45b51f7cc982a12ef260b14b38eed05d2cbaf64f206a645af03dee9da53f2a32\"},\"uid\":\"1\"}]"]')
# print(1)
#step(sk,'["[{\"method\":\"connect\",\"params\":{\"user\":\"\",\"info\":\"\",\"timestamp\":\"%s\",\"token\":\"2f88013c4db0f0bb554d6ea32e3846d61c0a724dd0fd94739b4ce5873539ba5e\"},\"uid\":\"8\"}]"]')
#print(1)
#step(sk,'["[{\"method\":\"subscribe\",\"params\":{\"channel\":\"tick:20171211T053930.358139747148\",\"recover\":true,\"last\":\"KhZ54486zAlDJl7p5OFyFF\"},\"uid\":\"9\"}]"]')
#print(1)
#step(sk,'["[{\"method\":\"subscribe\",\"params\":{\"channel\":\"tick:20171211T053930.358139747148\",\"recover\":true,\"last\":\"KhZ54486zAlDJl7p5OFyFF\"},\"uid\":\"9\"}]"]')
#print(1)
