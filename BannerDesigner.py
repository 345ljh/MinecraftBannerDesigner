from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout, QSizePolicy, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor
import sys

import SingleBannerDesigner
import ui_banner_designer
import pattern

class BannerDesigner(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = ui_banner_designer.Ui_BannerDesigner()
        self.ui.setupUi(self)

        self.now_banner = [0, 0]
        self.banner_pattern = {}

        self.single_designer = SingleBannerDesigner.SingleBannerDesigner()
        self.single_designer.setGeometry(0, 0, 800, 600)
        self.single_designer.setParent(self)

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
                if(f"{_i},{j}" not in self.banner_pattern):
                    self.banner_pattern[f"{_i},{j}"] = "0,0,0,0,0,0,0,0,0,0,0,0,0"

        self.GridButtonClicked(self.ui.RowSpinBox.value() - 2, 0)


    def GridButtonClicked(self, i, j):
        try:  # 防减少行列数越界
            self.ui.GridLayout.itemAtPosition(self.now_banner[0], self.now_banner[1]).widget().setStyleSheet("background-color: white")
        except:
            pass
        self.now_banner = [i, j]
        self.ui.GridLayout.itemAtPosition(i, j).widget().setStyleSheet("background-color: rgb(255, 128, 128)")

        _i = self.ui.RowSpinBox.value() - i - 1
        self.single_designer.LoadPattern(self.banner_pattern[f"{_i},{j}"])

    def SaveBanner(self):  # 暂存旗帜
        self.ui.GridLayout.itemAtPosition(self.now_banner[0], self.now_banner[1]).widget().setStyleSheet("background-color: rgb(128, 255, 128)")
        s = f"{self.single_designer.ui.BannerColorComboBox.currentIndex()},"
        for i in range(6):
            s += f"{self.single_designer.ui.PatternVLayout.itemAt(i).widget().button_group.checkedId()}, \
            {self.single_designer.ui.PatternVLayout.itemAt(i).widget().ui.PatternColorComboBox.currentIndex()},"
        self.banner_pattern[f"{self.ui.RowSpinBox.value() - self.now_banner[0] - 1},{self.now_banner[1]}"] = s




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BannerDesigner()
    window.show()
    sys.exit(app.exec_())