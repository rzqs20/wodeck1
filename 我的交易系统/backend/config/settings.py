"""
应用配置模块
负责加载和管理应用各项配置
统一变量名
小纸条没写呢、等后面看看要不要配置多人环境
"""
import os
from datetime import timedelta


def load_settings():
    """
    加载应用配置
    
    Returns:
        dict: 应用配置字典
              - app_name: 应用名称
              - debug: 调试模式开关
              - secret_key: 密钥
              - environment: 运行环境(development/production)
              
    Note:
        - 从环境变量或配置文件加载
        - 支持不同环境的配置切换
        - 敏感信息应从环境变量读取
    """
    # 获取运行环境（默认development）
    environment = os.getenv('APP_ENV', 'development')#本地开发环境
    
    # 基础配置
    config = {
        'app_name': '个人看盘指标系统',
        'environment': environment,
        'debug': os.getenv('DEBUG', 'True').lower() == 'true' if environment == 'development' else False,
        
        # Flask配置
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'JSON_AS_ASCII': False,  # 支持中文JSON
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 最大上传16MB
        
        # JWT配置
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'),
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=24),  # Token过期时间
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),   # 刷新Token过期时间
        
        # 数据库配置（引用database模块）
        # 注意：这里不直接导入，避免循环依赖
        # 实际使用时通过 create_engine_instance() 获取
        
        # 日志配置
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'LOG_DIR': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'),
        
        # 文件上传配置
        'UPLOAD_FOLDER': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads'),
        'ALLOWED_EXTENSIONS': {'csv', 'xlsx', 'xls'},
    }
    
    # 根据环境添加特定配置
    if environment == 'development':
        config.update({
            'SQLALCHEMY_ECHO': True,  # 打印SQL语句
            'TESTING': False,
        })
    elif environment == 'production':
        config.update({
            'SQLALCHEMY_ECHO': False,
            'TESTING': False,
            # 目前用的是适配我本地的、如果以后要多人的话要写入环境变量或配置文件
            # TODO: 生产环境应该从环境变量或配置文件中读取以下敏感信息
            # 为什么写不了：这些是敏感信息，不应该硬编码在代码中
            # 你需要：
            # 1. 创建 .env 文件存放敏感配置
            # 2. 使用 python-dotenv 库加载
            # 3. 或者从云服务的环境变量中获取
            # 'SECRET_KEY': os.getenv('PROD_SECRET_KEY'),
            # 'JWT_SECRET_KEY': os.getenv('PROD_JWT_SECRET_KEY'),
        })
    elif environment == 'testing':
        config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # 测试用内存数据库
        })
    
    return config


def get_api_config():
    """
    获取API配置
    
    Returns:
        dict: API配置字典
              - base_url: API基础URL
              - version: API版本
              - rate_limit: 速率限制配置
              - cors_origins: CORS允许的源
              - timeout: 请求超时时间
              
    Note:
        - 使用国金QMT作为数据源
        - QMT是本地客户端，无需网络API密钥
    """
    return {
        # API基础配置
        'base_url': '/api',
        'version': 'v1',
        
        # CORS配置（跨域资源共享）
        # 前端开发时可能需要跨域访问
        'cors_origins': os.getenv('CORS_ORIGINS', '*').split(','),
        # 生产环境建议改为具体域名，如：['http://localhost:3000']
        
        # 速率限制配置
        'rate_limit': {
            'default': {
                'limit': 100,      # 默认每小时100次请求
                'period': 3600,    # 时间窗口（秒）
            },
            'auth': {
                'limit': 10,       # 认证接口更严格（防暴力破解）
                'period': 3600,    # 每小时10次登录尝试
            },
            'data': {
                'limit': 200,      # 数据查询较宽松
                'period': 3600,    # 每小时200次
            },
        },
        
        # 请求超时配置
        'timeout': {
            'connect': 5,    # 连接超时（秒）
            'read': 30,      # 读取超时（秒）
            'write': 30,     # 写入超时（秒）
        },
        
        # 分页配置
        'pagination': {
            'default_page_size': 20,   # 默认每页20条
            'max_page_size': 100,      # 最多每页100条
        },
        
        # 国金QMT配置
        'qmt': {
            # TODO: QMT客户端配置需要根据你的实际安装情况填写
            # 
            # 为什么需要配置：
            # 1. QMT是桌面客户端，需要通过xtquant库调用
            # 2. 需要指定QMT的安装路径和用户账号
            # 3. QMT必须在运行状态才能获取数据
            #
            # 你需要做的：
            # 1. 安装国金QMT客户端
            # 2. 登录你的交易账号
            # 3. 在QMT中开启Python接口权限
            # 4. 安装xtquant库：pip install xtquant
            # 5. 填写下面的配置
            
            'enabled': True,
            
            # QMT安装路径（示例，需要根据实际情况修改）
            # Windows常见路径：
            # - C:\\国金证券QMT\\
            # - D:\\QMT\\
            # - 或者你自定义的路径
            'install_path': os.getenv('QMT_INSTALL_PATH', 'D:\\国金证券QMT交易端\\'),
            
            # QMT登录的账号（用于区分不同用户的数据）
            'account_id': os.getenv('QMT_ACCOUNT_ID', ''),#暂时没写交易账户、后面要写交易功能时再加
            
            # xtquant会话ID（可选，xtquant会自动管理）
            'session_id': None,
            
            # 数据缓存策略
            'cache_strategy': {
                'use_local_cache': True,        # 是否使用本地缓存
                'cache_dir': os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'data',
                    'qmt_cache'
                ),
                'cache_ttl': 300,  # 缓存5分钟（QMT实时数据更新较快）
            },
            
            # 支持的数据类型
            'supported_data_types': [
                'tick',           # 分时数据
                '1m',             # 1分钟K线
                '5m',             # 5分钟K线
                '15m',            # 15分钟K线
                '30m',            # 30分钟K线
                '1h',             # 1小时K线
                '1d',             # 日线
                '1w',             # 周线
                '1mon',           # 月线
            ],
            
            # 批量获取配置
            'batch_fetch': {
                'max_stocks_per_batch': 100,  # 每次最多获取100只股票
                'retry_times': 3,              # 失败重试次数
                'retry_delay': 1,              # 重试间隔（秒）
            },
        },
        
        # API文档配置（如果使用Swagger/Redoc）
        'docs': {
            'enabled': False,  # 个人项目可能不需要
            'swagger_url': '/api/docs',
            'redoc_url': '/api/redoc',
        },
    }


