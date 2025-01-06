#!/bin/bash

# =====================================================
# 环境要求说明：
# 1. 操作系统：Linux Ubuntu
# 2. 权限要求：需要 root 权限
# 3. 测试环境：IDE Cloud Studio
# 4. 使用方法：
#    方法1：下载后直接运行：
#    ./ai2u.sh <应用名称> [edit|run]
#    方法2：使用curl方式运行：
#    deactivate && apt-get update && apt-get install -y curl; bash -c "$(curl -fsSL https://gitee.com/fuliai/ai2u/raw/main/ai2u.sh)" - <应用名称> [edit|run]
#    
#    参数说明：
#    - 应用名称：必填，须与apps目录下的安装文件名一致
#    - 运行模式：可选，edit或run，默认为run
# =====================================================

# 获取最后一个参数作为应用名称
APP_NAME="${@: -2:1}"
RUN_MODE="${@: -1}"

# 如果最后一个参数不是 edit 或 run，则假定它是应用名称
if [[ "$RUN_MODE" != "edit" && "$RUN_MODE" != "run" ]]; then
    APP_NAME="${@: -1}"
    RUN_MODE="run"
fi

# 检查是否提供了应用名称
if [ -z "$APP_NAME" ]; then
    echo "错误：请提供应用名称(须与apps目录下的安装文件名一致)"
    echo "使用方法：./ai2u.sh <应用名称> [edit|run]"
    exit 1
fi

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
    
    # 如果目录已存在，先删除，再clone https://gitee.com/fuliai/ai2u.git
    if [ -d "ai2u" ]; then
        log "删除已存在的项目目录..."
        rm -rf ai2u
    fi
    log "克隆项目..."
    git clone https://gitee.com/fuliai/ai2u.git
    cd ai2u
    
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

# 启动服务
start_services() {
    log "启动服务..."

    # 临时禁用错误退出
    set +e

    log "正在启动 KSA..."
    if [ ! -x "$WORK_DIR/apps/ksa/ksa_x64" ]; then
        log "错误: KSA 可执行文件不存在或没有执行权限"
        chmod +x "$WORK_DIR/apps/ksa/ksa_x64" 2>/dev/null || {
            log "错误: 无法设置执行权限"
            return 1
        }
    fi

    rm -f "$WORK_DIR/ksa_ID_Token.txt"  # 先删除可能存在的旧文件
    
    # 运行 KSA 并捕获返回值
    "$WORK_DIR/apps/ksa/ksa_x64" > "$WORK_DIR/ksa_ID_Token.txt" 2>&1
    KSA_STATUS=$?
    
    if [ $KSA_STATUS -ne 0 ]; then
        log "警告: KSA 返回状态码 $KSA_STATUS"
    fi
    
    # 检查文件是否生成并有内容
    if [ -s "$WORK_DIR/ksa_ID_Token.txt" ]; then
        log "KSA 已运行完成，ID和Token已保存到 $WORK_DIR/ksa_ID_Token.txt"
        echo "==================================="
        echo "KSA 已运行完成，ID和Token已保存到 $WORK_DIR/ksa_ID_Token.txt"
        echo "详细使用请进群获取: https://qr61.cn/oohivs/qRp62U6"
        echo "==================================="
        echo ""
    else
        log "警告: KSA 未生成有效的 ID 和 Token，尝试再次运行"
        "$WORK_DIR/apps/ksa/ksa_x64" > "$WORK_DIR/ksa_ID_Token.txt" 2>&1
        if [ ! -s "$WORK_DIR/ksa_ID_Token.txt" ]; then
            log "错误: KSA 再次运行失败"
            log "请自行部署内网穿透工具来访问服务"
        fi
    fi

    # 重新启用错误退出
    set -e
    
    # 启动 frp
    log "检查配置文件,存在才启动frp"
    if [ -f "$WORK_DIR/apps/frpc.ini" ]; then
        log "配置文件存在，正在启动 FRP..."
        chmod +x "$WORK_DIR/apps/frpc"
        cd "$WORK_DIR/apps"
        ./frpc > "$WORK_DIR/logs/frp.log" 2>&1 &
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
    else
        log "错误: frpc.ini 不存在，请获取后重试，并放在 $WORK_DIR/apps/ 目录下"
        log "获取方式: 加群 https://qr61.cn/oohivs/qRp62U6"
        log "跳过启动frp"
    fi
    
    # 启动 SD
    log "启动-AI应用-安装程序"
    cd $WORK_DIR
    # 启动的文件名称，使用APP_NAME变量
    if [ "$RUN_MODE" = "run" ]; then
        log "启动应用：$APP_NAME"
        log "启动端口：7860"
        log "如果不会内网穿透，请使用终端模式：退出安装程序运行以下命令"
        log "python 'apps/${APP_NAME}.py'"
        marimo run "apps/${APP_NAME}.py" -p 7860 --no-token
    else
        log "启动应用：$APP_NAME (模式: 编辑模式)"
        marimo edit "apps/${APP_NAME}.py" -p 7860 --no-token
    fi
}

# 主函数
main() {
    log "开始安装..."
    log "工作目录: $WORK_DIR"
    log "应用名称: $APP_NAME"
    log "运行模式: $RUN_MODE"
    
    check_requirements
    setup_venv
    install_dependencies
    setup_project
    start_services
}

# 执行主函数
main
