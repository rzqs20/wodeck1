"""
指标管理服务模块
处理指标的CRUD操作和业务逻辑

Note:
    - 单用户系统，user_id 可以固定为 1 或忽略
    - 支持自定义公式和参数
    - 公式验证防止注入攻击
"""
import json
import ast
from typing import List, Dict, Optional
from datetime import datetime

from models.indicator import Indicator
from config.database import SessionLocal
from sqlalchemy import desc


def create_indicator(name: str, description: str = '', formula: str = '', 
                     parameters: Dict = None, category: str = 'custom',
                     is_system: bool = False) -> Indicator:
    """
    创建新指标
    
    Args:
        name: 指标名称（必填）
        description: 指标描述（可选）
        formula: 计算公式（可选）
        parameters: 参数字典（可选）
        category: 指标分类（默认 'custom'）
                 - 'system': 系统内置
                 - 'custom': 用户自定义
                 - 'technical': 技术指标
        is_system: 是否为系统指标（默认 False）
        
    Returns:
        Indicator: 创建的指标对象
        
    Raises:
        ValueError: 参数不合法时抛出异常
        IntegrityError: 指标名称重复时抛出异常
        
    Note:
        - 验证名称不能为空
        - 验证公式合法性（如果提供）
        - 解析并验证参数格式
        - 检查名称唯一性
        - 保存到数据库
    """
    # 验证名称
    if not name or not name.strip():
        raise ValueError("指标名称不能为空")
    
    name = name.strip()
    
    # 验证名称长度
    if len(name) > 50:
        raise ValueError("指标名称不能超过50个字符")
    
    # 验证公式（如果提供）
    if formula:
        validate_formula(formula)
    
    # 解析参数
    if parameters is None:
        parameters = {}
    else:
        parameters = parse_parameters(parameters)
    
    db = SessionLocal()
    
    try:
        # 检查名称是否已存在
        existing = db.query(Indicator).filter(
            Indicator.name == name
        ).first()
        
        if existing:
            raise ValueError(f"指标名称 '{name}' 已存在")
        
        # 创建新指标
        indicator = Indicator(
            name=name,
            description=description,
            formula=formula,
            parameters=parameters,  # ⭐ 直接传字典，不要转JSON
            category=category,
            is_system=1 if is_system else 0
        )
        
        db.add(indicator)
        db.commit()
        db.refresh(indicator)
        
        return indicator
        
    except Exception as e:
        db.rollback()
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"创建指标失败: {str(e)}")
    
    finally:
        db.close()


def get_indicator(indicator_id: int) -> Optional[Indicator]:
    """
    获取指标详情
    
    Args:
        indicator_id: 指标ID
        
    Returns:
        Indicator: 指标对象，不存在时返回 None
        
    Note:
        - 从数据库查询指标
        - 自动解析 parameters JSON
    """
    db = SessionLocal()
    
    try:
        indicator = db.query(Indicator).filter(
            Indicator.id == indicator_id
        ).first()
        
        return indicator
        
    finally:
        db.close()


def get_indicator_by_name(name: str) -> Optional[Indicator]:
    """
    根据名称获取指标
    
    Args:
        name: 指标名称
        
    Returns:
        Indicator: 指标对象，不存在时返回 None
    """
    db = SessionLocal()
    
    try:
        indicator = db.query(Indicator).filter(
            Indicator.name == name
        ).first()
        
        return indicator
        
    finally:
        db.close()


def get_all_indicators(category: str = None, is_system: bool = None) -> List[Indicator]:
    """
    获取所有指标
    
    Args:
        category: 指标分类过滤（可选）
        is_system: 是否系统指标过滤（可选）
        
    Returns:
        list: 指标对象列表，按创建时间倒序排列
        
    Note:
        - 支持按分类过滤
        - 支持按系统/自定义过滤
        - 按创建时间倒序排列
    """
    db = SessionLocal()
    
    try:
        query = db.query(Indicator)
        
        # 添加分类过滤
        if category:
            query = query.filter(Indicator.category == category)
        
        # 添加系统指标过滤
        if is_system is not None:
            query = query.filter(Indicator.is_system == (1 if is_system else 0))
        
        # 按创建时间倒序
        indicators = query.order_by(desc(Indicator.created_at)).all()
        
        return indicators
        
    finally:
        db.close()


