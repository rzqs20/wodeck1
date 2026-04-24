"""
预警路由模块
注册预警规则相关的URL路由
"""
from flask import Blueprint
from controllers.alert_controller import (
    create_alert, get_alerts, update_alert,
    delete_alert, test_alert
)

alert_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')


def register_alert_routes(app):
    """
    注册预警相关路由
    
    Args:
        app: Flask应用实例
        
    Routes:
        POST /api/alerts - 创建预警规则
        GET /api/alerts - 获取所有预警规则
        PUT /api/alerts/<id> - 更新预警规则
        DELETE /api/alerts/<id> - 删除预警规则
        POST /api/alerts/<id>/test - 测试预警规则
        
    Note:
        - 所有路由都需要认证
    """
    alert_bp.add_url_rule('', view_func=create_alert, methods=['POST'])
    alert_bp.add_url_rule('', view_func=get_alerts, methods=['GET'])
    alert_bp.add_url_rule('/<int:alert_id>', view_func=update_alert, methods=['PUT'])
    alert_bp.add_url_rule('/<int:alert_id>', view_func=delete_alert, methods=['DELETE'])
    alert_bp.add_url_rule('/<int:alert_id>/test', view_func=test_alert, methods=['POST'])
    
    app.register_blueprint(alert_bp)
