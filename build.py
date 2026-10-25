#!/usr/bin/env python3
"""一键构建：python3 build.py

1. 运行 src/gen.py：按几何参数计算音箱坐标、角度、尺寸，生成全部 SVG，
   填进 src/template.html，得到页面片段 build/page.html。
2. 套上 src/skeleton-head.html（doctype、viewport、基础样式），输出可以直接打开的 index.html。
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)

frag_path = os.path.join(BUILD, "page.html")
subprocess.run([sys.executable, os.path.join(SRC, "gen.py"), frag_path, os.path.join(SRC, "template.html")], check=True)

head = open(os.path.join(SRC, "skeleton-head.html"), encoding="utf-8").read()
frag = open(frag_path, encoding="utf-8").read()
out = os.path.join(ROOT, "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(head + frag + "\n</body></html>")
print("built", out)
