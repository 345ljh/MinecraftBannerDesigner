from PyQt5.QtWidgets import (QApplication, QSizePolicy, QWidget, QGridLayout,
                             QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QIcon, QStandardItemModel, QStandardItem, QColor
import sys
import cv2

import ui_pattern_selector
import pattern


class PatternSelector(QWidget):
    patternChanged = pyqtSignal()

    def __init__(self, index = 0):
        super().__init__()
        self.ui = ui_pattern_selector.Ui_PatternSelector()
        self.ui.setupUi(self)

        self.setFixedHeight(180)  # 保证父级Layout按照该高度排列

        self.ui.Index.setText(str(index))

        model = QStandardItemModel()
        for key in pattern.color:
            # self.ui.BannerColorComboBox.addItem(key)
            item = QStandardItem(key)
            item.setBackground(QColor(*pattern.color[key]))
            gray = int((pattern.color[key][0] + pattern.color[key][1] + pattern.color[key][2]) / 3)
            item.setForeground(gray >= 128 and QColor(0, 0, 0) or QColor(255, 255, 255))
            model.appendRow(item)

        # 底色选项
        self.ui.PatternColorComboBox.currentIndexChanged.connect(self.patternChanged.emit)
        for key in pattern.color:
            self.ui.PatternColorComboBox.setModel(model)

        while self.ui.PatternStyleGLayout.count():
            item = self.ui.PatternStyleGLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(self.ui.scrollAreaWidgetContents)  # 转移父控件
        self.ui.gridLayoutWidget.deleteLater()
        self.ui.PatternStyleGLayout = QGridLayout(self.ui.scrollAreaWidgetContents)
        
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.ui.PatternStyleGLayout.setAlignment(Qt.AlignLeft)
        self.ui.PatternStyleGLayout.setSpacing(1)

        self.button_group = QButtonGroup(self)
        for i, name in enumerate(pattern.type):
            icon = pattern.getIcon(name)
            icon_qimage = QImage((255 - icon).tobytes(), 20, 40, 20, QImage.Format_Grayscale8)

            radio = QRadioButton()
            radio.setIcon(QIcon(QPixmap.fromImage(icon_qimage)))
            radio.clicked.connect(self.patternChanged)
            self.button_group.addButton(radio, i)
            self.ui.PatternStyleGLayout.addWidget(radio, i // 6, i % 6)

        self.button_group.button(0).setChecked(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PatternSelector()
    window.show()
    sys.exit(app.exec_())