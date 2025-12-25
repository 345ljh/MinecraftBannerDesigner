def StrBannerToList(str_banner: str):
    '''返回list元素为int'''
    splited = str_banner.split(':')
    length = (len(splited) - 1) // 2
    splited = [int(i) for i in splited]
    return length, splited

def ListToStrBanner(list_banner: list):
    list_banner = [str(i) for i in list_banner]
    return ':'.join(list_banner)


from PyQt5.QtCore import Qt

def key_to_text(key):
    """基础按键代码转文本"""
    # 字母键 (A-Z)
    if Qt.Key_A <= key <= Qt.Key_Z:
        return chr(key)
    
    # 数字键 (0-9)
    elif Qt.Key_0 <= key <= Qt.Key_9:
        return chr(key)
    
    # 功能键 (F1-F12)
    elif Qt.Key_F1 <= key <= Qt.Key_F12:
        return f"F{key - Qt.Key_F1 + 1}"
    
    # 特殊键映射
    special_keys = {
        Qt.Key_Space: "Space",
        Qt.Key_Escape: "Esc",
        Qt.Key_Return: "Enter",
        Qt.Key_Enter: "Enter",
        Qt.Key_Tab: "Tab",
        Qt.Key_Backspace: "Backspace",
        Qt.Key_Delete: "Delete",
        Qt.Key_Insert: "Insert",
        Qt.Key_Home: "Home",
        Qt.Key_End: "End",
        Qt.Key_PageUp: "PageUp",
        Qt.Key_PageDown: "PageDown",
        Qt.Key_Left: "←",
        Qt.Key_Right: "→",
        Qt.Key_Up: "↑",
        Qt.Key_Down: "↓",
        Qt.Key_CapsLock: "CapsLock",
        Qt.Key_NumLock: "NumLock",
        Qt.Key_ScrollLock: "ScrollLock",
        Qt.Key_Pause: "Pause",
        Qt.Key_Print: "PrintScreen",
        Qt.Key_Menu: "Menu",  # Windows菜单键
        Qt.Key_Help: "Help",
        
        # 符号键
        Qt.Key_Period: ".",
        Qt.Key_Comma: ",",
        Qt.Key_Semicolon: ";",
        Qt.Key_QuoteDbl: '"',
        Qt.Key_QuoteLeft: "`",
        Qt.Key_BracketLeft: "[",
        Qt.Key_BracketRight: "]",
        Qt.Key_Backslash: "\\",
        Qt.Key_Slash: "/",
        Qt.Key_Minus: "-",
        Qt.Key_Equal: "=",
        Qt.Key_Plus: "+",  # 小键盘加号
        Qt.Key_Asterisk: "*",  # 小键盘星号
        Qt.Key_ParenLeft: "(",
        Qt.Key_ParenRight: ")",
        Qt.Key_Exclam: "!",
        Qt.Key_At: "@",
        Qt.Key_NumberSign: "#",
        Qt.Key_Dollar: "$",
        Qt.Key_Percent: "%",
        Qt.Key_AsciiCircum: "^",
        Qt.Key_Ampersand: "&",
        
        # 控制键
        Qt.Key_Control: "Ctrl",
        Qt.Key_Shift: "Shift",
        Qt.Key_Alt: "Alt",
        Qt.Key_Meta: "Meta",  # Windows键/Command键
        Qt.Key_AltGr: "AltGr",
    }
    
    return special_keys.get(key, f"Key_{key}")