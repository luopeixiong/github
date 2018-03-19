from urllib import request
from http import cookiejar
from settings import BASEHEADERS


headers = BASEHEADERS

class Cookies(object):
    def __init__(self):
        self.url = "http://"+BASEHEADERS["Host"]
        self.cj = cookiejar.LWPCookieJar()
        cookie_support = request.HTTPCookieProcessor(self.cj)
        opener = request.build_opener(cookie_support,request.HTTPHandler)
        request.install_opener(opener)
        try:
            requester = request.Request(self.url,headers)
            request.urlopen(requester)
        except Exception as e:
            print(e)
            
    def get_cookies_dict(self):
        lwp = self.cj._cookies
        lwp_dict = lwp[BASEHEADERS["Host"]]
        
        return lwp_dict
        
    def get_cookie(self,name):
        lwp_dict = self.get_cookies_dict()
        cookie_dict = lwp_dict["/"]
        if type(name) == "str":
            self.cookie = cookie_dict[name]
        if type(name) == "list":
            self.cookie = []
            for n in name:
                self.cookie.append(cookie_dict[n])

        return self.cookie

    def cookie_str(self,name):
        cookie = self.get_cookie(name)
        if type(name) == "str":
            self.s = "{name}:{values}".format({"name":cookie.name},{"values":cookie.values})
        if type(name) == "list":
            self.s = "{name}:{values}".format({"name":cookie[0].name},{"values":cookie[0].values})+";  "+"{name}:{values}".format({"name":cookie[1].name},{"values":cookie[1].values})

        return self.s