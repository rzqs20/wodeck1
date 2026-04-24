"""
指标计算服务模块
负责执行指标计算和结果缓存

Note:
    - 支持常用技术指标（MA、MACD、RSI、KDJ、BOLL）
    - 自动从数据库获取历史数据
    - 内存缓存避免重复计算
    - 单用户系统，简化缓存策略
"""
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math

from services.stock_data_service import get_stock_data
from models.indicator import Indicator


# 简单的内存缓存（生产环境可用Redis）
_cache = {}


def calculate_indicator(stock_code: str, indicator_name: str, 
                       parameters: Dict = None, start_date: str = None, 
                       end_date: str = None) -> Dict:
    """
    计算指定指标
    
    Args:
        stock_code: 股票代码（如 '600000.SH'）
        indicator_name: 指标名称（如 'MA', 'MACD', 'RSI'）
        parameters: 指标参数字典（如 {'N': 5}）
        start_date: 开始日期（格式：'2024-01-01'，默认最近1年）
        end_date: 结束日期（格式：'2024-12-31'，默认今天）
        
    Returns:
        dict: 计算结果
              {
                  'indicator_name': 'MA',
                  'stock_code': '600000.SH',
                  'parameters': {'N': 5},
                  'data': [
                      {'date': '2024-01-15', 'value': 10.5},
                      ...
                  ],
                  'metadata': {
                      'calc_time': 0.05,  # 计算耗时（秒）
                      'data_points': 250,  # 数据点数
                      'cache_hit': False   # 是否命中缓存
                  }
              }
        
    Raises:
        ValueError: 参数不合法或指标不存在
        Exception: 计算失败
        
    Note:
        - 先检查缓存
        - 获取历史数据
        - 执行计算
        - 缓存结果
    """
    start_time = time.time()
    
    # 设置默认参数
    if parameters is None:
        parameters = {}
    
    # 设置默认日期范围（最近1年）
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # 生成缓存键
    cache_key = _generate_cache_key(stock_code, indicator_name, parameters, start_date, end_date)
    
    # 检查缓存
    cached_result = get_cached_result(cache_key)
    if cached_result:
        calc_time = time.time() - start_time
        cached_result['metadata']['calc_time'] = calc_time
        cached_result['metadata']['cache_hit'] = True
        return cached_result
    
    # 获取历史数据
    historical_data = get_historical_data(stock_code, start_date, end_date)
    
    if not historical_data:
        raise ValueError(f"未获取到 {stock_code} 的历史数据")
    
    # 执行计算
    try:
        result_data = _execute_calculation(indicator_name, historical_data, parameters)
    except Exception as e:
        raise Exception(f"指标计算失败: {str(e)}")
    
    # 组装结果
    result = {
        'indicator_name': indicator_name,
        'stock_code': stock_code,
        'parameters': parameters,
        'data': result_data,
        'metadata': {
            'calc_time': time.time() - start_time,
            'data_points': len(result_data),
            'cache_hit': False,
            'start_date': start_date,
            'end_date': end_date
        }
    }
    
    # 缓存结果（TTL 1小时）
    cache_indicator_result(cache_key, result, ttl=3600)
    
    return result


def calculate_multiple_indicators(stock_code: str, indicator_list: List[Dict], 
                                  start_date: str = None, end_date: str = None) -> Dict:
    """
    批量计算多个指标
    
    Args:
        stock_code: 股票代码
        indicator_list: 指标列表
                       [
                           {'name': 'MA', 'parameters': {'N': 5}},
                           {'name': 'MACD', 'parameters': {'FAST': 12, 'SLOW': 26, 'SIGNAL': 9}}
                       ]
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        dict: 批量计算结果
              {
                  'stock_code': '600000.SH',
                  'indicators': {
                      'MA': {...},
                      'MACD': {...}
                  },
                  'total_time': 0.15
              }
        
    Note:
        - 一次性获取历史数据，避免重复查询
        - 逐个计算指标
        - 统一返回格式
    """
    total_start = time.time()
    
    # 设置默认日期
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # 一次性获取历史数据
    historical_data = get_historical_data(stock_code, start_date, end_date)
    
    if not historical_data:
        raise ValueError(f"未获取到 {stock_code} 的历史数据")
    
    # 计算每个指标
    results = {}
    for ind_config in indicator_list:
        indicator_name = ind_config['name']
        parameters = ind_config.get('parameters', {})
        
        try:
            result_data = _execute_calculation(indicator_name, historical_data, parameters)
            
            results[indicator_name] = {
                'indicator_name': indicator_name,
                'stock_code': stock_code,
                'parameters': parameters,
                'data': result_data,
                'metadata': {
                    'data_points': len(result_data)
                }
            }
        except Exception as e:
            results[indicator_name] = {
                'error': str(e),
                'indicator_name': indicator_name
            }
    
    return {
        'stock_code': stock_code,
        'indicators': results,
        'total_time': time.time() - total_start
    }


