from settings import PROXIES_POOL,PROXIES_API
from random import choice
from urllib import request


class Proxies(object):
    def __init__(self):
        self.proxies = []

    def manual(self):
        self.proxies = choice(PROXIES_POOL)

        return self.proxies

    def api_get_proxies(self):
        requester = request.urlopen(PROXIES_API)
        response = requester.read()
        self.proxies_pool = response.split()
        self.times = 0

        return self.proxies_pool

    def proxies(self,method):
        if method == "manual":
            self.proxies = self.manual()
        if method == "api":
            self.proxies = self.get_proxies()
        proxies_handler = request.ProxyHandler(self.proxies)
        opener = request.build_opener(proxies_handler)
        request.install_opener(opener)
        self.pool.pop()

    def get_proxies(self):
        if len(self.pool) == 0:
            self.pool = self.api_get_proxies()
        proxies = self.pool[-1]

        return proxies