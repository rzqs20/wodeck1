"""
股票数据服务模块
负责股票数据的获取、存储和查询

Note:
    - 使用国金QMT（xtquant）作为数据源
    - QMT必须在运行状态才能获取数据
    - 数据自动保存到SQLite数据库
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import time

from models.stock_data import StockData
from config.database import SessionLocal
from config.settings import get_api_config
from sqlalchemy import desc, and_


def fetch_stock_data_from_qmt(stock_code: str, period: str = '1d', 
                               start_date: str = None, end_date: str = None) -> List[Dict]:
    """
    从国金QMT获取股票数据
    
    Args:
        stock_code: 股票代码（如 '600000.SH'）
        period: 数据周期
                - '1d': 日线（默认）
                - '1m': 1分钟
                - '5m': 5分钟
                - '15m': 15分钟
                - '30m': 30分钟
                - '1h': 1小时
                - '1w': 周线
                - '1mon': 月线
        start_date: 开始日期（格式：'20240101' 或 '2024-01-01'）
        end_date: 结束日期（格式：'20241231' 或 '2024-12-31'）
        
    Returns:
        list: 股票数据列表，每个元素为字典
              [
                  {
                      'date': '2024-01-15',
                      'open': 10.5,
                      'high': 10.8,
                      'low': 10.3,
                      'close': 10.7,
                      'volume': 1000000,
                      'amount': 10600000
                  }
              ]
        
    Raises:
        ImportError: xtquant库未安装时抛出
        ConnectionError: QMT未连接时抛出
        ValueError: 参数不合法时抛出
        
    Note:
        - QMT客户端必须处于登录状态
        - 首次使用需要初始化xtquant
        - 数据格式会自动标准化
    """
    try:
        from xtquant import xtdata
    except ImportError:
        raise ImportError(
            "xtquant库未安装，请先安装：\n"
            "1. 确保已安装国金QMT客户端\n"
            "2. 在QMT安装目录下找到xtquant库\n"
            "3. 运行: pip install xtquant"
        )
    
    # 验证参数
    if not stock_code:
        raise ValueError("股票代码不能为空")
    
    # 格式化日期
    if start_date:
        start_date = _format_date_for_qmt(start_date)
    if end_date:
        end_date = _format_date_for_qmt(end_date)
    
    try:
        # 订阅数据（确保数据可用）
        xtdata.subscribe_quote(stock_code, period=period)
        
        # 等待数据就绪
        time.sleep(0.5)
        
        # 获取历史数据
        data = xtdata.get_market_data(
            field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[stock_code],
            period=period,
            start_time=start_date,
            end_time=end_date,
            count=-1  # 获取所有数据
        )
        
        # 检查是否获取到数据
        if not data or len(data) == 0:
            raise ValueError(f"未获取到 {stock_code} 的数据")
        
        # 解析数据
        result = _parse_qmt_data(data, stock_code)
        
        return result
        
    except Exception as e:
        raise ConnectionError(f"从QMT获取数据失败: {str(e)}")


def _format_date_for_qmt(date_str: str) -> str:
    """
    格式化日期为QMT需要的格式（YYYYMMDD）
    
    Args:
        date_str: 日期字符串
        
    Returns:
        str: 格式化后的日期（如 '20240115'）
    """
    # 移除分隔符
    date_str = date_str.replace('-', '').replace('/', '')
    
    # 验证格式
    if len(date_str) != 8 or not date_str.isdigit():
        raise ValueError(f"日期格式不正确: {date_str}，应为 YYYYMMDD 或 YYYY-MM-DD")
    
    return date_str


def _parse_qmt_data(raw_data: Dict, stock_code: str) -> List[Dict]:
    """
    解析QMT返回的原始数据
    
    Args:
        raw_data: QMT返回的原始数据
        stock_code: 股票代码
        
    Returns:
        list: 标准化后的数据列表
    """
    result = []
    
    try:
        # QMT返回的数据结构可能因版本而异，这里做兼容处理
        # 通常是一个字典，key是字段名，value是时间序列数据
        
        times = raw_data.get('time', [])
        opens = raw_data.get('open', [])
        highs = raw_data.get('high', [])
        lows = raw_data.get('low', [])
        closes = raw_data.get('close', [])
        volumes = raw_data.get('volume', [])
        amounts = raw_data.get('amount', [])
        
        # 确保所有字段长度一致
        min_len = min(len(times), len(opens), len(highs), len(lows), 
                     len(closes), len(volumes))
        
        for i in range(min_len):
            # 转换时间戳
            timestamp = times[i]
            if isinstance(timestamp, (int, float)):
                # 时间戳转换为日期
                date_obj = datetime.fromtimestamp(timestamp)
                date_str = date_obj.strftime('%Y-%m-%d')
            else:
                date_str = str(timestamp)[:10]  # 取前10位
            
            record = {
                'stock_code': stock_code,
                'date': date_str,
                'open': float(opens[i]) if opens[i] else 0,
                'high': float(highs[i]) if highs[i] else 0,
                'low': float(lows[i]) if lows[i] else 0,
                'close': float(closes[i]) if closes[i] else 0,
                'volume': float(volumes[i]) if volumes[i] else 0,
                'amount': float(amounts[i]) if i < len(amounts) and amounts[i] else 0,
            }
            
            result.append(record)
        
        # 按日期排序
        result.sort(key=lambda x: x['date'])
        
    except Exception as e:
        raise ValueError(f"解析QMT数据失败: {str(e)}")
    
    return result


def save_stock_data(stock_data_list: List[Dict]) -> int:
    """
    保存股票数据到数据库
    
    Args:
        stock_data_list: 股票数据列表，每个元素为字典
                        格式见 fetch_stock_data_from_qmt 的返回值
        
    Returns:
        int: 成功保存的记录数
        
    Raises:
        ValueError: 数据格式不正确时抛出
        
    Note:
        - 批量插入以提高性能
        - 自动去重（相同股票+日期只保留一条）
        - 事务管理，失败自动回滚
    """
    if not stock_data_list:
        return 0
    
    db = SessionLocal()
    saved_count = 0
    
    try:
        for data_dict in stock_data_list:
            # 验证必需字段
            required_fields = ['stock_code', 'date', 'open', 'high', 'low', 'close', 'volume']
            for field in required_fields:
                if field not in data_dict:
                    raise ValueError(f"缺少必需字段: {field}")
            
            # ⭐ 关键修复：将日期字符串转换为datetime对象
            date_str = data_dict['date']
            if isinstance(date_str, str):
                # 如果是字符串，转换为datetime
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            elif isinstance(date_str, datetime):
                # 如果已经是datetime，直接使用
                date_obj = date_str
            else:
                raise ValueError(f"日期格式不支持: {type(date_str)}")
            
            # 检查是否已存在（使用datetime对象查询）
            existing = db.query(StockData).filter(
                and_(
                    StockData.stock_code == data_dict['stock_code'],
                    StockData.date == date_obj  # ⭐ 使用datetime对象
                )
            ).first()
            
            if existing:
                # 更新现有记录
                existing.open = data_dict['open']
                existing.high = data_dict['high']
                existing.low = data_dict['low']
                existing.close = data_dict['close']
                existing.volume = data_dict['volume']
                existing.amount = data_dict.get('amount', 0)
            else:
                # 创建新记录
                stock_data = StockData(
                    stock_code=data_dict['stock_code'],
                    date=date_obj,  # ⭐ 使用datetime对象
                    open_price=data_dict['open'],
                    high=data_dict['high'],
                    low=data_dict['low'],
                    close=data_dict['close'],
                    volume=data_dict['volume'],
                    amount=data_dict.get('amount', 0)
                )
                db.add(stock_data)
            
            saved_count += 1
        
        # 提交事务
        db.commit()
        
        return saved_count
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"保存数据失败: {str(e)}")
    
    finally:
        db.close()


def get_stock_data(stock_code: str, start_date: str = None, 
                   end_date: str = None, limit: int = None) -> List[Dict]:
    """
    从数据库查询股票数据
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期（可选，格式：'2024-01-01'）
        end_date: 结束日期（可选，格式：'2024-12-31'）
        limit: 限制返回数量（可选，默认全部）
        
    Returns:
        list: 股票数据列表，按日期升序排列
              每个元素为字典（调用 to_dict()）
        
    Note:
        - 优先从本地数据库查询
        - 支持日期范围筛选
        - 支持分页限制
    """
    db = SessionLocal()
    
    try:
        query = db.query(StockData).filter(StockData.stock_code == stock_code)
        
        # 添加日期过滤（转换为datetime）
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(StockData.date >= start_date)
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(StockData.date <= end_date)
        
        # 按日期升序排列
        query = query.order_by(StockData.date.asc())
        
        # 限制数量
        if limit:
            query = query.limit(limit)
        
        # 执行查询
        stocks = query.all()
        
        # 转换为字典
        result = [stock.to_dict() for stock in stocks]
        
        return result
        
    finally:
        db.close()


def update_stock_data(stock_code: str, period: str = '1d') -> Dict:
    """
    更新股票数据（增量更新）
    
    Args:
        stock_code: 股票代码
        period: 数据周期（默认日线）
        
    Returns:
        dict: 更新结果
              {
                  'success': True/False,
                  'updated_count': 更新的记录数,
                  'latest_date': 最新数据日期,
                  'message': 提示信息
              }
        
    Note:
        - 先查询数据库中最新日期
        - 只获取该日期之后的新数据
        - 避免重复下载
    """
    db = SessionLocal()
    
    try:
        # 1. 查询数据库中最新的日期
        latest_record = db.query(StockData).filter(
            StockData.stock_code == stock_code
        ).order_by(desc(StockData.date)).first()
        
        if latest_record:
            # 从下一天开始获取
            next_date = (latest_record.date + timedelta(days=1)).strftime('%Y-%m-%d')
            start_date = next_date
            message = f"从 {next_date} 开始更新"
        else:
            # 没有历史数据，获取最近1年
            one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            start_date = one_year_ago
            message = "首次获取数据"
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 2. 从QMT获取新数据
        print(f"正在{message}...")
        new_data = fetch_stock_data_from_qmt(
            stock_code=stock_code,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        if not new_data:
            return {
                'success': True,
                'updated_count': 0,
                'latest_date': latest_record.date.strftime('%Y-%m-%d') if latest_record else None,
                'message': '没有新数据'
            }
        
        # 3. 保存到数据库
        saved_count = save_stock_data(new_data)
        
        # 4. 获取最新日期
        latest_record = db.query(StockData).filter(
            StockData.stock_code == stock_code
        ).order_by(desc(StockData.date)).first()
        
        return {
            'success': True,
            'updated_count': saved_count,
            'latest_date': latest_record.date.strftime('%Y-%m-%d') if latest_record else None,
            'message': f'成功更新 {saved_count} 条数据'
        }
        
    except Exception as e:
        return {
            'success': False,
            'updated_count': 0,
            'latest_date': None,
            'message': f'更新失败: {str(e)}'
        }
    
    finally:
        db.close()


def get_latest_price(stock_code: str) -> Optional[Dict]:
    """
    获取最新价格信息
    
    Args:
        stock_code: 股票代码
        
    Returns:
        dict: 最新价格信息
              {
                  'stock_code': '600000.SH',
                  'date': '2024-01-15',
                  'open': 10.5,
                  'high': 10.8,
                  'low': 10.3,
                  'close': 10.7,
                  'volume': 1000000,
                  'change_info': {
                      'change': 0.2,
                      'change_percent': 1.9,
                      'is_up': True
                  }
              }
              如果没有数据返回 None
        
    Note:
        - 从数据库查询最新一条记录
        - 自动计算相对于前一日的涨跌幅
    """
    db = SessionLocal()
    
    try:
        # 获取最新数据
        latest = db.query(StockData).filter(
            StockData.stock_code == stock_code
        ).order_by(desc(StockData.date)).first()
        
        if not latest:
            return None
        
        # 获取前一日数据
        prev = db.query(StockData).filter(
            and_(
                StockData.stock_code == stock_code,
                StockData.date < latest.date
            )
        ).order_by(desc(StockData.date)).first()
        
        # 组装结果
        result = latest.to_dict()
        
        # 计算涨跌幅
        if prev:
            change_info = latest.calculate_change_from_prev(prev.close)
            result['prev_close'] = prev.close
            result['change_info'] = change_info
        else:
            result['prev_close'] = None
            result['change_info'] = {
                'change': None,
                'change_percent': None,
                'is_up': None,
                'note': '首日上市或无历史数据'
            }
        
        return result
        
    finally:
        db.close()


def batch_fetch_and_save(stock_codes: List[str], period: str = '1d', 
                         days: int = 365) -> Dict:
    """
    批量获取并保存多只股票数据
    
    Args:
        stock_codes: 股票代码列表
        period: 数据周期（默认日线）
        days: 获取天数（默认365天）
        
    Returns:
        dict: 批量处理结果
              {
                  'total': 总数,
                  'success': 成功数量,
                  'failed': 失败数量,
                  'details': [
                      {'code': '600000.SH', 'status': 'success', 'count': 250},
                      {'code': 'INVALID', 'status': 'failed', 'error': '...'}
                  ]
              }
        
    Note:
        - 逐个处理，避免并发问题
        - 部分失败不影响其他股票
        - 适合初始化大量股票数据
    """
    results = {
        'total': len(stock_codes),
        'success': 0,
        'failed': 0,
        'details': []
    }
    
    for i, stock_code in enumerate(stock_codes, 1):
        print(f"[{i}/{len(stock_codes)}] 正在处理 {stock_code}...")
        
        try:
            # 计算日期范围
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 获取数据
            data = fetch_stock_data_from_qmt(
                stock_code=stock_code,
                period=period,
                start_date=start_date,
                end_date=end_date
            )
            
            # 保存数据
            if data:
                saved_count = save_stock_data(data)
                results['success'] += 1
                results['details'].append({
                    'code': stock_code,
                    'status': 'success',
                    'count': saved_count
                })
                print(f"  ✅ 成功保存 {saved_count} 条数据")
            else:
                results['failed'] += 1
                results['details'].append({
                    'code': stock_code,
                    'status': 'failed',
                    'error': '未获取到数据'
                })
                print(f"  ❌ 未获取到数据")
            
            # 避免请求过快
            time.sleep(0.5)
            
        except Exception as e:
            results['failed'] += 1
            results['details'].append({
                'code': stock_code,
                'status': 'failed',
                'error': str(e)
            })
            print(f"  ❌ 失败: {str(e)}")
    
    return results


def init_default_watchlist_data(watchlist_id: int = None) -> Dict:
    """
    初始化自选股列表的数据（便捷方法）
    
    Args:
        watchlist_id: 自选列表ID（如果提供，只更新该列表的股票）
        
    Returns:
        dict: 更新结果
        
    Note:
        - 这是一个便捷方法，用于快速更新关注的股票
        - 可以配合定时任务使用
    """
    from models.watchlist import Watchlist
    
    db = SessionLocal()
    
    try:
        if watchlist_id:
            # 更新指定列表
            watchlist = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
            if not watchlist:
                return {'success': False, 'message': '自选列表不存在'}
            
            stock_codes = watchlist.get_stocks()
        else:
            # 更新所有默认列表
            default_lists = db.query(Watchlist).filter(Watchlist.is_default == 1).all()
            stock_codes = []
            for wl in default_lists:
                stock_codes.extend(wl.get_stocks())
            
            # 去重
            stock_codes = list(set(stock_codes))
        
        if not stock_codes:
            return {'success': False, 'message': '没有股票需要更新'}
        
        # 批量更新
        result = batch_fetch_and_save(stock_codes, period='1d', days=30)
        
        return {
            'success': True,
            'message': f'完成更新: {result["success"]}成功, {result["failed"]}失败',
            'details': result
        }
        
    finally:
        db.close()