def get_historical_data(stock_code: str, start_date: str, end_date: str, 
                       force_refresh: bool = False) -> List[Dict]:
    """
    智能获取历史行情数据（带降级策略）
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        force_refresh: 是否强制从QMT刷新（默认False）
        
    Returns:
        list: 历史数据列表，按日期排序
              [
                  {'date': '2024-01-15', 'open': 10.5, 'high': 10.8, 
                   'low': 10.3, 'close': 10.7, 'volume': 1000000},
                  ...
              ]
        
    Note:
        - 优先从本地数据库查询
        - 如果数据不足或强制刷新，尝试从QMT获取
        - QMT失败时返回已有的旧数据
        - 数据按日期升序排列
    """
    # 1️⃣ 如果不强制刷新，先查数据库
    if not force_refresh:
        db_data = get_stock_data(stock_code, start_date, end_date)
        if db_data and len(db_data) > 0:
            print(f"✅ 从数据库获取到 {len(db_data)} 条数据")
            return _format_data(db_data)
    
    # 2️⃣ 数据库没有数据或强制刷新，尝试从QMT获取
    print(f"⚠️  数据库无数据或强制刷新，尝试从QMT获取...")
    
    try:
        from services.stock_data_service import (
            fetch_stock_data_from_qmt,
            save_stock_data,
            update_stock_data
        )
        
        # 2.1 先尝试增量更新（更快）
        print(f"   尝试增量更新...")
        update_result = update_stock_data(stock_code, period='1d')
        
        if update_result['success'] and update_result['updated_count'] > 0:
            print(f"   ✅ 增量更新成功，新增 {update_result['updated_count']} 条数据")
            
            # 更新成功后，再从数据库读取
            db_data = get_stock_data(stock_code, start_date, end_date)
            if db_data:
                return _format_data(db_data)
        
        # 2.2 增量更新没数据或失败，直接全量获取
        print(f"   增量更新无新数据，尝试全量获取...")
        qmt_data = fetch_stock_data_from_qmt(
            stock_code=stock_code,
            period='1d',
            start_date=start_date,
            end_date=end_date
        )
        
        if qmt_data and len(qmt_data) > 0:
            # 保存到数据库（下次就可以直接从数据库读了）
            save_stock_data(qmt_data)
            print(f"   ✅ 从QMT获取并保存了 {len(qmt_data)} 条数据")
            return _format_data(qmt_data)
        
    except Exception as e:
        print(f"   ❌ QMT获取失败: {e}")
        print(f"   💡 提示：请确保QMT客户端已登录，或在工作日运行")
        
        # 3️⃣ QMT也失败，尝试返回数据库中已有的旧数据
        print(f"   尝试返回数据库中已有的历史数据...")
        old_data = get_stock_data(stock_code, None, None)  # 获取所有数据
        
        if old_data and len(old_data) > 0:
            print(f"   ⚠️  返回数据库中已有的 {len(old_data)} 条数据（可能不是最新）")
            # 过滤日期范围
            filtered_data = [
                item for item in old_data 
                if (not start_date or item['date'] >= start_date) and
                   (not end_date or item['date'] <= end_date)
            ]
            if filtered_data:
                return _format_data(filtered_data)
    
    # 4️⃣ 所有方法都失败，返回空列表
    print(f"   ❌ 无法获取任何数据")
    return []


