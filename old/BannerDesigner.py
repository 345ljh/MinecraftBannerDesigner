from PyQt5.QtWidgets import (QApplication, QShortcut, QWidget, QGridLayout, QScrollArea, QVBoxLayout,
QSizePolicy, QPushButton, QFileDialog, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QKeySequence
import sys, os
import PIL

import SingleBannerDesigner
import ui_banner_designer
import pattern

class BannerDesigner(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = ui_banner_designer.Ui_BannerDesigner()
        self.ui.setupUi(self)

        self.filepath = ""
        self.designs = {}
        self.current_design_name = ""
        self.current_banner = [0, 0]
        self.current_banner_pattern = {}
        self.clipboard = ""

        self.displaywindow = None

        self.single_designer = SingleBannerDesigner.SingleBannerDesigner()
        self.single_designer.setGeometry(0, 100, 800, 600)
        self.single_designer.setParent(self)
        self.ui.FilePathLabel.setWordWrap(True)

        while self.ui.GridLayout.count():
            item = self.ui.GridLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutWidget.deleteLater()
        self.ui.GridLayout = QGridLayout(self.ui.scrollAreaWidgetContents)
        
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) 
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.ui.GridLayout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.ui.GridLayout.setSpacing(5)

        self.UpdateGridButton()
        self.GridButtonClicked(0,0)

        self.ui.ColumnSpinBox.valueChanged.connect(self.UpdateGridButton)
        self.ui.RowSpinBox.valueChanged.connect(self.UpdateGridButton)
        self.single_designer.ui.SaveButton.clicked.connect(self.SaveBanner)
        self.single_designer.PatternChanged.connect( # 修改后提示未保存 
            lambda: self.ui.GridLayout.itemAtPosition(self.current_banner[0], self.current_banner[1]).widget().setStyleSheet("background-color: rgb(255, 128, 128)"))
        self.ui.OpenFileButton.clicked.connect(self.OpenFile)
        self.ui.SaveFileButton.clicked.connect(self.SaveFile)
        self.ui.DesignSelectComboBox.currentIndexChanged.connect(lambda: self.LoadDesign(self.ui.DesignSelectComboBox.currentText()))
        self.ui.NewDesignButton.clicked.connect(self.NewDesign)
        self.ui.DisplayButton.clicked.connect(self.DisplayDesign)
        self.ui.CommandButton.clicked.connect(self.GenerateCommand)
        self.ui.CalculateButton.clicked.connect(self.CalculateDesignDye)
        self.single_designer.ui.CopyBannerButton.clicked.connect(self.CopyBanner)
        self.single_designer.ui.PasteBannerButton.clicked.connect(self.PasteBanner)
        self.ui.InfoButton.clicked.connect(lambda: QMessageBox.information(self, '提示', '''快捷键：
Ctrl+C 复制旗帜
Ctrl+V 粘贴旗帜
Ctrl+S 保存旗帜
Ctrl+D 快速对称
Ctrl+1/2/3/4/5/6/7/8/9/0/Q/W/E/R/T/Y/del 设置旗帜背景颜色
Ctrl+Shift+N 根据名称查找/新建设计
Ctrl+Shift+O 打开.banner文件
Ctrl+Shift+S 保存.banner文件
Ctrl+Shift+Q 生成MineCraft指令
        '''))

        # 快捷键
        # 单面旗帜操作
        self.shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut_copy.activated.connect(self.CopyBanner)
        self.shortcut_paste = QShortcut(QKeySequence("Ctrl+V"), self)
        self.shortcut_paste.activated.connect(self.PasteBanner)
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.SaveBanner)
        self.shortcut_symm = QShortcut(QKeySequence("Ctrl+D"), self)
        self.shortcut_symm.activated.connect(self.SymmetricBanner)
        # 快速设置背景
        self.shortcut_background = [QShortcut(QKeySequence(f"Ctrl+{key}"), self) for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'Q', 'W', 'E', 'R', 'T', 'Y', 'del']]
        for i, shortcut in enumerate(self.shortcut_background):
            shortcut.activated.connect(lambda idx=i: self.single_designer.ui.BannerColorComboBox.setCurrentIndex(idx))

        # 设计层面操作
        self.shortcut_new_design = QShortcut(QKeySequence("Ctrl+Shift+N"), self)
        self.shortcut_new_design.activated.connect(self.NewDesign)
        self.shortcut_openfile = QShortcut(QKeySequence("Ctrl+Shift+O"), self)
        self.shortcut_openfile.activated.connect(self.OpenFile)
        self.shortcut_savefile = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.shortcut_savefile.activated.connect(self.SaveFile)
        self.shortcut_generate_command = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        self.shortcut_generate_command.activated.connect(self.GenerateCommand)

    def UpdateGridButton(self):
        while self.ui.GridLayout.count():
            item = self.ui.GridLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for i in range(self.ui.RowSpinBox.value() - 1):
            for j in range(self.ui.ColumnSpinBox.value()):
                _i = self.ui.RowSpinBox.value() - i - 1  # 图案定义的i为倒序排列, 且从1开始(最底下方块为0不放旗帜)
                button = QPushButton(f"{_i},{j}")
                button.setFixedSize(40, 40)
                button.setStyleSheet("background-color: white")
                self.ui.GridLayout.addWidget(button, i, j)
                button.clicked.connect(lambda checked, i=i, j=j: self.GridButtonClicked(i, j))
                if(f"{_i}:{j}" not in self.current_banner_pattern):
                    self.current_banner_pattern[f"{_i}:{j}"] = pattern.getDefaultBannerStr()

        self.GridButtonClicked(self.ui.RowSpinBox.value() - 2, 0)

    def GridButtonClicked(self, i, j):
        try:  # 防减少行列数越界
            self.ui.GridLayout.itemAtPosition(self.current_banner[0], self.current_banner[1]).widget().setStyleSheet("background-color: white")
        except:
            pass
        self.current_banner = [i, j]
        self.ui.GridLayout.itemAtPosition(i, j).widget().setStyleSheet("background-color: rgb(255, 128, 128)")

        _i = self.ui.RowSpinBox.value() - i - 1
        self.single_designer.LoadPattern(self.current_banner_pattern[f"{_i}:{j}"])

    def SymmetricBanner(self):  # 水平对称对称旗帜
        banner = []
        banner.append(str(self.single_designer.ui.BannerColorComboBox.currentIndex()))
        for i in range(pattern.MAX_BANNER):
            try:
                banner.append(str(pattern.symmetric_pair[self.single_designer.ui.PatternVLayout.itemAt(i).widget().button_group.checkedId()]))
                banner.append(str(self.single_designer.ui.PatternVLayout.itemAt(i).widget().ui.PatternColorComboBox.currentIndex()))
            except IndexError:
                pass
        new_banner = ""
        for i in range(2 * pattern.MAX_BANNER + 1):
            try:
                new_banner += banner[i] + ":"
            except IndexError:
                pass
        self.single_designer.LoadPattern(new_banner)

    def SaveBanner(self):  # 暂存旗帜
        self.ui.GridLayout.itemAtPosition(self.current_banner[0], self.current_banner[1]).widget().setStyleSheet("background-color: rgb(128, 255, 128)")
        s = f"{self.single_designer.ui.BannerColorComboBox.currentIndex()}:"
        for i in range(pattern.MAX_BANNER):
            try:
                s += f"{self.single_designer.ui.PatternVLayout.itemAt(i).widget().button_group.checkedId()}:{self.single_designer.ui.PatternVLayout.itemAt(i).widget().ui.PatternColorComboBox.currentIndex()}:"
            except IndexError:
                pass
        self.current_banner_pattern[f"{self.ui.RowSpinBox.value() - self.current_banner[0] - 1}:{self.current_banner[1]}"] = s[:-1]
        self.SaveDesign()

    def SaveDesign(self): 
        current_design_value = []
        for key in self.current_banner_pattern.keys():
            # 解析当前旗帜图案
            pattern_data = self.current_banner_pattern[key].split(":")
            banner_color = pattern_data[0]
            
            # 过滤图案为0的部分
            filtered_pattern = [banner_color]
            for i in range(pattern.MAX_BANNER):
                try:
                    pattern_idx = int(pattern_data[2*i + 1])
                    color_idx = int(pattern_data[2*i + 2])
                    if pattern_idx != 0:  # 只保存图案不为0的部分
                        filtered_pattern.append(str(pattern_idx))
                        filtered_pattern.append(str(color_idx))
                except (IndexError, ValueError):
                    break
            
            # 重新组合为字符串
            filtered_pattern_str = ":".join(filtered_pattern)
            current_design_value.append(str(key) + ":" + filtered_pattern_str)

        self.designs[self.current_design_name] = [str(self.ui.RowSpinBox.value()), str(self.ui.ColumnSpinBox.value()), current_design_value]
        
    def OpenFile(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        if path:
            self.designs = {}
            self.filepath = path
            self.ui.FilePathLabel.setText(path)
            if os.path.exists(path):
                self.ui.DesignSelectComboBox.clear()
                # 使用UTF-8编码打开
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f.readlines():
                            try:
                                line = line.strip().split(",")
                                if len(line) < 3:  # 检验必要部分
                                    raise Exception("缺少关键信息")
                                for banner in line[3:]:  # 依次检验旗帜部分是否符合格式
                                    if banner == '':
                                        continue
                                    elems = banner.split(":")
                                    # if len(elems) < 2 * pattern.MAX_BANNER + 3:  # 检验长度, 其中[0:2]为坐标,[2:15]为颜色与图案
                                    #     raise Exception("长度错误")
                                    # for elem_index, elem in enumerate(elems):  # 图案0~40, 颜色0~15
                                    #     if elem_index >= 2:
                                    #         if elem_index % 2 == 0:
                                    #             if int(elem) < 0 or int(elem) > 15 + (elem_index == 2):  # 不能转换int会报错
                                    #                 raise Exception("颜色值错误")
                                    #         else:
                                    #             if int(elem) < 0 or int(elem) > 40:
                                    #                 raise Exception("图案值错误")
                                    #     else:
                                    #         if int(elem) < 0:
                                    #             raise Exception("坐标不能为负数")
                                    for elem_index in range(pattern.MAX_BANNER):
                                        pass
                            except Exception as e:
                                print(e)
                                continue
                            # 存储
                            self.designs[line[0]] = [line[1], line[2], line[3:]]
                            self.ui.DesignSelectComboBox.addItem(line[0])
                        # 加载第一个
                        if self.designs != {}:
                            self.ui.DesignSelectComboBox.setCurrentIndex(0)
                            self.LoadDesign(self.ui.DesignSelectComboBox.itemText(0))
                except UnicodeDecodeError:
                    QMessageBox.warning(self, "错误", "文件编码不支持")

    def SaveFile(self):
        # 检查路径是否为空
        if self.filepath == "":
            self.filepath, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        # 打开文件
        if self.filepath != "":
            # 使用UTF-8编码保存
            with open(self.filepath, "w", encoding="utf-8") as f:
                for name in self.designs:
                    design = self.designs[name]
                    design_str = f"{name},{design[0]},{design[1]},"
                    for banner in design[2]:
                        design_str = design_str + banner + ","
                    f.write(f"{design_str[:-1]}\n")

    def LoadDesign(self, name: str):
        if name != "" and name in self.designs and self.current_banner_pattern != {}:
            self.current_banner_pattern = {}
            # 记录坐标
            self.ui.RowSpinBox.setValue(int(self.designs[name][0]))
            self.ui.ColumnSpinBox.setValue(int(self.designs[name][1]))
            self.UpdateGridButton()
            # 依次存储单面旗帜字符串
            for b in self.designs[name][2]:
                if b != "":
                    p = b.split(":", 2)
                    self.current_banner_pattern[f"{p[0]}:{p[1]}"] = p[2]
            self.current_banner = [0, 0]
            self.GridButtonClicked(self.ui.RowSpinBox.value() - 2, 0)
            self.single_designer.LoadPattern(self.current_banner_pattern["1:0"])
            self.current_design_name = name
            return True
        else:
            return False

    def NewDesign(self):
        name = self.ui.NewDesignTextEdit.toPlainText()
        if name != "":
            if ',' in name or ':' in name:
                self.ui.NewDesignTextEdit.setPlainText("无效的名称")
                return
            if not self.LoadDesign(name):
                self.designs[name] = ['2', '2', ['1:0:' + pattern.getDefaultBannerStr(), '1:1:' + pattern.getDefaultBannerStr(), '']]  # 初始化设计
            self.ui.NewDesignTextEdit.setPlainText("")
            self.ui.DesignSelectComboBox.addItem(name)
            self.ui.DesignSelectComboBox.setCurrentText(name)
        else:
            self.ui.NewDesignTextEdit.setPlainText("设计名不能为空")

    def DisplayDesign(self):
        if hasattr(self, 'display_window') and self.display_window:
            self.display_window.close()
        
        grid_size = 100
        if self.ui.RealMarginCheckBox.isChecked():
            # 旗帜边界到方块边界的距离
            extra_offset_x = 2 * grid_size // 20
            extra_offset_y = 4 * grid_size // 20
        else:
            extra_offset_x = 0
            extra_offset_y = 0
            
        width = (grid_size + 2 * extra_offset_x) * int(self.ui.ColumnSpinBox.value())
        height = (grid_size + extra_offset_y) * int(self.ui.RowSpinBox.value())
        
        # 创建绘制窗口
        self.display_window = QWidget()
        self.display_window.setWindowTitle("设计预览")
        
        # 计算缩放比例
        max_width = 1600
        max_height = 1000
        scale_factor = 1.0
        
        if width > max_width or height > max_height:
            width_scale = max_width / width
            height_scale = max_height / height
            scale_factor = min(width_scale, height_scale)
            
            # 设置缩放后的窗口大小
            scaled_width = int(width * scale_factor)
            scaled_height = int(height * scale_factor)
            self.display_window.setFixedSize(scaled_width, scaled_height)
        else:
            self.display_window.setFixedSize(width, height)
        
        # 重写 paintEvent
        def paintEvent(event):
            painter = QPainter(self.display_window)
            painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
            
            # 填充白色背景
            painter.fillRect(0, 0, self.display_window.width(), self.display_window.height(), QColor(255, 255, 255))
            
            # 如果需要缩放，应用变换矩阵
            if scale_factor < 1.0:
                painter.scale(scale_factor, scale_factor)
            
            rows = self.ui.RowSpinBox.value()
            columns = self.ui.ColumnSpinBox.value()
            
            for row in range(1, rows):
                for column in range(columns):
                    y_offset = (grid_size + extra_offset_y) * (rows - row - 1)
                    x_offset = (grid_size + extra_offset_x) * column + extra_offset_x // 2
                    
                    pattern_key = f"{row}:{column}"
                    if pattern_key in self.current_banner_pattern:

                        p = self.current_banner_pattern[pattern_key].split(":")           
                        if p[0] == "16":
                            continue
                        
                        # 绘制背景矩形
                        bg_color = QColor(*pattern.color[pattern.color_name[int(p[0])]])
                        painter.fillRect(x_offset, y_offset, grid_size, 2 * grid_size, bg_color)
                        
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
        
        self.display_window.paintEvent = paintEvent
        self.display_window.show()

    def CalculateDesignDye(self):
        dye = [0] * 16
        for key in self.current_banner_pattern:
            banner = [int(i) for i in self.current_banner_pattern[key].split(":")]
            if banner[0] == 16:
                continue
            dye[banner[0]] += 6
            for idx in range((len(banner) - 1) // 2):
                if banner[2 * idx + 1] != 0:
                    dye[banner[2 * idx + 2]] += 1
        msg = QMessageBox()
        msg.setWindowTitle("染料计算")

        htm_str = ""
        for i in range(16):
            htm_str += f'''
            <p>{str(dye[i])}</p>
            <img src="images/dyes/{str(i)}.png" width="26" height="26">
            '''
        
        # 1132*52
        html_content = f"""
        <div style="text-align:center">
            <p>{htm_str}</p>
            <p>适用18w43a/1.14以上版本</p>
        </div>
        """
        msg.setText(html_content)
        msg.exec_()


    def CopyBanner(self):
        self.clipboard = self.current_banner_pattern[f"{self.ui.RowSpinBox.value() - self.current_banner[0] - 1}:{self.current_banner[1]}"] 

    def PasteBanner(self):
        self.current_banner_pattern[f"{self.ui.RowSpinBox.value() - self.current_banner[0] - 1}:{self.current_banner[1]}"] = self.clipboard
        self.single_designer.LoadPattern(self.clipboard)

    def GenerateCommand(self):
        command = ""
        generated_num = 0

        for i in range(self.ui.RowSpinBox.value() - 1):
            _i = self.ui.RowSpinBox.value() - i - 1
            for j in range(self.ui.ColumnSpinBox.value()):
                # 旗帜属性    
                now_banner = self.current_banner_pattern[f"{_i}:{j}"].split(":")

                if now_banner[0] != "16":
                    if generated_num % 27 == 0:
                        # 指令前缀, 缩进似乎会影响指令执行, 因此不缩进不换行
                        command += f'''/give @p minecraft:chest{{display: {{Name: '{{"text":"{self.current_design_name}","color":"gold"}}'}},BlockEntityTag:{{Items:['''

                    command += f'''{{Slot:{generated_num % 27}b,id:"minecraft:{pattern.color_name[int(now_banner[0])]}_banner",Count:1b,tag:{{display: {{Name: '{{"text":"{_i}_{j}"}}'}},'''

                    # 判断是否需要添加图案, 即[1:2:13]是否全为'0'
                    if not all(x == '0' for x in now_banner[1::2]):

                        command += f'''BlockEntityTag:{{Patterns:['''

                        for k in range(pattern.MAX_BANNER):
                            try:
                                if int(now_banner[2 * k + 1]) != 0:
                                    command += f"{{Pattern:\"{pattern.type[int(now_banner[2 * k + 1])]}\",Color:{now_banner[2 * k + 2]}}},"
                            except IndexError:
                                pass
                        command += f"]}}"

                    command += f'''}}}},'''

                    if generated_num % 27 == 26:
                        # 指令后缀
                        command += f''']}}}}
                        ___________________________
                        '''

                    generated_num += 1
        
        if generated_num % 27 != 0:
            # 指令后缀
            command += f''']}}}}
            ___________________________
            '''
        # 复制剪贴板
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        clipboard = app.clipboard()
        clipboard.setText(command)
        QMessageBox.information(self, '生成成功！', f'已复制指令到剪贴板，共{(generated_num - 1) // 27 + 1}条')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BannerDesigner()
    window.show()
    sys.exit(app.exec_())