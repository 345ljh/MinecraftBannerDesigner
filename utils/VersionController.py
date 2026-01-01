import oss2
from PyQt5.QtWidgets import QMessageBox

# 版本更新时需修改current_version, 同时将对应内容写入version.txt上传OSS
# OSS为公共read且仅支持网页内手动write
# current_version需严格递增
current_version = 260101  # 当前版本(int)

def get_version():
    """从OSS获取版本号"""
    try:
        auth = oss2.AnonymousAuth()
        bucket = oss2.Bucket(auth, 'https://oss-cn-shenzhen.aliyuncs.com', 'minecraft-banner-designer')
        # 直接读取到内存
        content = bucket.get_object('version.txt').read().decode('utf-8')
        version = content.strip()
        return int(version)
    except Exception as e:  # 一般是网络错误
        return -1

def get_update():
    """获取更新内容"""
    try:
        auth = oss2.AnonymousAuth()
        bucket = oss2.Bucket(auth, 'https://oss-cn-shenzhen.aliyuncs.com', 'minecraft-banner-designer')
        path = f'ver{get_version()}.zip'
        bucket.get_object_to_file('mcbd.zip', path)
        # 下载完成后提示完成并输出路径
        QMessageBox.information(None, '提示', f'下载完成，压缩包已保存至./{path}')

    except Exception as e:
        QMessageBox.information(None, '提示', '网络错误，请检查网络连接后重试')