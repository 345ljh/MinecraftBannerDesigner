import cv2
from PyQt5.QtGui import QColor

color = {
    "white": QColor(255, 255, 255),
    "orange": QColor(255, 128, 0),
    "magenta": QColor(255, 0, 255),
    "light_blue": QColor(128, 128, 255),
    "yellow": QColor(255, 255, 0),
    "lime": QColor(128, 255, 0),
    "pink": QColor(255, 128, 128),
    "gray": QColor(128, 128, 128),
    "light_gray": QColor(192, 192, 192),
    "cyan": QColor(0, 255, 255),
    "purple": QColor(128, 0, 128),
    "blue": QColor(0, 0, 255),
    "brown": QColor(128, 64, 0),
    "green": QColor(0, 128, 0),
    "red": QColor(255, 0, 0),
    "black": QColor(0, 0, 0)
}

type = [
    "no", "bl", "br", "tl", "tr", "bs", "ts",
    "ls", "rs", "cs", "ms", "drs", "dls",
    "ss", "cr", "sc", "bt", "tt", "bts",
    "tts", "ld", "rd", "lud", "rud", "mc",
    "mr", "vh", "hh", "vhr", "hhb", "bo",
    "cbo", "gra", "gru", "bri",
    "flo", "cre", "sku", "moj", "glb", "pig"
]

icon = {}

def getIcon(n = ""):
    if icon == {}:
        for name in type:
            image = cv2.imread("icons/" + name + ".png", cv2.IMREAD_UNCHANGED)
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)[1:21, 1:21]
            image = image[1:41, 1:21, 3]
            icon[name] = image
    if n == "":
        return icon
    else:
        return icon[n]


if __name__ == "__main__":
    named_window = cv2.namedWindow("aaa")
    # print(getIcon()["vh"])
    cv2.imshow("aaa", getIcon("rud"))
    cv2.waitKey(0)