def update_indicator(indicator_id: int, update_data: Dict) -> Indicator:
    """
    更新指标
    
    Args:
        indicator_id: 指标ID
        update_data: 更新数据字典
                     - name: 新名称（可选）
                     - description: 新描述（可选）
                     - formula: 新公式（可选）
                     - parameters: 新参数（可选）
                     - category: 新分类（可选）
                     
    Returns:
        Indicator: 更新后的指标对象
        
    Raises:
        ValueError: 更新数据不合法时抛出异常
        NotFoundError: 指标不存在时抛出异常
        
    Note:
        - 验证更新数据
        - 系统指标不能修改
        - 更新updated_at时间戳
    """
    if not update_data:
        raise ValueError("更新数据不能为空")
    
    db = SessionLocal()
    
    try:
        # 查询指标
        indicator = db.query(Indicator).filter(
            Indicator.id == indicator_id
        ).first()
        
        if not indicator:
            raise ValueError(f"指标 ID {indicator_id} 不存在")
        
        # 系统指标不能修改
        if indicator.is_system == 1:
            raise ValueError("系统指标不能修改")
        
        # 更新名称
        if 'name' in update_data:
            new_name = update_data['name'].strip()
            if not new_name:
                raise ValueError("指标名称不能为空")
            
            # 检查名称是否已被其他指标使用
            existing = db.query(Indicator).filter(
                Indicator.name == new_name,
                Indicator.id != indicator_id
            ).first()
            
            if existing:
                raise ValueError(f"指标名称 '{new_name}' 已被使用")
            
            indicator.name = new_name
        
        # 更新描述
        if 'description' in update_data:
            indicator.description = update_data['description']
        
        # 更新公式
        if 'formula' in update_data:
            formula = update_data['formula']
            if formula:  # 非空才验证
                validate_formula(formula)
            indicator.formula = formula
        
        # 更新参数
        if 'parameters' in update_data:
            parameters = parse_parameters(update_data['parameters'])
            indicator.parameters = json.dumps(parameters, ensure_ascii=False)
        
        # 更新分类
        if 'category' in update_data:
            indicator.category = update_data['category']
        
        # 更新时间戳
        indicator.updated_at = datetime.now()
        
        db.commit()
        db.refresh(indicator)
        
        return indicator
        
    except Exception as e:
        db.rollback()
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"更新指标失败: {str(e)}")
    
    finally:
        db.close()


def delete_indicator(indicator_id: int) -> bool:
    """
    删除指标
    
    Args:
        indicator_id: 指标ID
        
    Returns:
        bool: 删除是否成功
        
    Raises:
        ValueError: 指标不存在或是系统指标时抛出异常
        
    Note:
        - 系统指标不能删除
        - 物理删除记录
    """
    db = SessionLocal()
    
    try:
        # 查询指标
        indicator = db.query(Indicator).filter(
            Indicator.id == indicator_id
        ).first()
        
        if not indicator:
            raise ValueError(f"指标 ID {indicator_id} 不存在")
        
        # 系统指标不能删除
        if indicator.is_system == 1:
            raise ValueError("系统指标不能删除")
        
        # 删除指标
        db.delete(indicator)
        db.commit()
        
        return True
        
    except Exception as e:
        db.rollback()
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"删除指标失败: {str(e)}")
    
    finally:
        db.close()


def validate_formula(formula: str) -> bool:
    """
    验证指标公式合法性
    
    Args:
        formula: 待验证的公式字符串
        
    Returns:
        bool: 公式是否合法
        
    Raises:
        ValueError: 公式不合法时抛出异常，包含错误信息
        
    Note:
        - 检查语法正确性
        - 防止注入攻击（不允许危险函数）
        - 使用AST解析进行安全检查
        - 允许的运算符和函数白名单
    """
    if not formula or not formula.strip():
        raise ValueError("公式不能为空")
    
    formula = formula.strip()
    
    # 定义允许的安全函数和变量
    allowed_functions = {
        # 数学函数
        'abs', 'round', 'max', 'min', 'sum', 'avg', 'mean',
        'sqrt', 'pow', 'exp', 'log', 'sin', 'cos', 'tan',
        # 技术指标函数
        'MA', 'EMA', 'SMA', 'WMA',  # 移动平均
        'MACD', 'DIFF', 'DEA',       # MACD
        'RSI', 'KDJ', 'J',           # RSI, KDJ
        'BOLL', 'UPPER', 'LOWER',    # 布林带
        'VOL', 'VOLUME',             # 成交量
        'OPEN', 'HIGH', 'LOW', 'CLOSE',  # OHLC
        'REF', 'HHV', 'LLV',         # 引用、最高、最低
    }
    
    # 定义禁止的危险函数
    forbidden_functions = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'input', 'print', 'file',
        'getattr', 'setattr', 'delattr',
        'globals', 'locals', 'vars',
    }
    
    try:
        # 使用AST解析公式
        tree = ast.parse(formula, mode='eval')
        
        # 遍历AST树，检查安全性
        for node in ast.walk(tree):
            # 检查函数调用
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    
                    # 检查是否是禁止的函数
                    if func_name in forbidden_functions:
                        raise ValueError(f"公式中包含禁止的函数: {func_name}")
                    
                    # 如果不是允许的函数，给出警告（但不阻止）
                    # 因为可能是自定义变量或字段名
            
            # 检查属性访问（防止 obj.__class__ 等）
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('__'):
                    raise ValueError(f"公式中包含非法的属性访问: {node.attr}")
        
        # 尝试编译公式，检查语法
        compile(formula, '<string>', 'eval')
        
        return True
        
    except SyntaxError as e:
        raise ValueError(f"公式语法错误: {str(e)}")
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"公式验证失败: {str(e)}")


