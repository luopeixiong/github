from urllib import request


class Spider(object):
    def __init__(self,url):
        self.url = url
        self.response = ""

    def spider(self,headers=None):
        try:
            requester = request.Request(self.url,headers)
            openurl = request.urlopen(requester)
            self.response = openurl.read().decode("utf-8")
            time.sleep(randint(1,12))
        except Exception as e:
            print(e)

        return self.response