from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout, QSizePolicy, QPushButton, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor
import sys, os

import SingleBannerDesigner
import ui_banner_designer
import pattern

class BannerDesigner(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = ui_banner_designer.Ui_BannerDesigner()
        self.ui.setupUi(self)

        self.now_banner = [0, 0]
        self.now_banner_name = ""
        self.banner_pattern = {}
        self.filepath = ""
        self.fileload = {}

        self.single_designer = SingleBannerDesigner.SingleBannerDesigner()
        self.single_designer.setGeometry(0, 100, 800, 600)
        self.single_designer.setParent(self)
        self.ui.FilePathLabel.setWordWrap(True)

        while self.ui.GridLayout.count():
            item = self.ui.GridLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutWidget.deleteLater()
        self.ui.GridLayout = QGridLayout(self.ui.scrollAreaWidgetContents)
        
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) 
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.ui.GridLayout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.ui.GridLayout.setSpacing(5)

        self.UpdateGridButton()
        self.GridButtonClicked(0,0)

        self.ui.ColumnSpinBox.valueChanged.connect(self.UpdateGridButton)
        self.ui.RowSpinBox.valueChanged.connect(self.UpdateGridButton)
        self.single_designer.ui.SaveButton.clicked.connect(self.SaveBanner)
        self.single_designer.PatternChanged.connect( # 修改后提示未保存 
            lambda: self.ui.GridLayout.itemAtPosition(self.now_banner[0], self.now_banner[1]).widget().setStyleSheet("background-color: rgb(255, 128, 128)"))
        self.ui.FileButton.clicked.connect(self.OpenFile)
        self.ui.BannerSelectComboBox.currentIndexChanged.connect(lambda: self.LoadBanner(self.ui.BannerSelectComboBox.currentText()))

    def UpdateGridButton(self):
        while self.ui.GridLayout.count():
            item = self.ui.GridLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for i in range(self.ui.RowSpinBox.value() - 1):
            for j in range(self.ui.ColumnSpinBox.value()):
                _i = self.ui.RowSpinBox.value() - i - 1  # 图案定义的i为倒序排列, 且从1开始(最底下方块为0不放旗帜)
                button = QPushButton(f"{_i},{j}")
                button.setFixedSize(40, 40)
                button.setStyleSheet("background-color: white")
                self.ui.GridLayout.addWidget(button, i, j)
                button.clicked.connect(lambda checked, i=i, j=j: self.GridButtonClicked(i, j))
                if(f"{_i}:{j}" not in self.banner_pattern):
                    self.banner_pattern[f"{_i}:{j}"] = "0:0:0:0:0:0:0:0:0:0:0:0:0"

        self.GridButtonClicked(self.ui.RowSpinBox.value() - 2, 0)

    def GridButtonClicked(self, i, j):
        try:  # 防减少行列数越界
            self.ui.GridLayout.itemAtPosition(self.now_banner[0], self.now_banner[1]).widget().setStyleSheet("background-color: white")
        except:
            pass
        self.now_banner = [i, j]
        self.ui.GridLayout.itemAtPosition(i, j).widget().setStyleSheet("background-color: rgb(255, 128, 128)")

        _i = self.ui.RowSpinBox.value() - i - 1
        self.single_designer.LoadPattern(self.banner_pattern[f"{_i}:{j}"])

    def SaveBanner(self):  # 暂存旗帜
        self.ui.GridLayout.itemAtPosition(self.now_banner[0], self.now_banner[1]).widget().setStyleSheet("background-color: rgb(128, 255, 128)")
        s = f"{self.single_designer.ui.BannerColorComboBox.currentIndex()}:"
        for i in range(6):
            s += f"{self.single_designer.ui.PatternVLayout.itemAt(i).widget().button_group.checkedId()}: \
            {self.single_designer.ui.PatternVLayout.itemAt(i).widget().ui.PatternColorComboBox.currentIndex()}:"
        self.banner_pattern[f"{self.ui.RowSpinBox.value() - self.now_banner[0] - 1}:{self.now_banner[1]}"] = s
        
    def OpenFile(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        if path:
            self.fileload = {}
            self.filepath = path
            self.ui.FilePathLabel.setText(path)
            if os.path.exists(path):
                self.ui.BannerSelectComboBox.clear()
                # 按照csv格式解析
                # 名称,行数,列数,旗帜0,旗帜1,...
                with open(path, "r") as f:
                    for line in f.readlines():
                        try:
                            line = line.strip().split(",")
                            if(line.__len__() < 3):  # 检验必要部分
                                raise Exception("缺少关键信息")
                            for banner in line[3:]:  # 依次检验旗帜部分是否符合格式
                                if banner == '':
                                    continue
                                elems = banner.split(":")
                                if(elems.__len__() < 15):  # 检验长度, 其中[0:2]为坐标,[2:15]为颜色与图案
                                    raise Exception("长度错误")
                                for elem_index, elem in enumerate(elems):  # 图案0~40, 颜色0~15
                                    if elem_index >= 2:
                                        if elem_index % 2 == 0:
                                            if int(elem) < 0 or int(elem) > 15:  # 不能转换int会报错
                                                raise Exception("颜色值错误")
                                        else:
                                            if int(elem) < 0 or int(elem) > 40:
                                                raise Exception("图案值错误")
                                    else:
                                        if int(elem) < 0:
                                            raise Exception("坐标不能为负数")
                        except Exception as e:
                            print(e)
                            continue
                        # 存储
                        self.fileload[line[0]] = [line[1], line[2], line[3:]]
                        self.ui.BannerSelectComboBox.addItem(line[0])
                    # 加载第一个
                    if self.fileload != {}:
                        self.ui.BannerSelectComboBox.setCurrentIndex(0)
                        self.LoadBanner(self.ui.BannerSelectComboBox.itemText(0))

    def LoadBanner(self, name: str):
        if name != "" and name in self.fileload and self.banner_pattern != {}:
            self.banner_pattern = {}
            # 记录坐标
            self.ui.RowSpinBox.setValue(int(self.fileload[name][0]))
            self.ui.ColumnSpinBox.setValue(int(self.fileload[name][1]))
            self.UpdateGridButton()
            # 依次存储单面旗帜字符串
            for b in self.fileload[name][2]:
                if b != "":
                    p = b.split(":", 2)
                    self.banner_pattern[f"{p[0]}:{p[1]}"] = p[2]
            self.now_banner = [0, 0]
            self.GridButtonClicked(self.ui.RowSpinBox.value() - 2, 0)
            self.single_designer.LoadPattern(self.banner_pattern["1:0"])




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BannerDesigner()
    window.show()
    sys.exit(app.exec_())