def get_indicator_config():
    """
    获取指标配置
    
    Returns:
        dict: 指标配置字典
              - cache_ttl: 指标缓存过期时间(秒)
              - max_calculation_time: 最大计算时间(秒)
              - supported_indicators: 支持的指标列表
              - default_parameters: 默认参数配置
              - batch_size: 批量计算大小
              
    Note:
        - 配置指标计算的默认参数
        - 设置性能优化相关参数
    """
    return {
        # 缓存配置
        'cache_ttl': {
            'indicator_result': 3600,      # 指标计算结果缓存1小时
            'stock_data': 86400,           # 股票数据缓存24小时（当日数据不变）
            'indicator_definition': 86400, # 指标定义缓存24小时
        },
        
        # 性能限制
        'max_calculation_time': 30,   # 单个指标最大计算时间（秒）
        'max_history_days': 365 * 5,  # 最多获取5年历史数据
        'batch_size': 50,             # 批量计算时每批处理的股票数量
        
        # 支持的指标列表
        'supported_indicators': {
            # 内置技术指标
            'technical': [
                'MA',     # 移动平均线
                'EMA',    # 指数移动平均线
                'MACD',   # 平滑异同移动平均线
                'RSI',    # 相对强弱指标
                'BOLL',   # 布林带
                'KDJ',    # 随机指标
                # TODO: 可以继续添加更多指标
                # 扩展方法：
                # 1. 在 indicators/technical_indicators.py 中实现新指标类
                # 2. 在这里添加指标名称
                # 3. 在 indicator_registry 中注册
            ],
            
            # 自定义指标（用户定义的公式）
            'custom': [],  # 动态添加，初始为空
        },
        
        # 指标默认参数
        'default_parameters': {
            'MA': {
                'period': 20,  # 默认20日均线
                'valid_periods': [5, 10, 20, 30, 60, 120, 250],  # 常用周期
            },
            'EMA': {
                'period': 12,
                'valid_periods': [5, 12, 26, 50],
            },
            'MACD': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9,
            },
            'RSI': {
                'period': 14,
                'valid_periods': [6, 12, 14, 24],
            },
            'BOLL': {
                'period': 20,
                'std_dev': 2,  # 标准差倍数
            },
            'KDJ': {
                'n': 9,
                'm1': 3,
                'm2': 3,
            },
            # TODO: 如果添加了新指标，需要在这里添加默认参数
        },
        
        # 计算精度配置
        'precision': {
            'price': 2,      # 价格保留2位小数
            'volume': 0,     # 成交量整数
            'indicator': 4,  # 指标值保留4位小数
            'percentage': 2, # 百分比保留2位小数
        },
        
        # 预警配置
        'alert': {
            'check_interval': 60,         # 预警检查间隔（秒）
            'max_alerts_per_user': 50,    # 每个用户最多预警规则数
            'notification_methods': ['email'],  # 通知方式
            # TODO: 可以扩展更多通知方式
            # - sms: 短信通知（需要接入短信服务）
            # - wechat: 微信推送（需要微信公众号/企业微信）
            # - dingtalk: 钉钉机器人
            # 为什么暂时不实现：这些需要额外的第三方服务集成
            # 后续如需扩展：
            # 1. 选择需要的通知方式
            # 2. 注册相应服务
            # 3. 配置API密钥
            # 4. 在 alert_service.py 中实现发送逻辑
        },
        
        # 数据更新配置
        'data_update': {
            'schedule': '15:30',   # 每天收盘后更新（A股15:00收盘，留30分钟缓冲）
            'auto_update': True,   # 是否自动更新
            'update_timeout': 300, # 更新超时时间（秒）
        },
    }
