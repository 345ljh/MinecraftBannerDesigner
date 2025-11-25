from PyQt5.QtWidgets import (QApplication, QShortcut, QWidget, QGridLayout, QScrollArea, QVBoxLayout,
QSizePolicy, QPushButton, QFileDialog, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QKeySequence
import sys, os, psutil
import PIL

import ToolBox, SingleBannerDesigner, DesignPreviewer
import AdaptiveManager
import pattern



class MainWindow(QWidget):
    # mainwindow本身不存储数据(调用数据主要放在toolbox),负责调用其他组件
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
        self.toolbox.UpdateZoom.connect(self.design_previewer.SetZoomFactor)
        self.design_previewer.onBannerClicked.connect(self.LoadBanner)
        self.single_banner_designer.BannerUpdated.connect(self.SetBanner)

        self.adaptive_components = [
            self.design_previewer, self.single_banner_designer, self.toolbox
        ]
        self.adaptive_manager = AdaptiveManager.AdaptiveManager(self, self.adaptive_components)
        
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.adaptive_manager.AdaptiveResize()


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
        self.toolbox.SetPatternsData(patterns_data, size)
        self.LoadBanner([1, 0])

    def LoadBanner(self, pos=[1,0]):
        '''设置preview中banner坐标提示(红框), 并加载singleDesigner的banner配置界面'''
        pd = self.toolbox.current_design_patterns
        size = self.toolbox.current_design_size
        if pos is None or len(pos) != 2:
            return
        if pos[0] < 1 or pos[1] < 0 or pos[0] >= size[0] or pos[1] >= size[1]:
            return
        if f"{pos[0]}:{pos[1]}" in pd:
            b = pd[f"{pos[0]}:{pos[1]}"]
        else:
            b = "16"
        self.design_previewer.SetEditBannerPosition(pos)
        self.toolbox.banner_pos = pos
        self.single_banner_designer.LoadBanner(b, isNew=True)

    def SetBanner(self, banner):
        '''singleDesigner更新banner后, 更新design_previewer和toolbox'''
        b = self.single_banner_designer.GetBanner(isStr=True)
        pos = self.toolbox.banner_pos
        self.toolbox.current_design_patterns[f"{pos[0]}:{pos[1]}"] = b
        self.toolbox.SaveCurrentDesign()
        self.design_previewer.SetPatternsData(self.toolbox.current_design_patterns, self.toolbox.current_design_size)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())