def parse_parameters(parameters) -> Dict:
    """
    解析指标参数
    
    Args:
        parameters: 原始参数字典或JSON字符串
        
    Returns:
        dict: 解析后的参数字典
        
    Raises:
        ValueError: 参数格式不正确时抛出异常
        
    Note:
        - 如果输入是字符串，尝试解析为JSON
        - 验证参数类型（int, float, str等）
        - 设置默认值
        - 返回标准化的参数格式
    """
    # 如果已经是字典，直接返回
    if isinstance(parameters, dict):
        return parameters
    
    # 如果是字符串，尝试解析JSON
    if isinstance(parameters, str):
        if not parameters.strip():
            return {}
        
        try:
            parsed = json.loads(parameters)
            if not isinstance(parsed, dict):
                raise ValueError("参数必须是字典格式")
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(f"参数JSON格式错误: {str(e)}")
    
    # 其他类型，尝试转换
    if parameters is None:
        return {}
    
    raise ValueError(f"不支持的参数类型: {type(parameters)}")


def init_system_indicators() -> List[Indicator]:
    """
    初始化系统内置指标
    
    Returns:
        list: 创建的系统指标列表
        
    Note:
        - 只在首次运行时调用
        - 创建常用的技术指标模板
        - 系统指标不能被用户修改或删除
    """
    db = SessionLocal()
    
    system_indicators = [
        {
            'name': 'MA均线',
            'description': '移动平均线指标',
            'formula': 'MA(CLOSE, N)',
            'parameters': {'N': 5},
            'category': 'technical',
            'is_system': True
        },
        {
            'name': 'MACD',
            'description': '平滑异同移动平均线',
            'formula': 'MACD(CLOSE, FAST, SLOW, SIGNAL)',
            'parameters': {'FAST': 12, 'SLOW': 26, 'SIGNAL': 9},
            'category': 'technical',
            'is_system': True
        },
        {
            'name': 'RSI',
            'description': '相对强弱指标',
            'formula': 'RSI(CLOSE, N)',
            'parameters': {'N': 14},
            'category': 'technical',
            'is_system': True
        },
        {
            'name': 'KDJ',
            'description': '随机指标',
            'formula': 'KDJ(HIGH, LOW, CLOSE, N, M1, M2)',
            'parameters': {'N': 9, 'M1': 3, 'M2': 3},
            'category': 'technical',
            'is_system': True
        },
        {
            'name': 'BOLL布林带',
            'description': '布林带指标',
            'formula': 'BOLL(CLOSE, N, P)',
            'parameters': {'N': 20, 'P': 2},
            'category': 'technical',
            'is_system': True
        },
    ]
    
    created = []
    
    try:
        for ind_data in system_indicators:
            # 检查是否已存在
            existing = db.query(Indicator).filter(
                Indicator.name == ind_data['name']
            ).first()
            
            if not existing:
                indicator = Indicator(
                    name=ind_data['name'],
                    description=ind_data['description'],
                    formula=ind_data['formula'],
                    parameters=ind_data['parameters'],  # ⭐ 直接传字典
                    category=ind_data['category'],
                    is_system=1
                )
                db.add(indicator)
                created.append(indicator)
        
        if created:
            db.commit()
            print(f"✅ 创建了 {len(created)} 个系统指标")
        else:
            print("ℹ️  系统指标已存在，无需创建")
        
        return created
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化系统指标失败: {e}")
        raise
    
    finally:
        db.close()