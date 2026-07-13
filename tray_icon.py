import sys
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (QSystemTrayIcon, QMenu, QDialog, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, 
                             QPushButton, QApplication, QMessageBox, QComboBox)
from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QAction, QBrush, QPixmap

class SettingsDialog(QDialog):
    def __init__(self, config, on_save_callback):
        super().__init__()
        self.config = config
        self.on_save_callback = on_save_callback
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("护眼助手 - 设置")
        self.setFixedSize(320, 360)
        
        # 整体美化样式表（深色科技风格）
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                color: #e0e0e0;
                font-family: "Segoe UI", "Microsoft YaHei";
            }
            QLabel {
                color: #c0c0c8;
                font-size: 13px;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #2a2a35;
                color: #ffffff;
                border: 1px solid #4a4a5a;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
                min-width: 80px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #7c4dff;
            }
            QPushButton {
                background-color: #3f51b5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5c6bc0;
            }
            QPushButton:pressed {
                background-color: #303f9f;
            }
            QPushButton#cancelBtn {
                background-color: #424242;
            }
            QPushButton#cancelBtn:hover {
                background-color: #616161;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_label = QLabel("🔬 科学护眼参数设置")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #7c4dff; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 字段表单
        self.spin_work = self.create_row(layout, "工作时长 (分钟):", 1, 120, self.config["work_duration_minutes"])
        self.spin_rest = self.create_row(layout, "休息时长 (秒):", 5, 600, self.config["rest_duration_seconds"])
        self.spin_idle = self.create_row(layout, "判定空闲时间 (秒):", 2, 60, self.config["idle_threshold_seconds"])
        self.spin_max_r = self.create_row(layout, "黑洞最大半径 (像素):", 50, 800, self.config["blackhole_max_radius"])
        
        # 增长速度 (Double)
        hbox = QHBoxLayout()
        lbl = QLabel("黑洞生长速度:")
        hbox.addWidget(lbl)
        self.spin_growth = QDoubleSpinBox()
        self.spin_growth.setRange(0.1, 10.0)
        self.spin_growth.setSingleStep(0.1)
        self.spin_growth.setValue(self.config["blackhole_growth_rate"])
        hbox.addWidget(self.spin_growth)
        layout.addLayout(hbox)
        
        # 3. 追加黑洞漂移移动速度调节器 (QDoubleSpinBox)
        hbox_drift = QHBoxLayout()
        lbl_drift = QLabel("黑洞漂移速度:")
        hbox_drift.addWidget(lbl_drift)
        self.spin_drift = QDoubleSpinBox()
        self.spin_drift.setRange(0.0, 10.0)
        self.spin_drift.setSingleStep(0.1)
        self.spin_drift.setValue(self.config.get("blackhole_drift_speed", 1.0))
        hbox_drift.addWidget(self.spin_drift)
        layout.addLayout(hbox_drift)
        
        layout.addSpacing(10)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def create_row(self, parent_layout, label_text, min_v, max_v, current_v):
        hbox = QHBoxLayout()
        lbl = QLabel(label_text)
        hbox.addWidget(lbl)
        spin = QSpinBox()
        spin.setRange(min_v, max_v)
        spin.setValue(current_v)
        hbox.addWidget(spin)
        parent_layout.addLayout(hbox)
        return spin
        
    def save_settings(self):
        self.config["work_duration_minutes"] = self.spin_work.value()
        self.config["rest_duration_seconds"] = self.spin_rest.value()
        self.config["idle_threshold_seconds"] = self.spin_idle.value()
        self.config["blackhole_max_radius"] = self.spin_max_r.value()
        self.config["blackhole_growth_rate"] = self.spin_growth.value()
        self.config["blackhole_drift_speed"] = self.spin_drift.value()
        
        self.on_save_callback(self.config)
        self.accept()


class EyeCareTrayIcon(QSystemTrayIcon):
    def __init__(self, timer_manager, config, save_config_callback):
        super().__init__()
        self.timer_manager = timer_manager
        self.config = config
        self.save_config_callback = save_config_callback
        
        self.init_icon()
        self.init_menu()
        
        # 监听时间更新
        self.timer_manager.time_updated.connect(self.update_status_info)
        
        # 双击托盘图标打开设置
        self.activated.connect(self.on_tray_activated)
        
    def init_icon(self):
        """动态绘制一个精美的托盘图标，免去外部图片依赖"""
        # 绘制一个 32x32 的图
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 外环 - 深色渐变
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(30, 20, 50)))
        painter.drawEllipse(2, 2, 28, 28)
        
        # 中环 - 护眼绿色
        painter.setBrush(QBrush(QColor(46, 204, 113)))
        painter.drawEllipse(6, 6, 20, 20)
        
        # 内环（瞳孔/黑洞） - 纯黑色
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(11, 11, 10, 10)
        
        painter.end()
        
        self.setIcon(QIcon(pixmap))
        
    def init_menu(self):
        self.menu = QMenu()
        
        # 统一菜单样式
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #24242c;
                color: #e0e0e0;
                border: 1px solid #444454;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #3f51b5;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #444454;
                margin: 4px 0px;
            }
        """)
        
        # 状态展示项 (作为不可点击的灰色项)
        self.status_action = QAction("状态: 初始化中...", self)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        
        self.menu.addSeparator()
        
        # 设置项
        settings_action = QAction("⚙️ 设置...", self)
        settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(settings_action)
        
        # 手动重置项
        reset_action = QAction("🔄 重置计时", self)
        reset_action.triggered.connect(self.timer_manager.force_rest)
        self.menu.addAction(reset_action)
        
        self.menu.addSeparator()
        
        # 退出项
        exit_action = QAction("❌ 退出程序", self)
        exit_action.triggered.connect(self.quit_app)
        self.menu.addAction(exit_action)
        
        self.setContextMenu(self.menu)
        
    def on_tray_activated(self, reason):
        # 双击左键打开设置
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings()
            
    def show_settings(self):
        dialog = SettingsDialog(self.config, self.save_config_callback)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 配置在保存时会调用回调，这里再通知 timer_manager 更新配置缓存
            self.timer_manager.update_config_cache()
            
    def update_status_info(self, remaining_work, current_rest, status_str):
        """实时更新托盘右键菜单和悬浮提示信息"""
        if status_str == "working":
            min_left = remaining_work // 60
            sec_left = remaining_work % 60
            info = f"工作中 (剩余: {min_left}分{sec_left}秒)"
            tooltip = f"护眼助手\n状态: 正常工作中\n离休息还有: {min_left}分{sec_left}秒"
        elif status_str == "reminding":
            info = "⚠️ 请立即休息！"
            tooltip = "护眼助手\n状态: 超时未休息！\n黑洞正在吞噬您的屏幕..."
        elif status_str == "resting":
            info = f"💤 休息中 ({current_rest}秒)"
            tooltip = f"护眼助手\n状态: 正在检测休息\n已连续休息: {current_rest}秒"
        else:
            info = "未知状态"
            tooltip = "护眼助手"
            
        self.status_action.setText(f"状态: {info}")
        self.setToolTip(tooltip)
        
    def quit_app(self):
        # 停止所有子线程和定时器，防止死锁
        self.timer_manager.stop()
        QApplication.quit()
