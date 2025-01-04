import marimo

__generated_with = "0.10.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import subprocess
    import sys
    import os
    import logging
    from datetime import datetime
    return datetime, logging, mo, os, subprocess, sys


@app.cell
def _(mo):
    aitool_name = mo.ui.dropdown(
        ["comfyUI", "openWebUI", "StableDifusion"], value="StableDifusion"
    )

    return (aitool_name,)


@app.cell
def _(aitool_name, datetime, logging, os):
    def setup_logger():
        # 创建logs目录（如果不存在）
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # 设置日志文件名（使用当前日期）
        log_file = (
            f'logs/{aitool_name.value}_{datetime.now().strftime("%Y%m%d")}.log'
        )

        # 配置日志记录器
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        logger = logging.getLogger("{aitool_name.value}")
        return logger


    # 初始化日志记录器
    logger = setup_logger()


    def log_info(message):
        """记录信息级别的日志"""
        logger.info(message)


    def log_error(message):
        """记录错误级别的日志"""
        logger.error(message)


    def log_warning(message):
        """记录警告级别的日志"""
        logger.warning(message)
    return log_error, log_info, log_warning, logger, setup_logger


@app.cell
def _(mo):
    def main_title():
        return mo.md(
            """
            # Ai for U
            """
        ).callout()
    return (main_title,)


@app.cell
def _(log_info, mo, os, subprocess, sys):
    def show_info():
        info = []

        # 当前路径信息
        current_path = os.getcwd()
        info.append(f"当前路径: {current_path}")
        log_info(f"系统路径: {current_path}")

        # Python 版本
        python_version = sys.version.split()[0]
        info.append(f"\n Python 版本: {python_version}")
        log_info(f"Python版本: {python_version}")

        # Node.js 版本
        try:
            node_version = subprocess.check_output(
                ["node", "--version"], text=True
            ).strip()
            info.append(f"\n Node.js版本: {node_version}")
            log_info(f"Node.js版本: {node_version}")
        except:
            info.append(f"\n Node.js 未安装")
            log_info("Node.js未安装")

        # uv 版本
        try:
            uv_version = subprocess.check_output(
                ["uv", "--version"], text=True
            ).strip()
            info.append(f"\n uv版本: {uv_version}")
            log_info(f"uv版本: {uv_version}")
        except:
            info.append(f"\n uv 未安装")
            log_info("uv未安装")

        # 虚拟环境信息
        if "VIRTUAL_ENV" in os.environ:
            venv_path = os.environ["VIRTUAL_ENV"]
            info.append(f"\n 已激活，虚拟环境路径: {venv_path}")
            log_info(f"虚拟环境路径: {venv_path}")
        else:
            info.append("\n 未在虚拟环境中运行")
            log_info("未在虚拟环境中运行")

        # 检查指定软件安装情况
        info.append(f"\n#### 已安装的包")
        try:
            import marimo

            info.append(f"✓ marimo {marimo.__version__}")
            log_info(f"marimo版本: {marimo.__version__}")
        except:
            info.append("✗ marimo 未安装")
            log_info("marimo未安装")

        try:
            import fastapi

            info.append(f"✓ fastapi {fastapi.__version__}")
            log_info(f"fastapi版本: {fastapi.__version__}")
        except:
            info.append("✗ fastapi 未安装")
            log_info("fastapi未安装")

        return mo.md("\n".join(info))
    return (show_info,)


@app.cell
def _(main_title):
    main_title()
    return


@app.cell
def _(aitool_name):
    aitool_name
    return


@app.cell
def _(show_info):
    # 调用 show_info 来显示基本信息
    show_info()
    return


