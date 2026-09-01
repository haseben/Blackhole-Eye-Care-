import os
import subprocess
import sys
from pathlib import Path

def build():
    """Build a self-contained Windows executable.

    The shader is shipped as data so the packaged application keeps the same
    visual effect as a source checkout.  The runtime also contains an inline
    fallback, but bundling the file makes future shader updates predictable.
    """
    print("Building Blackhole Eye Care as a single-file Windows executable...")
    
    # 确保依赖项安装
    try:
        import PyInstaller
    except ImportError:
        print("未检测到 PyInstaller，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    import PyInstaller.__main__
    
    project_dir = Path(__file__).resolve().parent
    shader_path = project_dir / "blackhole.glsl"
    if not shader_path.exists():
        raise FileNotFoundError(f"Missing shader file: {shader_path}")

    # PyInstaller uses ';' as the data-file separator on Windows.
    params = [
        str(project_dir / "main.py"),
        "--onefile",
        "--noconsole",
        "--name=Blackhole-Eye-Care",
        "--clean",
        f"--add-data={shader_path}{os.pathsep}.",
    ]
    
    # 在 Windows 下运行打包
    PyInstaller.__main__.run(params)
    print("Build complete. Find the executable in dist/Blackhole-Eye-Care.exe.")

if __name__ == "__main__":
    build()

