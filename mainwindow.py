from PyQt5.QtWidgets import (QApplication, QShortcut, QWidget, QGridLayout, QScrollArea, QVBoxLayout,
QSizePolicy, QPushButton, QFileDialog, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QKeySequence, QIcon
import sys, os, psutil
import PIL

import ToolBox, SingleBannerDesigner, DesignPreviewer
import utils.AdaptiveManager as AdaptiveManager
import utils.pattern as pattern
import utils.DataStorage as DataStorage

class MainWindow(QWidget):
    # 窗口组件本身不存储数据, 数据通过DataStorage单例进行共享
    # mainwindow负责连接与调用其他组件
    def __init__(self):
        super().__init__()
        self.__setupStyles()

        self.setWindowTitle("Minecraft Banner Designer V2.0")
        self.setWindowIcon(QIcon("images/icon.png"))

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
        self.toolbox.ui.ViewRealtimeDisplayCheckBox.stateChanged.connect(self.SetRealtimeDisplay)

        self.adaptive_components = [
            self.design_previewer, self.single_banner_designer, self.toolbox
        ]
        self.adaptive_manager = AdaptiveManager.AdaptiveManager(self, self.adaptive_components)

        # 快捷键
        self.shortcut_horizonalflip = QShortcut(QKeySequence("H"), self)
        self.shortcut_horizonalflip.activated.connect(self.single_banner_designer.HorizonalFlip)
        self.shortcut_vertialflip = QShortcut(QKeySequence("V"), self)
        self.shortcut_vertialflip.activated.connect(self.single_banner_designer.VerticalFlip)
        self.shortcut_addpattern = QShortcut(QKeySequence("Shift+="), self)  # 添加空图案
        self.shortcut_addpattern.activated.connect(self.single_banner_designer.AddPattern)
        self.shortcut_clearpattern = QShortcut(QKeySequence("Delete"), self)  # 清除所有图案
        self.shortcut_clearpattern.activated.connect(self.single_banner_designer.ClearPattern)
        self.shortcut_deletelastpattern = QShortcut(QKeySequence("Backspace"), self)  # 删除最后一个图案
        self.shortcut_deletelastpattern.activated.connect(lambda: self.single_banner_designer.OperatePattern(self.single_banner_designer.pattern_len - 1, 2))
        self.shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)  # 复制当前banner
        self.shortcut_copy.activated.connect(self.single_banner_designer.CopyPattern)
        self.shortcut_paste = QShortcut(QKeySequence("Ctrl+V"), self)  # 粘贴banner
        self.shortcut_paste.activated.connect(self.single_banner_designer.PastePattern)
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self)  # 撤销
        self.shortcut_undo.activated.connect(self.single_banner_designer.Undo)
        self.shortcut_redo = QShortcut(QKeySequence("Ctrl+X"), self)  # 重做
        self.shortcut_redo.activated.connect(self.single_banner_designer.Redo)
        self.shortcut_savebanner = QShortcut(QKeySequence("Ctrl+S"), self)  # 保存当前banner
        self.shortcut_savebanner.activated.connect(self.single_banner_designer.UpdateBanner)
        self.shortcut_background = [QShortcut(QKeySequence(f"Ctrl+{key}"), self)  # 设置当前Banner背景
                                    for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'T', 'Y', 'U', 'I', 'O', 'P', 'del']]
        for i, shortcut in enumerate(self.shortcut_background):
            shortcut.activated.connect(lambda idx=i: self.single_banner_designer.ui.BannerColorComboBox.setCurrentIndex(idx))
        self.shortcut_patterncolor = [QShortcut(QKeySequence(f"{key}"), self)  # 设置最后一个操作的颜色
                                    for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'T', 'Y', 'U', 'I', 'O', 'P']]
        for i, shortcut in enumerate(self.shortcut_patterncolor):
            shortcut.activated.connect(lambda idx=i: self.single_banner_designer.SetLastPatternColor(idx))
        self.shortcut_backgroundcolor = [QShortcut(QKeySequence(f"Shift+{key}"), self)  # 设置背景颜色
                                    for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'T', 'Y', 'U', 'I', 'O', 'P', 'del']]
        for i, shortcut in enumerate(self.shortcut_backgroundcolor):
            shortcut.activated.connect(lambda idx=i: self.toolbox.SetDefaultBackgroundColor(idx))
        self.shortcut_upbanner = QShortcut(QKeySequence("Up"), self)  # 选择上方banner
        self.shortcut_upbanner.activated.connect(lambda: self.LoadBanner([DataStorage.get_instance().banner_pos[0] + 1, DataStorage.get_instance().banner_pos[1]]))
        self.shortcut_downbanner = QShortcut(QKeySequence("Down"), self)  # 选择下方banner
        self.shortcut_downbanner.activated.connect(lambda: self.LoadBanner([DataStorage.get_instance().banner_pos[0] - 1, DataStorage.get_instance().banner_pos[1]]))
        self.shortcut_leftbanner = QShortcut(QKeySequence("Left"), self)  # 选择左方banner
        self.shortcut_leftbanner.activated.connect(lambda: self.LoadBanner([DataStorage.get_instance().banner_pos[0], DataStorage.get_instance().banner_pos[1] - 1]))
        self.shortcut_rightbanner = QShortcut(QKeySequence("Right"), self)  # 选择右方banner
        self.shortcut_rightbanner.activated.connect(lambda: self.LoadBanner([DataStorage.get_instance().banner_pos[0], DataStorage.get_instance().banner_pos[1] + 1]))
        self.shortcut_zoomup = QShortcut(QKeySequence("Ctrl+="), self)  # 放大
        self.shortcut_zoomup.activated.connect(lambda: self.toolbox.SetZoom(True))
        self.shortcut_zoomdown = QShortcut(QKeySequence("Ctrl+-"), self)  # 缩小
        self.shortcut_zoomdown.activated.connect(lambda: self.toolbox.SetZoom(False))
        self.shortcut_new_design = QShortcut(QKeySequence("Ctrl+N"), self)  # 选择/新建设计
        self.shortcut_new_design.activated.connect(self.toolbox.SelectDesign)
        self.shortcut_search_design = QShortcut(QKeySequence("Ctrl+F"), self)  # 搜索设计
        self.shortcut_search_design.activated.connect(self.toolbox.SearchDesign)
        self.shortcut_openfile = QShortcut(QKeySequence("Ctrl+Shift+O"), self)  # 打开文件
        self.shortcut_openfile.activated.connect(self.toolbox.OpenFile)
        self.shortcut_savefile = QShortcut(QKeySequence("Ctrl+Shift+S"), self)  # 保存文件
        self.shortcut_savefile.activated.connect(self.toolbox.SaveFile)
        self.shortcut_gencommand = QShortcut(QKeySequence("Ctrl+Shift+C"), self)  # 生成指令
        self.shortcut_gencommand.activated.connect(self.toolbox.GenerateCommand)
        self.shortcut_caldye = QShortcut(QKeySequence("Ctrl+Shift+D"), self)  # 计算染料数量
        self.shortcut_caldye.activated.connect(self.toolbox.CalculateDesignDye)
        self.shortcut_focus_design_name = QShortcut(QKeySequence("Tab"), self)   # 将输入光标移动到下一个输入框
        self.shortcut_focus_design_name.activated.connect(self.toolbox.UpdateFocus)
        self.shortcut_padding_checkbox = QShortcut(QKeySequence("Shift+P"), self)   # 真实间隔选项开启/关闭
        self.shortcut_padding_checkbox.activated.connect(lambda: self.toolbox.ui.ViewPaddingCheckBox.setChecked(not self.toolbox.ui.ViewPaddingCheckBox.isChecked()))
        self.shortcut_realtime_checkbox = QShortcut(QKeySequence("Shift+D"), self)   # 实时渲染示选项开启/关闭
        self.shortcut_realtime_checkbox.activated.connect(lambda: self.toolbox.ui.ViewRealtimeDisplayCheckBox.setChecked(not self.toolbox.ui.ViewRealtimeDisplayCheckBox.isChecked()))
        rowcol_operation = [["Ctrl+Up", True, True, False], ["Ctrl+Down", False, True, False], ["Ctrl+Left", False, False, False], ["Ctrl+Right", True, False, False],
                     ["Shift+Up", True, True, True], ["Shift+Down", False, True, True], ["Shift+Left", False, False, True], ["Shift+Right", True, False, True]]
        self.shortcut_rowcol_operation = [QShortcut(QKeySequence(f"{rc[0]}"), self)  # 行列增删
                                    for rc in rowcol_operation]
        for i, shortcut in enumerate(self.shortcut_rowcol_operation):
            shortcut.activated.connect(lambda idx=i: self.toolbox.RowColumnOperation(*rowcol_operation[idx][1:]))

        # 多键操作
        self.multi_key_sequence = ""
        self.multi_key = ["q", "w", "e", "a", "s", "d", "z", "x", "c"]
        self.shortcut_multikey = [QShortcut(QKeySequence(key), self) for key in self.multi_key]
        for i, shortcut in enumerate(self.shortcut_multikey):
            shortcut.activated.connect(lambda idx=i: self.MultiKey(self.multi_key[idx]))
        
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.adaptive_manager.AdaptiveResize()

    def __setupStyles(self):
        """统一设置应用样式表"""
        import utils.stylesheet
        # 应用样式表到整个应用
        self.setStyleSheet(utils.stylesheet.style_sheet)

    def DesignDisplay(self):
        '''渲染加载的设计'''
        self.design_previewer.Update()
        self.LoadBanner([1, 0])

    def LoadBanner(self, pos=[1,0]):
        '''设置preview中banner坐标提示(红框), 并加载singleDesigner的banner配置界面'''
        pd = DataStorage.get_instance().current_design_patterns
        size = DataStorage.get_instance().current_design_size
        if pos is None or len(pos) != 2:
            return
        if pos[0] < 1 or pos[1] < 0 or pos[0] >= size[0] or pos[1] >= size[1]:
            return
        if f"{pos[0]}:{pos[1]}" in pd:
            b = pd[f"{pos[0]}:{pos[1]}"]
        else:
            b = "16"
        if self.toolbox.ui.ViewRealtimeDisplayCheckBox.isChecked():
            self.design_previewer.SetEditBannerPosition(pos)
        DataStorage.get_instance().banner_pos = pos
        self.single_banner_designer.LoadBanner(b, isNew=True)

    def SetRealtimeDisplay(self):
        if self.toolbox.ui.ViewRealtimeDisplayCheckBox.isChecked():
            self.design_previewer.SetEditBannerPosition(DataStorage.get_instance().banner_pos)
        else:
            self.design_previewer.SetEditBannerPosition([-1, -1])

    def SetBanner(self):
        '''singleDesigner更新banner后, 更新design_previewer和toolbox'''
        b = self.single_banner_designer.GetBanner(isStr=True)
        pos = DataStorage.get_instance().banner_pos
        DataStorage.get_instance().current_design_patterns[f"{pos[0]}:{pos[1]}"] = b
        self.toolbox.SaveCurrentDesign()
        if self.toolbox.ui.ViewRealtimeDisplayCheckBox.isChecked():
            self.design_previewer.Update()

    def MultiKey(self, key):
        '''多键操作, 一组键长度最大为5'''
        self.multi_key_sequence += key
        if len(self.multi_key_sequence) > 10:
            self.multi_key_sequence = self.multi_key_sequence[-5:]
        for i in range(len(pattern.multi_operation)):
            if pattern.multi_operation[i] in self.multi_key_sequence:
                self.single_banner_designer.AddPattern(i)
                self.multi_key_sequence = ""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())