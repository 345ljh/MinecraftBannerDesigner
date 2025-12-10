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
    "black": [30, 30, 30]
}

color_name = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]

type = [
    "no", "bl", "br", "tl", "tr", "bs", 
    "ts", "ls", "rs", "cs", "ms", "drs", 
    "dls", "ss", "cr", "sc", "bt", "tt", 
    "bts", "tts", "ld", "rd", "lud", "rud", 
    "mc", "mr", "vh", "hh", "vhr", "hhb", 
    "bo", "cbo", "gra", "gru", "bri", "flo", 
    "cre", "sku", "moj", "glb", "pig"
]

symmetric_pair = [
0, 2, 1, 4, 3, 5, 
6, 8, 7, 9, 10, 12, 
11, 13, 14, 15, 16, 17, 
18, 19, 23, 22, 21, 20, 
24, 25, 28, 27, 26, 29, 
30, 31, 32, 33, 34, 35, 
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