import os
import subprocess
import sys

def build():
    print("开始打包 '护眼助手' 为单文件 EXE...")
    
    # 确保依赖项安装
    try:
        import PyInstaller
    except ImportError:
        print("未检测到 PyInstaller，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    import PyInstaller.__main__
    
    # 打包参数
    params = [
        'main.py',
        '--onefile',            # 打包成单个可执行文件
        '--noconsole',          # 不显示控制台黑窗口
        '--name=护眼助手',       # 生成的可执行文件名
        '--clean',              # 清理 PyInstaller 缓存
    ]
    
    # 在 Windows 下运行打包
    PyInstaller.__main__.run(params)
    print("打包完成！请在 'dist' 文件夹中查找 '护眼助手.exe'。")

if __name__ == "__main__":
    build()
