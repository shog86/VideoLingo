#!/bin/bash

# VideoLingo 安装脚本
# 确保使用正确的 Python 3.10.0 环境

echo "🔍 初始化 Conda..."

# 加载 Conda 配置
if [ -n "$CONDA_EXE" ]; then
    CONDA_ROOT=$(dirname $(dirname "$CONDA_EXE"))
elif [ -d "/opt/homebrew/anaconda3" ]; then
    CONDA_ROOT="/opt/homebrew/anaconda3"
elif [ -d "/opt/homebrew/miniconda3" ]; then
    CONDA_ROOT="/opt/homebrew/miniconda3"
elif [ -d "$HOME/anaconda3" ]; then
    CONDA_ROOT="$HOME/anaconda3"
elif [ -d "$HOME/miniconda3" ]; then
    CONDA_ROOT="$HOME/miniconda3"
fi

if [ -f "$CONDA_ROOT/etc/profile.d/conda.sh" ]; then
    source "$CONDA_ROOT/etc/profile.d/conda.sh"
else
    # Try which conda
    CONDA_PATH=$(which conda)
    if [ -n "$CONDA_PATH" ]; then
        CONDA_ROOT=$(dirname $(dirname "$CONDA_PATH"))
        if [ -f "$CONDA_ROOT/etc/profile.d/conda.sh" ]; then
            source "$CONDA_ROOT/etc/profile.d/conda.sh"
        fi
    fi
fi

if ! command -v conda &> /dev/null; then
    echo "❌ 错误: 找不到 Conda 命令"
    exit 1
fi

echo "✅ Conda 已加载"

# 检查并激活 videolingo 环境
echo "🔧 检查 videolingo 环境..."

if conda info --envs | grep -q "^videolingo "; then
    echo "✅ 找到 videolingo 环境"
else
    echo "创建 videolingo 环境 (Python 3.10)..."
    conda create -n videolingo python=3.10 -y
    if [ $? -ne 0 ]; then
        echo "❌ 错误: 无法创建 videolingo 环境"
        exit 1
    fi
fi

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
