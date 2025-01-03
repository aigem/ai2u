#!/bin/bash

# 设置错误时退出
set -e
# 设置工作目录
WORK_DIR=$(pwd)

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a logs/preinstall.log
}

# 检查系统要求
check_requirements() {
    log "检查系统要求..."
    
    # 检查 Python 版本
    if ! command -v python3 &> /dev/null; then
        log "错误: 未安装 Python3"
        exit 1
    fi
    
    # 检查 pip 版本并升级
    log "升级 pip..."
    python -m pip install --upgrade pip --trusted-host mirrors.cloud.tencent.com -i http://mirrors.cloud.tencent.com/pypi/simple
    
    # 检查必要命令
    for cmd in wget curl git unzip aria2; do
        if ! command -v $cmd &> /dev/null; then
            log "安装必要工具: $cmd"
            apt update && apt install -y $cmd
        fi
    done
}

# 创建虚拟环境
setup_venv() {
    log "创建虚拟环境..."
    
    # 如果已存在虚拟环境，先删除
    if [ -d ".venv" ]; then
        log "删除已存在的虚拟环境..."
        rm -rf .venv
    fi
    
    # 安装并使用 uv
    if ! command -v uv &> /dev/null; then
        log "安装 uv..."
        pip install uv -i http://mirrors.cloud.tencent.com/pypi/simple --trusted-host mirrors.cloud.tencent.com
    fi
    
    uv venv -p 3.10
    source .venv/bin/activate
}

# 安装依赖
install_dependencies() {
    log "安装依赖..."
    uv pip install -U marimo -i http://mirrors.cloud.tencent.com/pypi/simple
}

# 设置项目文件
setup_project() {
    log "设置项目文件..."
    
    # 如果目录已存在，先删除
    if [ -d "ai2u" ]; then
        log "更新已存在的项目目录..."
        cd ai2u
        git pull
    else
        log "克隆项目..."
        # git clone https://github.com/aigem/ai2u.git
        git clone https://gitee.com/fuliai/ai2u.git
        cd ai2u
    fi
    
    # 检查并创建日志目录
    mkdir -p logs
    
    # 解压 frp.zip
    if [ -f frp.zip ]; then
        log "解压 frp.zip..."
        unzip -o frp.zip
    else
        log "错误: frp.zip 不存在"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    log "检查配置文件..."
    if [ ! -f ./apps/web.ini ]; then
        echo "==================================="
        log "错误: web.ini 不存在，请获取后重试"
        log "获取方式: 加群 https://qr61.cn/oohivs/qRp62U6"
        echo "==================================="
        exit 1
    fi
}

# 启动服务
start_services() {
    log "启动服务..."
    
    # 启动 frp
    ./frp/frpc -c ./apps/web.ini &
    FRP_PID=$!
    
    # 记录 PID
    echo $FRP_PID > frp.pid
    
    log "FRP 服务已启动 (PID: $FRP_PID)"
    
    # 显示访问信息
    echo ""
    echo "==================================="
    echo "请使用以下地址打开安装界面:"
    echo "http://hb.frp.one:10086/"
    echo ""
    echo "安装日志位置: $WORK_DIR/logs/"
    echo "==================================="
    echo ""
    
    # 启动 SD
    log "启动AI应用【Stable Diffusion】安装程序"
    cd $WORK_DIR
    marimo run apps/sd.py
}

# 清理函数
cleanup() {
    log "执行清理..."
    if [ -f frp.pid ]; then
        kill $(cat frp.pid) 2>/dev/null || true
        rm frp.pid
    fi
}

# 设置清理钩子
trap cleanup EXIT

# 主函数
main() {
    log "开始安装..."
    
    check_requirements
    setup_venv
    install_dependencies
    setup_project
    check_config
    start_services
}

# 执行主函数
main