def _format_data(data: List[Dict]) -> List[Dict]:
    """
    格式化数据为标准格式
    
    Args:
        data: 原始数据列表
        
    Returns:
        list: 标准化后的数据
    """
    result = []
    for item in data:
        result.append({
            'date': item['date'],
            'open': item['open'],
            'high': item['high'],
            'low': item['low'],
            'close': item['close'],
            'volume': item['volume'],
            'amount': item.get('amount', 0)
        })
    
    # 确保按日期排序
    result.sort(key=lambda x: x['date'])
    
    return result


def _execute_calculation(indicator_name: str, historical_data: List[Dict], 
                        parameters: Dict) -> List[Dict]:
    """
    执行具体的指标计算
    
    Args:
        indicator_name: 指标名称
        historical_data: 历史数据
        parameters: 参数
        
    Returns:
        list: 计算结果
    """
    # 根据指标名称调用相应的计算函数
    calculation_functions = {
        'MA': _calculate_ma,
        'EMA': _calculate_ema,
        'MACD': _calculate_macd,
        'RSI': _calculate_rsi,
        'KDJ': _calculate_kdj,
        'BOLL': _calculate_boll,
    }
    
    if indicator_name not in calculation_functions:
        raise ValueError(f"不支持的指标: {indicator_name}")
    
    calc_func = calculation_functions[indicator_name]
    return calc_func(historical_data, parameters)


# ==================== 指标计算算法 ====================

def _calculate_ma(data: List[Dict], params: Dict) -> List[Dict]:
    """
    计算移动平均线（MA）
    
    Args:
        data: 历史数据
        params: 参数 {'N': 周期}
        
    Returns:
        list: [{'date': ..., 'ma': ...}]
    """
    n = params.get('N', 5)
    
    if len(data) < n:
        raise ValueError(f"数据不足，需要至少 {n} 条数据")
    
    result = []
    closes = [item['close'] for item in data]
    
    for i in range(len(data)):
        if i < n - 1:
            # 数据不足，返回None
            result.append({'date': data[i]['date'], 'ma': None})
        else:
            # 计算MA
            ma = sum(closes[i-n+1:i+1]) / n
            result.append({
                'date': data[i]['date'],
                'ma': round(ma, 4)
            })
    
    return result


def _calculate_ema(data: List[Dict], params: Dict) -> List[Dict]:
    """
    计算指数移动平均（EMA）
    
    Args:
        data: 历史数据
        params: 参数 {'N': 周期}
        
    Returns:
        list: [{'date': ..., 'ema': ...}]
    """
    n = params.get('N', 12)
    
    if len(data) < n:
        raise ValueError(f"数据不足，需要至少 {n} 条数据")
    
    result = []
    closes = [item['close'] for item in data]
    
    # 计算平滑系数
    alpha = 2 / (n + 1)
    
    # 第一个EMA值使用简单平均
    ema = sum(closes[:n]) / n
    
    for i in range(len(data)):
        if i < n - 1:
            result.append({'date': data[i]['date'], 'ema': None})
        elif i == n - 1:
            result.append({'date': data[i]['date'], 'ema': round(ema, 4)})
        else:
            # EMA = α * 当前价格 + (1-α) * 前一个EMA
            ema = alpha * closes[i] + (1 - alpha) * ema
            result.append({
                'date': data[i]['date'],
                'ema': round(ema, 4)
            })
    
    return result


