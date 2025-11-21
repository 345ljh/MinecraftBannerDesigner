from PyQt5.QtWidgets import (QApplication, QShortcut, QWidget, QGridLayout, QScrollArea, QVBoxLayout,
QSizePolicy, QPushButton, QFileDialog, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QKeySequence
import sys, os
import PIL

import ToolBox, SingleBannerDesigner, DesignPreviewer
import AdaptiveManager
import pattern



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1800, 900)
        self.design_previewer = DesignPreviewer.DesignPreviewer()
        self.design_previewer.setGeometry(0, 0, self.design_previewer.width(), self.design_previewer.height())
        self.design_previewer.setParent(self)

        self.single_banner_designer = SingleBannerDesigner.SingleBannerDesigner()
        self.single_banner_designer.setGeometry(self.design_previewer.width(), 0, self.single_banner_designer.width(), self.single_banner_designer.height())
        self.single_banner_designer.setParent(self)

        self.toolbox = ToolBox.ToolBox()
        self.toolbox.setGeometry(self.design_previewer.width() + self.single_banner_designer.width(), 0, self.toolbox.width(), self.toolbox.height())
        self.toolbox.setParent(self)

        # 设置信号连接
        self.toolbox.LoadDesign.connect(self.DesignDisplay)

    def DesignDisplay(self, design):
        '''design_previewer渲染设计'''
        # 输入: [row, col, [r1:c1:banner1, ...]]
        # 输出: {"r1:c1", banner1, ...}
        size = [design[0], design[1]]
        patterns_data = {}
        for banner in design[2]:
            b = banner.split(":", 2)
            key = b[0] + ":" + b[1]
            patterns_data[key] = b[2]
        self.design_previewer.SetPatternsData(patterns_data, size)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())