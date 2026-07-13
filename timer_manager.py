import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from input_monitor import InputMonitor

class Status:
    WORKING = "working"      # 正常工作中
    REMINDING = "reminding"  # 超时提醒中（黑洞出现）
    RESTING = "resting"      # 判定休息中（无键盘鼠标输入）

class TimerManager(QObject):
    # 信号通知 UI 状态变化或时间更新
    status_changed = pyqtSignal(str)              # 状态改变信号
    time_updated = pyqtSignal(int, int, str)       # 剩余工作时间(秒), 当前连续休息时间(秒), 状态字符串

    def __init__(self, config, blackhole_overlay):
        super().__init__()
        self.config = config
        self.blackhole = blackhole_overlay
        
        # 输入监控器
        self.monitor = InputMonitor()
        
        # 计时器状态
        self.status = Status.WORKING
        self.elapsed_work_time = 0.0  # 累计工作秒数
        self.continuous_rest_time = 0.0  # 累计连续休息秒数
        
        # 主逻辑定时器 (1秒执行一次)
        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.tick_1s)
        
        # 缓存参数
        self.update_config_cache()
        
    def update_config_cache(self):
        self.work_seconds = self.config.get("work_duration_minutes", 20) * 60
        self.rest_seconds = self.config.get("rest_duration_seconds", 20)
        self.idle_threshold = self.config.get("idle_threshold_seconds", 5)
        
    def start(self):
        self.monitor.start()
        self.main_timer.start(1000)
        self.status = Status.WORKING
        self.elapsed_work_time = 0.0
        self.continuous_rest_time = 0.0
        self.status_changed.emit(self.status)
        
    def stop(self):
        self.main_timer.stop()
        self.monitor.stop()
        self.blackhole.stop()
        
    def tick_1s(self):
        """每秒执行一次的调度状态机"""
        idle_time = self.monitor.get_idle_time()
        
        # 状态机跳转逻辑
        if self.status == Status.WORKING:
            if idle_time >= self.idle_threshold:
                # 键盘鼠标空闲，转为休息判定
                self.change_status(Status.RESTING)
                self.continuous_rest_time = idle_time
            else:
                # 正常打字工作中
                self.elapsed_work_time += 1.0
                if self.elapsed_work_time >= self.work_seconds:
                    self.change_status(Status.REMINDING)
                    
        elif self.status == Status.REMINDING:
            if idle_time >= self.idle_threshold:
                # 键盘鼠标空闲，转为休息判定，但黑洞暂时保留，直到休息完成才消失
                self.change_status(Status.RESTING)
                self.continuous_rest_time = idle_time
            else:
                # 依然在强行工作，黑洞持续保留并增大
                self.elapsed_work_time += 1.0
                
        elif self.status == Status.RESTING:
            if idle_time < self.idle_threshold:
                # 用户又动了键盘/鼠标！说明只是短暂发呆，未达到彻底休息。
                # 根据之前的工作时间，判断退回到工作还是提醒状态
                if self.elapsed_work_time >= self.work_seconds:
                    self.change_status(Status.REMINDING)
                else:
                    self.change_status(Status.WORKING)
                self.continuous_rest_time = 0.0
            else:
                # 持续无输入，累加休息时间
                self.continuous_rest_time = idle_time
                if self.continuous_rest_time >= self.rest_seconds:
                    # 休息时间足够！重置计时，清除黑洞
                    self.reset_timer()
                    
        # 发送时间更新信号给 UI
        remaining_work = max(0, int(self.work_seconds - self.elapsed_work_time))
        current_rest = int(self.continuous_rest_time)
        self.time_updated.emit(remaining_work, current_rest, self.status)
            
    def change_status(self, new_status):
        if self.status == new_status:
            return
            
        self.status = new_status
        self.status_changed.emit(self.status)
        
        # 根据新状态启动/关闭黑洞
        if self.status == Status.REMINDING:
            self.monitor.stop()
            self.blackhole.start()
            self.monitor.start()
        elif self.status == Status.WORKING:
            self.blackhole.stop()
        elif self.status == Status.RESTING:
            # 处于 RESTING 时，黑洞不需要立即关闭，但也不要新建。
            # 如果是从 REMINDING 进来的，黑洞会继续留在屏幕上，但不继续增长（或者继续慢慢增长，取决于用户想不想它消失）。
            # 当满足 rest_seconds 后，reset_timer() 会将其彻底关闭。
            pass

    def reset_timer(self):
        """重置计时器，全部归零，回到 WORKING 状态"""
        self.elapsed_work_time = 0.0
        self.continuous_rest_time = 0.0
        self.change_status(Status.WORKING)
        self.blackhole.stop()
        self.monitor.reset_activity()
        
    def force_rest(self):
        """手动重置/休息"""
        self.reset_timer()
