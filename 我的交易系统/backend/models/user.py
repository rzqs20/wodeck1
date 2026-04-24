"""
用户模型
定义用户数据结构和相关方法

Note:
    - 单用户系统，只需要一个默认用户
    - 简化设计，不包含复杂的权限管理
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class User(Base):
    """
    用户模型类
    
    Attributes:
        id: 用户唯一标识
        username: 用户名
        email: 邮箱地址
        password_hash: 密码哈希值
        created_at: 创建时间
        updated_at: 更新时间
        
    Methods:
        set_password(): 设置密码（加密）
        verify_password(): 验证密码
        to_dict(): 转换为字典格式
    """
    
    # 表名
    __tablename__ = 'users'
    
    # 字段定义
    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户唯一标识')
    username = Column(String(50), nullable=False, unique=True, index=True, comment='用户名')
    email = Column(String(100), nullable=True, comment='邮箱地址')
    password_hash = Column(String(255), nullable=False, comment='密码哈希值')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __init__(self, username, email=None, password=None):
        """
        初始化用户对象
        
        Args:
            username: 用户名
            email: 邮箱地址（可选）
            password: 原始密码（可选）
        """
        if not username or not username.strip():
            raise ValueError("用户名不能为空")
        
        self.username = username.strip()
        self.email = email
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 如果提供了密码，则设置密码哈希
        if password:
            self.set_password(password)
        else:
            self.password_hash = ''
    
    def set_password(self, password):
        """
        设置密码（进行哈希加密）
        
        Args:
            password: 原始密码字符串
            
        Note:
            - 使用 Werkzeug 的 generate_password_hash
            - 采用 pbkdf2:sha256 算法，不可逆加密
            - 每次生成的哈希值都不同（包含随机盐）
        """
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def verify_password(self, password):
        """
        验证密码是否正确
        
        Args:
            password: 待验证的原始密码
            
        Returns:
            bool: 密码是否正确
            
        Note:
            - 使用 check_password_hash 对比
            - 自动处理盐值匹配
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """
        将用户对象转换为字典格式
        
        Args:
            include_sensitive: 是否包含敏感信息（默认False）
            
        Returns:
            dict: 用户数据字典
                  {
                      'id': 用户ID,
                      'username': 用户名,
                      'email': 邮箱,
                      'created_at': 创建时间字符串
                  }
                  
        Note:
            - 默认不包含密码哈希
            - API响应时使用此方法
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def __repr__(self):
        """字符串表示（用于调试）"""
        return f'<User(id={self.id}, username="{self.username}")>'
    
    def __str__(self):
        """字符串显示"""
        return f"用户: {self.username}"


def create_default_user():
    """
    创建默认用户（单用户系统）
    
    Returns:
        User: 默认用户对象
        
    Note:
        - 只在首次运行时调用
        - 如果已存在则返回现有用户
    """
    from config.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # 检查是否已有用户
        existing_user = db.query(User).first()
        
        if existing_user:
            print(f"ℹ️  默认用户已存在: {existing_user.username}")
            return existing_user
        
        # 创建默认用户
        default_user = User(
            username='admin',
            email='admin@localhost',
            password='admin123'  # 默认密码
        )
        
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        
        print(f"✅ 创建默认用户: {default_user.username} (密码: admin123)")
        return default_user
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建默认用户失败: {e}")
        raise
    
    finally:
        db.close()