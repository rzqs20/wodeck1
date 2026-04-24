"""
股票数据模型
定义股票行情数据结构
"""
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StockData(Base):
    """
    股票数据模型类
    
    Attributes:
        id: 数据记录唯一标识
        stock_code: 股票代码
        date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        amount: 成交额
        timestamp: 记录创建时间
        
    Methods:
        to_dict(): 转换为字典格式
        calculate_intraday_return(): 计算日内收益率
        calculate_change_from_prev(): 计算相对前一日涨跌幅
        get_limit_status(): 获取涨跌停状态
        get_kline_info(): 获取K线形态信息
    """
    
    # 表名
    __tablename__ = 'stock_data'
    
    # 字段定义
    id = Column(Integer, primary_key=True, autoincrement=True, comment='数据记录唯一标识')
    stock_code = Column(String(20), nullable=False, index=True, comment='股票代码（如 600000.SH）')
    date = Column(DateTime, nullable=False, index=True, comment='交易日期')
    open = Column(Float, nullable=False, comment='开盘价')
    high = Column(Float, nullable=False, comment='最高价')
    low = Column(Float, nullable=False, comment='最低价')
    close = Column(Float, nullable=False, comment='收盘价')
    volume = Column(Float, nullable=False, comment='成交量（手）')
    amount = Column(Float, default=0, comment='成交额（元）')
    timestamp = Column(DateTime, default=datetime.now, comment='记录创建时间')
    
    # 复合索引（优化常用查询）
    __table_args__ = (
        Index('idx_stock_date', 'stock_code', 'date'),  # 按股票代码和日期查询
        {'comment': '股票行情数据表'}
    )
    
    def __init__(self, stock_code, date, open_price, high, low, close, volume, amount=0):
        """
        初始化股票数据对象
        
        Args:
            stock_code: 股票代码（如 '600000.SH'）
            date: 交易日期（datetime对象或字符串）
            open_price: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
            volume: 成交量
            amount: 成交额（可选，默认为0）
            
        Raises:
            ValueError: 数据不合法时抛出异常
            TypeError: 参数类型错误时抛出异常
            
        Note:
            - 如果date是字符串，会自动转换为datetime对象
            - 价格不能为负数
            - 成交量不能为负数
            - 最高价 >= 最低价
            - 最高价 >= 开盘价、收盘价
            - 最低价 <= 开盘价、收盘价
        """
        # 验证股票代码
        if not stock_code or not isinstance(stock_code, str):
            raise ValueError("股票代码不能为空且必须为字符串")
        
        # 处理日期格式
        if isinstance(date, str):
            self.date = self._parse_date(date)
        elif isinstance(date, datetime):
            self.date = date
        else:
            raise TypeError(f"日期类型错误，应为datetime或str，实际为: {type(date)}")
        
        # 验证价格数据合法性
        self._validate_price_data(open_price, high, low, close)
        
        # 验证成交量
        if volume < 0:
            raise ValueError("成交量不能为负数")
        
        # 赋值（统一精度处理）
        self.stock_code = stock_code.upper()  # 统一转为大写
        self.open = self._round_price(open_price)
        self.high = self._round_price(high)
        self.low = self._round_price(low)
        self.close = self._round_price(close)
        self.volume = round(volume, 2)
        self.amount = round(amount, 2)
        self.timestamp = datetime.now()
    
    def _parse_date(self, date_str):
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            
        Returns:
            datetime: 解析后的日期对象
            
        Raises:
            ValueError: 无法解析日期格式时抛出
        """
        # 支持的日期格式列表
        date_formats = [
            '%Y-%m-%d',           # 2024-01-15
            '%Y%m%d',             # 20240115
            '%Y-%m-%d %H:%M:%S',  # 2024-01-15 09:30:00
            '%Y/%m/%d',           # 2024/01/15
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"无法解析日期格式: {date_str}，支持的格式: {', '.join(date_formats)}")
    
    def _validate_price_data(self, open_price, high, low, close):
        """
        验证价格数据合法性
        
        Args:
            open_price: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
            
        Raises:
            ValueError: 数据不合法时抛出
        """
        # 检查是否为负数
        if open_price < 0 or high < 0 or low < 0 or close < 0:
            raise ValueError("价格不能为负数")
        
        # 检查最高价 >= 最低价
        if high < low:
            raise ValueError(f"最高价({high})不能小于最低价({low})")
        
        # 检查最高价 >= 开盘价和收盘价
        if high < open_price or high < close:
            raise ValueError(f"最高价({high})必须大于等于开盘价({open_price})和收盘价({close})")
        
        # 检查最低价 <= 开盘价和收盘价
        if low > open_price or low > close:
            raise ValueError(f"最低价({low})必须小于等于开盘价({open_price})和收盘价({close})")
    
    def _round_price(self, price):
        """
        价格精度处理（四舍五入到4位小数）
        
        Args:
            price: 原始价格
            
        Returns:
            float: 处理后的价格
        """
        return round(price, 4)
    
    def to_dict(self, include_timestamp=True):
        """
        将股票数据对象转换为字典格式
        
        Args:
            include_timestamp: 是否包含timestamp字段（默认True）
            
        Returns:
            dict: 股票数据字典
                  - id: 记录ID
                  - stock_code: 股票代码
                  - date: 日期（字符串格式 YYYY-MM-DD）
                  - open: 开盘价
                  - high: 最高价
                  - low: 最低价
                  - close: 收盘价
                  - volume: 成交量
                  - amount: 成交额
                  - timestamp: 时间戳（可选）
                  
        Note:
            - 用于API响应序列化
            - 日期转换为字符串格式
        """
        result = {
            'id': self.id,
            'stock_code': self.stock_code,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'amount': self.amount,
        }
        
        if include_timestamp:
            result['timestamp'] = self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        
        return result
    
    def calculate_intraday_return(self):
        """
        计算日内收益率（开盘到收盘）
        
        Returns:
            float: 日内收益率（百分比）
            
        Formula:
            日内收益率 = (收盘价 - 开盘价) / 开盘价 * 100
            
        Note:
            - 这是单条数据的内部计算，不涉及跨日比较
            - 处理除零错误
            - 返回None如果开盘价为0
        """
        if self.open == 0:
            return None
        
        intraday_return = (self.close - self.open) / self.open * 100
        return round(intraday_return, 4)
    
    def calculate_intraday_amplitude(self):
        """
        计算日内振幅
        
        Returns:
            float: 日内振幅（百分比）
            
        Formula:
            日内振幅 = (最高价 - 最低价) / 开盘价 * 100
            
        Note:
            - 反映当日价格波动程度
            - 处理除零错误
        """
        if self.open == 0:
            return None
        
        amplitude = (self.high - self.low) / self.open * 100
        return round(amplitude, 2)
    
    def calculate_change_from_prev(self, prev_close):
        """
        计算相对于前一日收盘价的涨跌幅
        
        Args:
            prev_close: 前一日收盘价
            
        Returns:
            dict: 包含涨跌信息的字典
                  - change: 涨跌额 = close - prev_close
                  - change_percent: 涨跌幅（百分比）
                  - is_up: 是否上涨
                  
        Note:
            - 这个方法需要外部传入前一日收盘价
            - 通常在 service 层调用，由 service 负责查询前一天数据
            - 模型层只负责计算，不负责数据查询
        """
        if prev_close is None or prev_close == 0:
            return {
                'change': None,
                'change_percent': None,
                'is_up': None,
            }
        
        change = self.close - prev_close
        change_percent = (change / prev_close) * 100
        
        return {
            'change': round(change, 4),
            'change_percent': round(change_percent, 4),
            'is_up': change > 0,
        }
    
    def get_limit_status(self, prev_close=None, stock_type='main'):
        """
        获取涨跌停状态
        
        Args:
            prev_close: 前一日收盘价（必需）
            stock_type: 股票类型
                       - 'main': 主板（涨跌幅10%）
                       - 'star': 科创板（涨跌幅20%）
                       - 'chinext': 创业板（涨跌幅20%）
                       - 'st': ST股票（涨跌幅5%）
            
        Returns:
            str: 涨跌停状态
                 - 'up_limit': 涨停
                 - 'down_limit': 跌停
                 - 'normal': 正常
                 - 'unknown': 无法判断（缺少前收盘价）
                 
        Note:
            - 这是判断涨跌停的统一入口
            - 必须提供前一日收盘价才能判断
            - 不同板块涨跌幅限制不同
        """
        if prev_close is None or prev_close == 0:
            return 'unknown'
        
        # 根据股票类型确定涨跌幅限制
        limit_map = {
            'main': 10.0,      # 主板
            'star': 20.0,      # 科创板
            'chinext': 20.0,   # 创业板
            'st': 5.0,         # ST股票
        }
        
        limit_percent = limit_map.get(stock_type, 10.0)
        threshold = limit_percent - 0.5  # 留0.5%的容差
        
        # 计算涨跌幅
        change_percent = (self.close - prev_close) / prev_close * 100
        
        if change_percent >= threshold:
            return 'up_limit'
        elif change_percent <= -threshold:
            return 'down_limit'
        else:
            return 'normal'
    
    def get_kline_info(self):
        """
        获取K线形态信息
        
        Returns:
            dict: K线信息
                  - body_size: 实体长度（绝对值）
                  - upper_shadow: 上影线长度
                  - lower_shadow: 下影线长度
                  - kline_type: K线类型
                      * 'yang': 阳线（收盘>开盘）
                      * 'yin': 阴线（收盘<开盘）
                      * 'doji': 十字星（收盘≈开盘）
                  - body_ratio: 实体占比 = 实体/总振幅 * 100
                  - total_range: 总振幅（最高-最低）
                  
        Note:
            - 用于技术分析和K线形态识别
            - 实体占比越大，趋势越强
        """
        body = self.close - self.open
        body_size = abs(body)
        
        # 上影线 = 最高价 - max(开盘, 收盘)
        upper_shadow = self.high - max(self.open, self.close)
        
        # 下影线 = min(开盘, 收盘) - 最低价
        lower_shadow = min(self.open, self.close) - self.low
        
        # 总振幅
        total_range = self.high - self.low
        
        # 判断K线类型（实体小于0.1%视为十字星）
        if self.open != 0 and body_size / self.open < 0.001:
            kline_type = 'doji'
        elif body > 0:
            kline_type = 'yang'
        elif body < 0:
            kline_type = 'yin'
        else:
            kline_type = 'doji'
        
        # 实体占比
        body_ratio = (body_size / total_range * 100) if total_range > 0 else 0
        
        return {
            'body_size': round(body_size, 4),
            'upper_shadow': round(upper_shadow, 4),
            'lower_shadow': round(lower_shadow, 4),
            'kline_type': kline_type,
            'body_ratio': round(body_ratio, 2),
            'total_range': round(total_range, 4),
        }
    
    def get_price_range(self):
        """
        获取价格区间信息（简化版）
        
        Returns:
            dict: 价格区间信息
                  - range: 价格区间（最高-最低）
                  - range_percent: 区间幅度百分比（相对于开盘价）
                  - body: 实体长度（收盘-开盘）
                  - body_percent: 实体长度百分比
        """
        if self.open == 0:
            return {
                'range': 0,
                'range_percent': 0,
                'body': 0,
                'body_percent': 0,
            }
        
        price_range = self.high - self.low
        body = self.close - self.open
        
        return {
            'range': round(price_range, 4),
            'range_percent': round((price_range / self.open) * 100, 4),
            'body': round(body, 4),
            'body_percent': round((body / self.open) * 100, 4),
        }
    
    def __repr__(self):
        """
        对象的字符串表示（用于调试）
        
        Returns:
            str: 对象描述
        """
        date_str = self.date.strftime('%Y-%m-%d') if self.date else 'N/A'
        return f"<StockData(code={self.stock_code}, date={date_str}, close={self.close})>"
    
    def __str__(self):
        """
        对象的友好字符串表示
        
        Returns:
            str: 友好的对象描述
        """
        date_str = self.date.strftime('%Y-%m-%d') if self.date else 'N/A'
        return f"{self.stock_code} | {date_str} | 开:{self.open} 高:{self.high} 低:{self.low} 收:{self.close} 量:{self.volume}"