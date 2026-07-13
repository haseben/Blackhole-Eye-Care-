import time
from pynput import mouse, keyboard

class InputMonitor:
    def __init__(self):
        self.last_activity_time = time.time()
        self.mouse_listener = None
        self.keyboard_listener = None
        self.running = False

    def _on_activity(self, *args):
        self.last_activity_time = time.time()

    def start(self):
        if self.running:
            return
        
        self.running = True
        self.last_activity_time = time.time()

        # 启动鼠标事件监听
        self.mouse_listener = mouse.Listener(
            on_move=self._on_activity,
            on_click=self._on_activity,
            on_scroll=self._on_activity
        )
        self.mouse_listener.daemon = True
        self.mouse_listener.start()

        # 启动键盘事件监听
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_activity
        )
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
            self.mouse_listener = None

        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception:
                pass
            self.keyboard_listener = None

    def get_idle_time(self):
        """返回当前的空闲时间（单位：秒）"""
        return time.time() - self.last_activity_time

    def reset_activity(self):
        """强制重置最后活动时间"""
        self.last_activity_time = time.time()
