"""
认证路由模块
注册认证相关的URL路由
"""
from flask import Blueprint
from controllers.auth_controller import (
    register, login, logout,
    get_profile, update_profile, change_password
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def register_auth_routes(app):
    """
    注册认证相关路由
    
    Args:
        app: Flask应用实例
        
    Routes:
        POST /api/auth/register - 用户注册
        POST /api/auth/login - 用户登录
        POST /api/auth/logout - 用户登出
        GET /api/auth/profile - 获取用户资料
        PUT /api/auth/profile - 更新用户资料
        PUT /api/auth/password - 修改密码
        
    Note:
        - 使用Blueprint组织路由
        - 所有路由前缀为/api/auth
        - 部分路由需要认证（由控制器装饰器处理）
    """
    auth_bp.add_url_rule('/register', view_func=register, methods=['POST'])
    auth_bp.add_url_rule('/login', view_func=login, methods=['POST'])
    auth_bp.add_url_rule('/logout', view_func=logout, methods=['POST'])
    auth_bp.add_url_rule('/profile', view_func=get_profile, methods=['GET'])
    auth_bp.add_url_rule('/profile', view_func=update_profile, methods=['PUT'])
    auth_bp.add_url_rule('/password', view_func=change_password, methods=['PUT'])
    
    app.register_blueprint(auth_bp)
