from PyQt5.QtWidgets import (QApplication, QShortcut, QWidget, QGridLayout, QScrollArea, QVBoxLayout,
QSizePolicy, QPushButton, QFileDialog, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QKeySequence
import sys, os
import PIL
import pattern

# 显示完整的设计, widget大小理论上无限
class DesignPreviewerWidget(QWidget):
    onBannerClicked = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Design Previewer')
        self.setGeometry(0, 0, 800, 600)

        self.grid_size = 100  # 一个方块大小
        self.zoom_factor = 1  # 缩放因子
        self.real_margin = True  # 真实间距
        self.pattern_size = [3, 3]  # 行列数

        self.patterns_data = {}
        self.to_resize = False

    # 传入设计
    def SetPatternsData(self, patterns_data, size):
        self.patterns_data = patterns_data
        self.pattern_size = size
        self.to_resize = True
        self.update()

    # 渲染旗帜
    def paintEvent(self, event):
        # 计算窗口大小(计算取float)
        real_grid_size = self.grid_size * self.zoom_factor
        if self.real_margin:
            extra_offset_x = 2 * self.grid_size / 20
            extra_offset_y = 4 * self.grid_size / 20
        else:
            extra_offset_x = 0
            extra_offset_y = 0
        width = (real_grid_size + extra_offset_x * self.zoom_factor) * self.pattern_size[1]
        height = real_grid_size * self.pattern_size[0] + extra_offset_y * self.zoom_factor * (self.pattern_size[0] - 1)
        # 重设窗口大小
        if self.to_resize:
            self.setFixedSize(int(width), int(height))

        # 从上到下依次绘制图案
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        painter.scale(self.zoom_factor, self.zoom_factor)  # 应用变换矩阵
            
        # 填充白色背景
        painter.fillRect(0, 0, int(width / self.zoom_factor), int(height / self.zoom_factor), QColor(255, 255, 255))
            
        for row in range(1, self.pattern_size[0]):
            for column in range(self.pattern_size[1]):
                # 此处为原始坐标
                y_offset = int(round((self.grid_size + extra_offset_y) * (self.pattern_size[0] - row - 1), 0))
                x_offset = int(round((self.grid_size + extra_offset_x) * column + extra_offset_x / 2, 0))
                
                pattern_key = f"{row}:{column}"
                if pattern_key in self.patterns_data:

                    p = self.patterns_data[pattern_key].split(":")           
                    if p[0] == "16":
                        continue
                    
                    # 绘制背景矩形
                    bg_color = QColor(*pattern.color[pattern.color_name[int(p[0])]])
                    painter.fillRect(x_offset, y_offset, self.grid_size, 2 * self.grid_size, bg_color)
                    
                    # 绘制图案
                    for i in range(pattern.MAX_BANNER):
                        try:
                            color_idx = int(p[2 * i + 2])
                            pattern_idx = int(p[2 * i + 1])
                            
                            icon = pattern.getIcon(pattern.type[pattern_idx])
                            
                            for y in range(40):
                                for x in range(20):
                                    pattern_color = QColor(*pattern.color[pattern.color_name[color_idx]] + [icon[y,x]])
                                    painter.fillRect(x_offset + x * 5, y_offset + y * 5, 5, 5, pattern_color)
                        except IndexError:
                            pass

    # 鼠标点击响应
    def mousePressEvent(self, event):
        real_grid_size = self.grid_size * self.zoom_factor
        if self.real_margin:
            extra_offset_x = 2 * self.grid_size / 20
            extra_offset_y = 4 * self.grid_size / 20
        else:
            extra_offset_x = 0
            extra_offset_y = 0
        # 获取点击坐标
        x = event.x() / self.zoom_factor
        y = event.y() / self.zoom_factor
        # 计算行列
        column = int(x // (self.grid_size + extra_offset_x))
        row = self.pattern_size[0] - 1 - int(y // (self.grid_size + extra_offset_y))
        self.onBannerClicked.emit([row, column])
        

# 对DesignPreviewerWidget进行接口封装, 以及使用滚轮实现固定大小窗口
class DesignPreviewer(QWidget):
    onBannerClicked = pyqtSignal(list)  # 点击显示界面, 返回对应banner的行列数

    def __init__(self):
        super().__init__()
        self.previewer = DesignPreviewerWidget()
        self.previewer.onBannerClicked.connect(self.onBannerClicked.emit)
        self.onBannerClicked.connect(lambda x: print(x))
        self.setupUi()
    
    def setupUi(self):
        self.setGeometry(0, 0, 1000, 800)
        self.setWindowTitle('DesignPreviewer Example')
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 允许widget调整大小
        
        # 将previewer放入滚动区域
        scroll_area.setWidget(self.previewer)
        
        # 设置主布局 - 只包含滚动区域
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

    def SetZoomFactor(self, zoom_factor):
        '''
        设置缩放比例
            zoom_factor: 缩放比例(1.0为原始大小)
        '''
        self.previewer.zoom_factor = zoom_factor
        self.previewer.to_resize = True
        self.update()

    def SetPatternsData(self, patterns_data, size):
        '''
        传入设计
            patterns_data: 设计数据  dict{'r:c': 'b:p:c:p:c:...', ...}
            size: 设计大小 [row, column]
        '''
        self.previewer.SetPatternsData(patterns_data, size)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    default_patterns = {'7:0': '16', '7:1': '0:11:9:10:9:26:0:27:0', '7:2': '0:10:9:28:0:11:9:8:9:27:0', '7:3': '0:30:9:29:0:5:9:1:0:2:0:35:9', '7:4': '0:10:9:26:0:12:9:7:9:27:0', '7:5': '0:12:9:10:9:28:0:27:0', '7:6': '16', '6:0': '16:30:9:21:0:11:9:9:9:22:0:26:0', '6:1': '16:30:9:22:0:21:0', '6:2': '16:10:9:9:9:7:0:27:0', '6:3': '16', '6:4': '16:10:9:9:9:8:0:27:0', '6:5': '16:30:9:22:0:21:0', '6:6': '16:30:9:22:0:12:9:9:9:21:0:28:0', '5:0': '0:30:9:21:0:11:9:9:9:22:0:26:0', '5:1': '0:30:9:22:0:21:0', '5:2': '0:10:9:9:9:7:0:27:0', '5:3': '9:4:0:3:0:29:0', '5:4': '0:10:9:9:9:8:0:27:0', '5:5': '0:30:9:22:0:21:0', '5:6': '0:30:9:22:0:12:9:9:9:21:0:28:0', '4:0': '16', '4:1': '16', '4:2': '16', '4:3': '16', '4:4': '16', '4:5': '16', '4:6': '16', '3:0': '0:25:9:29:9:9:9', '3:1': '0:8:9:29:9', '3:2': '0:13:9:30:0:6:9', '3:3': '9:13:0:6:9:5:9', '3:4': '0:13:9:30:0:6:9', '3:5': '0:7:9:29:9', '3:6': '0:25:9:29:9:9:9', '2:0': '16', '2:1': '16', '2:2': '16', '2:3': '16', '2:4': '16', '2:5': '16', '2:6': '16', '1:0': '16', '1:1': '0:12:9:10:9:20:0:29:0', '1:2': '0:12:9:10:9:27:0:8:0:6:9:5:9', '1:3': '0:6:9:5:9', '1:4': '0:11:9:10:9:27:0:7:0:6:9:5:9', '1:5': '0:11:9:10:9:23:0:29:0', '1:6': '16', '8:0': '16', '8:1': '16', '8:2': '16', '8:3': '16', '8:4': '16', '8:5': '16', '8:6': '16', '9:0': '16', '9:1': '16', '9:2': '16', '9:3': '16', '9:4': '16', '9:5': '16', '9:6': '16', '10:0': '16', '10:1': '16', '10:2': '16', '10:3': '16', '10:4': '16', '10:5': '16', '10:6': '16'}

    window = DesignPreviewer()
    window.show()
    window.SetPatternsData(default_patterns, [8, 7])
    sys.exit(app.exec_())