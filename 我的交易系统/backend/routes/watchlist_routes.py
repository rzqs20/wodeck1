"""
自选股路由模块
注册自选股相关的URL路由
"""
from flask import Blueprint
from controllers.watchlist_controller import (
    create_watchlist, get_watchlists, get_watchlist,
    update_watchlist, delete_watchlist,
    add_stock, remove_stock,
    get_watchlist_with_indicators
)

watchlist_bp = Blueprint('watchlists', __name__, url_prefix='/api/watchlists')


def register_watchlist_routes(app):
    """
    注册自选股相关路由
    
    Args:
        app: Flask应用实例
        
    Routes:
        POST /api/watchlists - 创建自选列表
        GET /api/watchlists - 获取所有自选列表
        GET /api/watchlists/<id> - 获取指定自选列表
        PUT /api/watchlists/<id> - 更新自选列表
        DELETE /api/watchlists/<id> - 删除自选列表
        POST /api/watchlists/<id>/stocks - 添加股票
        DELETE /api/watchlists/<id>/stocks/<code> - 移除股票
        GET /api/watchlists/<id>/with-indicators - 获取带指标的自选列表
        
    Note:
        - 所有路由都需要认证
        - RESTful风格设计
    """
    watchlist_bp.add_url_rule('', view_func=create_watchlist, methods=['POST'])
    watchlist_bp.add_url_rule('', view_func=get_watchlists, methods=['GET'])
    watchlist_bp.add_url_rule('/<int:watchlist_id>', view_func=get_watchlist, methods=['GET'])
    watchlist_bp.add_url_rule('/<int:watchlist_id>', view_func=update_watchlist, methods=['PUT'])
    watchlist_bp.add_url_rule('/<int:watchlist_id>', view_func=delete_watchlist, methods=['DELETE'])
    watchlist_bp.add_url_rule('/<int:watchlist_id>/stocks', view_func=add_stock, methods=['POST'])
    watchlist_bp.add_url_rule('/<int:watchlist_id>/stocks/<string:stock_code>', view_func=remove_stock, methods=['DELETE'])
    watchlist_bp.add_url_rule('/<int:watchlist_id>/with-indicators', view_func=get_watchlist_with_indicators, methods=['GET'])
    
    app.register_blueprint(watchlist_bp)
