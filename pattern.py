import cv2
from PyQt5.QtGui import QColor

color = {
    "white": QColor(239, 239, 239),
    "orange": QColor(239, 124, 28),
    "magenta": QColor(216, 84, 205),
    "light_blue": QColor(68, 194, 236),
    "yellow": QColor(239, 232, 66),
    "lime": QColor(138, 214, 33),
    "pink": QColor(241, 134, 164),
    "gray": QColor(69, 77, 80),
    "light_gray": QColor(169, 169, 169),
    "cyan": QColor(24, 169, 169),
    "purple": QColor(147, 54, 198),
    "blue": QColor(65, 74, 184),
    "brown": QColor(142, 91,54),
    "green": QColor(101, 134, 24),
    "red": QColor(191, 50, 40),
    "black": QColor(30, 30, 30)
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