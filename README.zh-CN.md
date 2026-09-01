# Blackhole Eye Care（黑洞护眼助手）

> 用一个会吞噬屏幕的黑洞，提醒你真正离开电脑休息。

[![最新版本](https://img.shields.io/github/v/release/haseben/Blackhole-Eye-Care-?display_name=tag&sort=semver&color=ffb45f)](https://github.com/haseben/Blackhole-Eye-Care-/releases/latest)
[![Windows](https://img.shields.io/badge/平台-Windows-0078D4?logo=windows&logoColor=white)](https://github.com/haseben/Blackhole-Eye-Care-/releases/latest)
[![许可证](https://img.shields.io/badge/license-MIT-8fd694.svg)](LICENSE)
[![English](https://img.shields.io/badge/docs-English-8ab4f8)](README.md)

Blackhole Eye Care 是一款基于 **20-20-20 护眼法则**的 Windows 护眼助手。连续工作达到设定时长后，一个由 GPU 渲染的黑洞会逐渐扭曲并吞噬桌面，直到你真正停下来休息。

它不是一个可以顺手关闭的弹窗：放下鼠标和键盘，持续休息，黑洞才会消失，并自动开始下一轮工作计时。

![Blackhole Eye Care 视觉预览](assets/demo.gif)

## 下载

**[下载最新 Windows 版本](https://github.com/haseben/Blackhole-Eye-Care-/releases/latest)** · [查看全部版本](https://github.com/haseben/Blackhole-Eye-Care-/releases)

Release 页面提供单文件绿色版 `Blackhole-Eye-Care.exe` 和 SHA-256 校验值。由于是新的未签名开源程序，Windows 可能显示 SmartScreen 提示；运行前请先核对校验值。

## 核心特点

- **视觉提醒，而不是弹窗**：黑洞缓慢生长，足够醒目但不会突然打断。
- **自动识别休息**：无需点击“开始休息”，键鼠持续无操作达到设定时长后自动重置。
- **GPU 加速渲染**：在显卡支持所需 OpenGL 上下文时，着色器会渲染引力透镜、吸积盘、多普勒不对称和光子环。
- **隐私优先**：项目没有遥测、账号系统或网络服务。桌面截图只在本地用于覆盖层纹理，不会上传。

## 工作原理

```text
工作中 ──达到工作时长──▶ 提醒中 ──停止操作──▶ 休息中
   ▲                         │                    │
   └────────恢复操作─────────┘                    │
                         休息完成 ─────────────────┘
```

托盘程序通过 `pynput` 监听本地输入。达到工作时长后，透明、鼠标穿透的覆盖层会截取当前桌面并渲染黑洞着色器。持续无输入达到休息时长后，覆盖层关闭并开始新的工作周期。

## 从源码运行

需要 Windows、Python 3.8+，以及支持所需 OpenGL 上下文的显卡驱动。

```bash
git clone https://github.com/haseben/Blackhole-Eye-Care-.git
cd Blackhole-Eye-Care-
python -m pip install -r requirements.txt
python main.py
```

本地构建绿色版 EXE：

```bash
python build_exe.py
```

生成文件位于 `dist/Blackhole-Eye-Care.exe`。向仓库推送 `v*` 标签也会触发 GitHub Actions，自动构建并发布 Release。

## 默认参数

右键托盘图标，选择“设置”。配置保存在 `%USERPROFILE%\\.eye_care_assistant.json`。

| 参数 | 默认值 | 说明 |
| --- | ---: | --- |
| 工作时长 | 20 分钟 | 连续工作多久后出现提醒 |
| 休息时长 | 20 秒 | 需要持续无操作多久才重置 |
| 判定空闲时间 | 5 秒 | 多久无操作开始计入休息 |
| 黑洞最大半径 | 350 px | 黑洞视觉尺寸上限 |
| 生长速度 | 0.003 | 每帧归一化增长量 |
| 漂移速度 | 1.0 | 黑洞在屏幕上的移动速度 |

## 项目结构

```text
main.py                # 程序入口与组件装配
black_hole.py          # 透明 OpenGL 覆盖层与动画
blackhole.glsl         # 引力透镜片段着色器
timer_manager.py       # 工作 / 提醒 / 休息状态机
input_monitor.py       # 键鼠活动监听
tray_icon.py           # 系统托盘菜单与设置面板
config.py              # JSON 配置持久化
build_exe.py           # PyInstaller 打包脚本
tools/generate_demo.py # 离线视觉预览生成器
```

## 参与贡献

欢迎提交 Issue 和 Pull Request。修改着色器或计时逻辑时，请附上简短录屏或可复现步骤，方便审查视觉效果和休息识别行为。

## 许可证

MIT，详见 [LICENSE](LICENSE)。

English：[README.md](README.md)

