#!/bin/bash

# 设置错误时退出
set -e
# 设置工作目录
WORK_DIR=$(pwd)

# 确保日志目录存在
mkdir -p $WORK_DIR/logs

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $WORK_DIR/logs/preinstall.log
}

# 初始化日志文件
log "=== 开始新的安装会话 ==="
log "初始化工作目录: $WORK_DIR"

# 检查系统要求
check_requirements() {
    log "检查系统要求..."
    
    # 检查 Python 版本
    if ! command -v python &> /dev/null; then
        log "错误: 未安装 Python"
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
        git clone https://github.com/aigem/ai2u.git
        # git clone https://gitee.com/fuliai/ai2u.git
        cd ai2u
    fi
    
    # 解压 frp.zip
    if [ -f frp.zip ]; then
        log "解压 frp.zip..."
        unzip -o frp.zip -d $WORK_DIR/apps/
    else
        log "错误: frp.zip 不存在"
        exit 1
    fi

    # 解压 ksa.zip
    if [ -f ksa.zip ]; then
        log "解压 ksa.zip..."
        unzip -o ksa.zip -d $WORK_DIR/apps/
    else
        log "错误: ksa.zip 不存在"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    log "检查配置文件..."
    if [ ! -f $WORK_DIR/apps/frpc.ini ]; then
        echo "==================================="
        log "错误: frpc.ini 不存在，请获取后重试，并放在 $WORK_DIR/apps/ 目录下"
        log "获取方式: 加群 https://qr61.cn/oohivs/qRp62U6"
        echo "==================================="
        exit 1
    fi
}

# 启动服务
start_services() {
    log "启动服务..."

    # 启动 ksa（添加超时控制）
    log "正在启动 KSA..."
    chmod +x $WORK_DIR/apps/ksa/ksa_x64
    $WORK_DIR/apps/ksa/ksa_x64 > $WORK_DIR/ksa_ID_Token.txt 2>&1 &
    log "KSA 已运行完成，ID和Token已保存到 $WORK_DIR/ksa_ID_Token.txt"
    log "详细使用请进群获取: https://qr61.cn/oohivs/qRp62U6"
    
    # 启动 frp
    log "正在启动 FRP..."
    chmod +x $WORK_DIR/apps/frpc
    cd $WORK_DIR/apps
    ./frpc > $WORK_DIR/logs/frp.log 2>&1 &
    FRP_PID=$!
    echo $FRP_PID > frp.pid
    log "FRP 服务已启动 (PID: $FRP_PID)"
    
    # 显示访问信息
    echo ""
    echo "==================================="
    echo "请使用以下地址打开安装界面:"
    echo ""
    echo "http://hb.frp.one:10086/"
    echo ""
    echo "安装日志位置: $WORK_DIR/logs/"
    echo "==================================="
    echo ""
    
    # 启动 SD
    log "启动AI应用【Stable Diffusion】安装程序"
    cd $WORK_DIR
    marimo run apps/sd.py -p 7860 --no-token
}

# 主函数
main() {
    log "开始安装..."
    log "工作目录: $WORK_DIR"
    
    check_requirements
    setup_venv
    install_dependencies
    setup_project
    check_config
    start_services
}

# 执行主函数
main
