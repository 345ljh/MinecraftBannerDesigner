from PyQt5.QtWidgets import (QApplication, QShortcut, QWidget, QGridLayout, QScrollArea, QVBoxLayout,
QSizePolicy, QPushButton, QFileDialog, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import sys, os
import pattern

import ui_toolbox
import AdaptiveManager

zoom_level_to_factor = [25,33,50,67,75,80,90,100,110,125,150,175,200,250,300,400,500]

class ToolBox(QWidget):
    LoadDesign = pyqtSignal(list)  # [row, col, [r1:c1:banner1, ...]]
    UpdateZoom = pyqtSignal(float, bool)  # zoom_factor, real_margin

    def __init__(self):
        super().__init__()
        self.ui = ui_toolbox.Ui_ToolBox()
        self.ui.setupUi(self)

        self.filepath = ""  # 当前文件路径
        self.designs = {}  # 设计列表: {'name': [row, col, [r1:c1:banner1, ...]]}
        self.search_designs = {}  # 搜索结果
        self.current_design_name = ""
        self.current_design_size = [3, 3]  # [row, col]
        self.current_design_patterns = {}  #  dict{'r:c': 'b:p:c:p:c:...', ...}
        self.zoom_level = 7  # 缩放等级, 对应100%
        self.banner_pos = [1, 0]  # 当前点击的banner的行列数

        self.ui.FileLoadButton.clicked.connect(self.OpenFile)
        self.ui.FileSaveButton.clicked.connect(self.SaveFile)
        self.ui.DesignSelectComboBox.currentIndexChanged.connect(self.DesignSelected)
        self.ui.DesignSearchButton.clicked.connect(self.SearchDesign)
        self.ui.DesignRowSpinBox.valueChanged.connect(self.ChangeDesignSize)
        self.ui.DesignColumnSpinBox.valueChanged.connect(self.ChangeDesignSize)
        self.ui.DesignSelectButton.clicked.connect(self.SelectDesign)
        self.ui.ViewZoomUpButton.clicked.connect(lambda: self.SetZoom(ZoomUp=True))
        self.ui.ViewZoomDownButton.clicked.connect(lambda: self.SetZoom(ZoomUp=False))
        self.ui.ViewPaddingCheckBox.clicked.connect(lambda: self.UpdateZoom.emit(zoom_level_to_factor[self.zoom_level] / 100, self.ui.ViewPaddingCheckBox.isChecked()))

        self.adaptive_components = [
            self.ui.FileLabel, self.ui.FilePathText, self.ui.FileLoadButton, self.ui.FileSaveButton,
            self.ui.DesignLabel, self.ui.DesignNameHintLabel, self.ui.DesignNameText, self.ui.DesignSelectHintLabel, self.ui.DesignSelectComboBox, self.ui.DesignSearchButton, self.ui.DesignSelectButton, self.ui.DesignRowHintLabel, self.ui.DesignRowSpinBox, self.ui.DesignColumnHintLabel, self.ui.DesignColumnSpinBox,
            self.ui.ViewLabel, self.ui.ViewPaddingCheckBox, self.ui.ViewZoomLabel, self.ui.ViewZoomUpButton, self.ui.ViewZoomDownButton,
            self.ui.UtilsLabel, self.ui.UtilsDyeCalcButton, self.ui.UtilsGenCommandButton, self.ui.UtilsShortCutButton
        ]
        self.adaptive_manager = AdaptiveManager.AdaptiveManager(self, self.adaptive_components)
        
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.adaptive_manager.AdaptiveResize()

    def OpenFile(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        if path:
            self.designs = {}
            self.filepath = path
            self.ui.FilePathText.setText(path)
            if os.path.exists(path):
                self.ui.DesignSelectComboBox.clear()
                # 使用UTF-8编码打开
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f.readlines():
                            try:
                                line = line.strip().split(",")
                                if len(line) < 3:  # 检验必要部分
                                    raise Exception("缺少关键信息")
                                for banner in line[3:]:  # 依次检验旗帜部分是否符合格式
                                    if banner == '':
                                        continue
                                    elems = banner.split(":")
                                    for elem_index, elem in enumerate(elems):  # 图案0~40, 颜色0~15
                                        if elem_index >= 2:
                                            if elem_index % 2 == 0:
                                                if int(elem) < 0 or int(elem) > 15 + (elem_index == 2):  # 不能转换int会报错
                                                    raise Exception("颜色值错误")
                                            else:
                                                if int(elem) < 0 or int(elem) > len(pattern.type):
                                                    raise Exception("图案值错误")
                                        else:
                                            if int(elem) < 0:
                                                raise Exception("坐标不能为负数")
                            except Exception as e:
                                print(e)
                                continue
                            # 存储
                            self.designs[line[0]] = [int(line[1]), int(line[2]), line[3:]]
                            self.ui.DesignSelectComboBox.addItem(line[0])
                        # 加载第一个
                        if self.designs != {}:
                            self.ui.DesignSelectComboBox.setCurrentIndex(0)
                            self.DesignSelected()
                except UnicodeDecodeError:
                    QMessageBox.warning(self, "错误", "文件编码不支持")

    def SaveFile(self):
        # 检查路径是否为空
        if self.filepath == "":
            self.filepath, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        # 打开文件
        if self.filepath != "":
            # 使用UTF-8编码保存
            with open(self.filepath, "w", encoding="utf-8") as f:
                for name in self.designs:
                    design = self.designs[name]
                    design_str = f"{name},{design[0]},{design[1]},"
                    for banner in design[2]:
                        design_str = design_str + banner + ","
                    f.write(f"{design_str[:-1]}\n")

    def DesignSelected(self):
        if self.ui.DesignSelectComboBox.currentText():
            r = self.designs[self.ui.DesignSelectComboBox.currentText()][0]
            c = self.designs[self.ui.DesignSelectComboBox.currentText()][1]
            self.ui.DesignRowSpinBox.setValue(r)  # 加载行数
            self.ui.DesignColumnSpinBox.setValue(c)  # 加载列数
            self.LoadDesign.emit(self.designs[self.ui.DesignSelectComboBox.currentText()])

    def ChangeDesignSize(self):
        if self.ui.DesignSelectComboBox.currentText():
            self.designs[self.ui.DesignSelectComboBox.currentText()][0] = self.ui.DesignRowSpinBox.value()
            self.designs[self.ui.DesignSelectComboBox.currentText()][1] = self.ui.DesignColumnSpinBox.value()
            self.LoadDesign.emit(self.designs[self.ui.DesignSelectComboBox.currentText()])
            
    def SearchDesign(self):
        '''匹配搜索'''
        self.search_designs = {}
        for design_name in self.designs:
            if self.ui.DesignNameText.text() in design_name:
                self.search_designs[design_name] = self.designs[design_name]
        self.ui.DesignSelectComboBox.clear()
        for name in self.search_designs:
            self.ui.DesignSelectComboBox.addItem(name)

    def SelectDesign(self):
        name = self.ui.DesignNameText.text()
        if name != "":
            if ',' in name or ':' in name:
                self.ui.DesignNameText.setText("无效的名称")
                return
            if name in self.designs:  # 名称已存在
                self.current_design_name = name
                self.ui.DesignSelectComboBox.setCurrentText(name)
                self.DesignSelected()
            else:
                self.designs[name] = [3,3,[]]
                self.ui.DesignSelectComboBox.addItem(name)
                self.ui.DesignSelectComboBox.setCurrentText(name)
                self.current_design_name = name
                self.DesignSelected()

            self.ui.DesignNameText.setText("")
        else:
            self.ui.DesignNameText.setText("设计名不能为空")

    def SetZoom(self, ZoomUp=True):
        if ZoomUp:
            if self.zoom_level < len(zoom_level_to_factor) - 1:
                self.zoom_level += 1
        else:
            if self.zoom_level > 0:
                self.zoom_level -= 1
        self.ui.ViewZoomLabel.setText(f"缩放: {zoom_level_to_factor[self.zoom_level]}%")
        self.UpdateZoom.emit(zoom_level_to_factor[self.zoom_level] / 100, self.ui.ViewPaddingCheckBox.isChecked())

    def SetPatternsData(self, patterns_data, size):
        self.current_design_patterns = patterns_data
        self.current_design_size = size

    def GetPatternsData(self):
        return self.current_design_patterns, self.current_design_size

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToolBox()
    window.show()
    sys.exit(app.exec_())