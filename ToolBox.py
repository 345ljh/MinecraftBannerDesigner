from PyQt5.QtWidgets import (QApplication, QShortcut, QWidget, QGridLayout, QScrollArea, QVBoxLayout,
QSizePolicy, QPushButton, QFileDialog, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import sys, os

import ui_toolbox
import utils.AdaptiveManager as AdaptiveManager
import utils.pattern as pattern
import utils.DataStorage as DataStorage

zoom_level_to_factor = [25,33,50,67,75,80,90,100,110,125,150,175,200,250,300,400,500]

class ToolBox(QWidget):
    LoadDesign = pyqtSignal()
    UpdateZoom = pyqtSignal(float, bool)  # zoom_factor, real_margin

    def __init__(self):
        super().__init__()
        self.ui = ui_toolbox.Ui_ToolBox()
        self.ui.setupUi(self)

        DataStorage.get_instance().filepath = ""  # 当前文件路径
        DataStorage.get_instance().designs = {}  # 设计列表: {'name': [row, col, [r1:c1:banner1, ...]]}
        DataStorage.get_instance().search_designs = {}  # 搜索结果
        DataStorage.get_instance().current_design_name = ""
        DataStorage.get_instance().current_design_size = [3, 3]  # [row, col]
        DataStorage.get_instance().current_design_patterns = {}  #  dict{'r:c': 'b:p:c:p:c:...', ...}
        DataStorage.get_instance().zoom_level = 7  # 缩放等级, 对应100%
        DataStorage.get_instance().banner_pos = [1, 0]  # 当前点击的banner的行列数

        self.ui.FileLoadButton.clicked.connect(self.OpenFile)
        self.ui.FileSaveButton.clicked.connect(self.SaveFile)
        self.ui.DesignSelectComboBox.currentIndexChanged.connect(self.DesignSelected)
        self.ui.DesignSearchButton.clicked.connect(self.SearchDesign)
        self.ui.DesignRowSpinBox.valueChanged.connect(self.ChangeDesignSize)
        self.ui.DesignColumnSpinBox.valueChanged.connect(self.ChangeDesignSize)
        self.ui.DesignSelectButton.clicked.connect(self.SelectDesign)
        self.ui.ViewZoomUpButton.clicked.connect(lambda: self.SetZoom(ZoomUp=True))
        self.ui.ViewZoomDownButton.clicked.connect(lambda: self.SetZoom(ZoomUp=False))
        self.ui.ViewPaddingCheckBox.stateChanged.connect(lambda: self.UpdateZoom.emit(zoom_level_to_factor[DataStorage.get_instance().zoom_level] / 100, self.ui.ViewPaddingCheckBox.isChecked()))
        self.ui.UtilsGenCommandButton.clicked.connect(self.GenerateCommand)
        self.ui.UtilsDyeCalcButton.clicked.connect(self.CalculateDesignDye)
        self.ui.ViewRealtimeDisplayCheckBox.stateChanged.connect(self.__setRealtimeCheckboxText)
        self.ui.ViewBackgroundRedSchollbar.valueChanged.connect(self.SetBackgroundColor)
        self.ui.ViewBackgroundGreenSchollbar.valueChanged.connect(self.SetBackgroundColor)
        self.ui.ViewBackgroundBlueSchollbar.valueChanged.connect(self.SetBackgroundColor)

        self.adaptive_components = [
            self.ui.FileLabel, self.ui.FilePathText, self.ui.FileLoadButton, self.ui.FileSaveButton,
            self.ui.DesignLabel, self.ui.DesignNameHintLabel, self.ui.DesignNameText, self.ui.DesignSelectHintLabel, self.ui.DesignSelectComboBox, self.ui.DesignSearchButton, self.ui.DesignSelectButton, self.ui.DesignRowHintLabel, self.ui.DesignRowSpinBox, self.ui.DesignColumnHintLabel, self.ui.DesignColumnSpinBox,
            self.ui.ViewLabel, self.ui.ViewPaddingCheckBox, self.ui.ViewZoomLabel, self.ui.ViewZoomUpButton, self.ui.ViewZoomDownButton, self.ui.ViewRealtimeDisplayCheckBox,
            self.ui.ViewBackgroundColorLabel, self.ui.ViewBackgroundRedSchollbar, self.ui.ViewBackgroundGreenSchollbar, self.ui.ViewBackgroundBlueSchollbar,
            self.ui.UtilsLabel, self.ui.UtilsDyeCalcButton, self.ui.UtilsGenCommandButton, self.ui.UtilsShortCutButton
        ]
        self.adaptive_manager = AdaptiveManager.AdaptiveManager(self, self.adaptive_components)
        
    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.adaptive_manager.AdaptiveResize()

    def __setRealtimeCheckboxText(self):
        if self.ui.ViewRealtimeDisplayCheckBox.isChecked():
            self.ui.ViewRealtimeDisplayCheckBox.setText("开启实时渲染")
        else:
            self.ui.ViewRealtimeDisplayCheckBox.setText("重新勾选后渲染")

    def OpenFile(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        if path:
            DataStorage.get_instance().designs = {}
            DataStorage.get_instance().filepath = path
            self.ui.FilePathText.setText(path)
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
                                    for elem_index, elem in enumerate(elems):  # 图案0~40, 颜色0~15
                                        if elem_index >= 2:
                                            if elem_index % 2 == 0:
                                                if int(elem) < 0 or int(elem) > 15 + (elem_index == 2):  # 不能转换int会报错
                                                    raise Exception("颜色值错误")
                                            else:
                                                if int(elem) < 0 or int(elem) > len(pattern.type):
                                                    raise Exception("图案值错误")
                                        else:
                                            if int(elem) < 0:
                                                raise Exception("坐标不能为负数")
                            except Exception as e:
                                print(e)
                                continue
                            # 存储
                            DataStorage.get_instance().designs[line[0]] = [int(line[1]), int(line[2]), line[3:]]
                            self.ui.DesignSelectComboBox.addItem(line[0])
                        # 加载第一个
                        if DataStorage.get_instance().designs != {}:
                            self.ui.DesignSelectComboBox.setCurrentIndex(0)
                            self.DesignSelected()
                except UnicodeDecodeError:
                    QMessageBox.warning(self, "错误", "文件编码不支持")

    def SaveFile(self):
        # 检查路径是否为空
        if DataStorage.get_instance().filepath == "":
            DataStorage.get_instance().filepath, _ = QFileDialog.getSaveFileName(self, "选择旗帜文件", "", "旗帜文件(*.banner)")
        # 打开文件
        if DataStorage.get_instance().filepath != "":
            # 使用UTF-8编码保存
            with open(DataStorage.get_instance().filepath, "w", encoding="utf-8") as f:
                for name in DataStorage.get_instance().designs:
                    design = DataStorage.get_instance().designs[name]
                    design_str = f"{name},{design[0]},{design[1]},"
                    for banner in design[2]:
                        design_str = design_str + banner + ","
                    f.write(f"{design_str[:-1]}\n")

    def DesignSelected(self):
        if self.ui.DesignSelectComboBox.currentText():
            DataStorage.get_instance().current_design_name = self.ui.DesignSelectComboBox.currentText()
            r = DataStorage.get_instance().designs[self.ui.DesignSelectComboBox.currentText()][0]
            c = DataStorage.get_instance().designs[self.ui.DesignSelectComboBox.currentText()][1]
            self.ui.DesignRowSpinBox.setValue(r)  # 加载行数
            self.ui.DesignColumnSpinBox.setValue(c)  # 加载列数

            design = DataStorage.get_instance().designs[DataStorage.get_instance().current_design_name]
            patterns_data = {}
            for banner in design[2]:
                b = banner.split(":", 2)
                key = b[0] + ":" + b[1]
                patterns_data[key] = b[2]
            DataStorage.get_instance().current_design_patterns = patterns_data
            DataStorage.get_instance().current_design_size = [r,c]
            DataStorage.get_instance().banner_pos = [1,0]

            self.LoadDesign.emit()

    def ChangeDesignSize(self):
        if self.ui.DesignSelectComboBox.currentText():
            DataStorage.get_instance().designs[self.ui.DesignSelectComboBox.currentText()][0] = self.ui.DesignRowSpinBox.value()
            DataStorage.get_instance().designs[self.ui.DesignSelectComboBox.currentText()][1] = self.ui.DesignColumnSpinBox.value()
            DataStorage.get_instance().current_design_size = [DataStorage.get_instance().designs[self.ui.DesignSelectComboBox.currentText()][0],
                                                              DataStorage.get_instance().designs[self.ui.DesignSelectComboBox.currentText()][1]]
            self.LoadDesign.emit()
            
    def SearchDesign(self):
        '''匹配搜索'''
        DataStorage.get_instance().search_designs = {}
        for design_name in DataStorage.get_instance().designs:
            if self.ui.DesignNameText.text() in design_name:
                DataStorage.get_instance().search_designs[design_name] = DataStorage.get_instance().designs[design_name]
        self.ui.DesignSelectComboBox.clear()
        for name in DataStorage.get_instance().search_designs:
            self.ui.DesignSelectComboBox.addItem(name)
        self.ui.DesignSelectComboBox.setFocus()
        # 展开下拉
        self.ui.DesignSelectComboBox.showPopup()

    def UpdateFocus(self):
        '''轮换设置聚焦 失焦-设计选择框-设计名输入框'''
        # 判断是否聚焦以及聚焦的控件
        f1 = self.ui.DesignSelectComboBox.hasFocus()
        f2 = self.ui.DesignNameText.hasFocus()
        if f1:
            self.ui.DesignNameText.setFocus()
            self.ui.DesignSelectComboBox.hidePopup()
        elif f2:
            self.ui.DesignNameText.clearFocus()
        else:
            self.ui.DesignSelectComboBox.setFocus()
            self.ui.DesignSelectComboBox.showPopup()

    def SelectDesign(self):
        name = self.ui.DesignNameText.text()
        if name != "":
            if ',' in name or ':' in name:
                self.ui.DesignNameText.setText("无效的名称")
                return
            if name in DataStorage.get_instance().designs:  # 名称已存在
                DataStorage.get_instance().current_design_name = name
                self.ui.DesignSelectComboBox.setCurrentText(name)
                self.DesignSelected()
            else:
                DataStorage.get_instance().designs[name] = [3,3,[]]
                self.ui.DesignSelectComboBox.addItem(name)
                self.ui.DesignSelectComboBox.setCurrentText(name)
                DataStorage.get_instance().current_design_name = name
                self.DesignSelected()
            self.ui.DesignNameText.setText("")
        else:
            self.ui.DesignNameText.setText("设计名不能为空")

    def SaveCurrentDesign(self):
        '''保存当前设计到designs列表中'''
        cd = []
        for banner_key in DataStorage.get_instance().current_design_patterns:
            cd.append(f"{banner_key}:{DataStorage.get_instance().current_design_patterns[banner_key]}")
        DataStorage.get_instance().designs[DataStorage.get_instance().current_design_name] = [DataStorage.get_instance().current_design_size[0], DataStorage.get_instance().current_design_size[1], cd]

    def SetZoom(self, ZoomUp=True):
        if ZoomUp:
            if DataStorage.get_instance().zoom_level < len(zoom_level_to_factor) - 1:
                DataStorage.get_instance().zoom_level += 1
        else:
            if DataStorage.get_instance().zoom_level > 0:
                DataStorage.get_instance().zoom_level -= 1
        self.ui.ViewZoomLabel.setText(f"缩放: {zoom_level_to_factor[DataStorage.get_instance().zoom_level]}%")
        self.UpdateZoom.emit(zoom_level_to_factor[DataStorage.get_instance().zoom_level] / 100, self.ui.ViewPaddingCheckBox.isChecked())

    def SetBackgroundColor(self):
            DataStorage.get_instance().background_color = [self.ui.ViewBackgroundRedSchollbar.value(), 
                                                           self.ui.ViewBackgroundGreenSchollbar.value(), 
                                                           self.ui.ViewBackgroundBlueSchollbar.value()]
            
    def SetDefaultBackgroundColor(self, color_id: int):
        '''设置旗帜库中颜色作为背景'''
        self.ui.ViewBackgroundRedSchollbar.setValue(pattern.color[pattern.color_name[color_id]][0])
        self.ui.ViewBackgroundGreenSchollbar.setValue(pattern.color[pattern.color_name[color_id]][1])
        self.ui.ViewBackgroundBlueSchollbar.setValue(pattern.color[pattern.color_name[color_id]][2])

    def GenerateCommand(self):
        '''生成指令'''
        command = ""
        generated_num = 0

        for i in range(DataStorage.get_instance().current_design_size[0] - 1):
            _i = DataStorage.get_instance().current_design_size[0] - i - 1
            for j in range(DataStorage.get_instance().current_design_size[1]):
                # 旗帜属性    
                if f"{_i}:{j}" not in DataStorage.get_instance().current_design_patterns:
                    continue
                now_banner = DataStorage.get_instance().current_design_patterns[f"{_i}:{j}"].split(":")

                if now_banner[0] != "16":
                    if generated_num % 27 == 0:
                        # 指令前缀, 缩进似乎会影响指令执行, 因此不缩进不换行
                        command += f'''/give @p minecraft:chest{{display: {{Name: '{{"text":"{DataStorage.get_instance().current_design_name}","color":"gold"}}'}},BlockEntityTag:{{Items:['''

                    command += f'''{{Slot:{generated_num % 27}b,id:"minecraft:{pattern.color_name[int(now_banner[0])]}_banner",Count:1b,tag:{{display: {{Name: '{{"text":"{_i}_{j}"}}'}},'''

                    # 判断是否需要添加图案
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

    def CalculateDesignDye(self):
        dye = [0] * 16
        for key in DataStorage.get_instance().current_design_patterns:
            banner = [int(i) for i in DataStorage.get_instance().current_design_patterns[key].split(":")]
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

    def RowColumnOperation(self, isAdd: bool = True, isRow: bool = True, inverted: bool = False):
        '''
            从右或上/左或下添加/删除一行/一列
            isAdd: true - 添加  false - 删除
            isRow: true - 行  false - 列
            inverted: true - 从左或下操作  false - 从右或上操作
        '''
        if inverted:
            new_patterns = {}
            for b_key in DataStorage.get_instance().current_design_patterns:
                if isRow and isAdd:
                    key_split = b_key.split(":")
                    n_key = f"{int(key_split[0]) + 1}:{key_split[1]}"
                    new_patterns[n_key] = DataStorage.get_instance().current_design_patterns[b_key]
                elif isRow and not isAdd:
                    key_split = b_key.split(":")
                    if int(key_split[0]) <= 0:
                        continue
                    n_key = f"{int(key_split[0]) - 1}:{key_split[1]}"
                    new_patterns[n_key] = DataStorage.get_instance().current_design_patterns[b_key]
                elif not isRow and isAdd:
                    key_split = b_key.split(":")
                    n_key = f"{key_split[0]}:{int(key_split[1]) + 1}"
                    new_patterns[n_key] = DataStorage.get_instance().current_design_patterns[b_key]
                elif not isRow and not isAdd:
                    key_split = b_key.split(":")
                    if int(key_split[1]) <= 0:
                        continue
                    n_key = f"{key_split[0]}:{int(key_split[1]) - 1}"
            DataStorage.get_instance().current_design_patterns = new_patterns
        if isRow:
            self.ui.DesignRowSpinBox.setValue(self.ui.DesignRowSpinBox.value() + 1 if isAdd else self.ui.DesignRowSpinBox.value() - 1)
        else:
            self.ui.DesignColumnSpinBox.setValue(self.ui.DesignColumnSpinBox.value() + 1 if isAdd else self.ui.DesignColumnSpinBox.value() - 1)
        self.SaveCurrentDesign()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToolBox()
    window.show()
    sys.exit(app.exec_())