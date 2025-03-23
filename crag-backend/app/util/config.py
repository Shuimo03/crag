import logging
import os
import yaml
from typing import Dict, Any

# 标记日志是否已初始化
_logging_initialized = False

# 记录已加载的配置文件
_loaded_config_files = set()

# 标记配置是否已尝试加载
_config_load_attempted = False

def setup_logging():
    """
    设置日志配置，确保只初始化一次
    """
    global _logging_initialized
    
    # 检查是否已经有处理器，如果有则说明已经初始化过
    root_logger = logging.getLogger()
    if _logging_initialized or root_logger.handlers:
        return
    
    # 设置日志级别
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # 输出到控制台
        ]
    )
    
    _logging_initialized = True
    logging.info("日志系统已初始化")

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

# 配置单例
_config: Dict[str, Any] = {}


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        Dict[str, Any]: 配置字典
    """
    global _config, _loaded_config_files, _config_load_attempted
    
    # 确保日志系统已初始化
    setup_logging()
    
    # 如果已经尝试过加载配置，直接返回当前配置
    if _config_load_attempted:
        return _config
    
    # 标记已尝试加载配置
    _config_load_attempted = True
    
    # 如果配置已经有内容，并且配置文件已经加载过，则直接返回
    if _config and config_path in _loaded_config_files:
        logger.debug(f"配置文件已加载过，跳过: {config_path}")
        return _config

    # 如果已指定配置文件路径
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                file_content = file.read()
                if not file_content.strip():
                    logger.error(f"配置文件为空: {config_path}")
                    return _config
                
                new_config = yaml.safe_load(file_content)
                if not new_config:
                    logger.error(f"配置文件解析结果为空: {config_path}")
                    return _config
                
                # 更新配置
                _config.update(new_config)
                _loaded_config_files.add(config_path)
                
                # 记录配置项
                config_keys = list(_config.keys())
                logger.info(f"成功加载配置文件: {config_path}, 配置项: {config_keys}")
        except Exception as e:
            logger.error(f"无法加载配置文件 {config_path}: {str(e)}")
    else:
        if config_path:
            logger.error(f"配置文件不存在: {config_path}")

    # 如果配置为空，尝试从环境变量加载（只在第一次尝试时记录日志）
    if not _config:
        logger.warning("配置为空，尝试从环境变量加载")
        # 尝试从环境变量加载常用配置
        env_config = {}
        for key in ["GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET", "GITHUB_REDIRECT_URI"]:
            if key in os.environ:
                env_config[key] = os.environ[key]
        
        if env_config:
            logger.info(f"从环境变量加载了 {len(env_config)} 个配置项")
            _config.update(env_config)

    return _config


def get_config() -> Dict[str, Any]:
    """
    获取配置字典

    Returns:
        Dict[str, Any]: 配置字典
    """
    global _config
    
    # 如果配置为空且未尝试加载，尝试从环境变量加载
    if not _config and not _config_load_attempted:
        # 尝试从环境变量加载常用配置
        env_config = {}
        for key in ["GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET", "GITHUB_REDIRECT_URI"]:
            if key in os.environ:
                env_config[key] = os.environ[key]
        
        if env_config:
            _config.update(env_config)
    
    return _config


def get_value(key: str, default=None) -> Any:
    """
    获取配置值

    Args:
        key: 配置键名
        default: 默认值

    Returns:
        Any: 配置值
    """
    # 先从配置中获取
    value = get_config().get(key)
    
    # 如果配置中没有，尝试从环境变量获取
    if value is None:
        value = os.environ.get(key)
    
    # 如果环境变量中也没有，使用默认值
    if value is None:
        value = default
    
    return value