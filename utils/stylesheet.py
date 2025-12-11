style_sheet = '''
/* Minecraft 工作台风格样式表 - 使用指定字体文件 */

/* 使用@font-face加载自定义字体 */
@font-face {
    font-family: 'zpix';
    src: url('zpix.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
}

/* 如果没有找到zpix字体，回退到其他字体 */
* {
    font-family: 'zpix', 'Courier New', 'Monaco', 'Lucida Console', monospace;
    color: #3f3f3f;
}

/* 主窗口背景 */
QWidget {
    background-color: #c6c6c6;
}

/* 工具按钮 - 类似工作台的方格按钮 */
QPushButton {
    color: #ffffff;
    border: 4px solid;
    background-color: #717171;
    border-top-color: #aaaaaa;
    border-left-color: #aaaaaa;
    border-right-color: #565656;
    border-bottom-color: #565656;

    text-align: center;
    text-shadow: 2px 2px 0px #000000;
}

/* 按钮悬停效果 */
QPushButton:hover {
    background-color: #828282;
    border-top-color: #a8a8a8;
    border-left-color: #a8a8a8;
    border-right-color: #6a6a6a;
    border-bottom-color: #6a6a6a;
    color: #ffffa0;
}

/* 按钮按下效果 - 反转边框颜色实现凹陷效果 */
QPushButton:pressed {
    background-color: #626262;
    border-top-color: #5a5a5a;
    border-left-color: #5a5a5a;
    border-right-color: #9a9a9a;
    border-bottom-color: #9a9a9a;
}

/* 按钮禁用状态 */
QPushButton:disabled {
    background-color: #5a5a5a;
    color: #a0a0a0;
    border-color: #4a4a4a;
    text-shadow: none;
}

/* 标签样式 */
QLabel {
    color: #3f3f3f;
    text-shadow: 2px 2px 0px #000000;
    border: none;
}


/* 输入框 - 类似Minecraft聊天框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #8b8b8b;
    color: #ffffff;
    border: 4px solid;
    border-top-color: #373737;
    border-left-color: #5a5a5a;
    border-right-color: #ffffff;
    border-bottom-color: #ffffff;
    border-radius: 0px;

    selection-background-color: #404040;
    selection-color: #3f3f3f;
}

/* 输入框获得焦点时的效果 */
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    background-color: #0a0a0a;
    color: #ffffff;
}

/* 组合框 - 下拉菜单 */
QComboBox {
    background-color: #c6c6c6;
    color: #3f3f3f;
    border: 4px solid;
    border-top-color: #9a9a9a;
    border-left-color: #9a9a9a;
    border-right-color: #5a5a5a;
    border-bottom-color: #5a5a5a;
    border-radius: 0px;

    text-shadow: 1px 1px 0px #000000;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
    color: #ffffff;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #3f3f3f;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #727272;
    color: #ffffff;
    border: 4px solid #5a5a5a;
    selection-background-color: #404040;
    selection-color: #ffffa0;

}

/* 复选框 */
QCheckBox {
    spacing: 6px;
    color: #3f3f3f;

    text-shadow: 1px 1px 0px #000000;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    background-color: #727272;
    border: 2px solid;
    border-top-color: #9a9a9a;
    border-left-color: #9a9a9a;
    border-right-color: #5a5a5a;
    border-bottom-color: #5a5a5a;
}

QCheckBox::indicator:checked {
    background-color: #3c8527;
}

QCheckBox::indicator:hover {
    background-color: #828282;
}

/* 单选按钮 */
QRadioButton {
    spacing: 6px;
    color: #3f3f3f;

    text-shadow: 1px 1px 0px #000000;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    background-color: #727272;
    border: 2px solid;
    border-top-color: #9a9a9a;
    border-left-color: #9a9a9a;
    border-right-color: #5a5a5a;
    border-bottom-color: #5a5a5a;
}

QRadioButton::indicator:checked {
    background-color: #3c8527;
    border: 3px solid #727272;
}

/* 滚动区域 */
QScrollArea {
    background-color: #727272;
    border: 4px solid;
    border-top-color: #5a5a5a;
    border-left-color: #5a5a5a;
    border-right-color: #9a9a9a;
    border-bottom-color: #9a9a9a;
    border-radius: 0px;
}

QScrollArea QWidget {
    background-color: #c6c6c6;
}

/* 滚动条 */
QScrollBar:vertical, QScrollBar:horizontal {
    background-color: #5a5a5a;
    border: 2px solid #4a4a4a;
    border-radius: 0px;
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background-color: #727272;
    border: 2px solid;
    border-top-color: #9a9a9a;
    border-left-color: #9a9a9a;
    border-right-color: #5a5a5a;
    border-bottom-color: #5a5a5a;
    min-height: 20px;
    min-width: 20px;
}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background-color: #828282;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

/* spinbox */
QSpinBox {
    background-color: #c6c6c6;
    color: #3f3f3f;
    border: 4px solid;
    border-top-color: #9a9a9a;
    border-left-color: #9a9a9a;
    border-right-color: #5a5a5a;
    border-bottom-color: #5a5a5a;
    border-radius: 0px;

    text-shadow: 1px 1px 0px #000000;
}

/* 输入框获得焦点时的效果 */
QSpinBox:focus {
    background-color: #0a0a0a;
    color: #ffffff;
}


/* 分组框 - 类似Minecraft界面中的分组 */
QGroupBox {

    color: #ffff55;
    text-shadow: 2px 2px 0px #000000;
    border: 4px solid;
    border-top-color: #5a5a5a;
    border-left-color: #5a5a5a;
    border-right-color: #9a9a9a;
    border-bottom-color: #9a9a9a;
    border-radius: 0px;
    margin-top: 8px;
    padding-top: 8px;
    background-color: rgba(90, 90, 90, 0.8);
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0px 6px;
    background-color: #727272;
    border: 2px solid #5a5a5a;
    margin-left: 10px;
}

/* 标签页 */
QTabWidget::pane {
    background-color: #727272;
    border: 4px solid;
    border-top-color: #5a5a5a;
    border-left-color: #5a5a5a;
    border-right-color: #9a9a9a;
    border-bottom-color: #9a9a9a;
    border-radius: 0px;
    margin-top: -1px;
}

QTabWidget::tab-bar {
    left: 6px;
}

QTabBar::tab {
    background-color: #5a5a5a;
    color: #3f3f3f;
    border: 2px solid #4a4a4a;
    border-bottom-color: transparent;
    padding: 6px 12px;
    margin-right: 2px;

    text-shadow: 1px 1px 0px #000000;
}

QTabBar::tab:selected {
    background-color: #727272;
    border: 2px solid;
    border-top-color: #5a5a5a;
    border-left-color: #5a5a5a;
    border-right-color: #9a9a9a;
    border-bottom-color: #727272;
    margin-bottom: -1px;
}

QTabBar::tab:hover {
    background-color: #6a6a6a;
    color: #ffffa0;
}

/* 进度条 */
QProgressBar {
    background-color: #5a5a5a;
    border: 2px solid #4a4a4a;
    border-radius: 0px;
    text-align: center;

    color: #3f3f3f;
    text-shadow: 1px 1px 0px #000000;
}

QProgressBar::chunk {
    background-color: #3c8527;
    border: 2px solid #2a641c;
    border-radius: 0px;
}

/* 滑块 */
QSlider::groove:horizontal {
    background-color: #5a5a5a;
    border: 2px solid #4a4a4a;
    border-radius: 0px;
}

QSlider::handle:horizontal {
    background-color: #727272;
    border: 4px solid;
    border-top-color: #9a9a9a;
    border-left-color: #9a9a9a;
    border-right-color: #5a5a5a;
    border-bottom-color: #5a5a5a;
    width: 16px;
    height: 16px;
    margin: -8px 0;
}

/* 列表框 */
QListWidget {
    background-color: #727272;
    border: 4px solid;
    border-top-color: #5a5a5a;
    border-left-color: #5a5a5a;
    border-right-color: #9a9a9a;
    border-bottom-color: #9a9a9a;
    border-radius: 0px;
    color: #3f3f3f;

    outline: none;
}

QListWidget::item {
    background-color: transparent;
    padding: 4px 6px;
    border: 2px solid transparent;
}

QListWidget::item:selected {
    background-color: #404040;
    border: 2px solid #3c8527;
    color: #ffffa0;
}

QListWidget::item:hover {
    background-color: rgba(255, 255, 160, 0.1);
    color: #ffffa0;
}

/* 表格 */
QTableWidget {
    background-color: #727272;
    border: 4px solid;
    border-top-color: #5a5a5a;
    border-left-color: #5a5a5a;
    border-right-color: #9a9a9a;
    border-bottom-color: #9a9a9a;
    border-radius: 0px;
    gridline-color: #5a5a5a;
    color: #3f3f3f;

}

QTableWidget::item {
    background-color: transparent;
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #404040;
    color: #ffffa0;
}

QHeaderView::section {
    background-color: #5a5a5a;
    color: #3f3f3f;

    padding: 4px;
    border: 2px solid #4a4a4a;
    text-shadow: 1px 1px 0px #000000;
}

/* 工具提示 */
QToolTip {
    background-color: #000000;
    color: #3f3f3f;
    border: 2px solid #3c8527;
    border-radius: 0px;
    padding: 4px;

    opacity: 230;
}

/* 分隔符 */
QSplitter::handle {
    background-color: #5a5a5a;
    border: 2px solid #4a4a4a;
}

QSplitter::handle:hover {
    background-color: #3c8527;
}

/* 菜单栏 */
QMenuBar {
    background-color: #5a5a5a;
    border-bottom: 4px solid #4a4a4a;
    color: #3f3f3f;

}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
    margin: 0px 1px;
}

QMenuBar::item:selected {
    background-color: #727272;
    border: 2px solid #5a5a5a;
}

QMenu {
    background-color: #5a5a5a;
    border: 4px solid #4a4a4a;
    color: #3f3f3f;

}

QMenu::item {
    padding: 4px 20px 4px 10px;
    background-color: transparent;
}

QMenu::item:selected {
    background-color: #727272;
    color: #ffffa0;
}

QMenu::separator {
    height: 1px;
    background-color: #4a4a4a;
    margin: 2px 4px;
}
'''