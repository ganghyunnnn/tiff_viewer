import sys
from PyInstaller import __main__ as pyi

# 실행 파일로 만들 스크립트 파일
script = "tiff_opener.py"

# 제외할 모듈
excluded_modules = [
    'altgraph',
    'cv_Logging',
    'lief',
    'packaging',
    'pefile',
    'pip',
    'pyinstaller',
    'pyinstaller-hooks-contrib',
    'pyproj',
    'pywin32-ctypes',
    'setuptools',
    'wheel'
]

# 실행 파일 생성
pyi.run([
    '--name=ImageViewer',
    '--onefile',  # 실행 파일을 하나로 설정
    '--windowed',  # GUI 어플리케이션으로 설정
    '--icon=viewer_icon.ico', # 아이콘 파일 지정
    *[f"--exclude-module={module}" for module in excluded_modules],
    script  # 변환할 스크립트 파일
])
