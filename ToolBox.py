from PyQt5.QtWidgets import (QApplication, QSizePolicy, QWidget, QVBoxLayout)
from PyQt5.QtCore import Qt
import sys

import ui_toolbox

class ToolBox(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = ui_toolbox.Ui_ToolBox()
        self.ui.setupUi(self)

        self.blocks = [self.ui.FileButtonGridWidget]
        self.buttons = [[self.ui.FileLoadButton, self.ui.FileSaveButton]]
        self.labels = [self.ui.FileLabel, self.ui.FilePathLabel, self.ui.FilePathHintLabel]
        self.AdaptiveSetting()
        
    def AdaptiveSetting(self):
        '''自适应设置'''
        self.ui.ToolBoxVLayout.setAlignment(Qt.AlignTop)
        for block_id, block in enumerate(self.blocks):   
            # 设置按钮的宽高比例约束
            for button in self.buttons[block_id]:
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumSize(80, 80)
                button.setMaximumSize(200, 200)
            # 设置水平布局的约束
            for i in range(len(self.buttons[block_id])):
                self.ui.FileButtonGrid.setRowStretch(i, 1)
            self.ui.FileButtonGrid.setAlignment(Qt.AlignLeft)
            self.ui.FileButtonGrid.setAlignment(Qt.AlignTop)

    def resizeEvent(self, a0):
        super().resizeEvent(a0)

        for block_id, block in enumerate(self.blocks):   
            for button in self.buttons[block_id]:
                width = self.width()
                height = self.height()
                size_limit = max(min(width, height) // 8, 80)
                button.setMaximumSize(size_limit, size_limit)  # 动态设置设置最大尺寸避免过大
        for label in self.labels:
                # 设置label最大高度
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                font_height = label.fontMetrics().height()
                label.setFixedHeight(font_height + 8)  # 固定高度，不会影响布局



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToolBox()
    window.show()
    sys.exit(app.exec_())