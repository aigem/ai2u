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
    """UI 组件：工具选择"""
    aitool_name = mo.ui.dropdown(
        ["comfyUI", "openWebUI", "StableDifusion"], 
        value="StableDifusion",
        label="选择AI工具"
    )
    return (aitool_name,)


@app.cell
def _(datetime, logging, os):
    """日志处理类"""
    class Logger:
        def __init__(self, name):
            self.logger = self._setup_logger(name)

        def _setup_logger(self, name):
            os.makedirs("logs", exist_ok=True)
            log_file = f'logs/{name}_{datetime.now().strftime("%Y%m%d")}.log'

            logger = logging.getLogger(name)
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(log_file, encoding="utf-8"),
                    logging.StreamHandler(),
                ],
            )
            return logger

        def info(self, msg): self.logger.info(msg)
        def error(self, msg): self.logger.error(msg)
        def warning(self, msg): self.logger.warning(msg)
    return (Logger,)


@app.cell
def _(mo):
    """UI 组件：功能开关"""
    switches = {
        "system": mo.ui.switch(label="系统依赖安装", value=False),
        "venv": mo.ui.switch(label="虚拟环境设置", value=False),
        "repo": mo.ui.switch(label="程序文件设置", value=False),
        "app": mo.ui.switch(label="启动应用程序", value=False),
        "download": mo.ui.switch(label="文件或模型下载", value=False),
    }
    return (switches,)


@app.cell
def _(Logger, aitool_name):
    """初始化日志记录器"""
    logger = Logger(aitool_name.value)
    return (logger,)


@app.cell
def _(subprocess):
    """命令执行工具类"""
    class CommandRunner:
        @staticmethod
        def run(cmd, logger, check=True):
            try:
                logger.info(f"执行命令: {cmd}")
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=check,
                    text=True,
                )
                logger.info("命令执行成功")
                return True, None
            except subprocess.CalledProcessError as e:
                error_msg = f"命令执行失败: {e.stderr}"
                logger.error(error_msg)
                return False, error_msg
    return (CommandRunner,)


@app.cell
def _(aitool_name):
    """虚拟环境所在文件夹、git REPO"""
    uv_venv_dir = f"ai_{aitool_name.value}"
    git_repo_url = "https://github.com/love9678/stable-diffusion-webui-forge.git"
    repo_name = "stable-diffusion-webui-forge"
    app_log = f"{aitool_name.value}.log"
    return app_log, git_repo_url, repo_name, uv_venv_dir


@app.cell
def _():
    """配置类"""
    class Config:
        SYSTEM_DEPS = [
            "apt-get install sudo -y",
            "echo \"Set disable_coredump false\" >> /etc/sudo.conf",
            "apt-get update",
            "apt install build-essential libgl1 libtcmalloc-minimal4 ffmpeg bc -y",
        ]

        @staticmethod
        def get_venv_commands(venv_dir):
            return [
                f"cd {venv_dir} && uv venv -p 3.10 && . .venv/bin/activate",
                f"cd {venv_dir} && . .venv/bin/activate && uv pip install -U pip setuptools wheel",
                f"cd {venv_dir} && . .venv/bin/activate && uv pip install -U  torch==2.3.1 torchvision torchaudio aria2 -i http://mirrors.cloud.tencent.com/pypi/simple"
            ]

        @staticmethod
        def setup_repo_commands(venv_dir, git_url, repo_name):
            return [
                # 先检查并删除已存在的目录
                f"cd {venv_dir} && rm -rf {repo_name}",
                # 然后克隆仓库
                f"cd {venv_dir} && git clone {git_url} {repo_name}",
            ]

        @staticmethod
        def get_start_command(venv_dir, repo_name, app_log):
            """获取启动命令"""
            return {
                'cmd': f"cd {venv_dir} && . .venv/bin/activate && cd {repo_name} && export HF_ENDPOINT=https://hf-mirror.com && nohup ./webui.sh -f > {app_log} 2>&1 &",
                'check_cmd': "pgrep -f 'python.*launch.py'"
            }

        @staticmethod
        def get_stop_commands():
            """获取停止命令"""
            return {
                'commands': [
                    # 查找并终止 python 进程
                    "pkill -f 'python.*launch.py'",
                    # 查找并终止 webui.sh 进程
                    "pkill -f 'webui.sh'",
                    # 使用 kill 命令终止（如果找到了PID）
                    "for pid in $(pgrep -f 'python.*launch.py'); do kill -9 $pid 2>/dev/null; done",
                ],
                'check_cmd': "pgrep -f 'python.*launch.py'"
            }

        @staticmethod
        def download_commands(venv_dir, repo_name):
            return [
                f"mkdir {venv_dir}/{repo_name}/models/Stable-diffusion/flux",
                f"cd {venv_dir}/{repo_name}/models/Stable-diffusion/flux && aria2c -c -x 16 -s 16 -k 50M https://hf-mirror.com/lllyasviel/flux1-dev-bnb-nf4/resolve/main/flux1-dev-bnb-nf4-v2.safetensors -o flux1-dev-bnb-nf4-v2.safetensors",
            ]
    return (Config,)


@app.cell
def _(aitool_name):
    aitool_name
    return


