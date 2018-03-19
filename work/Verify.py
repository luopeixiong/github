from Parser import HtmlParser

def get_title(response):
    title = HtmlParser(response).parser("title")
    # parser = HtmlParser(response)
    # title = parser.parser("title")

    return title

def verify(response):
    verify_data = get_title(response)
    if "会员登录 - 企查查" in verify_data:
        return False
    elif "用户验证_企查查" in verify_data:
        return False
    elif len(verify_data) == 0:
        return False
    else:
        return True