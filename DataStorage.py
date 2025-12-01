# 储存旗帜数据
# 该对象为单例

_instance = None

class DataStorage:
    """实际的单例类"""
    def __init__(self):
        self.filepath = ""  # 当前文件路径
        self.designs = {}  # 设计列表: {'name': [row, col, [r1:c1:banner1, ...]]}
        self.search_designs = {}  # 搜索结果
        self.current_design_name = ""
        self.current_design_size = [3, 3]  # [row, col]
        self.current_design_patterns = {}  #  dict{'r:c': 'b:p:c:p:c:...', ...}
        self.zoom_level = 7  # 缩放等级, 对应100%
        self.banner_pos = [1, 0]  # 当前点击的banner的行列数

def get_instance():
    """获取单例实例的全局函数"""
    global _instance
    if _instance is None:
        _instance = DataStorage()
    return _instance