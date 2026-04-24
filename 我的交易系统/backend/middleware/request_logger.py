"""
请求日志中间件模块
记录API请求和响应日志
"""
import time
from flask import request, g
from utils.logger import get_logger

logger = get_logger('request_logger')


def log_request(request):
    """
    记录请求日志
    
    Args:
        request: Flask请求对象
        
    Note:
        - 在请求开始时调用
        - 记录请求方法、URL、IP、用户ID等
        - 记录请求时间戳用于计算耗时
    """
    pass


def log_response(response, duration):
    """
    记录响应日志
    
    Args:
        response: Flask响应对象
        duration: 请求处理耗时（秒）
        
    Note:
        - 在响应返回前调用
        - 记录响应状态码、耗时
        - 记录慢请求（如>1秒）
    """
    pass


def register_logger_middleware(app):
    """
    注册日志中间件
    
    Args:
        app: Flask应用实例
        
    Note:
        - 使用app.before_request注册log_request
        - 使用app.after_request注册log_response
        - 使用g对象传递请求开始时间
    """
    
    @app.before_request
    def before_request():
        """请求前钩子"""
        pass
    
    @app.after_request
    def after_request(response):
        """请求后钩子"""
        pass
    
    app.before_request(before_request)
    app.after_request(after_request)
