import os
import json

DEFAULT_CONFIG = {
    "work_duration_minutes": 20,          # 工作时间（分钟）
    "rest_duration_seconds": 20,          # 达到该时长无输入，判定为休息成功，并重置计时（秒）
    "idle_threshold_seconds": 5,          # 判定用户开始“静止/休息”的无输入等待阈值（秒）
    "blackhole_start_delay_seconds": 30,  # 警告后（即达到工作时间后）多久黑洞开始显示
    "blackhole_initial_radius": 15,       # 黑洞初始半径（像素）
    "blackhole_max_radius": 350,          # 黑洞最大半径（像素）
    "blackhole_growth_rate": 0.003,        # 归一化每帧黑洞半径增长量 (OpenGL 专属)
    "animation_fps": 20,                  # 动画帧率
    "blackhole_drift_speed": 1.0          # 黑洞移动漂移速度系数
}

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".eye_care_assistant.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 合并默认配置，防止新字段缺失
                for k, v in DEFAULT_CONFIG.items():
                    if k not in config:
                        config[k] = v
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")
