"""
应用主入口
Flask应用工厂和配置
"""
from flask import Flask
from flask_cors import CORS
from config.database import create_engine_instance, get_session_factory
from config.settings import load_settings
from middleware.error_handler import register_error_handlers
from middleware.request_logger import register_logger_middleware
from indicators.indicator_registry import IndicatorRegistry


def create_app(config_name='development'):
    """
    创建Flask应用实例（应用工厂模式）
    
    Args:
        config_name: 配置名称 ('development' | 'production' | 'testing')
        
    Returns:
        Flask: 配置好的Flask应用实例
        
    Note:
        - 使用工厂模式便于测试和多环境部署
        - 按顺序初始化各个组件
    """
    app = Flask(__name__)
    
    # 加载配置
    settings = load_settings()
    app.config.from_object(settings)
    
    # 注册扩展
    register_extensions(app)
    
    # 注册蓝图（路由）
    register_blueprints(app)
    
    # 注册中间件
    register_middlewares(app)
    
    # 配置CORS
    configure_cors(app)
    
    # 设置定时任务
    setup_scheduler(app)
    
    # 初始化指标注册中心
    IndicatorRegistry.initialize_default_indicators()
    
    return app


def register_blueprints(app):
    """
    注册所有蓝图
    
    Args:
        app: Flask应用实例
        
    Note:
        - 注册认证、指标、股票、自选股、预警等模块的路由
        - 从routes包导入注册函数
    """
    from routes.auth_routes import register_auth_routes
    from routes.indicator_routes import register_indicator_routes
    from routes.stock_routes import register_stock_routes
    from routes.watchlist_routes import register_watchlist_routes
    from routes.alert_routes import register_alert_routes
    
    register_auth_routes(app)
    register_indicator_routes(app)
    register_stock_routes(app)
    register_watchlist_routes(app)
    register_alert_routes(app)


def register_extensions(app):
    """
    注册扩展（数据库、缓存等）
    
    Args:
        app: Flask应用实例
        
    Note:
        - 初始化数据库引擎
        - 初始化缓存客户端
        - 其他第三方扩展
    """
    # 数据库
    engine = create_engine_instance()
    session_factory = get_session_factory()
    
    # 将数据库对象附加到app
    app.extensions['db_engine'] = engine
    app.extensions['session_factory'] = session_factory
    
    # 缓存
    from utils.cache import init_cache
    cache_config = {
        'type': 'redis',
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }
    init_cache(cache_config)


def register_middlewares(app):
    """
    注册中间件
    
    Args:
        app: Flask应用实例
        
    Note:
        - 注册错误处理器
        - 注册日志中间件
        - 其他自定义中间件
    """
    register_error_handlers(app)
    register_logger_middleware(app)


def configure_cors(app):
    """
    配置CORS（跨域资源共享）
    
    Args:
        app: Flask应用实例
        
    Note:
        - 允许前端跨域访问
        - 配置允许的源、方法、头信息
    """
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],  # 前端地址
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })


def setup_scheduler(app):
    """
    设置定时任务调度器
    
    Args:
        app: Flask应用实例
        
    Note:
        - 使用APScheduler或Celery
        - 注册定时任务：
          * 定时更新股票数据
          * 定时检查预警条件
          * 定时清理过期缓存
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # 定时更新股票数据（每个交易日15:30）
    scheduler.add_job(
        func=schedule_stock_data_update,
        trigger='cron',
        hour=15,
        minute=30,
        day_of_week='mon-fri',
        id='update_stock_data'
    )
    
    # 定时检查预警（每5分钟）
    scheduler.add_job(
        func=schedule_alert_check,
        trigger='interval',
        minutes=5,
        id='check_alerts'
    )
    
    # 定时清理缓存（每天凌晨2点）
    scheduler.add_job(
        func=schedule_cache_cleanup,
        trigger='cron',
        hour=2,
        minute=0,
        id='cleanup_cache'
    )
    
    scheduler.start()
    app.extensions['scheduler'] = scheduler


def schedule_stock_data_update():
    """
    定时更新股票数据
    
    Note:
        - 获取所有用户的自选股
        - 批量更新最新行情数据
        - 在后台线程中执行
    """
    pass


def schedule_alert_check():
    """
    定时检查预警条件
    
    Note:
        - 调用alert_service.check_alerts()
        - 发送触发的预警通知
        - 在后台线程中执行
    """
    pass


def schedule_cache_cleanup():
    """
    定时清理过期缓存
    
    Note:
        - 清理过期的缓存键
        - 释放内存/Redis空间
        - 在后台线程中执行
    """
    pass


def run_development():
    """
    运行开发环境
    
    Note:
        - 启用调试模式
        - 自动重载代码
        - 显示详细错误信息
    """
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)


def run_production():
    """
    运行生产环境
    
    Note:
        - 使用Gunicorn WSGI服务器
        - 禁用调试模式
        - 多worker进程
        - 命令行: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    """
    app = create_app('production')
    return app


if __name__ == '__main__':
    run_development()
