from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QStandardItemModel, QStandardItem
import sys

import ui_single_banner_designer
import PatternSelector
import pattern
import AdaptiveManager

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
        grid_y = self.height() / 40
        grid_x = self.width() / 20

        for index in range(len(self.patterns_data)):
            r, g, b, a = QColor(*pattern.color[self.patterns_data[index][0]]).getRgb()
            style_index = self.patterns_data[index][1]

            for y in range(40):
                for x in range(20):
                    color = QColor(r, g, b, pattern.getIcon(pattern.type[style_index])[y, x])
                    painter.fillRect(round(x * grid_x), round(y * grid_y), 
                                     round((x + 1) * grid_x) - round(x * grid_x),
                                     round((y + 1) * grid_y) - round(y * grid_y), color)  # 消除非整数网格
            
        
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
        self.pattern_len = 0

        # 替换原有的 BannerPainter 为自定义控件
        self.__replaceBannerPainter()

        # 实现comboBox中选项背景带颜色
        model = QStandardItemModel()
        for key in pattern.color:
            # self.ui.BannerColorComboBox.addItem(key)
            item = QStandardItem(key)
            item.setBackground(QColor(*pattern.color[key]))
            gray = int((pattern.color[key][0] + pattern.color[key][1] + pattern.color[key][2]) / 3)
            item.setForeground(gray >= 128 and QColor(0, 0, 0) or QColor(255, 255, 255))
            model.appendRow(item)

        item = QStandardItem("no banner")
        item.setBackground(QColor(230, 230, 230))
        item.setForeground(QColor(0, 0, 0))
        model.appendRow(item)

        # 底色选项
        self.ui.BannerColorComboBox.setModel(model)

        # 处理图案染色对象
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

        for i in range(1):
            w = PatternSelector.PatternSelector(i)
            w.patternChanged.connect(self.BannerDisplay)
            self.ui.PatternVLayout.addWidget(w)

        self.ui.BannerColorComboBox.currentIndexChanged.connect(self.BannerDisplay)
        self.ui.AddButton.clicked.connect(self.AddPattern)

        self.adaptive_components = [
            self.banner_displayer, self.ui.BannerColorLabel, self.ui.BannerColorComboBox, self.ui.scrollArea,
            self.ui.AddButton, self.ui.ClearButton, self.ui.CopyButton, self.ui.PasteButton, self.ui.UndoButton, self.ui.RedoButton, self.ui.UpdateButton
        ]
        self.adaptive_manager = AdaptiveManager.AdaptiveManager(self, self.adaptive_components)
    
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.adaptive_manager.AdaptiveResize()
        r = self.adaptive_manager.getCurrentRatio()
        self.ui.PatternVLayout.setSpacing(int(PatternSelector.PatternSelector().height() * r[1]))
        self.ui.PatternVLayout.setContentsMargins(0, 0, 0, int(PatternSelector.PatternSelector().height() * r[1]))  # 使滚轮能显示所有控件

    def __replaceBannerPainter(self):
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
        '''直接读取控件中的index进行渲染'''
        self.PatternChanged.emit()
        if self.ui.BannerColorComboBox.currentIndex() != 16:
            # 设置背景颜色
            bg_color = QColor(*pattern.color[self.ui.BannerColorComboBox.currentText()])
            self.banner_displayer.setBackgroundColor(bg_color)
            
            # 设置图案
            patterns_data = []
            for pattern_index in range(self.pattern_len):
                patterns_data.append([
                    self.ui.PatternVLayout.itemAt(pattern_index).widget().ui.ColorComboBox.currentText(),  # color_text
                    self.ui.PatternVLayout.itemAt(pattern_index).widget().button_group.checkedId()  # type_index
                ])

            self.banner_displayer.setPatternsData(patterns_data)
        else:
            # 空旗帜
            self.banner_displayer.setBackgroundColor(QColor(230, 230, 230))
            self.banner_displayer.setPatternsData([])

    def AddPattern(self):
        '''添加图案'''
        w = PatternSelector.PatternSelector(self.pattern_len)
        print(w.width(), w.height())
        self.ui.PatternVLayout.addWidget(w)
        self.ui.PatternVLayout.itemAt(self.pattern_len).widget().sequenceOperation.connect(lambda x, y: print(x, y))
        w.patternChanged.connect(self.BannerDisplay)
        self.pattern_len += 1
        self.BannerDisplay()

    def LoadBanner(self, str):
        '''加载字符串形式的旗帜'''
        # 单旗帜表示
        splited = str.split(':')
        self.ui.BannerColorComboBox.setCurrentIndex(int(splited[0]))
        self.pattern_len = (len(splited) - 1) // 2
        # 清空原有染色步骤
        while self.ui.PatternVLayout.count():
            item = self.ui.PatternVLayout.takeAt(0)
            widget = item.widget()
            if widget:
                try:
                    widget.blockSignals(True) 
                    widget.disconnect()
                except:
                    pass 
                widget.deleteLater() 
        # 添加新染色步骤
        for i in range(self.pattern_len):
            w = PatternSelector.PatternSelector(i)
            self.ui.PatternVLayout.addWidget(w)
            self.ui.PatternVLayout.itemAt(i).widget().button_group.button(int(splited[2*i+1])).setChecked(True)
            self.ui.PatternVLayout.itemAt(i).widget().ui.ColorComboBox.setCurrentIndex(int(splited[2*i+2]))
            self.ui.PatternVLayout.itemAt(i).widget().sequenceOperation.connect(lambda x, y: print(x, y))
            w.patternChanged.connect(self.BannerDisplay)
        self.BannerDisplay()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SingleBannerDesigner()
    window.LoadBanner("0:1:1:3:3")
    window.show()
    sys.exit(app.exec_())
