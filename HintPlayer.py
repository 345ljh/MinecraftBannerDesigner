import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os

# images/hint下图片文件数量(图片需按顺序命名)
PAGES = len([f for f in os.listdir('images/hint') if f.endswith('.PNG')])

class HintPlayer(QMainWindow):
    """更现代化的图片播放器版本"""
    def __init__(self):
        super().__init__()
        self.images = []
        self.current_index = 0
        
        self.__initUI()
        self.__loadImages()
        
    def __initUI(self):
        """初始化现代化UI"""
        self.setWindowTitle('使用提示（可按←或→翻页）')
        self.setMinimumSize(400, 225)  # 最小保持16:9
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 使用网格布局
        layout = QGridLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 图片显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(100, 100)
        
        # 应用图片区域样式
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: none;
            }
        """)
        
        layout.addWidget(self.image_label, 0, 0, 1, 3)
        
        # 创建透明覆盖层用于导航提示
        self.overlay_left = QLabel(self.image_label)
        self.overlay_left.setAlignment(Qt.AlignCenter)
        self.overlay_left.setText("◀")
        self.overlay_left.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 100);
                color: white;
                font-size: 40px;
                font-weight: bold;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        self.overlay_left.hide()
        
        self.overlay_right = QLabel(self.image_label)
        self.overlay_right.setAlignment(Qt.AlignCenter)
        self.overlay_right.setText("▶")
        self.overlay_right.setStyleSheet(self.overlay_left.styleSheet())
        self.overlay_right.hide()
        
        # 底部控制栏
        control_panel = QWidget()
        control_panel.setFixedHeight(60)
        control_panel.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
            }
        """)
        
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 10, 20, 10)
        
        # 导航按钮
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        self.btn_prev = self.__createNavButton("◀", "上一张 (←)")
        self.btn_prev.clicked.connect(self.showPrevious)
        
        self.btn_next = self.__createNavButton("▶", "下一张 (→)")
        self.btn_next.clicked.connect(self.showNext)

        # 快捷键
        self.shortcut_previous = QShortcut(QKeySequence("Left"), self)
        self.shortcut_previous.activated.connect(self.showPrevious)
        self.shortcut_next = QShortcut(QKeySequence("Right"), self)
        self.shortcut_next.activated.connect(self.showNext)
        
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch(1)
        
        # 页码指示器
        self.page_indicator = QLabel()
        self.page_indicator.setAlignment(Qt.AlignCenter)
        self.page_indicator.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
                background-color: #404040;
                border-radius: 10px;
            }
        """)
        nav_layout.addWidget(self.page_indicator)
        
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.btn_next)
        
        control_layout.addLayout(nav_layout)
        
        layout.addWidget(control_panel, 1, 0, 1, 3)
        
        # 应用窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
        """)
        
    def __createNavButton(self, icon, tooltip=""):
        """创建导航按钮"""
        button = QPushButton(icon)
        button.setFixedSize(40, 40)
        button.setToolTip(tooltip)
        button.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: 2px solid #505050;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #606060;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QPushButton:disabled {
                background-color: #303030;
                color: #606060;
                border-color: #404040;
            }
        """)
        return button
        
    def __loadImages(self):
        """加载图片"""
        for i in range(PAGES):
            img_path = f"images/hint/{i}.png"
            pixmap = QPixmap(img_path)
            
            if not pixmap.isNull():
                self.images.append(pixmap)
            else:
                # 创建占位图片
                placeholder = QPixmap(800, 450)
                placeholder.fill(QColor(60, 60, 60))
                
                # 在占位图片上绘制文字
                painter = QPainter(placeholder)
                painter.setPen(QColor(200, 200, 200))
                painter.setFont(QFont("Arial", 20, QFont.Bold))
                painter.drawText(placeholder.rect(), Qt.AlignCenter, f"图片 {i} 未找到")
                painter.end()
                
                self.images.append(placeholder)
                
        if self.images:
            self.__showCurrentImage()
            self.__updateUI()
            
    def __showCurrentImage(self):
        """显示当前图片"""
        if self.images:
            pixmap = self.images[self.current_index]
            
            # 计算缩放尺寸，保持纵横比
            label_size = self.image_label.size()
            scaled_pixmap = pixmap.scaled(
                label_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            
            # 更新页码指示器
            self.page_indicator.setText(f"{self.current_index + 1} / {len(self.images)}")
            
    def __updateUI(self):
        """更新UI状态"""
        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(self.images) - 1)
        
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        # 保持16:9比例
        if not self.isMaximized() and not self.isFullScreen():
            new_width = self.width()
            new_height = int(new_width * 9 / 16)
            if new_height != self.height():
                self.resize(new_width, new_height)
        
        super().resizeEvent(event)
        
        # 更新覆盖层位置
        if hasattr(self, 'overlay_left'):
            label_height = self.image_label.height()
            overlay_width = min(100, self.image_label.width() // 4)
            self.overlay_left.setGeometry(0, 0, overlay_width, label_height)
            self.overlay_right.setGeometry(
                self.image_label.width() - overlay_width, 
                0, 
                overlay_width, 
                label_height
            )
            
        # 重新显示图片
        if self.images:
            self.__showCurrentImage()
            
    def showPrevious(self):
        """显示上一张"""
        if self.current_index > 0:
            self.current_index -= 1
            self.__showCurrentImage()
            self.__updateUI()
            self.__showNavigationHint('left')
            
    def showNext(self):
        """显示下一张"""
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.__showCurrentImage()
            self.__updateUI()
            self.__showNavigationHint('right')
            
    def __showNavigationHint(self, direction):
        """显示导航提示"""
        if direction == 'left':
            self.overlay_left.show()
            QTimer.singleShot(300, self.overlay_left.hide)
        else:
            self.overlay_right.show()
            QTimer.singleShot(300, self.overlay_right.hide)
            
    def keyPressEvent(self, event):
        """键盘控制"""
        if event.key() == Qt.Key_Left:
            self.showPrevious()
        elif event.key() == Qt.Key_Right:
            self.showNext()
        elif event.key() == Qt.Key_Home:
            self.current_index = 0
            self.__showCurrentImage()
            self.__updateUI()
        elif event.key() == Qt.Key_End:
            self.current_index = len(self.images) - 1
            self.__showCurrentImage()
            self.__updateUI()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
            
    def wheelEvent(self, event):
        """鼠标滚轮控制"""
        if event.angleDelta().y() > 0:
            self.showPrevious()
        else:
            self.showNext()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建并显示窗口
    viewer = HintPlayer()
    viewer.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    # 确保图片目录存在
    os.makedirs("images/hint", exist_ok=True)
    
    # 如果没有图片，创建示例图片
    for i in range(PAGES):
        img_path = f"images/hint/{i}.png"
        if not os.path.exists(img_path):
            # 创建示例图片
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (800, 450), color=(40, 40, 60))
            d = ImageDraw.Draw(img)
            d.text((400, 225), f"Hint Image {i}", fill=(200, 200, 255), 
                  anchor="mm", font_size=30)
            img.save(img_path)
            print(f"已创建示例图片: {img_path}")
    
    main()