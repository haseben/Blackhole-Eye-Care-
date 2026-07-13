import sys
import os
import tempfile
from PyQt6.QtCore import QLockFile
from PyQt6.QtWidgets import QApplication, QMessageBox

from config import load_config, save_config
from black_hole import BlackHoleOverlay
from timer_manager import TimerManager
from tray_icon import EyeCareTrayIcon

def main():
    # 1. 保证单实例运行 (防多开)
    lock_path = os.path.join(tempfile.gettempdir(), "eye_care_assistant.lock")
    lock_file = QLockFile(lock_path)
    
    # 强制在 Qt 实例前初始化，如果锁不住，直接退出
    # 需要保留 lock_file 的引用，否则它出了作用域会被自动垃圾回收，导致锁失效
    # 所以我们把它挂在全局或者主函数本地，但要在程序退出时依然存活
    if not lock_file.tryLock(100):
        # 创建一个临时的 QApplication 用于显示提示弹窗
        temp_app = QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "护眼助手",
            "护眼助手已经在运行中！\n请检查系统右下角托盘图标。",
            QMessageBox.StandardButton.Ok
        )
        sys.exit(0)

    # 2. 正常初始化应用
    app = QApplication(sys.argv)
    
    # 避免程序在所有窗口关闭时退出 (因为我们平常主窗口是隐藏的/没有主窗口)
    app.setQuitOnLastWindowClosed(False)
    
    # 3. 加载用户配置
    config = load_config()
    
    # 4. 配置保存回调
    def on_config_save(new_config):
        save_config(new_config)
    
    # 5. 创建透明置顶的黑洞 overlay 窗口
    overlay = BlackHoleOverlay(config)
    
    # 6. 创建时间管理器
    manager = TimerManager(config, overlay)
    
    # 7. 创建系统托盘
    tray = EyeCareTrayIcon(manager, config, on_config_save)
    tray.show()
    
    # 8. 启动计时
    manager.start()
    
    # 9. 运行应用
    exit_code = app.exec()
    
    # 10. 退出时释放文件锁
    lock_file.unlock()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
