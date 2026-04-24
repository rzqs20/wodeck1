"""
自选股列表模型
定义用户自选股数据结构

Note:
    - 个人自用系统可以只有一个默认自选列表
    - 也可以创建多个分类列表（如：关注、持仓、观察等）
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
import re

Base = declarative_base()


class Watchlist(Base):
    """
    自选股列表模型类
    
    Attributes:
        id: 自选列表唯一标识
        name: 列表名称
        description: 列表描述（可选）
        stock_codes: 股票代码列表（JSON数组格式存储）
        is_default: 是否为默认列表
        created_at: 创建时间
        updated_at: 更新时间
        
    Methods:
        to_dict(): 转换为字典格式
        add_stock(): 添加股票到列表
        remove_stock(): 从列表移除股票
        has_stock(): 检查股票是否在列表中
        get_stock_count(): 获取股票数量
    """
    
    # 表名
    __tablename__ = 'watchlists'
    
    # 字段定义
    id = Column(Integer, primary_key=True, autoincrement=True, comment='自选列表唯一标识')
    name = Column(String(50), nullable=False, comment='列表名称')
    description = Column(Text, nullable=True, comment='列表描述')
    stock_codes = Column(Text, nullable=False, default='[]', comment='股票代码列表（JSON数组）')
    is_default = Column(Integer, nullable=False, default=0, comment='是否为默认列表：1-是，0-否')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 索引
    __table_args__ = (
        Index('idx_name', 'name'),
        {'comment': '自选股列表表'}
    )
    
    def __init__(self, name, description=None, stock_codes=None, is_default=False):
        """
        初始化自选股列表对象
        
        Args:
            name: 列表名称
            description: 列表描述（可选）
            stock_codes: 初始股票代码列表（可选，默认为空列表）
            is_default: 是否为默认列表（可选，默认False）
            
        Raises:
            ValueError: 参数不合法时抛出异常
            TypeError: 参数类型错误时抛出异常
            
        Note:
            - 列表名称不能为空
            - 股票代码必须符合格式规范（如：600000.SH）
            - 自动去重
        """
        # 验证列表名称
        self._validate_name(name)
        
        # 赋值
        self.name = name.strip()
        self.description = description.strip() if description else ''
        self.is_default = 1 if is_default else 0
        
        # 处理股票代码列表
        if stock_codes is None:
            self.stock_codes = '[]'
        elif isinstance(stock_codes, list):
            # 验证并标准化股票代码
            validated_codes = self._validate_and_normalize_codes(stock_codes)
            import json
            self.stock_codes = json.dumps(validated_codes, ensure_ascii=False)
        elif isinstance(stock_codes, str):
            # 如果传入的是JSON字符串，验证其合法性
            import json
            try:
                codes_list = json.loads(stock_codes)
                if not isinstance(codes_list, list):
                    raise ValueError("股票代码必须是列表格式")
                validated_codes = self._validate_and_normalize_codes(codes_list)
                self.stock_codes = json.dumps(validated_codes, ensure_ascii=False)
            except json.JSONDecodeError:
                raise ValueError("股票代码列表格式错误，应为JSON数组")
        else:
            raise TypeError("stock_codes 必须为列表或JSON字符串")
        
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def _validate_name(self, name):
        """
        验证列表名称
        
        Args:
            name: 列表名称
            
        Raises:
            ValueError: 名称不合法时抛出
        """
        if not name or not isinstance(name, str):
            raise ValueError("列表名称不能为空且必须为字符串")
        
        if len(name) > 50:
            raise ValueError("列表名称长度不能超过50个字符")
        
        # 只允许字母、数字、下划线、中文、空格
        if not re.match(r'^[\w\u4e00-\u9fa5\s]+$', name):
            raise ValueError("列表名称只能包含字母、数字、下划线、中文和空格")
    
    def _validate_stock_code(self, code):
        """
        验证单个股票代码格式
        
        Args:
            code: 股票代码
            
        Returns:
            str: 标准化后的股票代码（大写）
            
        Raises:
            ValueError: 代码格式不正确时抛出
            
        Note:
            - A股格式：6位数字.市场代码（如：600000.SH, 000001.SZ）
            - 港股格式：5位数字.HK（如：00700.HK）
            - 美股格式：字母代码.US（如：AAPL.US）
        """
        if not code or not isinstance(code, str):
            raise ValueError(f"股票代码不能为空且必须为字符串: {code}")
        
        code = code.strip().upper()
        
        # A股格式验证
        a_stock_pattern = r'^\d{6}\.(SH|SZ|BJ)$'
        # 港股格式验证
        hk_stock_pattern = r'^\d{5}\.HK$'
        # 美股格式验证
        us_stock_pattern = r'^[A-Z]+\.(US|NASDAQ|NYSE)$'
        
        if re.match(a_stock_pattern, code):
            return code
        elif re.match(hk_stock_pattern, code):
            return code
        elif re.match(us_stock_pattern, code):
            return code
        else:
            raise ValueError(
                f"股票代码格式不正确: {code}\n"
                f"支持的格式:\n"
                f"  - A股: 600000.SH, 000001.SZ, 834567.BJ\n"
                f"  - 港股: 00700.HK\n"
                f"  - 美股: AAPL.US, TSLA.NASDAQ"
            )
    
    def _validate_and_normalize_codes(self, codes_list):
        """
        验证并标准化股票代码列表
        
        Args:
            codes_list: 股票代码列表
            
        Returns:
            list: 验证并去重后的股票代码列表
            
        Raises:
            ValueError: 任何代码格式不正确时抛出
        """
        if not isinstance(codes_list, list):
            raise TypeError("股票代码必须为列表类型")
        
        validated_codes = []
        seen_codes = set()
        
        for code in codes_list:
            # 验证并标准化
            normalized_code = self._validate_stock_code(code)
            
            # 去重
            if normalized_code not in seen_codes:
                validated_codes.append(normalized_code)
                seen_codes.add(normalized_code)
        
        return validated_codes
    
    def _get_codes_list(self):
        """
        获取股票代码列表（从JSON字符串解析）
        
        Returns:
            list: 股票代码列表
        """
        import json
        try:
            return json.loads(self.stock_codes)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def _set_codes_list(self, codes_list):
        """
        设置股票代码列表（转换为JSON字符串）
        
        Args:
            codes_list: 股票代码列表
        """
        import json
        self.stock_codes = json.dumps(codes_list, ensure_ascii=False)
        self.updated_at = datetime.now()
    
    def to_dict(self, include_stocks=True):
        """
        将自选列表对象转换为字典格式
        
        Args:
            include_stocks: 是否包含股票列表（默认True）
            
        Returns:
            dict: 自选列表信息字典
                  - id: 列表ID
                  - name: 列表名称
                  - description: 描述
                  - stock_codes: 股票代码列表（如果include_stocks=True）
                  - stock_count: 股票数量
                  - is_default: 是否为默认列表
                  - created_at: 创建时间
                  - updated_at: 更新时间
                  
        Note:
            - 用于API响应序列化
        """
        import json
        
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stock_count': self.get_stock_count(),
            'is_default': bool(self.is_default),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
        
        if include_stocks:
            try:
                result['stock_codes'] = json.loads(self.stock_codes)
            except (json.JSONDecodeError, TypeError):
                result['stock_codes'] = []
        
        return result
    
    def add_stock(self, stock_code):
        """
        添加股票到自选列表
        
        Args:
            stock_code: 股票代码
            
        Returns:
            bool: 添加是否成功
            
        Raises:
            ValueError: 股票已存在或格式不正确时抛出异常
            
        Note:
            - 检查股票代码是否已存在
            - 验证股票代码格式
            - 更新updated_at时间戳
        """
        # 验证股票代码格式
        normalized_code = self._validate_stock_code(stock_code)
        
        # 获取当前列表
        codes_list = self._get_codes_list()
        
        # 检查是否已存在
        if normalized_code in codes_list:
            raise ValueError(f"股票 {normalized_code} 已在列表中")
        
        # 添加股票
        codes_list.append(normalized_code)
        
        # 保存
        self._set_codes_list(codes_list)
        
        return True
    
    def add_stocks_batch(self, stock_codes):
        """
        批量添加股票到自选列表
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            dict: 添加结果
                  - added: 成功添加的数量
                  - skipped: 跳过的数量（已存在）
                  - errors: 错误信息列表
            
        Note:
            - 自动去重
            - 部分失败不影响其他股票
        """
        if not isinstance(stock_codes, list):
            raise TypeError("stock_codes 必须为列表类型")
        
        current_codes = self._get_codes_list()
        added = 0
        skipped = 0
        errors = []
        
        for code in stock_codes:
            try:
                # 验证格式
                normalized_code = self._validate_stock_code(code)
                
                # 检查是否已存在
                if normalized_code in current_codes:
                    skipped += 1
                    continue
                
                # 添加
                current_codes.append(normalized_code)
                added += 1
                
            except ValueError as e:
                errors.append({
                    'code': code,
                    'error': str(e)
                })
        
        # 保存
        if added > 0:
            self._set_codes_list(current_codes)
        
        return {
            'added': added,
            'skipped': skipped,
            'errors': errors,
            'total_processed': len(stock_codes)
        }
    
    def remove_stock(self, stock_code):
        """
        从自选列表移除股票
        
        Args:
            stock_code: 股票代码
            
        Returns:
            bool: 移除是否成功
            
        Raises:
            ValueError: 股票不存在时抛出异常
            
        Note:
            - 检查股票代码是否存在
            - 更新updated_at时间戳
        """
        # 标准化代码
        normalized_code = stock_code.strip().upper()
        
        # 获取当前列表
        codes_list = self._get_codes_list()
        
        # 检查是否存在
        if normalized_code not in codes_list:
            raise ValueError(f"股票 {normalized_code} 不在列表中")
        
        # 移除股票
        codes_list.remove(normalized_code)
        
        # 保存
        self._set_codes_list(codes_list)
        
        return True
    
    def has_stock(self, stock_code):
        """
        检查股票是否在列表中
        
        Args:
            stock_code: 股票代码
            
        Returns:
            bool: 是否在列表中
        """
        normalized_code = stock_code.strip().upper()
        codes_list = self._get_codes_list()
        return normalized_code in codes_list
    
    def get_stock_count(self):
        """
        获取股票数量
        
        Returns:
            int: 股票数量
        """
        codes_list = self._get_codes_list()
        return len(codes_list)
    
    def clear_all(self):
        """
        清空所有股票
        
        Returns:
            int: 清空的股票数量
        """
        codes_list = self._get_codes_list()
        count = len(codes_list)
        
        # 清空
        self._set_codes_list([])
        
        return count
    
    def get_stocks(self):
        """
        获取所有股票代码
        
        Returns:
            list: 股票代码列表
        """
        return self._get_codes_list()
    
    def __repr__(self):
        """对象的字符串表示（用于调试）"""
        stock_count = self.get_stock_count()
        return f"<Watchlist(id={self.id}, name='{self.name}', stocks={stock_count})>"
    
    def __str__(self):
        """对象的友好字符串表示"""
        stock_count = self.get_stock_count()
        stocks = self._get_codes_list()
        stocks_str = ', '.join(stocks[:5])  # 只显示前5个
        if len(stocks) > 5:
            stocks_str += f'... (+{len(stocks) - 5} more)'
        return f"{self.name} | {stock_count}只股票 | {stocks_str}"