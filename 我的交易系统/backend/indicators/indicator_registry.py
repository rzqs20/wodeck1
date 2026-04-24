"""
指标注册中心模块
统一管理所有可用指标的注册和获取
"""


class IndicatorRegistry:
    """
    指标注册中心
    
    单例模式，全局管理所有技术指标的注册和查询
    
    Methods:
        register(): 注册指标类
        get_indicator(): 获取指标实例
        get_all_indicators(): 获取所有可用指标
        unregister(): 注销指标
    """
    
    _instance = None
    _indicators = {}
    
    def __new__(cls):
        """
        单例模式实现
        
        Returns:
            IndicatorRegistry: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, indicator_class):
        """
        注册指标类
        
        Args:
            indicator_class: 指标类（必须继承BaseIndicator）
            
        Raises:
            TypeError: 不是BaseIndicator子类时抛出异常
            ValueError: 名称重复时抛出异常
            
        Note:
            - 验证indicator_class是BaseIndicator的子类
            - 实例化指标对象获取名称
            - 存储到_indicators字典
            - 自动注册常用技术指标
        """
        pass
    
    def get_indicator(self, name):
        """
        获取指标实例
        
        Args:
            name: 指标名称
            
        Returns:
            BaseIndicator: 指标实例或None（不存在时）
            
        Note:
            - 从_indicators字典查找
            - 返回新实例（避免状态污染）
        """
        pass
    
    def get_all_indicators(self):
        """
        获取所有可用指标
        
        Returns:
            dict: 所有指标信息字典 {name: indicator_info}
                  每个indicator_info包含:
                  - name: 指标名称
                  - description: 描述
                  - parameters: 参数说明
                  
        Note:
            - 遍历_indicators字典
            - 返回元数据而非实例
        """
        pass
    
    def unregister(self, name):
        """
        注销指标
        
        Args:
            name: 指标名称
            
        Returns:
            bool: 注销是否成功
            
        Note:
            - 从_indicators字典移除
            - 谨慎使用，可能影响正在使用的功能
        """
        pass
    
    @classmethod
    def initialize_default_indicators(cls):
        """
        初始化默认技术指标
        
        Note:
            - 注册MA、EMA、MACD、RSI、BOLL、KDJ等常用指标
            - 在应用启动时调用一次
        """
        pass
