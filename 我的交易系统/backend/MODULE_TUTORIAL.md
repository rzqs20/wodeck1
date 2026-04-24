# 个人看盘指标系统 - 模块功能详解教程

## 📚 目录

1. [配置模块 (config/)](#1-配置模块-config)
2. [数据模型层 (models/)](#2-数据模型层-models)
3. [业务逻辑层 (services/)](#3-业务逻辑层-services)
4. [控制器层 (controllers/)](#4-控制器层-controllers)
5. [路由层 (routes/)](#5-路由层-routes)
6. [中间件层 (middleware/)](#6-中间件层-middleware)
7. [工具函数层 (utils/)](#7-工具函数层-utils)
8. [指标计算引擎 (indicators/)](#8-指标计算引擎-indicators)
9. [应用入口 (app.py)](#9-应用入口-apppy)
10. [数据流转示例](#10-数据流转示例)

---

## 1. 配置模块 (config/)

### 🎯 核心职责

**统一管理所有配置信息，让应用在不同环境下都能正常运行。**

### 📁 包含文件

#### `database.py` - 数据库配置

**作用：** 管理数据库连接的所有细节

**为什么需要它？**

- 避免在代码中硬编码数据库密码
- 方便切换开发/生产环境的数据库
- 集中管理连接池参数

**主要函数：**

```python
get_database_config()      # 返回数据库连接信息（主机、端口、用户名、密码等）
create_engine_instance()   # 创建SQLAlchemy引擎（管理数据库连接池）
get_session_factory()      # 创建会话工厂（用于数据库操作）
```

**实际应用场景：**

- 开发环境：连接本地MySQL
- 生产环境：连接云服务器PostgreSQL
- 测试环境：使用SQLite内存数据库

---

#### `settings.py` - 应用配置

**作用：** 管理应用的各项设置

**为什么需要它？**

- API密钥、加密密钥等敏感信息统一管理
- 不同环境使用不同配置（调试模式开关等）
- 第三方服务配置集中存放

**主要函数：**

```python
load_settings()            # 从环境变量或配置文件加载所有设置
get_api_config()           # 获取API相关配置（速率限制、CORS等）
get_indicator_config()     # 获取指标计算相关配置（缓存时间、精度等）
```

**配置项示例：**

```python
{
    "app_name": "看盘指标系统",
    "debug": True,                    # 开发环境开启调试
    "secret_key": "xxx",              # JWT加密密钥
    "environment": "development",     # 运行环境
    "api_rate_limit": 100,            # API限流
    "cache_ttl": 3600,                # 缓存过期时间
}
```

---

## 2. 数据模型层 (models/)

### 🎯 核心职责

**定义数据结构，相当于数据库表的"蓝图"。只负责数据长什么样，不处理业务逻辑。**

### 📁 包含文件

#### `user.py` - 用户模型

**作用：** 定义用户数据的结构

**字段说明：**

- `id`: 用户唯一标识
- `username`: 用户名
- `email`: 邮箱地址
- `password_hash`: 加密后的密码（不是明文！）
- `created_at`: 注册时间

**方法说明：**

```python
set_password(password)      # 将明文密码加密后存储
verify_password(password)   # 验证密码是否正确
to_dict()                   # 转换为字典格式（用于JSON响应）
```

**为什么要加密密码？**

- 安全性：即使数据库泄露，黑客也拿不到明文密码
- 使用bcrypt算法，不可逆加密

---

#### `indicator.py` - 指标定义模型

**作用：** 定义技术指标的元数据

**字段说明：**

- `id`: 指标唯一标识
- `name`: 指标名称（如"MA"、"MACD"）
- `description`: 指标描述
- `formula`: 计算公式（字符串或函数引用）
- `parameters`: 默认参数字典 `{"period": 20}`
- `user_id`: 创建者ID
- `created_at`: 创建时间

**使用场景：**

- 系统内置指标：MA、EMA、MACD等
- 用户自定义指标：保存用户的公式和参数

---

#### `stock_data.py` - 股票数据模型

**作用：** 定义股票行情数据的结构

**字段说明：**

- `stock_code`: 股票代码（如"600000.SH"）
- `date`: 交易日期
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量

**方法说明：**

```python
calculate_returns()    # 计算收益率 = (今日收盘价 - 昨日收盘价) / 昨日收盘价
```

**数据存储策略：**

- 历史数据持久化到数据库
- 最新数据定期更新
- 支持按日期范围查询

---

#### `user_indicator.py` - 用户指标关联模型

**作用：** 记录用户使用哪些指标，以及自定义的参数

**为什么需要这个表？**

- 一个用户可以有多个指标
- 一个指标可以被多个用户使用
- 每个用户可以为同一个指标设置不同的参数

**字段说明：**

- `user_id`: 用户ID
- `indicator_id`: 指标ID
- `custom_parameters`: 用户自定义参数 `{"period": 30}`（覆盖默认值）
- `is_active`: 是否激活该指标

**实际例子：**

```
用户A: MA指标，周期=20
用户B: MA指标，周期=50
→ 两个用户使用同一个指标，但参数不同
```

---

#### `watchlist.py` - 自选股列表模型

**作用：** 管理用户的自选股

**字段说明：**

- `user_id`: 用户ID
- `name`: 列表名称（如"关注列表"、"科技股"）
- `stock_codes`: 股票代码列表 `["600000.SH", "000001.SZ"]`

**方法说明：**

```python
add_stock(stock_code)      # 添加股票到列表
remove_stock(stock_code)   # 从列表移除股票
```

**使用场景：**

- 用户可以创建多个自选列表
- 每个列表可以有多只股票
- 快速查看多只股票的指标

---

## 3. 业务逻辑层 (services/)

### 🎯 核心职责

**实现核心业务逻辑，是整个系统的"大脑"。处理数据验证、业务规则、调用外部API等。**

### 📁 包含文件

#### `auth_service.py` - 认证服务

**作用：** 处理用户注册、登录、令牌管理等

**核心流程：**

**注册流程：**

```python
register_user(username, email, password)
↓
1. 验证用户名格式（长度、特殊字符等）
2. 验证邮箱格式
3. 检查用户名/邮箱是否已存在
4. 密码强度验证（至少8位，包含字母和数字）
5. 密码加密（bcrypt）
6. 创建User对象并保存到数据库
7. 返回用户ID
```

**登录流程：**

```python
login_user(username, password)
↓
1. 根据用户名查找用户
2. 验证密码（对比哈希值）
3. 生成JWT令牌（包含用户ID和过期时间）
4. 返回令牌和用户信息
```

**JWT令牌是什么？**

- JSON Web Token，一种无状态的身份验证方式
- 包含用户ID、过期时间等信息
- 使用密钥签名，防止篡改
- 前端每次请求都要携带这个令牌

---

#### `indicator_service.py` - 指标管理服务

**作用：** 管理指标的增删改查

**核心功能：**

```python
create_indicator(user_id, name, formula, parameters)
↓
1. 验证指标名称唯一性
2. 验证公式合法性（语法检查）
3. 验证参数格式
4. 创建Indicator对象
5. 保存到数据库
6. 注册到指标注册中心
```

**为什么需要验证公式？**

- 防止恶意代码注入
- 确保公式语法正确
- 避免运行时错误

---

#### `indicator_calculation_service.py` - 指标计算服务

**作用：** 执行指标计算，管理缓存

**核心流程：**

```python
calculate_indicator(stock_code, indicator_name, parameters, start_date, end_date)
↓
1. 生成缓存键：f"{stock_code}_{indicator_name}_{parameters}"
2. 检查缓存是否存在 → 存在则直接返回
3. 获取历史数据（调用stock_data_service）
4. 从注册中心获取指标实例
5. 执行指标计算
6. 缓存结果（设置TTL）
7. 返回计算结果
```

**缓存的重要性：**

- 指标计算耗时（特别是复杂指标）
- 同一股票+同一指标+同一参数 = 相同结果
- 缓存可以避免重复计算
- 提升响应速度（从秒级降到毫秒级）

---

#### `stock_data_service.py` - 股票数据服务

**作用：** 从外部API获取股票数据，管理数据存储

**数据获取流程：**

```python
fetch_stock_data(stock_code, start_date, end_date)
↓
1. 选择数据源（akshare/tushare/yfinance）
2. 调用API获取数据
3. 处理API限流（等待重试）
4. 数据清洗（处理缺失值、异常值）
5. 格式标准化（统一为内部格式）
6. 返回StockData对象列表
```

**数据更新策略：**

```python
update_stock_data(stock_code)
↓
1. 获取数据库中最新日期
2. 从API获取该日期之后的新数据
3. 增量更新（只插入新数据）
4. 避免重复存储
```

**支持的API：**

- **akshare**: 免费，数据全面，适合A股
- **tushare**: 需要积分，数据质量高
- **yfinance**: 适合美股、港股

---

#### `watchlist_service.py` - 自选股服务

**作用：** 管理用户的自选股列表

**核心功能：**

```python
add_stock_to_watchlist(watchlist_id, stock_code)
↓
1. 验证自选列表是否存在
2. 验证股票代码格式
3. 检查股票是否已在列表中（去重）
4. 添加到stock_codes列表
5. 更新updated_at时间戳
6. 保存到数据库
```

**批量获取指标：**

```python
get_watchlist_indicators(watchlist_id)
↓
1. 获取自选列表中的所有股票代码
2. 对每只股票计算指定指标
3. 汇总结果
4. 返回格式化数据（便于前端展示表格）
```

---

#### `alert_service.py` - 预警服务

**作用：** 管理预警规则，定期检查条件

**预警规则示例：**

```python
create_alert(user_id, stock_code, indicator_name, condition, threshold)
# 当MA(20) > 50时发送通知
{
    "stock_code": "600000.SH",
    "indicator_name": "MA",
    "condition": ">",
    "threshold": 50
}
```

**条件类型：**

- `>`: 大于
- `<`: 小于
- `>=`: 大于等于
- `<=`: 小于等于
- `==`: 等于
- `cross_above`: 上穿（从下往上突破）
- `cross_below`: 下穿（从上往下突破）

**定时检查流程：**

```python
check_alerts()
↓
1. 获取所有激活的预警规则
2. 对每条规则：
   a. 获取最新股票数据
   b. 计算对应指标
   c. 判断条件是否满足
   d. 如果满足 → 发送通知
   e. 记录触发日志
3. 标记已触发的规则（避免重复通知）
```

**通知方式（可扩展）：**

- 邮件通知
- 短信通知
- 微信推送
- App推送

---

## 4. 控制器层 (controllers/)

### 🎯 核心职责

**处理HTTP请求，充当"翻译官"角色。接收前端请求 → 调用服务层 → 返回响应。**

### 📁 包含文件

#### `auth_controller.py` - 认证控制器

**作用：** 处理用户认证相关的HTTP请求

**请求处理流程：**

```python
POST /api/auth/register
↓
1. 从request.json提取数据
2. 验证必填字段（username, email, password）
3. 调用auth_service.register_user()
4. 捕获异常（用户名重复、邮箱格式错误等）
5. 返回成功/失败响应
```

**示例代码结构：**

```python
def register(request):
    # 1. 提取数据
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 2. 验证数据
    if not all([username, email, password]):
        return error_response("缺少必填字段", 400)

    # 3. 调用服务
    try:
        result = register_user(username, email, password)
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), 400)
```

---

#### `indicator_controller.py` - 指标控制器

**作用：** 处理指标管理的HTTP请求

**关键区别：**

- 需要认证（使用`@token_required`装饰器）
- 从令牌中提取当前用户
- 权限控制（只能操作自己的指标）

**示例：**

```python
@token_required
def create_indicator(current_user, request):
    # current_user由装饰器注入
    user_id = current_user.id

    # 调用服务时传入user_id
    result = create_indicator(user_id, name, formula, parameters)
    return success_response(result)
```

---

#### `stock_controller.py` - 股票控制器

**作用：** 处理股票数据查询请求

**特点：**

- 支持查询参数（start_date, end_date, limit）
- 数据量可能很大，需要分页
- 可能需要实时刷新数据

---

#### `watchlist_controller.py` - 自选股控制器

**作用：** 处理自选股管理请求

**典型请求：**

```
POST /api/watchlists          # 创建列表
GET /api/watchlists           # 获取所有列表
POST /api/watchlists/1/stocks # 向列表1添加股票
DELETE /api/watchlists/1/stocks/600000.SH  # 移除股票
```

---

#### `alert_controller.py` - 预警控制器

**作用：** 处理预警规则管理请求

**特殊功能：**

```python
test_alert(alert_id)
# 测试预警规则是否正常工作
# 不实际触发通知，只返回是否会触发
```

---

## 5. 路由层 (routes/)

### 🎯 核心职责

**定义URL与控制器函数的映射关系。告诉Flask："当用户访问这个URL时，调用哪个函数"。**

### 📁 包含文件

#### `auth_routes.py` - 认证路由

**作用：** 注册认证相关的URL

**路由定义：**

```python
POST /api/auth/register  →  auth_controller.register
POST /api/auth/login     →  auth_controller.login
POST /api/auth/logout    →  auth_controller.logout
GET  /api/auth/profile   →  auth_controller.get_profile
PUT  /api/auth/profile   →  auth_controller.update_profile
PUT  /api/auth/password  →  auth_controller.change_password
```

**为什么用Blueprint？**

- 模块化组织路由
- 统一URL前缀（`/api/auth`）
- 便于大型项目管理

---

#### `indicator_routes.py` - 指标路由

**路由定义：**

```python
POST   /api/indicators             →  创建指标
GET    /api/indicators             →  获取指标列表
GET    /api/indicators/<id>        →  获取单个指标
PUT    /api/indicators/<id>        →  更新指标
DELETE /api/indicators/<id>        →  删除指标
POST   /api/indicators/calculate   →  计算指标
POST   /api/indicators/batch-calculate →  批量计算
```

**RESTful设计原则：**

- GET: 查询数据（幂等，无副作用）
- POST: 创建资源
- PUT: 更新资源
- DELETE: 删除资源

---

#### 其他路由文件

- `stock_routes.py`: 股票数据路由
- `watchlist_routes.py`: 自选股路由
- `alert_routes.py`: 预警路由

---

## 6. 中间件层 (middleware/)

### 🎯 核心职责

**在请求到达控制器之前或响应返回之后执行的"拦截器"。处理横切关注点（认证、日志、限流等）。**

### 📁 包含文件

#### `auth_middleware.py` - 认证中间件

**作用：** 验证JWT令牌，保护需要认证的接口

**装饰器工作原理：**

```python
@token_required
def my_route(current_user):
    # current_user已经被注入
    pass
```

**执行流程：**

```
请求到达
↓
提取Authorization头中的令牌
↓
验证令牌有效性（签名、过期时间）
↓
从令牌中提取用户ID
↓
查询用户信息
↓
将用户对象注入到视图函数
↓
如果令牌无效 → 返回401错误
```

---

#### `error_handler.py` - 错误处理中间件

**作用：** 统一处理异常，返回友好的错误信息

**处理的异常类型：**

```python
ValidationError (400)      # 参数验证失败
AuthenticationError (401)  # 认证失败
PermissionError (403)      # 权限不足
NotFoundError (404)        # 资源不存在
InternalError (500)        # 服务器内部错误
```

**统一错误响应格式：**

```json
{
  "success": false,
  "message": "错误消息",
  "errors": ["详细错误信息"]
}
```

**好处：**

- 前端统一处理错误
- 不暴露敏感信息（如堆栈跟踪）
- 便于调试和日志记录

---

#### `rate_limiter.py` - 速率限制中间件

**作用：** 防止API被滥用（DDoS攻击、爬虫等）

**限流策略：**

```python
@rate_limit(limit=100, period=3600)
# 每小时最多100次请求
```

**实现原理：**

```
1. 以IP地址为key
2. 记录请求次数和时间窗口
3. 超过限制 → 返回429错误
4. 时间窗口结束后重置计数
```

**生产环境建议：**

- 使用Redis存储（分布式限流）
- 不同接口不同限制
  - 登录接口：更严格（防暴力破解）
  - 数据查询：较宽松

---

#### `request_logger.py` - 请求日志中间件

**作用：** 记录每个请求的详细信息

**记录的日志：**

```python
{
    "timestamp": "2024-01-01 12:00:00",
    "method": "GET",
    "endpoint": "/api/stocks/600000.SH",
    "ip": "192.168.1.100",
    "user_id": 123,
    "status_code": 200,
    "duration": 0.123  # 秒
}
```

**用途：**

- 性能监控（找出慢接口）
- 安全审计（追踪异常行为）
- 故障排查（重现问题）

---

## 7. 工具函数层 (utils/)

### 🎯 核心职责

**提供通用工具函数，被其他模块复用。避免重复造轮子。**

### 📁 包含文件

#### `response.py` - 响应工具

**作用：** 统一API响应格式

**为什么需要统一格式？**

- 前端可以统一处理响应
- 减少前端代码复杂度
- 提高可维护性

**响应格式：**

```python
# 成功响应
success_response(data={"id": 1}, message="创建成功")
→ {
    "success": true,
    "message": "创建成功",
    "data": {"id": 1}
}

# 错误响应
error_response(message="参数错误", errors=["email格式不正确"])
→ {
    "success": false,
    "message": "参数错误",
    "errors": ["email格式不正确"]
}

# 分页响应
pagination_response(data=[...], total=100, page=1, per_page=10)
→ {
    "success": true,
    "data": [...],
    "pagination": {
        "total": 100,
        "page": 1,
        "per_page": 10,
        "total_pages": 10
    }
}
```

---

#### `validators.py` - 验证器

**作用：** 提供常用数据验证函数

**验证函数：**

```python
validate_email(email)         # 验证邮箱格式
validate_stock_code(code)     # 验证股票代码（600000.SH）
validate_date_range(start, end) # 验证日期范围
validate_indicator_parameters(params) # 验证指标参数
```

**使用示例：**

```python
if not validate_email(email):
    raise ValueError("邮箱格式不正确")

if not validate_stock_code(code):
    raise ValueError("股票代码格式不正确，应为：600000.SH")
```

---

#### `cache.py` - 缓存工具

**作用：** 提供统一的缓存操作接口

**缓存策略：**

```python
# 设置缓存（1小时过期）
set_cache("ma_600000_20", result, ttl=3600)

# 获取缓存
result = get_cache("ma_600000_20")
if result is None:
    # 缓存未命中，重新计算
    result = calculate_ma(...)
    set_cache("ma_600000_20", result, ttl=3600)

# 清除缓存（数据更新时）
delete_cache("ma_600000_*")  # 通配符清除
```

**缓存键命名规范：**

```
{指标名}_{股票代码}_{参数}
例如：ma_600000_20, macd_000001_12_26_9
```

---

#### `logger.py` - 日志工具

**作用：** 统一管理日志记录

**日志级别：**

```python
DEBUG    # 调试信息（开发环境）
INFO     # 一般信息
WARNING  # 警告信息
ERROR    # 错误信息
CRITICAL # 严重错误
```

**日志内容：**

```python
log_api_call(endpoint, method, user_id, status_code, duration)
log_indicator_calculation(indicator_name, stock_code, duration)
```

**日志文件：**

```
logs/
├── app.log           # 应用日志
├── api_calls.log     # API调用日志
└── indicators.log    # 指标计算日志
```

---

#### `helpers.py` - 辅助工具

**作用：** 提供各种小工具函数

**常用函数：**

```python
format_date(date_obj, "%Y-%m-%d")       # 格式化日期
parse_query_params(request, schema)      # 解析查询参数
generate_cache_key("ma", "600000", 20)   # 生成缓存键
async_wrapper(func)                      # 异步包装器
```

---

## 8. 指标计算引擎 (indicators/)

### 🎯 核心职责

**核心的指标计算逻辑。采用面向对象设计，易于扩展新指标。**

### 📁 包含文件

#### `base_indicator.py` - 指标基类

**作用：** 定义所有指标的抽象基类

**设计模式：** 模板方法模式

**为什么需要基类？**

- 统一接口：所有指标都有`calculate()`方法
- 代码复用：公共逻辑放在基类
- 强制规范：子类必须实现`calculate()`方法

**抽象方法：**

```python
class BaseIndicator(ABC):
    @abstractmethod
    def calculate(self, data, parameters):
        """子类必须实现此方法"""
        pass

    def validate_parameters(self, parameters):
        """可选：验证参数"""
        pass
```

---

#### `technical_indicators.py` - 技术指标实现

**作用：** 实现常用的技术分析指标

**实现的指标：**

**1. MA（移动平均线）**

```python
MAIndicator().calculate(data, period=20)
# 计算20日移动平均线
# 公式：MA = (C1 + C2 + ... + Cn) / n
```

**2. EMA（指数移动平均线）**

```python
EMAIndicator().calculate(data, period=12)
# 对近期数据赋予更高权重
# 比MA更敏感
```

**3. MACD（平滑异同移动平均线）**

```python
MACDIndicator().calculate(data, fast=12, slow=26, signal=9)
# 返回：MACD线、信号线、柱状图
# 用于判断买卖时机
```

**4. RSI（相对强弱指标）**

```python
RSIIndicator().calculate(data, period=14)
# 范围：0-100
# >70: 超买，<30: 超卖
```

**5. BOLL（布林带）**

```python
BOLLIndicator().calculate(data, period=20, std_dev=2)
# 返回：上轨、中轨、下轨
# 价格触及上轨→可能回调，触及下轨→可能反弹
```

**6. KDJ（随机指标）**

```python
KDJIndicator().calculate(data, n=9, m1=3, m2=3)
# 返回：K值、D值、J值
# 用于短线交易
```

---

#### `custom_indicator_engine.py` - 自定义指标引擎

**作用：** 允许用户通过公式语言定义自己的指标

**使用场景：**

```python
# 用户自定义：双均线金叉
engine.register_indicator("MA_CROSS", lambda data: {
    ma5 = calculate_ma(data, 5)
    ma20 = calculate_ma(data, 20)
    return ma5 > ma20  # 金叉信号
})
```

**安全性考虑：**

```python
validate_custom_formula(formula)
# 禁止危险操作：os.system(), eval(), exec()
# 只允许数学运算和预定义函数
```

---

#### `indicator_registry.py` - 指标注册中心

**作用：** 单例模式，全局管理所有可用指标

**设计模式：** 注册中心模式 + 单例模式

**工作流程：**

```python
# 1. 注册指标
registry = IndicatorRegistry()
registry.register(MAIndicator)
registry.register(MACDIndicator)

# 2. 获取指标实例
ma = registry.get_indicator("MA")
macd = registry.get_indicator("MACD")

# 3. 计算指标
result = ma.calculate(data, period=20)
```

**为什么用注册中心？**

- 解耦：服务层不需要知道具体有哪些指标
- 动态扩展：新增指标只需注册，无需修改其他代码
- 统一管理：可以查询所有可用指标

---

## 9. 应用入口 (app.py)

### 🎯 核心职责

**Flask应用的工厂函数，负责组装所有组件。**

### 📄 核心函数

#### `create_app(config_name)` - 应用工厂

**作用：** 创建并配置Flask应用实例

**初始化顺序：**

```python
def create_app(config_name='development'):
    # 1. 创建Flask实例
    app = Flask(__name__)

    # 2. 加载配置
    settings = load_settings()
    app.config.from_object(settings)

    # 3. 注册扩展（数据库、CORS等）
    register_extensions(app)

    # 4. 注册蓝图（路由）
    register_blueprints(app)

    # 5. 注册中间件
    register_middlewares(app)

    # 6. 配置CORS
    configure_cors(app)

    # 7. 设置定时任务
    setup_scheduler(app)

    return app
```

**为什么用工厂模式？**

- 便于测试（可以创建多个应用实例）
- 支持多环境配置
- 延迟初始化（避免循环导入）

---

#### `register_blueprints(app)` - 注册蓝图

**作用：** 将所有路由模块注册到应用

```python
from routes.auth_routes import auth_bp
from routes.indicator_routes import indicator_bp
# ...

app.register_blueprint(auth_bp)
app.register_blueprint(indicator_bp)
# ...
```

---

#### `setup_scheduler(app)` - 定时任务

**作用：** 设置后台定时任务

**定时任务示例：**

```python
# 每天收盘后更新股票数据
scheduler.add_job(
    func=schedule_stock_data_update,
    trigger='cron',
    hour=15,
    minute=30
)

# 每分钟检查预警条件
scheduler.add_job(
    func=schedule_alert_check,
    trigger='interval',
    minutes=1
)

# 每小时清理过期缓存
scheduler.add_job(
    func=schedule_cache_cleanup,
    trigger='interval',
    hours=1
)
```

---

## 10. 数据流转示例

### 📊 完整请求流程

**场景：用户请求计算MA指标**

```
1. 前端发起请求
   POST /api/indicators/calculate
   Headers: Authorization: Bearer <jwt_token>
   Body: {
       "stock_code": "600000.SH",
       "indicator_name": "MA",
       "parameters": {"period": 20},
       "start_date": "2024-01-01",
       "end_date": "2024-01-31"
   }

2. 中间件拦截
   ├─ rate_limiter: 检查速率限制
   ├─ auth_middleware: 验证JWT令牌，提取用户信息
   └─ request_logger: 记录请求日志

3. 路由匹配
   routes/indicator_routes.py
   → 找到对应的控制器函数：calculate_indicator

4. 控制器处理
   controllers/indicator_controller.py
   ├─ 提取请求参数
   ├─ 验证参数合法性
   └─ 调用服务层

5. 服务层执行业务逻辑
   services/indicator_calculation_service.py
   ├─ 生成缓存键：ma_600000_20_2024-01-01_2024-01-31
   ├─ 检查缓存 → 未命中
   ├─ 调用stock_data_service获取历史数据
   ├─ 从注册中心获取MA指标实例
   ├─ 执行计算：ma.calculate(data, period=20)
   ├─ 缓存结果
   └─ 返回计算结果

6. 指标计算引擎
   indicators/technical_indicators.py
   └─ MAIndicator.calculate(data, period=20)
       └─ 遍历数据，计算20日移动平均

7. 数据服务层
   services/stock_data_service.py
   ├─ 检查数据库是否有缓存数据
   ├─ 如果没有 → 调用外部API（akshare）
   ├─ 保存数据到数据库
   └─ 返回StockData列表

8. 响应返回
   ├─ 控制器格式化响应
   ├─ utils.response.success_response()
   └─ 返回JSON给前端

9. 中间件后置处理
   └─ request_logger: 记录响应时间和状态码
```

---

### 🔄 模块依赖关系

```
app.py (应用入口)
  ↓
config/ (配置)
  ↓
middleware/ (中间件)
  ↓
routes/ (路由)
  ↓
controllers/ (控制器)
  ↓
services/ (业务逻辑)
  ↓
├─ models/ (数据模型)
├─ indicators/ (指标引擎)
└─ utils/ (工具函数)
```

**依赖方向：** 上层依赖下层，下层不依赖上层（单向依赖）

---

## 🎓 学习建议

### 初学者路线

1. **先理解数据模型**（models/）- 了解数据长什么样
2. **再看业务逻辑**（services/）- 了解如何处理数据
3. **然后看控制器**（controllers/）- 了解如何接收请求
4. **最后看路由和中间件** - 了解请求如何到达控制器

### 进阶学习

1. **研究设计模式**：工厂模式、单例模式、装饰器模式
2. **理解RESTful API**：HTTP方法、状态码、资源设计
3. **学习安全性**：JWT认证、密码加密、SQL注入防护
4. **性能优化**：缓存策略、数据库索引、异步处理

### 实践建议

1. 从一个简单功能开始实现（如用户注册）
2. 逐步添加功能（登录 → 指标管理 → 数据查询）
3. 边实现边测试（使用Postman或curl）
4. 阅读Flask官方文档，理解框架原理

---

## ❓ 常见问题

### Q1: 为什么要分层？

**A:**

- **可维护性**：修改某一层不影响其他层
- **可测试性**：可以单独测试每一层
- **可复用性**：服务层可以被多个控制器复用
- **职责清晰**：每层只做自己的事

### Q2: 什么时候用缓存？

**A:**

- 计算耗时的操作（指标计算）
- 频繁读取的数据（股票基本信息）
- 不经常变化的数据（指标定义）

### Q3: 如何扩展新指标？

**A:**

1. 创建新类继承`BaseIndicator`
2. 实现`calculate()`方法
3. 在`indicator_registry`中注册
4. 无需修改其他代码！

### Q4: 如何处理并发？

**A:**

- 使用Gunicorn多进程部署
- 数据库连接池管理
- Redis作为共享缓存
- 异步任务处理耗时操作

---

## 📖 推荐资源

- **Flask官方文档**: https://flask.palletsprojects.com/
- **SQLAlchemy文档**: https://docs.sqlalchemy.org/
- **RESTful API设计**: https://restfulapi.net/
- **JWT介绍**: https://jwt.io/introduction

---

**祝你学习愉快！有任何问题随时提问。** 🚀
