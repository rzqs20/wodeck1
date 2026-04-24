"""
股票数据路由模块
注册股票数据相关的URL路由
"""
from flask import Blueprint
from controllers.stock_controller import (
    get_stock_data, search_stocks,
    get_stock_detail, refresh_stock_data
)

stock_bp = Blueprint('stocks', __name__, url_prefix='/api/stocks')


def register_stock_routes(app):
    """
    注册股票数据相关路由
    
    Args:
        app: Flask应用实例
        
    Routes:
        GET /api/stocks/<code> - 获取股票历史数据
        GET /api/stocks/search - 搜索股票
        GET /api/stocks/<code>/detail - 获取股票详情
        POST /api/stocks/<code>/refresh - 刷新股票数据
        
    Note:
        - 所有路由都需要认证
        - <code>为股票代码参数
    """
    stock_bp.add_url_rule('/<string:stock_code>', view_func=get_stock_data, methods=['GET'])
    stock_bp.add_url_rule('/search', view_func=search_stocks, methods=['GET'])
    stock_bp.add_url_rule('/<string:stock_code>/detail', view_func=get_stock_detail, methods=['GET'])
    stock_bp.add_url_rule('/<string:stock_code>/refresh', view_func=refresh_stock_data, methods=['POST'])
    
    app.register_blueprint(stock_bp)