def get_cache_config():
    """
    获取缓存配置
    
    Returns:
        dict: 缓存配置字典
              - type: 缓存类型 (memory/redis)
              - redis: Redis配置（如果使用Redis）
              
    Note:
        - 开发环境使用内存缓存
        - 生产环境建议使用Redis
        - 个人项目用内存缓存即可
    """
    cache_type = os.getenv('CACHE_TYPE', 'memory')
    
    config = {
        'type': cache_type,
    }
    
    if cache_type == 'redis':
        # TODO: Redis配置需要根据实际情况填写
        # 为什么暂时不用Redis：
        # 1. 个人项目数据量不大，内存缓存足够
        # 2. Redis需要额外安装和配置
        # 3. 增加系统复杂度
        # 
        # 如果将来需要使用Redis：
        # 1. 安装Redis服务器
        # 2. 修改 CACHE_TYPE=redis
        # 3. 填写下面的配置
        config['redis'] = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0)),
            'password': os.getenv('REDIS_PASSWORD', None),  # 如果有密码
            'decode_responses': True,
        }
    
    return config

def get_scheduler_config():
    """
    获取定时任务配置
    
    Returns:
        dict: 定时任务配置字典
              - timezone: 时区
              - jobs: 定时任务列表
              
    Note:
        - 用于APScheduler定时任务调度器
        - 配置股票数据更新、预警检查等定时任务
    """
    return {
        # 时区配置
        'timezone': 'Asia/Shanghai',  # 中国时区
        
        # 定时任务列表
        'jobs': [
            {
                'id': 'update_stock_data',
                'name': '更新股票数据',
                'func': 'app:schedule_stock_data_update',
                'trigger': 'cron',
                'hour': 15,
                'minute': 30,
                'day_of_week': 'mon-fri',  # 工作日执行
                'misfire_grace_time': 300,  # 错过执行时间的容忍度（秒）
            },
            {
                'id': 'check_alerts',
                'name': '检查预警条件',
                'func': 'app:schedule_alert_check',
                'trigger': 'interval',
                'minutes': 1,  # 每分钟检查一次
                'misfire_grace_time': 60,
            },
            {
                'id': 'cleanup_cache',
                'name': '清理过期缓存',
                'func': 'app:schedule_cache_cleanup',
                'trigger': 'interval',
                'hours': 1,  # 每小时清理一次
                'misfire_grace_time': 300,
            },
        ],
        
        # 线程池配置
        'thread_pool': {
            'max_workers': 10,  # 最大工作线程数
        },
        
        # 进程池配置（如果需要）
        'process_pool': {
            'max_workers': 2,   # 最大工作进程数
        },
    }

def validate_settings(settings):
    """
    验证配置的有效性
    检查关键配置名称是否正确
    
    Args:
        settings: 配置字典
        
    Returns:
        bool: 配置是否有效
        
    Raises:
        ValueError: 配置无效时抛出异常
        
    Note:
        - 检查必填配置项是否存在
        - 验证配置值的合法性
        - 在应用启动时调用
    """
    required_keys = ['SECRET_KEY', 'app_name', 'environment']
    
    for key in required_keys:
        if key not in settings:
            raise ValueError(f"缺少必需的配置项: {key}")
    
    # 验证SECRET_KEY强度（生产环境）
    if settings['environment'] == 'production':
        secret_key = settings.get('SECRET_KEY', '')
        if len(secret_key) < 32:
            raise ValueError("生产环境的SECRET_KEY长度至少为32位")
        
        # 检查是否使用了默认密钥
        if secret_key == 'dev-secret-key-change-in-production':
            raise ValueError("生产环境必须修改SECRET_KEY，不能使用默认值")
    
    # 验证QMT配置
    api_config = get_api_config()
    if api_config['qmt']['enabled']:
        qmt_path = api_config['qmt']['install_path']
        if not os.path.exists(qmt_path):
            # 只是警告，不阻止启动
            print(f"警告: QMT安装路径不存在: {qmt_path}")
            print(f"请检查 QMT_INSTALL_PATH 环境变量或修改配置")
    
    return True

def print_config_summary():
    """
    打印配置摘要（用于调试）
    
    Note:
        - 显示当前生效的主要配置
        - 不包含敏感信息（如密钥）
        - 在应用启动时调用，方便确认配置
    """
    settings = load_settings()
    api_config = get_api_config()
    indicator_config = get_indicator_config()
    
    print("=" * 60)
    print("应用配置摘要")
    print("=" * 60)
    print(f"应用名称: {settings['app_name']}")
    print(f"运行环境: {settings['environment']}")
    print(f"调试模式: {settings['debug']}")
    print(f"数据库类型: SQLite")
    print(f"数据源: 国金QMT")
    print(f"QMT路径: {api_config['qmt']['install_path']}")
    print(f"支持指标: {', '.join(indicator_config['supported_indicators']['technical'])}")
    print(f"缓存类型: {get_cache_config()['type']}")
    print("=" * 60)