@app.cell
def _(switches):
    switches
    return


@app.cell
def _(CommandRunner, Config, logger, mo, switches):
    """系统依赖安装"""
    def install_system():
        if not switches["system"].value:
            return mo.md("⚠️ 请先启用系统依赖安装").callout(kind="warn")

        for cmd in Config.SYSTEM_DEPS:
            success, error = CommandRunner.run(cmd, logger)
            if not success:
                return mo.md(f"❌ {error}").callout(kind="danger")

        return mo.md("✅ 系统依赖安装完成").callout(kind="success")

    install_system()
    return (install_system,)


@app.cell
def _(CommandRunner, Config, logger, mo, os, switches, uv_venv_dir):
    """虚拟环境设置"""
    def setup_venv():
        if not switches["venv"].value:
            return mo.md("⚠️ 请先启用虚拟环境设置").callout(kind="warn")

        os.makedirs(uv_venv_dir, exist_ok=True)

        for cmd in Config.get_venv_commands(uv_venv_dir):
            success, error = CommandRunner.run(cmd, logger)
            if not success:
                return mo.md(f"❌ {error}").callout(kind="danger")

        return mo.md("✅ 虚拟环境设置完成").callout(kind="success")

    setup_venv()
    return (setup_venv,)


@app.cell
def _(
    CommandRunner,
    Config,
    git_repo_url,
    logger,
    mo,
    repo_name,
    switches,
    uv_venv_dir,
):
    """程序文件安装设置"""
    def setup_repo():
        if not switches["repo"].value:
            return mo.md("⚠️ 请先启用文件安装设置").callout(kind="warn")

        for cmd in Config.setup_repo_commands(uv_venv_dir,git_repo_url,repo_name):
            success, error = CommandRunner.run(cmd, logger)
            if not success:
                return mo.md(f"❌ {error}").callout(kind="danger")

        return mo.md("✅ 程序文件设置完成").callout(kind="success")

    setup_repo()
    return (setup_repo,)


@app.cell
def _(mo):
    """创建启动和停止按钮"""
    btn = mo.ui.run_button(label="启动服务", kind="info")
    btn1 = mo.ui.run_button(label="停止服务", kind="info")
    return btn, btn1


@app.cell
def _(btn):
    btn
    return


@app.cell
def _(btn1):
    btn1
    return


@app.cell
def _(
    Config,
    app_log,
    btn,
    btn1,
    logger,
    repo_name,
    subprocess,
    switches,
    uv_venv_dir,
):
    """启动/停止应用程序"""
    def handle_app():
        if not switches["app"].value:
            print("⚠️ 请先启用应用程序开关")
            return

        if btn.value:
            # 获取启动配置
            start_config = Config.get_start_command(uv_venv_dir, repo_name, app_log)
            logger.info(f"启动应用程序...")
            try:
                # 执行启动命令
                subprocess.run(start_config['cmd'], shell=True, check=True)
                print("✅ 应用程序已在后台启动")
                print(f"查看日志: tail -f {app_log}")

                # 等待几秒确保程序启动
                import time
                time.sleep(3)

                # 检查进程是否在运行
                result = subprocess.run(
                    start_config['check_cmd'], 
                    shell=True, 
                    text=True, 
                    capture_output=True
                )
                if result.returncode == 0:
                    print(f"进程ID: {result.stdout.strip()}")
                else:
                    print("⚠️ 进程可能未正常启动，请检查日志")

            except subprocess.CalledProcessError as e:
                print(f"❌ 启动失败: {e.stderr if e.stderr else str(e)}")
                logger.error(f"启动失败: {e.stderr if e.stderr else str(e)}")

        elif btn1.value:
            try:
                logger.info("停止应用程序...")
                # 获取停止配置
                stop_config = Config.get_stop_commands()

                # 执行停止命令
                for cmd in stop_config['commands']:
                    subprocess.run(cmd, shell=True, check=False)

                # 验证进程是否已停止
                result = subprocess.run(
                    stop_config['check_cmd'], 
                    shell=True, 
                    capture_output=True
                )
                if result.returncode != 0:
                    print("✅ 应用程序已停止")
                    logger.info("应用程序已停止")
                else:
                    print("⚠️ 进程可能未完全停止，请手动检查")
                    logger.warning("进程可能未完全停止")

            except Exception as e:
                print(f"❌ 停止失败: {str(e)}")
                logger.error(f"停止失败: {str(e)}")

    handle_app()
    return (handle_app,)


@app.cell
def _(CommandRunner, Config, logger, mo, repo_name, switches, uv_venv_dir):
    """下载：文件或模型"""
    def download_files():
        if not switches["download"].value:
            return mo.md("⚠️ 请先启用下载开关").callout(kind="warn")

        # 获取下载命令列表
        commands = Config.download_commands(uv_venv_dir, repo_name)
        for cmd in commands:
            success, error = CommandRunner.run(cmd, logger)
            if not success:
                return mo.md(f"❌ {error}").callout(kind="danger")

        return mo.md("✅ 相关下载已经完成").callout(kind="success")

    download_files()
    return (download_files,)


if __name__ == "__main__":
    app.run()