def _calculate_macd(data: List[Dict], params: Dict) -> List[Dict]:
    """
    计算MACD指标
    
    Args:
        data: 历史数据
        params: 参数 {'FAST': 12, 'SLOW': 26, 'SIGNAL': 9}
        
    Returns:
        list: [{'date': ..., 'dif': ..., 'dea': ..., 'macd': ...}]
    """
    fast = params.get('FAST', 12)
    slow = params.get('SLOW', 26)
    signal = params.get('SIGNAL', 9)
    
    if len(data) < slow:
        raise ValueError(f"数据不足，需要至少 {slow} 条数据")
    
    closes = [item['close'] for item in data]
    
    # 计算快速EMA
    ema_fast = _calculate_ema_values(closes, fast)
    # 计算慢速EMA
    ema_slow = _calculate_ema_values(closes, slow)
    
    result = []
    
    for i in range(len(data)):
        if i < slow - 1:
            result.append({
                'date': data[i]['date'],
                'dif': None,
                'dea': None,
                'macd': None
            })
        else:
            # DIF = EMA快 - EMA慢
            dif = ema_fast[i] - ema_slow[i]
            
            # DEA = DIF的EMA
            if i == slow - 1:
                dea = dif
            else:
                # 简化：使用前signal个DIF的平均
                dif_values = [ema_fast[j] - ema_slow[j] for j in range(slow-1, i)]
                if len(dif_values) >= signal:
                    dea = sum(dif_values[-signal:]) / signal
                else:
                    dea = dif
            
            # MACD = 2 * (DIF - DEA)
            macd = 2 * (dif - dea)
            
            result.append({
                'date': data[i]['date'],
                'dif': round(dif, 4),
                'dea': round(dea, 4),
                'macd': round(macd, 4)
            })
    
    return result


def _calculate_ema_values(prices: List[float], period: int) -> List[float]:
    """计算EMA值序列"""
    alpha = 2 / (period + 1)
    ema_values = []
    
    # 第一个值是简单平均
    if len(prices) >= period:
        ema = sum(prices[:period]) / period
    else:
        ema = prices[0]
    
    for i in range(len(prices)):
        if i < period - 1:
            ema_values.append(None)
        elif i == period - 1:
            ema_values.append(ema)
        else:
            ema = alpha * prices[i] + (1 - alpha) * ema
            ema_values.append(ema)
    
    return ema_values


