"""
指标路由模块
注册指标管理相关的URL路由
"""
from flask import Blueprint
from controllers.indicator_controller import (
    create_indicator, get_indicator, list_indicators,
    update_indicator, delete_indicator,
    calculate_indicator, batch_calculate
)

indicator_bp = Blueprint('indicators', __name__, url_prefix='/api/indicators')


def register_indicator_routes(app):
    """
    注册指标相关路由
    
    Args:
        app: Flask应用实例
        
    Routes:
        POST /api/indicators - 创建新指标
        GET /api/indicators - 获取指标列表
        GET /api/indicators/<id> - 获取指标详情
        PUT /api/indicators/<id> - 更新指标
        DELETE /api/indicators/<id> - 删除指标
        POST /api/indicators/calculate - 计算指标值
        POST /api/indicators/batch-calculate - 批量计算指标
        
    Note:
        - 所有路由都需要认证
        - 使用RESTful风格
    """
    indicator_bp.add_url_rule('', view_func=create_indicator, methods=['POST'])
    indicator_bp.add_url_rule('', view_func=list_indicators, methods=['GET'])
    indicator_bp.add_url_rule('/<int:indicator_id>', view_func=get_indicator, methods=['GET'])
    indicator_bp.add_url_rule('/<int:indicator_id>', view_func=update_indicator, methods=['PUT'])
    indicator_bp.add_url_rule('/<int:indicator_id>', view_func=delete_indicator, methods=['DELETE'])
    indicator_bp.add_url_rule('/calculate', view_func=calculate_indicator, methods=['POST'])
    indicator_bp.add_url_rule('/batch-calculate', view_func=batch_calculate, methods=['POST'])
    
    app.register_blueprint(indicator_bp)
