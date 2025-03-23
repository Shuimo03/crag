"""
服务提供者模块，用于集中管理所有服务的初始化和获取
"""
from typing import Dict, Any, Type, TypeVar

# 服务类型变量
T = TypeVar('T')

class ServiceProvider:
    """
    服务提供者类，用于管理应用中的服务实例
    """
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, service_class: Type[T]) -> None:
        """
        注册服务类
        
        Args:
            service_class: 要注册的服务类
        """
        service_name = service_class.__name__
        if service_name not in cls._instances:
            cls._instances[service_name] = service_class()
    
    @classmethod
    def register_instance(cls, service_class: Type[T], instance: T) -> None:
        """
        注册服务实例
        
        Args:
            service_class: 服务类
            instance: 服务实例
        """
        service_name = service_class.__name__
        cls._instances[service_name] = instance
    
    @classmethod
    def get(cls, service_class: Type[T]) -> T:
        """
        获取服务实例
        
        Args:
            service_class: 服务类
            
        Returns:
            服务实例
        """
        service_name = service_class.__name__
        if service_name not in cls._instances:
            cls.register(service_class)
        
        return cls._instances[service_name]

# 创建全局服务提供者实例
service_provider = ServiceProvider() 