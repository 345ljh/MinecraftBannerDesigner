from PyQt5.QtWidgets import (QApplication, QSizePolicy, QWidget, QVBoxLayout)
from PyQt5.QtCore import Qt
import sys

import ui_toolbox
import AdaptiveManager
class ToolBox(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = ui_toolbox.Ui_ToolBox()
        self.ui.setupUi(self)

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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToolBox()
    window.show()
    sys.exit(app.exec_())