from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QScrollArea, QVBoxLayout,
QSizePolicy, QPushButton, QFileDialog, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QKeySequence, QIcon, QFontDatabase
import sys, os, psutil
import PIL

import ToolBox, SingleBannerDesigner, DesignPreviewer
import utils.AdaptiveManager as AdaptiveManager
import utils.pattern as pattern
import utils.DataStorage as DataStorage
import utils.VersionController as VersionController
import utils.tools as tools

class MainWindow(QWidget):
    # 窗口组件本身不存储数据, 数据通过DataStorage单例进行共享
    # mainwindow负责连接与调用其他组件
    def __init__(self):
        super().__init__()
        self.__setupStyles()

        self.setWindowTitle(f"Minecraft Banner Designer Ver.{VersionController.current_version}")
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

        # 多键操作
        self.multi_key_sequence = ""

        self.toolbox.CheckUpdate(isSilent=True)

        self.installEventFilter(self)

    # 按键显示与快捷键响应
    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress or event.type() == event.KeyRelease:
            key = event.key()
            modifiers = event.modifiers()  # 获取修饰键状态

            # 方向键只会触发KeyRelease, 而其它键两者均触发
            if key not in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_Tab] and event.type() == event.KeyRelease:
                return super().eventFilter(obj, event)
            
            # 检查是否按下某个修饰键
            _is_ctrl = bool(modifiers & Qt.ControlModifier)  # 检查Ctrl
            _is_shift = bool(modifiers & Qt.ShiftModifier)    # 检查Shift
            is_pure = not _is_ctrl and not _is_shift
            is_ctrl = _is_ctrl and not _is_shift
            is_shift = _is_shift and not _is_ctrl
            is_ctrl_shift = _is_ctrl and _is_shift

            # 按键显示
            key_show_str = tools.key_to_text(key)
            if key == Qt.Key_Control or key == Qt.Key_Shift:
                if is_shift:
                    key_show_str = "Shift"
                elif is_ctrl:
                    key_show_str = "Ctrl"
                elif is_ctrl_shift:
                    key_show_str = "Ctrl+Shift"
            else:
                if is_shift:
                    key_show_str = "Shift+" + key_show_str
                elif is_ctrl:
                    key_show_str = "Ctrl+" + key_show_str
                elif is_ctrl_shift:
                    key_show_str = "Ctrl+Shift+" + key_show_str
            self.toolbox.ui.KeyShow.setText(key_show_str)

            # 最上面一排即1~=, 按shift时替换为正常
            first_row = [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_0, Qt.Key_Minus, Qt.Key_Equal]
            first_row_shift = [Qt.Key_Exclam, Qt.Key_At, Qt.Key_NumberSign, Qt.Key_Dollar, Qt.Key_Percent, Qt.Key_AsciiCircum, Qt.Key_Ampersand, Qt.Key_Asterisk, Qt.Key_ParenLeft, Qt.Key_ParenRight, Qt.Key_Underscore, Qt.Key_Plus]
            if key in first_row_shift:
                key = first_row[first_row_shift.index(key)]

            # 快捷键响应
            if key == Qt.Key_H and is_pure:  # 水平翻转
                self.single_banner_designer.HorizonalFlip()
            elif key == Qt.Key_V and is_pure:  # 垂直翻转
                self.single_banner_designer.VerticalFlip()
            elif key == Qt.Key_Equal and is_shift:  # 添加空图案
                self.single_banner_designer.AddPattern()
            elif key == Qt.Key_Delete and is_pure:  # 清空图案
                self.single_banner_designer.ClearPattern()
            elif key == Qt.Key_Backspace and is_pure:  # 删除最后一个图案
                self.single_banner_designer.OperatePattern(self.single_banner_designer.pattern_len - 1, 2)
            elif key == Qt.Key_C and is_ctrl:  # 复制当前banner
                self.single_banner_designer.CopyPattern()
            elif key == Qt.Key_V and is_ctrl:  # 粘贴banner
                self.single_banner_designer.PastePattern()
            elif key == Qt.Key_Z and is_ctrl:  # 撤销
                self.single_banner_designer.Undo()
            elif key == Qt.Key_X and is_ctrl:  # 重做
                self.single_banner_designer.Redo()
            elif key == Qt.Key_S and is_ctrl:  # 保存banner并更新
                self.single_banner_designer.UpdateBanner()
            elif key == Qt.Key_Equal and is_ctrl:  # 放大
                self.toolbox.SetZoom(True)
            elif key == Qt.Key_Minus and is_ctrl:  # 缩小
                self.toolbox.SetZoom(False)
            elif key == Qt.Key_N and is_ctrl:  # 选择/新建设计
                self.toolbox.SelectDesign()
            elif key == Qt.Key_F and is_ctrl:  # 搜索设计
                self.toolbox.SearchDesign()
            elif key == Qt.Key_O and is_ctrl_shift:  # 打开文件
                self.toolbox.OpenFile()
            elif key == Qt.Key_S and is_ctrl_shift:  # 保存文件
                self.toolbox.SaveFile()
            elif key == Qt.Key_C and is_ctrl_shift:  # 生成指令
                self.toolbox.GenerateCommand()
            elif key == Qt.Key_D and is_ctrl_shift:  # 计算染料数量
                self.toolbox.CalculateDesignDye()
            elif key == Qt.Key_Tab and is_pure:  # 将输入光标移动到下一个输入框
                self.toolbox.UpdateFocus()
            elif key == Qt.Key_M and is_shift:  # 真实间隔选项开启/关闭
                self.toolbox.ui.ViewPaddingCheckBox.setChecked(not self.toolbox.ui.ViewPaddingCheckBox.isChecked())
            elif key == Qt.Key_D and is_shift:  # 实时渲染示选项开启/关闭
                self.toolbox.ui.ViewRealtimeDisplayCheckBox.setChecked(not self.toolbox.ui.ViewRealtimeDisplayCheckBox.isChecked())
            elif key == Qt.Key_Delete and is_ctrl:  # 旗帜背景颜色为空
                self.single_banner_designer.ui.BannerColorComboBox.setCurrentIndex(16)

            for i, k in enumerate([Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, 
                        Qt.Key_9, Qt.Key_0, Qt.Key_T, Qt.Key_Y, Qt.Key_U, Qt.Key_I, Qt.Key_O, Qt.Key_P]):
                if k == key:
                    if is_pure:  # 设置最后一个图案颜色
                        self.single_banner_designer.SetLastPatternColor(i)
                    elif is_ctrl:  # 设置旗帜颜色
                        self.single_banner_designer.ui.BannerColorComboBox.setCurrentIndex(i)
                    elif is_shift:  # 设置背景颜色
                        self.toolbox.SetDefaultBackgroundColor(i)

            for i, k in enumerate([Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]):
                if k == key:
                    if is_pure:  # 选择当前编辑的banner
                        self.LoadBanner([DataStorage.get_instance().banner_pos[0] + (int(i == 0) - int(i == 1)), DataStorage.get_instance().banner_pos[1] + (int(i == 3) - int(i == 2))])
                    elif is_ctrl or is_shift:  # 增删行列
                        self.toolbox.RowColumnOperation((i == 0 or i == 3), (i == 0 or i == 1), is_shift)

            for i, k in enumerate([Qt.Key_Q, Qt.Key_W, Qt.Key_E, Qt.Key_A, Qt.Key_S, Qt.Key_D, Qt.Key_Z, Qt.Key_X, Qt.Key_C]):
                if k == key:
                    if is_pure:
                        multi_key = ["q", "w", "e", "a", "s", "d", "z", "x", "c"]
                        self.MultiKey(multi_key[i])


        return super().eventFilter(obj, event)
        
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.adaptive_manager.AdaptiveResize()

    def __setupStyles(self):
        """统一设置应用样式表"""
        # 加载字体
        font_id = QFontDatabase.addApplicationFont("./images/zpix.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        pix_font_family = font_families[0] if font_families else "Arial"
        # 应用样式表到整个应用
        import utils.stylesheet
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