def _calculate_rsi(data: List[Dict], params: Dict) -> List[Dict]:
    """
    计算RSI（相对强弱指标）
    
    Args:
        data: 历史数据
        params: 参数 {'N': 周期，默认14}
        
    Returns:
        list: [{'date': ..., 'rsi': ...}]
    """
    n = params.get('N', 14)
    
    if len(data) < n + 1:
        raise ValueError(f"数据不足，需要至少 {n + 1} 条数据")
    
    result = []
    closes = [item['close'] for item in data]
    
    for i in range(len(data)):
        if i < n:
            result.append({'date': data[i]['date'], 'rsi': None})
        else:
            # 计算涨跌幅
            gains = []
            losses = []
            
            for j in range(i - n + 1, i + 1):
                change = closes[j] - closes[j-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / n
            avg_loss = sum(losses) / n
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            result.append({
                'date': data[i]['date'],
                'rsi': round(rsi, 4)
            })
    
    return result


def _calculate_kdj(data: List[Dict], params: Dict) -> List[Dict]:
    """
    计算KDJ指标
    
    Args:
        data: 历史数据
        params: 参数 {'N': 9, 'M1': 3, 'M2': 3}
        
    Returns:
        list: [{'date': ..., 'k': ..., 'd': ..., 'j': ...}]
    """
    n = params.get('N', 9)
    m1 = params.get('M1', 3)
    m2 = params.get('M2', 3)
    
    if len(data) < n:
        raise ValueError(f"数据不足，需要至少 {n} 条数据")
    
    result = []
    
    for i in range(len(data)):
        if i < n - 1:
            result.append({
                'date': data[i]['date'],
                'k': None,
                'd': None,
                'j': None
            })
        else:
            # 计算N日内的最高价和最低价
            high_n = max([data[j]['high'] for j in range(i-n+1, i+1)])
            low_n = min([data[j]['low'] for j in range(i-n+1, i+1)])
            
            close = data[i]['close']
            
            # RSV = (收盘价 - N日最低) / (N日最高 - N日最低) * 100
            if high_n == low_n:
                rsv = 50
            else:
                rsv = (close - low_n) / (high_n - low_n) * 100
            
            # K = 2/3 * 前K + 1/3 * RSV
            if i == n - 1:
                k = rsv
                d = k
            else:
                prev_k = result[i-1]['k'] if result[i-1]['k'] else 50
                prev_d = result[i-1]['d'] if result[i-1]['d'] else 50
                k = (2/3) * prev_k + (1/3) * rsv
                d = (2/3) * prev_d + (1/3) * k
            
            # J = 3*K - 2*D
            j = 3 * k - 2 * d
            
            result.append({
                'date': data[i]['date'],
                'k': round(k, 4),
                'd': round(d, 4),
                'j': round(j, 4)
            })
    
    return result


def _calculate_boll(data: List[Dict], params: Dict) -> List[Dict]:
    """
    计算布林带（BOLL）
    
    Args:
        data: 历史数据
        params: 参数 {'N': 20, 'P': 2}
        
    Returns:
        list: [{'date': ..., 'upper': ..., 'middle': ..., 'lower': ...}]
    """
    n = params.get('N', 20)
    p = params.get('P', 2)
    
    if len(data) < n:
        raise ValueError(f"数据不足，需要至少 {n} 条数据")
    
    result = []
    closes = [item['close'] for item in data]
    
    for i in range(len(data)):
        if i < n - 1:
            result.append({
                'date': data[i]['date'],
                'upper': None,
                'middle': None,
                'lower': None
            })
        else:
            # 中轨 = MA
            middle = sum(closes[i-n+1:i+1]) / n
            
            # 标准差
            variance = sum([(closes[j] - middle) ** 2 for j in range(i-n+1, i+1)]) / n
            std = math.sqrt(variance)
            
            # 上轨 = 中轨 + P * 标准差
            upper = middle + p * std
            # 下轨 = 中轨 - P * 标准差
            lower = middle - p * std
            
            result.append({
                'date': data[i]['date'],
                'upper': round(upper, 4),
                'middle': round(middle, 4),
                'lower': round(lower, 4)
            })
    
    return result


# ==================== 缓存管理 ====================

def _generate_cache_key(stock_code: str, indicator_name: str, 
                       parameters: Dict, start_date: str, end_date: str) -> str:
    """生成缓存键"""
    param_str = json.dumps(parameters, sort_keys=True)
    return f"indicator:{stock_code}:{indicator_name}:{param_str}:{start_date}:{end_date}"


def cache_indicator_result(cache_key: str, result: Dict, ttl: int = 3600):
    """
    缓存指标计算结果
    
    Args:
        cache_key: 缓存键
        result: 计算结果
        ttl: 过期时间（秒），默认1小时
    """
    expire_time = time.time() + ttl
    _cache[cache_key] = {
        'data': result,
        'expire_time': expire_time
    }


def get_cached_result(cache_key: str) -> Optional[Dict]:
    """
    获取缓存的指标结果
    
    Args:
        cache_key: 缓存键
        
    Returns:
        dict: 缓存的结果或None（未命中或已过期）
    """
    if cache_key not in _cache:
        return None
    
    cached = _cache[cache_key]
    
    # 检查是否过期
    if time.time() > cached['expire_time']:
        del _cache[cache_key]
        return None
    
    return cached['data']


def clear_cache(pattern: str = None):
    """
    清除缓存
    
    Args:
        pattern: 缓存键模式（可选）
                 - None: 清除所有缓存
                 - "indicator:*": 清除所有指标缓存
                 - "indicator:600000:*": 清除特定股票的缓存
    """
    if pattern is None:
        _cache.clear()
        return
    
    # 简单模式匹配
    keys_to_delete = []
    for key in _cache.keys():
        if _match_pattern(key, pattern):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del _cache[key]


def _match_pattern(key: str, pattern: str) -> bool:
    """简单的通配符匹配"""
    if pattern == '*':
        return True
    
    parts_pattern = pattern.split('*')
    parts_key = key.split(':')
    
    # 简化处理：只支持末尾通配符
    if pattern.endswith('*'):
        prefix = pattern[:-1]
        return key.startswith(prefix)
    
    return key == pattern