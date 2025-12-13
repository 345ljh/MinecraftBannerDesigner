import cv2

MAX_BANNER = 6

color = {
    "white": [239, 239, 239],
    "orange": [239, 124, 28],
    "magenta": [216, 84, 205],
    "light_blue": [68, 194, 236],
    "yellow": [239, 232, 66],
    "lime": [138, 214, 33],
    "pink": [241, 134, 164],
    "gray": [69, 77, 80],
    "light_gray": [169, 169, 169],
    "cyan": [24, 169, 169],
    "purple": [147, 54, 198],
    "blue": [65, 74, 184],
    "brown": [142, 91,54],
    "green": [101, 134, 24],
    "red": [191, 50, 40],
    "black": [30, 30, 30],
    "none": [255, 255, 255]
}

color_name = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black", "none"]

type = [
    "no", "bl", "br", "tl", "tr", "bs", 
    "ts", "ls", "rs", "cs", "ms", "drs", 
    "dls", "ss", "cr", "sc", "bt", "tt", 
    "bts", "tts", "ld", "rd", "lud", "rud", 
    "mc", "mr", "vh", "hh", "vhr", "hhb", 
    "bo", "cbo", "gra", "gru", "bri", "flo", 
    "cre", "sku", "moj", "glb", "pig"
]

# 多键操作添加非空图案
multi_operation = [
    "none", "zzz", "ccc", "qqq", "eee", "zxc",
    "qwe", "qaz", "edc", "wsx", "asd", "qsc",
    "esz", "wswsw", "qcez", "adwx", "zscz", "qesq",
    "azscd", "aqsed", "qezq", "czec", "zqcz", "ecqe",
    "sss", "awdxa", "qwxzq", "qedaq", "wecxw", "adcza",
    "qeczq", "qezc", "wwwx", "xxxw", "wssx", "swdxa",
    "qezsc", "wacdz", "edazc", "wdcza", "adada"
]
# 依次判断multi_operation是否一个字符串是另一个子串
def moj():
    for i in range(len(multi_operation)):
        for j in range(len(multi_operation)):
            if i == j:
                continue
            if multi_operation[i] in multi_operation[j]:
                print(multi_operation[i], multi_operation[j])
# moj()

# 水平翻转对应组合
horizonal_flip_pair = [
0, 2, 1, 4, 3, 5, 
6, 8, 7, 9, 10, 12, 
11, 13, 14, 15, 16, 17, 
18, 19, 23, 22, 21, 20, 
24, 25, 28, 27, 26, 29, 
30, 31, 32, 33, 34, 35, 
36, 37, 38, 39, 40
]

# 垂直翻转对应组合
vertical_flip_pair = [
0, 3, 4, 1, 2, 6,
5, 7, 8, 9, 10, 12,
11, 13, 14, 15, 17, 16,
19, 18, 22, 23, 20, 21,
24, 25, 26, 29, 28, 27,
30, 31, 33, 32, 34, 35,
36, 37, 38, 39, 40
]

icon = {}

def getIcon(n = ""):
    if icon == {}:
        for name in type:
            image = cv2.imread("images/patterns/" + name + ".png", cv2.IMREAD_UNCHANGED)
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)[1:21, 1:21]
            image = image[1:41, 1:21, 3]
            icon[name] = image
    if n == "":
        return icon
    else:
        return icon[n]

def getDefaultBannerStr():
    # 格式类似16:0:0:0:0:0:0:0:0:0:0:0:0
    str = "16:"
    for i in range(MAX_BANNER):
        str += "0:0:"
    return str[:-1]

if __name__ == "__main__":
    named_window = cv2.namedWindow("aaa")
    # print(getIcon()["vh"])
    cv2.imshow("aaa", getIcon("rud"))
    cv2.waitKey(0)