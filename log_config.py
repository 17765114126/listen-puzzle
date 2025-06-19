import logging
import os
from datetime import datetime


# 基础版 - 每次启动生成当天日志文件
def setup_basic_logging():
    # 创建日志目录
    log_dir = "static/loginfo"
    os.makedirs(log_dir, exist_ok=True)

    # 生成带日期的文件名（格式：2024-05-15.log）
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = os.path.join(log_dir, f"{current_date}.log")

    # 配置日志系统
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


# 增强版 - 支持运行时自动按天滚动（推荐）
def setup_advanced_logging():
    from logging.handlers import TimedRotatingFileHandler

    # 创建日志目录
    log_dir = "static/loginfo"
    os.makedirs(log_dir, exist_ok=True)

    # 自定义文件名生成器
    def daily_namer(default_name):
        """将默认文件名转换为按日存储格式"""
        base, ext = os.path.splitext(default_name)
        return f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"

    # 配置按天滚动的Handler
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, "runtime.log"),  # 基础文件名
        when='midnight',  # 每天午夜滚动
        interval=1,  # 每天间隔
        backupCount=30,  # 保留30天日志
        encoding='utf-8'
    )
    file_handler.namer = daily_namer  # 注入自定义命名函数

    # 配置日志系统
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            file_handler,
            logging.StreamHandler()
        ]
    )


def log_run():
    setup_advanced_logging()  # 或 setup_basic_logging()
    logging.info("日志系统已初始化")
