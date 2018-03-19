# coding:utf8

import itchat,time
from itchat.content import *
def lcb():
    print("登录完成！")
def ecb():
    print("退出成功！")

newInstance = itchat.new_instance()
newInstance.auto_login(hotReload=True, statusStorageDir='newInstance.pkl',loginCallback=lcb,exitCallback=ecb)

@newInstance.msg_register(itchat.content.TEXT)
def reply(msg):
    return msg.text







friends = newInstance.get_friends(update=True)[1]
# q = itchat.send(msg="wechit 测试",toUserName=friends['UserName'])
# send_file # 发送文件
# send_image # 发送图片
# send_video # 发送视频


# get_chatrooms 获取群聊列表


# print(q)
# myUserName = newInstance.get_friends(update=True)[0]["UserName"]
# gzh = newInstance.get_mps()
# print(gzh)

# gzh = newInstance.search_mps(name='中国银行')

for i in newInstance.get_chatrooms():
    if i['NickName'] == '天通苑小分队':
            # newInstance.send(msg = 'wechat test %s' % time.strftime(time.ctime()    ), toUserName=i['UserName'])
    
        myUserName = i['UserName']

@itchat.msg_register(TEXT, isFriendChat=True, isGroupChat=True, isMpChat=True )
def text_reply(msg):
    if msg['FromUserName'] != myUserName:
        # 发送一条提示给文件助手
        itchat.send_msg(u"[%s]收到好友@%s 的信息：%s\n" %
                        (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['CreateTime'])),
                         msg['User']['NickName'],
                         msg['Text']), 'filehelper')
        # 回复给好友
        return u'[自动回复]您好，我现在有事不在，一会再和您联系。\n已经收到您的的信息：%s\n' % (msg['Text'])

newInstance.run()

newInstance.dump_login_status()