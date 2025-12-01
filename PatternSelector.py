from PyQt5.QtWidgets import (QApplication, QSizePolicy, QWidget, QGridLayout,
                             QPushButton, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QIcon, QStandardItemModel, QStandardItem, QColor
import sys
import cv2

import ui_pattern_selector
import utils.AdaptiveManager as AdaptiveManager
import utils.pattern as pattern


class PatternSelector(QWidget):
    patternChanged = pyqtSignal()  # 图案修改
    sequenceOperation = pyqtSignal(int, int)  # 序列调整或删除(par0:id, par1:向上0,向下1,删除2)

    def __init__(self, index = 0):
        super().__init__()
        self.ui = ui_pattern_selector.Ui_PatternSelector()
        self.ui.setupUi(self)

        # 只包含需要自适应的主要组件，不包括按钮
        self.adaptive_components = [
            self.ui.ColorComboBox, self.ui.ColorHintLabel, self.ui.UpButton, self.ui.DownButton, self.ui.DeleteButton,
            self.ui.Index, self.ui.PatternHintLabel,
            self.ui.scrollArea  # scrollArea自适应，内容会自动调整
        ]
        self.adaptive_manager = AdaptiveManager.AdaptiveManager(self, self.adaptive_components)

        self.ui.UpButton.clicked.connect(lambda: self.sequenceOperation.emit(int(self.ui.Index.text()), 0))
        self.ui.DownButton.clicked.connect(lambda: self.sequenceOperation.emit(int(self.ui.Index.text()), 1))
        self.ui.DeleteButton.clicked.connect(lambda: self.sequenceOperation.emit(int(self.ui.Index.text()), 2))
        self.ui.Index.setText(str(index))

        model = QStandardItemModel()
        for key in pattern.color:
            item = QStandardItem(key)
            item.setBackground(QColor(*pattern.color[key]))
            gray = int((pattern.color[key][0] + pattern.color[key][1] + pattern.color[key][2]) / 3)
            item.setForeground(gray >= 128 and QColor(0, 0, 0) or QColor(255, 255, 255))
            model.appendRow(item)

        # 底色选项
        self.ui.ColorComboBox.currentIndexChanged.connect(self.patternChanged.emit)
        for key in pattern.color:
            self.ui.ColorComboBox.setModel(model)

        # 清理原有布局并重新设置
        while self.ui.PatternStyleGLayout.count():
            item = self.ui.PatternStyleGLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutWidget.deleteLater()
        self.ui.PatternStyleGLayout = QGridLayout(self.ui.scrollAreaWidgetContents)
        
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.ui.PatternStyleGLayout.setAlignment(Qt.AlignLeft)
        self.ui.PatternStyleGLayout.setSpacing(1)

        # 设置列的比例，每列平均分配宽度
        for col in range(6):
            self.ui.PatternStyleGLayout.setColumnStretch(col, 1)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)  # 确保单选效果
        
        self.pattern_buttons = []
        
        for i, name in enumerate(pattern.type):
            icon = pattern.getIcon(name)
            icon_qimage = QImage((255 - icon).tobytes(), 20, 40, 20, QImage.Format_Grayscale8)

            button = QPushButton()
            button.setCheckable(True)
            button.setIcon(QIcon(QPixmap.fromImage(icon_qimage)))
            
            # 设置按钮尺寸策略：横向扩展，纵向固定（但通过样式表保持正方形）
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # 设置按钮样式 - 使用百分比保持正方形
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(180,180,180);
                    border: 1px solid gray;
                    max-width: 100px;
                    min-width: 20px;
                }
                QPushButton:checked {
                    background-color: rgb(255,160,160);
                    border: 2px solid darkred;
                }
            """)
            
            button.clicked.connect(self.patternChanged.emit)
            
            self.button_group.addButton(button, i)
            self.ui.PatternStyleGLayout.addWidget(button, i // 6, i % 6)
            self.pattern_buttons.append(button)

        # 设置第一个按钮为选中状态
        self.button_group.button(0).setChecked(True)

    def setIndex(self, index):
        self.ui.Index.setText(str(index))

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.adaptive_manager.AdaptiveResize()
        # 在resize事件中设置按钮为正方形
        self.updateButtonAspectRatio()
        

    def updateButtonAspectRatio(self):
        """更新按钮的宽高比，保持正方形"""
        if self.pattern_buttons:
            # 使用固定的列数计算，避免循环依赖
            columns = 6
            spacing = self.ui.PatternStyleGLayout.spacing()
            
            # 基于整个widget的宽度来计算，或者使用scrollArea的固定宽度
            available_width = self.ui.scrollArea.width() - 20  # 减去滚动条等边距
            
            column_width = (available_width - spacing * (columns - 1)) // columns
            
            # 设置所有按钮的固定尺寸为正方形
            for button in self.pattern_buttons:
                button.setFixedSize(column_width, column_width)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PatternSelector()
    window.show()
    sys.exit(app.exec_())