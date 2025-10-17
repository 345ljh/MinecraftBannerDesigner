from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor
import sys

import ui_single_banner_designer
import PatternSelector
import pattern


class BannerDisplayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border: 1px solid black;")
        self.background_color = QColor(255, 255, 255)
        self.patterns_data = []
        
    def setBackgroundColor(self, color):
        self.background_color = color
        self.update()
        
    def setPatternsData(self, patterns_data):
        self.patterns_data = patterns_data
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), self.background_color)

        # 绘制图案
        grid_y = self.height() // 40
        grid_x = self.width() // 20

        for index in range(len(self.patterns_data)):
            r, g, b, a = QColor(*pattern.color[self.patterns_data[index][0]]).getRgb()
            style_index = self.patterns_data[index][1]

            for y in range(40):
                for x in range(20):
                    color = QColor(r, g, b, pattern.getIcon(pattern.type[style_index])[y, x])
                    painter.fillRect(x * grid_x, y * grid_y, grid_x, grid_y, color)
            
        
        # 绘制边框
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRect(0, 0, self.width(), self.height())
        
        painter.end()


class SingleBannerDesigner(QWidget):
    PatternChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = ui_single_banner_designer.Ui_SingleBannerDesigner()
        self.ui.setupUi(self)

        # 替换原有的 BannerPainter 为自定义控件
        self.replaceBannerPainter()

        # 底色选项
        for key in pattern.color:
            self.ui.BannerColorComboBox.addItem(key)

        # 图案选项
        while self.ui.PatternVLayout.count():
            item = self.ui.PatternVLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(self.ui.scrollAreaWidgetContents)
        self.ui.verticalLayoutWidget.deleteLater()
        self.ui.PatternVLayout = QVBoxLayout(self.ui.scrollAreaWidgetContents)
        
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) 
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.ui.PatternVLayout.setAlignment(Qt.AlignTop)
        self.ui.PatternVLayout.setSpacing(5)

        for i in range(6):
            w = PatternSelector.PatternSelector(i)
            w.patternChanged.connect(self.BannerDisplay)
            self.ui.PatternVLayout.addWidget(w)

        self.ui.BannerColorComboBox.currentIndexChanged.connect(self.BannerDisplay)
        
        # 初始显示
        self.BannerDisplay()

    def replaceBannerPainter(self):
        old_widget = self.ui.BannerPainter
        parent = old_widget.parent()
        
        if parent and hasattr(parent, 'layout') and parent.layout():
            layout = parent.layout()
            
            # 找到 old_widget 在布局中的位置
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() == old_widget:
                    # 创建自定义控件
                    self.banner_displayer = BannerDisplayer(parent)
                    
                    # 复制属性
                    self.banner_displayer.setMinimumSize(old_widget.minimumSize())
                    self.banner_displayer.setMaximumSize(old_widget.maximumSize())
                    self.banner_displayer.setSizePolicy(old_widget.sizePolicy())
                    
                    # 替换控件
                    layout.replaceWidget(old_widget, self.banner_displayer)
                    old_widget.deleteLater()
                    break
        else:
            # 如果没有布局，直接替换
            self.banner_displayer = BannerDisplayer(old_widget.parent())
            self.banner_displayer.setGeometry(old_widget.geometry())
            old_widget.deleteLater()

    def BannerDisplay(self):
        self.PatternChanged.emit()
        # 设置背景颜色
        bg_color = QColor(*pattern.color[self.ui.BannerColorComboBox.currentText()])
        self.banner_displayer.setBackgroundColor(bg_color)
        
        # 设置图案
        patterns_data = []
        for pattern_index in range(6):
            patterns_data.append([
                self.ui.PatternVLayout.itemAt(pattern_index).widget().ui.PatternColorComboBox.currentText(),  # color_text
                self.ui.PatternVLayout.itemAt(pattern_index).widget().button_group.checkedId()  # type_index
            ])

        self.banner_displayer.setPatternsData(patterns_data)

    def LoadPattern(self, str):
        # 单旗帜表示,长度13
        splited = str.split(':')
        # 补0
        while len(splited) < 13:
            splited.append('0')
        self.ui.BannerColorComboBox.setCurrentIndex(int(splited[0]))
        for i in range(6):
            self.ui.PatternVLayout.itemAt(i).widget().button_group.button(int(splited[2*i+1])).setChecked(True)
            self.ui.PatternVLayout.itemAt(i).widget().ui.PatternColorComboBox.setCurrentIndex(int(splited[2*i+2]))
        self.BannerDisplay()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SingleBannerDesigner()
    window.show()
    sys.exit(app.exec_())
