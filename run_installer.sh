#!/bin/bash

# VideoLingo 安装脚本
# 确保使用正确的 Python 3.10.0 环境

echo "🔍 初始化 Conda..."

# 加载 Conda 配置
if [ -f "/Users/shog/miniconda3/etc/profile.d/conda.sh" ]; then
    source "/Users/shog/miniconda3/etc/profile.d/conda.sh"
else
    echo "❌ 错误: 找不到 Conda 配置文件"
    exit 1
fi

echo "✅ Conda 已加载"

# 激活 videolingo 环境
echo "🔧 激活 videolingo 环境..."
conda activate videolingo

if [ $? -ne 0 ]; then
    echo "❌ 错误: 无法激活 videolingo 环境"
    exit 1
fi

echo "✅ videolingo 环境已激活"

# 检查 Python 版本
echo "🐍 当前 Python 版本:"
python --version

# 检查使用的是哪个 Python
echo "📍 Python 路径:"
which python

# 运行安装程序
echo ""
echo "🚀 开始运行 VideoLingo 安装程序..."
echo "================================================"
python install.py
