#客户端处理线程
import requests
import urllib.parse
from user_agent import generate_user_agent


if __name__ == '__main__':
    Cookie_text = "pgv_pvi=893517824; mediawiki4baikehidetoc=1; _umdata=2BA477700510A7DF88B82C7537ECCF162782B5062009ECD024E1F96CD91F96AC0BF12AD8BA4F60BACD43AD3E795C914CCDE7A2813E420DC53F3796271DCCA59C; pgv_si=s6414157824; shfskey=20180125T022114.314058108155; svrid=23d57628f8ea08a6a48aeb1504665ac3; sessionid=wiet86u9hnpthwbd07q793ufcst6ndnf; checkCookieTime=1516849603563; csrftoken=74CmJmEBXM3RtjHAL2TgAvFN4vj3u40R; nTalk_CACHE_DATA={uid:kf_9050_ISME9754_guestC99471E5-CA5C-8D,tid:1516846868528770}; NTKF_T2D_CLIENTID=guestC99471E5-CA5C-8D58-BD54-44159AEE76A1"
    cookie = dict(urllib.parse.parse_qsl(Cookie_text))
    url = 'https://www.zk120.com/ji/read/565?uid=None'
    headers = {'User-Agent': generate_user_agent(os=('win',)),
                'Referer': 'https://www.zk120.com/ji/book/565',
                'Upgrade-Insecure-Requests': '1'}
    res = requests.get(url,headers=headers,)
    print(res.text)