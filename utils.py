def StrBannerToList(str_banner: str):
    '''返回list元素为int'''
    splited = str_banner.split(':')
    length = (len(splited) - 1) // 2
    splited = [int(i) for i in splited]
    return length, splited

def ListToStrBanner(list_banner: list):
    list_banner = [str(i) for i in list_banner]
    return ':'.join(list_banner)