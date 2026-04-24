"""
数据库配置模块
负责数据库连接配置和引擎管理
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def get_database_config():
    """
    函数1:

    获取数据库配置信息
    
    
    Returns:
        dict: 包含数据库连接信息的字典

              - driver: 数据库驱动类型 (sqlite/mysql/postgresql)

              - database: 数据库文件路径或名称

              - echo: 是否打印SQL语句(调试用)

    Note:
        - 使用SQLite无需配置用户名密码
        - 数据库文件自动创建在 data/ 目录下
        - 生产环境可从环境变量读取配置
    """
    # 获取项目根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建data目录（如果不存在）
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 数据库文件路径
    db_path = os.path.join(data_dir, 'stock_data.db')
    
    return {
        'driver': 'sqlite',
        'database': db_path,
        'echo': False,  # 生产环境设为False，调试时设为True
    }


def create_engine_instance():
    """
    函数2:

    创建数据库引擎实例
    
    Returns:
        Engine: SQLAlchemy数据库引擎对象
        
    Note:
        - 从get_database_config()获取配置
        - 设置连接池参数（pool_size, max_overflow等）
        - 启用SQL日志记录（开发环境）
        - SQLite需要特殊配置以支持多线程
    """
    config = get_database_config()
    
    if config['driver'] == 'sqlite':
        # SQLite配置
        engine = create_engine(
            f"sqlite:///{config['database']}",
            echo=config['echo'],
            connect_args={
                'check_same_thread': False  # 允许多线程访问
            },
            pool_pre_ping=True,  # 使用前检查连接有效性
            pool_recycle=3600,   # 连接回收时间（秒）
        )
        
        # 优化SQLite性能
        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL;"))  # WAL模式提升并发
            conn.execute(text("PRAGMA synchronous=NORMAL;"))  # 平衡性能和安全性
            conn.execute(text("PRAGMA cache_size=-64000;"))  # 64MB缓存
            conn.execute(text("PRAGMA temp_store=MEMORY;"))  # 临时表存内存
            
    elif config['driver'] == 'mysql':
        # MySQL配置示例（未来扩展用）
        engine = create_engine(
            f"mysql+pymysql://{config.get('username', 'root')}:"
            f"{config.get('password', '')}@"
            f"{config.get('host', 'localhost')}:"
            f"{config.get('port', 3306)}/"
            f"{config.get('database', 'stock_db')}",
            echo=config['echo'],
            pool_size=10,      # 连接池大小
            max_overflow=20,   # 最大溢出连接数
            pool_recycle=3600,
        )
        
    else:
        raise ValueError(f"不支持的数据库驱动: {config['driver']}")
    
    return engine



def get_session_factory():
    """
    函数3:

    获取会话工厂
    
    Returns:
        sessionmaker: SQLAlchemy会话工厂对象
        
    Note:
        - 会话工厂用于创建数据库会话
        - 每次数据库操作都应该使用独立的会话
        - 使用完毕后必须关闭会话
        - 建议在视图函数中使用上下文管理器
    """
    engine = create_engine_instance()
    
    # 创建会话工厂
    SessionFactory = sessionmaker(
        bind=engine,
        autocommit=False,    # 不自动提交
        autoflush=False,     # 不自动刷新
        expire_on_commit=False  # 提交后不过期对象
    )
    
    return SessionFactory


# 创建全局会话工厂实例（可选，方便快速使用）
# 注意：在生产环境中建议使用依赖注入方式传递
SessionLocal = get_session_factory()

def get_db_session():
    """
    函数4:
    
    获取数据库会话（生成器函数，用于依赖注入）
    
    Yields:
        Session: 数据库会话对象
        
    Usage:
        # 在FastAPI中作为依赖
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db_session)):
            return db.query(Item).all()
            
        # 在Flask中手动使用
        db = next(get_db_session())
        try:
            # 执行数据库操作
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()
            
    Note:
        - 使用生成器确保会话正确关闭
        - 异常时自动回滚
        - 推荐使用此方式而非直接使用SessionLocal
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# 导入text函数（用于执行原生SQL）
from sqlalchemy import text
