from PyQt5.QtWidgets import (QApplication, QSizePolicy, QWidget, QVBoxLayout)
from PyQt5.QtCore import Qt
import sys

class AdaptiveManager():
    def __init__(self, widget: QWidget, adaptive_components, widget_fix_ratio=True):
        self.widget = widget
        self.widget_fix_ratio = widget_fix_ratio # 固定窗口长宽比
        self.widget_initx = widget.width()
        self.widget_inity = widget.height()
        self.adaptive_components = adaptive_components
        self.adaptive_component_ratios = [[1,1,1,1]] * len(self.adaptive_components)

        # 记录自适应组件初始尺寸在屏幕中的比例
        for i in range(len(self.adaptive_components)):
            self.adaptive_component_ratios[i] = [self.adaptive_components[i].width() / self.widget.width(),
                                                 self.adaptive_components[i].height() / self.widget.height(),
                                                 self.adaptive_components[i].x() / self.widget.width(),
                                                 self.adaptive_components[i].y() / self.widget.height(),
                                                 self.adaptive_components[i].font().pointSize() / self.widget.height()]  # 字号
            
    def AdaptiveResize(self):
        for i in range(len(self.adaptive_components)):
            self.adaptive_components[i].setGeometry(int(self.widget.width() * self.adaptive_component_ratios[i][2]),
                                                    int(self.widget.height() * self.adaptive_component_ratios[i][3]),
                                                    int(self.widget.width() * self.adaptive_component_ratios[i][0]),
                                                    int(self.widget.height() * self.adaptive_component_ratios[i][1]))
            font = self.adaptive_components[i].font()
            font.setPointSize(int(self.widget.height() * self.adaptive_component_ratios[i][4]))
            self.adaptive_components[i].setFont(font)
        # 窗口固定比例
        self.widget.resize(self.widget.width(), int(self.widget.width() / self.widget_initx * self.widget_inity))

    def getCurrentRatio(self):
        return (self.widget.width() / self.widget_initx, self.widget.height() / self.widget_inity)
        