"""
指标基类模块
定义所有技术指标的抽象基类
"""
from abc import ABC, abstractmethod


class BaseIndicator(ABC):
    """
    指标基类（抽象类）
    
    所有具体指标类必须继承此类并实现calculate方法
    
    Attributes:
        name: 指标名称
        description: 指标描述
        
    Methods:
        calculate(): 计算指标值（抽象方法，子类必须实现）
        validate_parameters(): 验证参数合法性
        get_name(): 获取指标名称
        get_description(): 获取指标描述
    """
    
    def __init__(self, name, description=""):
        """
        初始化指标对象
        
        Args:
            name: 指标名称
            description: 指标描述（可选）
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def calculate(self, data, parameters):
        """
        计算指标值（抽象方法，子类必须实现）
        
        Args:
            data: 股票数据列表，每个元素包含OHLCV数据
            parameters: 指标参数字典
            
        Returns:
            list: 计算结果列表，每个元素包含日期和指标值
            
        Raises:
            NotImplementedError: 子类未实现此方法时抛出
            
        Note:
            - 这是核心计算方法
            - 处理数据不足的情况
            - 返回标准化格式的结果
        """
        pass
    
    def validate_parameters(self, parameters):
        """
        验证参数合法性
        
        Args:
            parameters: 待验证的参数字典
            
        Returns:
            bool: 参数是否合法
            
        Raises:
            ValueError: 参数不合法时抛出异常
            
        Note:
            - 检查必需参数是否存在
            - 验证参数类型和范围
            - 子类可以重写此方法实现自定义验证
        """
        pass
    
    def get_name(self):
        """
        获取指标名称
        
        Returns:
            str: 指标名称
        """
        return self.name
    
    def get_description(self):
        """
        获取指标描述
        
        Returns:
            str: 指标描述
        """
        return self.description
