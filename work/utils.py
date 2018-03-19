from urllib import parse


def set_url(host,key):
    key = parse.quote(key)
    url = host+key
    
    return url