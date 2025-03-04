@echo off
echo Setting global index-url to TUNA Tsinghua PyPI mirror...
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
echo Configuration complete.
pause