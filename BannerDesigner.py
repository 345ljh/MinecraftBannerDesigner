import PIL.Image
import PIL.ImageDraw
import PIL.ImageTk
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout, QSizePolicy, QPushButton, QFileDialog, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QImage
import sys, os, tkinter
import PIL

import SingleBannerDesigner
import ui_banner_designer
import pattern

class BannerDesigner(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = ui_banner_designer.Ui_BannerDesigner()
        self.ui.setupUi(self)

        self.filepath = ""
        self.designs = {}
        self.current_design_name = ""
        self.current_banner = [0, 0]
        self.current_banner_pattern = {}

        self.displaywindow = None

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
            lambda: self.ui.GridLayout.itemAtPosition(self.current_banner[0], self.current_banner[1]).widget().setStyleSheet("background-color: rgb(255, 128, 128)"))
        self.ui.OpenFileButton.clicked.connect(self.OpenFile)
        self.ui.SaveFileButton.clicked.connect(self.SaveFile)
        self.ui.DesignSelectComboBox.currentIndexChanged.connect(lambda: self.LoadDesign(self.ui.DesignSelectComboBox.currentText()))
        self.ui.NewDesignButton.clicked.connect(self.NewDesign)
        self.ui.DisplayButton.clicked.connect(self.DisplayDesign)

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
                if(f"{_i}:{j}" not in self.current_banner_pattern):
                    self.current_banner_pattern[f"{_i}:{j}"] = "0:0:0:0:0:0:0:0:0:0:0:0:0"

        self.GridButtonClicked(self.ui.RowSpinBox.value() - 2, 0)

    def GridButtonClicked(self, i, j):
        try:  # 防减少行列数越界
            self.ui.GridLayout.itemAtPosition(self.current_banner[0], self.current_banner[1]).widget().setStyleSheet("background-color: white")
        except:
            pass
        self.current_banner = [i, j]
        self.ui.GridLayout.itemAtPosition(i, j).widget().setStyleSheet("background-color: rgb(255, 128, 128)")

        _i = self.ui.RowSpinBox.value() - i - 1
        self.single_designer.LoadPattern(self.current_banner_pattern[f"{_i}:{j}"])

    def SaveBanner(self):  # 暂存旗帜
        self.ui.GridLayout.itemAtPosition(self.current_banner[0], self.current_banner[1]).widget().setStyleSheet("background-color: rgb(128, 255, 128)")
        s = f"{self.single_designer.ui.BannerColorComboBox.currentIndex()}:"
        for i in range(6):
            s += f"{self.single_designer.ui.PatternVLayout.itemAt(i).widget().button_group.checkedId()}:{self.single_designer.ui.PatternVLayout.itemAt(i).widget().ui.PatternColorComboBox.currentIndex()}:"
        self.current_banner_pattern[f"{self.ui.RowSpinBox.value() - self.current_banner[0] - 1}:{self.current_banner[1]}"] = s[:-1]
        self.SaveDesign()

    def SaveDesign(self): 
        current_design_value = []
        for key in self.current_banner_pattern.keys():
            current_design_value.append(str(key) + ":" + str(self.current_banner_pattern[key]))

        self.designs[self.current_design_name] = [str(self.ui.RowSpinBox.value()), str(self.ui.ColumnSpinBox.value()), current_design_value]

    def OpenFile(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        if path:
            self.designs = {}
            self.filepath = path
            self.ui.FilePathLabel.setText(path)
            if os.path.exists(path):
                self.ui.DesignSelectComboBox.clear()
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
                        self.designs[line[0]] = [line[1], line[2], line[3:]]
                        self.ui.DesignSelectComboBox.addItem(line[0])
                    # 加载第一个
                    if self.designs != {}:
                        self.ui.DesignSelectComboBox.setCurrentIndex(0)
                        self.LoadDesign(self.ui.DesignSelectComboBox.itemText(0))

    def SaveFile(self):
        # 检查路径是否为空
        if self.filepath == "":
            self.filepath, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        # 打开文件
        if self.filepath != "":
            with open(self.filepath, "w") as f:
                for name in self.designs:
                    design = self.designs[name]
                    design_str = f"{name},{design[0]},{design[1]},"
                    for banner in design[2]:
                        design_str = design_str + banner + ","
                    f.write(f"{design_str[:-1]}\n")

    def LoadDesign(self, name: str):
        if name != "" and name in self.designs and self.current_banner_pattern != {}:
            self.current_banner_pattern = {}
            # 记录坐标
            self.ui.RowSpinBox.setValue(int(self.designs[name][0]))
            self.ui.ColumnSpinBox.setValue(int(self.designs[name][1]))
            self.UpdateGridButton()
            # 依次存储单面旗帜字符串
            for b in self.designs[name][2]:
                if b != "":
                    p = b.split(":", 2)
                    self.current_banner_pattern[f"{p[0]}:{p[1]}"] = p[2]
            self.current_banner = [0, 0]
            self.GridButtonClicked(self.ui.RowSpinBox.value() - 2, 0)
            self.single_designer.LoadPattern(self.current_banner_pattern["1:0"])
            self.current_design_name = name
            return True
        else:
            return False

    def NewDesign(self):
        name = self.ui.NewDesignTextEdit.toPlainText()
        if name != "":
            if ',' in name or ':' in name:
                self.ui.NewDesignTextEdit.setPlainText("无效的名称")
                return
            if not self.LoadDesign(name):
                self.designs[name] = ['2', '2', ['1:0:0:0:0:0:0:0:0:0:0:0:0:0:0', '1:1:0:0:0:0:0:0:0:0:0:0:0:0:0', '']]  # 初始化设计
            self.ui.NewDesignTextEdit.setPlainText("")
            self.ui.DesignSelectComboBox.addItem(name)
            self.ui.DesignSelectComboBox.setCurrentText(name)
        else:
            self.ui.NewDesignTextEdit.setPlainText("设计名不能为空")

    def DisplayDesign(self):
        if hasattr(self, 'display_window') and self.display_window:
            self.display_window.close()
        
        grid_size = 100
        width = grid_size * int(self.ui.RowSpinBox.value())
        height = grid_size * int(self.ui.ColumnSpinBox.value())
        
        # 创建绘制窗口
        self.display_window = QWidget()
        self.display_window.setWindowTitle("设计预览")
        self.display_window.setFixedSize(width, height)
        
        # 重写 paintEvent
        def paintEvent(event):
            painter = QPainter(self.display_window)
            painter.fillRect(0, 0, width, height, QColor(255, 255, 255))
            
            rows = self.ui.RowSpinBox.value()
            columns = self.ui.ColumnSpinBox.value()
            
            for row in range(1, rows):
                for column in range(columns):
                    y_offset = grid_size * (rows - row - 1)
                    x_offset = grid_size * column
                    
                    pattern_key = f"{row}:{column}"
                    if pattern_key in self.current_banner_pattern:
                        p = self.current_banner_pattern[pattern_key].split(":")
                        
                        # 绘制背景矩形
                        bg_color = QColor(*pattern.color[pattern.color_name[int(p[0])]])
                        painter.fillRect(x_offset, y_offset, grid_size, 2 * grid_size, bg_color)
                        
                        # 绘制图案
                        for i in range(6):
                            color_idx = int(p[2 * i + 2])
                            pattern_idx = int(p[2 * i + 1])
                            
                            icon = pattern.getIcon(pattern.type[pattern_idx])
                            
                            for y in range(40):
                                for x in range(20):
                                    pattern_color = QColor(*pattern.color[pattern.color_name[color_idx]] + [icon[y,x]])
                                    painter.fillRect(x_offset + x * 5, y_offset + y * 5, 5, 5, pattern_color)
        
        self.display_window.paintEvent = paintEvent
        self.display_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BannerDesigner()
    window.show()
    sys.exit(app.exec_())