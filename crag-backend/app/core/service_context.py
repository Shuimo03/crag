"""
服务上下文管理器，用于管理服务的生命周期
"""
from typing import Dict, Any, Type, TypeVar, Optional
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

# 服务类型变量
T = TypeVar('T')

class ServiceContext:
    """
    服务上下文管理器，用于管理服务的生命周期
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化服务上下文
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.services: Dict[str, Any] = {}
        logger.info(f"服务上下文已初始化，配置项数量: {len(self.config)}")
    
    def register(self, service_class: Type[T], *args, **kwargs) -> T:
        """
        注册服务类并创建实例
        
        Args:
            service_class: 要注册的服务类
            *args: 传递给服务构造函数的位置参数
            **kwargs: 传递给服务构造函数的关键字参数
            
        Returns:
            服务实例
        """
        service_name = service_class.__name__
        if service_name not in self.services:
            # 如果 kwargs 中没有 config_dict，则添加
            if 'config_dict' not in kwargs and hasattr(service_class, '__init__') and 'config_dict' in service_class.__init__.__code__.co_varnames:
                kwargs['config_dict'] = self.config
            
            # 创建服务实例
            self.services[service_name] = service_class(*args, **kwargs)
            logger.info(f"服务已注册: {service_name}")
        
        return self.services[service_name]
    
    def register_instance(self, service_class: Type[T], instance: T) -> T:
        """
        注册服务实例
        
        Args:
            service_class: 服务类
            instance: 服务实例
            
        Returns:
            服务实例
        """
        service_name = service_class.__name__
        self.services[service_name] = instance
        logger.info(f"服务实例已注册: {service_name}")
        return instance
    
    def get(self, service_class: Type[T]) -> T:
        """
        获取服务实例
        
        Args:
            service_class: 服务类
            
        Returns:
            服务实例
        """
        service_name = service_class.__name__
        if service_name not in self.services:
            return self.register(service_class)
        
        return self.services[service_name]
    
    def __enter__(self):
        """
        进入上下文
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文，清理资源
        """
        for service_name, service in self.services.items():
            # 如果服务有 close 方法，则调用
            if hasattr(service, 'close') and callable(service.close):
                try:
                    service.close()
                    logger.info(f"服务已关闭: {service_name}")
                except Exception as e:
                    logger.error(f"关闭服务 {service_name} 时出错: {str(e)}")
        
        # 清空服务字典
        self.services.clear()
        logger.info("所有服务已清理")

# 创建全局服务上下文
service_context = None 