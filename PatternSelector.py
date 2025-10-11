from PyQt5.QtWidgets import (QApplication, QSizePolicy, QWidget, QHBoxLayout,
                             QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QIcon
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

        # 底色选项
        self.ui.PatternColorComboBox.currentIndexChanged.connect(self.patternChanged.emit)
        for key in pattern.color:
            self.ui.PatternColorComboBox.addItem(key)

        while self.ui.PatternStyleHLayout.count():
            item = self.ui.PatternStyleHLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(self.ui.scrollAreaWidgetContents)  # 转移父控件
        self.ui.horizontalLayoutWidget_2.deleteLater()
        self.ui.PatternStyleHLayout = QHBoxLayout(self.ui.scrollAreaWidgetContents)
        
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.ui.PatternStyleHLayout.setAlignment(Qt.AlignLeft)
        self.ui.PatternStyleHLayout.setSpacing(1)

        self.button_group = QButtonGroup(self)
        for i, name in enumerate(pattern.type):
            icon = pattern.getIcon(name)
            icon_qimage = QImage(icon.tobytes(), 20, 40, 20, QImage.Format_Grayscale8)

            radio = QRadioButton()
            radio.setIcon(QIcon(QPixmap.fromImage(icon_qimage)))
            radio.clicked.connect(self.patternChanged)
            self.button_group.addButton(radio, i)
            self.ui.PatternStyleHLayout.addWidget(radio)

        self.button_group.button(0).setChecked(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PatternSelector()
    window.show()
    sys.exit(app.exec_())