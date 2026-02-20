from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import oss2

import utils.VersionController as VersionController

class ShareItemWidget(QWidget):
    """单个分享项的自定义widget"""
    
    download_clicked = pyqtSignal(str)  # 下载信号，传递文件名
    
    def __init__(self, filename, size, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.size = size
        self.init_ui()
        
    def init_ui(self):
        # 解析文件名中的标题和作者
        # 格式: "标题-作者.banner" 或 "标题-作者"
        display_name = self.filename
        if self.filename.endswith('.banner'):
            display_name = self.filename[:-7]  # 移除 .banner 后缀
        
        # 分割标题和作者
        if '-' in display_name:
            parts = display_name.split('-', 1)
            self.title = parts[0].strip()
            self.author = parts[1].strip() if len(parts) > 1 else "未知作者"
        else:
            self.title = display_name
            self.author = "未知作者"
        
        # 创建主布局
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # 标题标签
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px")
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 作者标签
        self.author_label = QLabel(self.author)
        self.author_label.setAlignment(Qt.AlignCenter)
        self.author_label.setStyleSheet("font-size: 16px")
        self.author_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 大小标签
        size_str = self.format_size(self.size)
        self.size_label = QLabel(size_str)
        self.size_label.setAlignment(Qt.AlignCenter)
        self.size_label.setStyleSheet("font-size: 16px")
        self.size_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 下载按钮 - 固定大小
        self.download_btn = QPushButton("下载")
        self.download_btn.setFixedSize(60, 30)  # 与表头操作列宽度一致
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.clicked.connect(lambda: self.download_clicked.emit(self.filename))
        self.download_btn.setStyleSheet("QPushButton { background-color: #5a5a5a; }")
        
        # 添加所有组件到布局
        layout.addWidget(self.title_label)
        layout.addWidget(self.author_label)
        layout.addWidget(self.size_label)
        layout.addWidget(self.download_btn)
        
        # 设置拉伸因子
        layout.setStretchFactor(self.title_label, 3)   # 标题列弹性系数3
        layout.setStretchFactor(self.author_label, 2)  # 作者列弹性系数2
        layout.setStretchFactor(self.size_label, 1)    # 大小列弹性系数1
        # 下载按钮不设置拉伸，保持固定宽度
        
        self.setLayout(layout)
        
        
    def format_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

class ShareHub(QWidget):
    """分享中心widget，显示可下载的设计文件列表"""
    
    # 下载信号，传递文件名
    download_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.dist = VersionController.get_file_list()
        except:
            self.dist = {}
        self.item_widgets = []
        self.init_ui()
        self.load_items()
        
    def init_ui(self):
        """初始化UI"""
        self.setFixedSize(900, 700)
        self.setWindowTitle("设计工坊 - 测试版本")
        self.setWindowIcon(QIcon("images/icon.png"))

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #3A3A3A; max-height: 2px;")
        main_layout.addWidget(separator)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(2)
        self.content_layout.addStretch()  # 添加弹性空间使内容靠上
        
        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)
        
        # 状态栏
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        self.__setupStyles()

        # 连接下载信号
        self.download_requested.connect(lambda f: self.download_design(f))
        
    def create_header(self):
        """创建表头"""
        header = QWidget()
        header.setFixedHeight(40)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(15)
        
        # 表头标签 - 移除setFixedWidth，使用sizePolicy控制
        title_header = QLabel("设计标题")
        title_header.setAlignment(Qt.AlignCenter)
        title_header.setStyleSheet("font-size: 19px;")
        title_header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        author_header = QLabel("作者")
        author_header.setAlignment(Qt.AlignCenter)
        author_header.setStyleSheet("font-size: 19px;")
        author_header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        size_header = QLabel("大小")
        size_header.setAlignment(Qt.AlignCenter)
        size_header.setStyleSheet("font-size: 19px;")
        size_header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        action_header = QLabel("操作")
        action_header.setAlignment(Qt.AlignCenter)
        action_header.setStyleSheet("font-size: 19px;")
        # 操作标签也设置固定宽度，与下载按钮一致
        action_header.setFixedWidth(60)  # 与下载按钮宽度相同
        
        # 先添加所有组件
        layout.addWidget(title_header)
        layout.addWidget(author_header)
        layout.addWidget(size_header)
        layout.addWidget(action_header)
        
        # 设置拉伸因子 - 前三列拉伸，操作列固定
        layout.setStretchFactor(title_header, 3)   # 标题列弹性系数3
        layout.setStretchFactor(author_header, 2)  # 作者列弹性系数2
        layout.setStretchFactor(size_header, 1)    # 大小列弹性系数1
        # 操作列不设置拉伸，保持固定宽度
        
        header.setLayout(layout)
        return header

    def load_items(self):
        """加载所有分享项"""
        # 清空现有内容（除了最后的stretch）
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.item_widgets.clear()
        
        if not self.dist:
            # 显示空状态
            empty_label = QLabel("网络错误或暂无分享设计")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 40px;
                }
            """)
            self.content_layout.insertWidget(0, empty_label)
            self.status_label.setText("共 0 个设计")
            return
        
        # 按文件名排序（可选）
        sorted_items = sorted(self.dist.items(), key=lambda x: x[0])
        
        # 创建每个分享项的widget
        for i, (filename, size) in enumerate(sorted_items):
            item_widget = ShareItemWidget(filename, size)
            item_widget.download_clicked.connect(self.on_download_clicked)
            
            self.content_layout.insertWidget(i, item_widget)
            self.item_widgets.append(item_widget)
        
        # 更新状态栏
        total_size = sum(self.dist.values())
        self.status_label.setText(
            f"共 {len(self.dist)} 个设计 | "
            f"总大小: {self.format_total_size(total_size)}\n"
            "文件将下载到Download文件夹，请勿删除该文件夹\n"
            "当前版本无上传功能，分享设计请联系up主: iliqiIiq"
        )
        
    def format_total_size(self, size_bytes):
        """格式化总大小"""
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    def on_download_clicked(self, filename):
        """处理下载按钮点击"""
        self.download_requested.emit(filename)
        
    def download_design(self, filename):
        try:
            auth = oss2.AnonymousAuth()
            bucket = oss2.Bucket(auth, 'https://oss-cn-shenzhen.aliyuncs.com', 'minecraft-banner-designer')
            path = f'{filename}.banner'
            bucket.get_object_to_file(f"banners/{path}", f"./Download/{path}")
            # 下载完成后提示完成并输出路径
            QMessageBox.information(None, '提示', f'下载完成，已保存至./Download/{path}')

        except Exception as e:
            QMessageBox.information(None, '提示', '网络错误，请检查网络连接后重试')
            print(f"下载失败: {e}")

    def __setupStyles(self):
        """统一设置应用样式表"""
        # 加载字体
        font_id = QFontDatabase.addApplicationFont("./images/zpix.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        pix_font_family = font_families[0] if font_families else "Arial"
        # 应用样式表到整个应用
        import utils.stylesheet
        self.setStyleSheet(utils.stylesheet.style_sheet)


# 使用示例
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建ShareHub实例
    share_hub = ShareHub()
    share_hub.show()
    
    sys.exit(app.exec_())