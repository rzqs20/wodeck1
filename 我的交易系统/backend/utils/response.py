"""
响应工具模块
统一API响应格式
"""
from flask import jsonify


def success_response(data=None, message="操作成功", status_code=200):
    """
    成功响应格式化
    
    Args:
        data: 响应数据（可选）
        message: 成功消息
        status_code: HTTP状态码
        
    Returns:
        Response: JSON响应
                  {
                      "success": true,
                      "message": "操作成功",
                      "data": {...}
                  }
                  
    Note:
        - 统一成功响应格式
        - 支持自定义消息和数据
    """
    pass


def error_response(message="操作失败", status_code=400, errors=None):
    """
    错误响应格式化
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        errors: 详细错误信息列表（可选）
        
    Returns:
        Response: JSON响应
                  {
                      "success": false,
                      "message": "操作失败",
                      "errors": [...]
                  }
                  
    Note:
        - 统一错误响应格式
        - 支持详细的错误信息
    """
    pass


def pagination_response(data, total, page=1, per_page=20):
    """
    分页响应格式化
    
    Args:
        data: 当前页数据列表
        total: 总记录数
        page: 当前页码
        per_page: 每页数量
        
    Returns:
        Response: JSON响应
                  {
                      "success": true,
                      "data": [...],
                      "pagination": {
                          "total": 总数,
                          "page": 当前页,
                          "per_page": 每页数量,
                          "total_pages": 总页数,
                          "has_next": 是否有下一页,
                          "has_prev": 是否有上一页
                      }
                  }
                  
    Note:
        - 计算总页数
        - 判断是否有上下页
    """
    pass