@app.cell
def _(log_error, log_info, mo, subprocess):
    def configure_git_proxy():
        try:
            # 配置 Git 代理
            cmd = 'git config --global url."https://gh-proxy.com/".insteadOf https://'
            subprocess.run(cmd, shell=True, check=True)
            log_info("Git代理配置成功")
            return mo.md("✅ Git代理配置成功：已设置为使用 gh-proxy").callout(
                kind="success"
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"Git代理配置失败: {str(e)}"
            log_error(error_msg)
            return mo.md(f"❌ {error_msg}").callout(kind="error")


    # 执行配置
    configure_git_proxy()
    return (configure_git_proxy,)


@app.cell
def _(mo):
    install_system = mo.ui.switch(label="启用系统依赖安装", value=False)
    install_system
    return (install_system,)


@app.cell
def _(install_system, log_error, log_info, mo, subprocess):
    def install_system_dependencies():
        if not install_system.value:
            return mo.md("⚠️ 请先启用系统依赖安装开关").callout(kind="warn")

        dependencies = [
            "apt-get install sudo -y",
            "echo 'Set disable_coredump false' >> /etc/sudo.conf",
            "apt-get update",
            "apt install build-essential -y",
            "apt install libgl1 -y",
            "apt-get install libtcmalloc-minimal4 -y",
            "apt install ffmpeg -y",
            "apt-get install bc -y",
            "apt update",
            "apt upgrade -y",
        ]

        results = []
        success_count = 0

        for cmd in dependencies:
            try:
                log_info(f"执行命令: {cmd}")
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                success_count += 1
                results.append(f"✅ {cmd}")
                log_info(f"命令执行成功: {cmd}")
            except subprocess.CalledProcessError as e:
                error_msg = f"命令执行失败: {cmd}\n错误信息: {e.stderr}"
                results.append(f"❌ {cmd}")
                log_error(error_msg)

        # 生成安装报告
        status = "success" if success_count == len(dependencies) else "danger"
        report = [
            f"### 系统依赖安装报告",
            f"总计: {len(dependencies)} 行命令",
            f"成功: {success_count} 个",
            f"失败: {len(dependencies) - success_count} 个",
            "",
            "### 详细信息:",
            *results,
        ]

        return mo.md("\n".join(report)).callout(kind=status)


    # 安装依赖
    install_system_dependencies()
    return (install_system_dependencies,)


@app.cell
def _():
    # 只有上面的cell成功完成，再运行后面的cell
    return


@app.cell
def _(mo):
    uv_venv_setup = mo.ui.switch(label="虚拟环境的设置及启动", value=False)
    uv_venv_setup
    return (uv_venv_setup,)


@app.cell
def _(log_error, log_info, mo, subprocess, uv_venv_setup):
    def install_venv():
        if not uv_venv_setup.value:
            return mo.md("⚠️ 请先启用虚拟环境设置开关").callout(kind="warn")

        dependencies = [
            "source /workspace/.venv/bin/activate",
            "mkdir /workspace/webui-forge",
            "cd /workspace/webui-forge",
            "uv venv --prompt webui-forge -p 3.10",
            "source /workspace/{aitool_name.value}/.venv/bin/activate",
        ]

        results = []
        success_count = 0

        for cmd in dependencies:
            try:
                log_info(f"执行命令: {cmd}")
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                success_count += 1
                results.append(f"✅ {cmd}")
                log_info(f"命令执行成功: {cmd}")
            except subprocess.CalledProcessError as e:
                error_msg = f"命令执行失败: {cmd}\n错误信息: {e.stderr}"
                results.append(f"❌ {cmd}")
                log_error(error_msg)

        # 生成安装报告
        status = "success" if success_count == len(dependencies) else "danger"
        report = [
            f"### 系统依赖安装报告",
            f"总计: {len(dependencies)} 个依赖",
            f"成功: {success_count} 个",
            f"失败: {len(dependencies) - success_count} 个",
            "",
            "### 详细信息:",
            *results,
        ]

        return mo.md("\n".join(report)).callout(kind=status)


    # 安装依赖
    install_venv()
    return (install_venv,)


@app.cell
def _(mo):
    install_app = mo.ui.switch(label="启用程序安装", value=False)
    install_app
    return (install_app,)


@app.cell
def _(install_app, log_error, log_info, mo, subprocess):
    def install_step():
        if not install_app.value:
            return mo.md("⚠️ 请先启用程序安装开关").callout(kind="warn")

        dependencies = [
            "pip install torch torchvision torchaudio -i http://mirrors.cloud.tencent.com/pypi/simple",
        ]

        results = []
        success_count = 0

        for cmd in dependencies:
            try:
                log_info(f"执行命令: {cmd}")
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                success_count += 1
                results.append(f"✅ {cmd}")
                log_info(f"命令执行成功: {cmd}")
            except subprocess.CalledProcessError as e:
                error_msg = f"命令执行失败: {cmd}\n错误信息: {e.stderr}"
                results.append(f"❌ {cmd}")
                log_error(error_msg)

        # 生成安装报告
        status = "success" if success_count == len(dependencies) else "danger"
        report = [
            f"### 系统依赖安装报告",
            f"总计: {len(dependencies)} 个依赖",
            f"成功: {success_count} 个",
            f"失败: {len(dependencies) - success_count} 个",
            "",
            "### 详细信息:",
            *results,
        ]

        return mo.md("\n".join(report)).callout(kind=status)


    # 安装依赖
    install_step()
    return (install_step,)


@app.cell
def _(mo):
    def all_done():
        return mo.md(f"✅ 安装完成").callout(kind="success")


    all_done()
    return (all_done,)


if __name__ == "__main__":
    app.run()
