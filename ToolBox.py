from PyQt5.QtWidgets import (QApplication, QSizePolicy, QWidget, QVBoxLayout)
from PyQt5.QtCore import Qt
import sys

import ui_toolbox

class ToolBox(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = ui_toolbox.Ui_ToolBox()
        self.ui.setupUi(self)

        self.adaptive_components = [
            self.ui.FileLabel, self.ui.FilePathText, self.ui.FileLoadButton, self.ui.FileSaveButton,
            self.ui.DesignLabel, self.ui.DesignNameHintLabel, self.ui.DesignNameText, self.ui.DesignSelectHintLabel, self.ui.DesignSelectComboBox, self.ui.DesignSearchButton, self.ui.DesignSelectButton, self.ui.DesignRowHintLabel, self.ui.DesignRowSpinBox, self.ui.DesignColumnHintLabel, self.ui.DesignColumnSpinBox,
            self.ui.ViewLabel, self.ui.ViewPaddingCheckBox, self.ui.ViewZoomLabel, self.ui.ViewZoomUpButton, self.ui.ViewZoomDownButton,
            self.ui.EditLabel, self.ui.EditCopyButton, self.ui.EditPasteButton, self.ui.EditRedoButton, self.ui.EditUndoButton,
            self.ui.UtilsLabel, self.ui.UtilsDyeCalcButton, self.ui.UtilsGenCommandButton, self.ui.UtilsShortCutButton
        ]
        self.adaptive_component_ratios = [[1,1,1,1]] * len(self.adaptive_components)
        self.AdaptiveSetting()
        
    def AdaptiveSetting(self):
        '''自适应设置'''
        # 记录自适应组件初始尺寸在屏幕中的比例
        for i in range(len(self.adaptive_components)):
            self.adaptive_component_ratios[i] = [self.adaptive_components[i].width() / self.width(),
                                                 self.adaptive_components[i].height() / self.height(),
                                                 self.adaptive_components[i].x() / self.width(),
                                                 self.adaptive_components[i].y() / self.height(),
                                                 self.adaptive_components[i].font().pointSize() / self.height()]  # 字号
        # print(self.adaptive_component_ratios)
            
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        for i in range(len(self.adaptive_components)):
            self.adaptive_components[i].setGeometry(int(self.width() * self.adaptive_component_ratios[i][2]),
                                                    int(self.height() * self.adaptive_component_ratios[i][3]),
                                                    int(self.width() * self.adaptive_component_ratios[i][0]),
                                                    int(self.height() * self.adaptive_component_ratios[i][1]))
            font = self.adaptive_components[i].font()
            font.setPointSize(int(self.height() * self.adaptive_component_ratios[i][4]))
            self.adaptive_components[i].setFont(font)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToolBox()
    window.show()
    sys.exit(app.exec_())