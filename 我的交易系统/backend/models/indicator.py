"""
指标定义模型
定义技术指标的数据结构
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Indicator(Base):
    """
    指标定义模型类
    
    Attributes:
        id: 指标唯一标识
        name: 指标名称
        description: 指标描述
        formula: 指标计算公式（JSON格式或函数名）
        parameters: 指标参数字典（JSON格式）
        user_id: 创建用户ID（None表示系统内置指标）
        category: 指标分类（'technical'/'custom'）
        is_active: 是否激活
        created_at: 创建时间
        updated_at: 更新时间
        
    Methods:
        to_dict(): 转换为字典格式
        validate_parameters(): 验证参数合法性
        get_parameter_schema(): 获取参数schema
    """
    
    # 表名
    __tablename__ = 'indicators'
    
    # 字段定义
    id = Column(Integer, primary_key=True, autoincrement=True, comment='指标唯一标识')
    name = Column(String(50), nullable=False, unique=True, index=True, comment='指标名称')
    description = Column(Text, nullable=True, comment='指标描述')
    formula = Column(Text, nullable=True, comment='计算公式（JSON格式或函数名）')
    parameters = Column(JSON, nullable=False, comment='指标参数字典 {param_name: {type, default, min, max}}')
    category = Column(String(20), nullable=False, default='technical', comment='指标分类：technical/custom')
    is_system = Column(Integer, nullable=False, default=0, comment='是否系统指标：1-系统内置，0-用户自定义')
    is_active = Column(Integer, nullable=False, default=1, comment='是否激活：1-激活，0-禁用')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系定义
    # user = relationship("User", back_populates="indicators")
    
    def __init__(self, name, description, formula, parameters, category='technical', is_system=0):
        """
        初始化指标对象
        
        Args:
            name: 指标名称
            description: 指标描述
            formula: 计算公式（字符串或JSON）
            parameters: 参数字典，格式如下：
                       {
                           "period": {
                               "type": "int",
                               "default": 20,
                               "min": 1,
                               "max": 500,
                               "required": true
                           }
                       }
            category: 指标分类（'technical' 或 'custom'）
            is_system: 是否系统指标（0-用户自定义，1-系统内置）
            
        Raises:
            ValueError: 参数不合法时抛出异常
            TypeError: 参数类型错误时抛出异常
            
        Note:
            - 指标名称不能为空且必须唯一
            - 公式不能为空
            - 参数必须是指定的JSON格式
        """
        # 验证指标名称
        self._validate_name(name)
        
        # 验证公式
        self._validate_formula(formula)
        
        # 验证并标准化参数
        validated_params = self._validate_and_normalize_parameters(parameters)
        
        # 赋值
        self.name = name.strip()
        self.description = description.strip() if description else ''
        self.formula = formula
        self.parameters = validated_params
        self.category = category
        self.is_system = is_system
        self.is_active = 1
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def _validate_name(self, name):
        """
        验证指标名称
        
        Args:
            name: 指标名称
            
        Raises:
            ValueError: 名称不合法时抛出
        """
        if not name or not isinstance(name, str):
            raise ValueError("指标名称不能为空且必须为字符串")
        
        if len(name) > 50:
            raise ValueError("指标名称长度不能超过50个字符")
        
        # 只允许字母、数字、下划线、中文
        import re
        if not re.match(r'^[\w\u4e00-\u9fa5]+$', name):
            raise ValueError("指标名称只能包含字母、数字、下划线和中文")
    
    def _validate_formula(self, formula):
        """
        验证计算公式
        
        Args:
            formula: 计算公式（可以为空）
            
        Raises:
            ValueError: 公式不合法时抛出
        """
        # 允许公式为空
        if formula is None:
            return
        
        if not isinstance(formula, str):
            raise ValueError("计算公式必须为字符串")
        
        if len(formula) > 5000:
            raise ValueError("计算公式长度不能超过5000个字符")
    
    def _validate_and_normalize_parameters(self, parameters):
        """
        验证并标准化参数字典
        
        Args:
            parameters: 参数字典
            
        Returns:
            dict: 标准化后的参数字典
            
        Raises:
            ValueError: 参数不合法时抛出
            TypeError: 参数类型错误时抛出
        """
        if not isinstance(parameters, dict):
            raise TypeError("参数必须为字典类型")
        
        if len(parameters) == 0:
            # 允许无参数的指标
            return {}
        
        validated_params = {}
        
        for param_name, param_config in parameters.items():
            # 验证参数名
            if not isinstance(param_name, str) or not param_name.strip():
                raise ValueError(f"参数名必须为非空字符串: {param_name}")
            
            # 支持简单格式：{'N': 10} 自动转换为完整格式
            if not isinstance(param_config, dict):
                # 简单值，自动推断类型并生成完整配置
                param_config = self._auto_generate_param_config(param_name, param_config)
            
            # 标准化参数配置
            normalized = self._normalize_single_parameter(param_name, param_config)
            validated_params[param_name] = normalized
        
        return validated_params
    
    def _auto_generate_param_config(self, param_name, value):
        """
        根据值自动生成参数配置
        
        Args:
            param_name: 参数名
            value: 参数值
            
        Returns:
            dict: 完整的参数配置
        """
        # 推断类型
        if isinstance(value, bool):
            param_type = 'bool'
        elif isinstance(value, int):
            param_type = 'int'
        elif isinstance(value, float):
            param_type = 'float'
        elif isinstance(value, str):
            param_type = 'str'
        else:
            raise TypeError(f"不支持的参数类型: {type(value)}")
        
        # 生成默认配置
        config = {
            'type': param_type,
            'default': value,
        }
        
        # 根据类型添加合理的范围
        if param_type == 'int':
            config['min'] = max(0, value - 100)
            config['max'] = value + 100
        elif param_type == 'float':
            config['min'] = max(0.0, value - 10.0)
            config['max'] = value + 10.0
        
        return config
    
    def _normalize_single_parameter(self, param_name, param_config):
        """
        标准化单个参数配置
        
        Args:
            param_name: 参数名
            param_config: 参数配置
            
        Returns:
            dict: 标准化后的参数配置
        """
        # 必需字段
        if 'type' not in param_config:
            raise ValueError(f"参数 '{param_name}' 缺少必需字段 'type'")
        
        if 'default' not in param_config:
            raise ValueError(f"参数 '{param_name}' 缺少必需字段 'default'")
        
        # 支持的类型
        valid_types = ['int', 'float', 'str', 'bool']
        param_type = param_config['type']
        
        if param_type not in valid_types:
            raise ValueError(f"参数 '{param_name}' 的类型 '{param_type}' 不支持，支持的类型: {valid_types}")
        
        # 验证默认值类型
        default_value = param_config['default']
        if not self._check_value_type(default_value, param_type):
            raise TypeError(f"参数 '{param_name}' 的默认值类型错误，期望 {param_type}，实际 {type(default_value).__name__}")
        
        # 构建标准化配置
        normalized = {
            'type': param_type,
            'default': default_value,
            'required': param_config.get('required', False),
        }
        
        # 数值类型的范围验证
        if param_type in ['int', 'float']:
            if 'min' in param_config:
                normalized['min'] = param_config['min']
            if 'max' in param_config:
                normalized['max'] = param_config['max']
            
            # 验证范围合理性
            if 'min' in normalized and 'max' in normalized:
                if normalized['min'] > normalized['max']:
                    raise ValueError(f"参数 '{param_name}' 的最小值不能大于最大值")
        
        # 字符串类型的长度限制
        if param_type == 'str':
            if 'max_length' in param_config:
                normalized['max_length'] = param_config['max_length']
        
        return normalized
    
    def _check_value_type(self, value, expected_type):
        """
        检查值的类型是否符合预期
        
        Args:
            value: 待检查的值
            expected_type: 期望的类型字符串
            
        Returns:
            bool: 类型是否匹配
        """
        type_map = {
            'int': int,
            'float': (int, float),  # int也可以是float
            'str': str,
            'bool': bool,
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return False
        
        return isinstance(value, expected_python_type)
    
    def to_dict(self, include_schema=True):
        """
        将指标对象转换为字典格式
        
        Args:
            include_schema: 是否包含完整的参数schema（默认True）
                           False时只返回 {param_name: default_value}
            
        Returns:
            dict: 指标信息字典
                  - id: 指标ID
                  - name: 指标名称
                  - description: 描述
                  - formula: 公式
                  - parameters: 参数（根据include_schema决定格式）
                  - user_id: 用户ID
                  - category: 分类
                  - is_active: 是否激活
                  - created_at: 创建时间
                  - updated_at: 更新时间
                  
        Note:
            - 用于API响应序列化
            - 时间转换为字符串格式
        """
        # 处理参数格式
        if include_schema:
            # 完整schema格式
            params_output = self.parameters
        else:
            # 简化格式：{param_name: default_value}
            params_output = {
                name: config['default'] 
                for name, config in self.parameters.items()
            }
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'formula': self.formula,
            'parameters': params_output,
            'user_id': self.user_id,
            'category': self.category,
            'is_active': bool(self.is_active),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
    
    def validate_parameters(self, parameters):
        """
        验证指标参数的合法性
        
        Args:
            parameters: 待验证的参数字典 {param_name: value}
            
        Returns:
            dict: 验证结果
                  - valid: 是否合法
                  - errors: 错误信息列表
                  - normalized: 标准化后的参数（如果合法）
            
        Raises:
            ValueError: 参数结构严重错误时抛出
            
        Note:
            - 检查必需参数是否存在
            - 验证参数类型和范围
            - 对比定义的parameters schema
            - 返回详细的错误信息
        """
        if not isinstance(parameters, dict):
            raise TypeError("参数必须为字典类型")
        
        errors = []
        normalized = {}
        
        # 1. 检查必需参数
        for param_name, param_config in self.parameters.items():
            if param_config.get('required', False) and param_name not in parameters:
                errors.append(f"缺少必需参数: {param_name}")
        
        # 2. 验证提供的参数
        for param_name, value in parameters.items():
            # 检查参数是否在schema中定义
            if param_name not in self.parameters:
                errors.append(f"未定义的参数: {param_name}")
                continue
            
            param_config = self.parameters[param_name]
            
            # 验证类型
            if not self._check_value_type(value, param_config['type']):
                errors.append(f"参数 '{param_name}' 类型错误，期望 {param_config['type']}，实际 {type(value).__name__}")
                continue
            
            # 验证数值范围
            if param_config['type'] in ['int', 'float']:
                if 'min' in param_config and value < param_config['min']:
                    errors.append(f"参数 '{param_name}' 的值 {value} 小于最小值 {param_config['min']}")
                
                if 'max' in param_config and value > param_config['max']:
                    errors.append(f"参数 '{param_name}' 的值 {value} 大于最大值 {param_config['max']}")
            
            # 验证字符串长度
            if param_config['type'] == 'str' and 'max_length' in param_config:
                if len(value) > param_config['max_length']:
                    errors.append(f"参数 '{param_name}' 的长度超过限制 {param_config['max_length']}")
            
            # 添加到标准化结果
            normalized[param_name] = value
        
        # 3. 填充默认值
        for param_name, param_config in self.parameters.items():
            if param_name not in normalized:
                normalized[param_name] = param_config['default']
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'normalized': normalized if len(errors) == 0 else None,
        }
    
    def get_parameter_schema(self):
        """
        获取参数schema（用于前端表单生成）
        
        Returns:
            list: 参数schema列表
                  [
                      {
                          "name": "period",
                          "type": "int",
                          "default": 20,
                          "required": false,
                          "min": 1,
                          "max": 500,
                          "label": "周期"
                      }
                  ]
        """
        schema_list = []
        
        for param_name, param_config in self.parameters.items():
            schema = {
                'name': param_name,
                'type': param_config['type'],
                'default': param_config['default'],
                'required': param_config.get('required', False),
            }
            
            # 添加范围信息
            if 'min' in param_config:
                schema['min'] = param_config['min']
            if 'max' in param_config:
                schema['max'] = param_config['max']
            if 'max_length' in param_config:
                schema['max_length'] = param_config['max_length']
            
            schema_list.append(schema)
        
        return schema_list
    
    def is_system_indicator(self):
        """
        判断是否为系统内置指标
        
        Returns:
            bool: 是否为系统内置指标
        """
        return self.user_id is None
    
    def activate(self):
        """激活指标"""
        self.is_active = 1
        self.updated_at = datetime.now()
    
    def deactivate(self):
        """禁用指标"""
        self.is_active = 0
        self.updated_at = datetime.now()
    
    def update_formula(self, new_formula):
        """
        更新计算公式
        
        Args:
            new_formula: 新的计算公式
        """
        self._validate_formula(new_formula)
        self.formula = new_formula
        self.updated_at = datetime.now()
    
    def update_parameters(self, new_parameters):
        """
        更新参数定义
        
        Args:
            new_parameters: 新的参数定义
        """
        validated_params = self._validate_and_normalize_parameters(new_parameters)
        self.parameters = validated_params
        self.updated_at = datetime.now()
    
    def __repr__(self):
        """
        对象的字符串表示（用于调试）
        
        Returns:
            str: 对象描述
        """
        indicator_type = "系统" if self.is_system_indicator() else f"用户{self.user_id}"
        return f"<Indicator(id={self.id}, name='{self.name}', type={indicator_type})>"
    
    def __str__(self):
        """
        对象的友好字符串表示
        
        Returns:
            str: 友好的对象描述
        """
        param_count = len(self.parameters)
        return f"{self.name} | {self.description[:30]}... | {param_count}个参数"