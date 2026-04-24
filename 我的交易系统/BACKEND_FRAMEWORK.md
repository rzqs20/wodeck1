# 个人看盘指标系统 - 后端框架设计

## 项目结构概览

```
backend/
├── config/          # 配置模块
├── models/          # 数据模型层
├── services/        # 业务逻辑层
├── controllers/     # 控制器层
├── routes/          # 路由层
├── middleware/      # 中间件
├── utils/           # 工具函数
├── indicators/      # 指标计算引擎
└── app.py           # 应用入口
```

---

## 1. 配置模块 (config/)

### config/database.py

- `get_database_config()` - 获取数据库配置信息
- `create_engine_instance()` - 创建数据库引擎实例
- `get_session_factory()` - 获取会话工厂

### config/settings.py

- `load_settings()` - 加载应用配置
- `get_api_config()` - 获取API配置
- `get_indicator_config()` - 获取指标配置

---

## 2. 数据模型层 (models/)

### models/user.py

- `User` - 用户模型类
  - 字段: id, username, email, password_hash, created_at
  - 方法: `set_password()`, `verify_password()`, `to_dict()`

### models/indicator.py

- `Indicator` - 指标定义模型类
  - 字段: id, name, description, formula, parameters, user_id, created_at, updated_at
  - 方法: `to_dict()`, `validate_parameters()`

### models/stock_data.py

- `StockData` - 股票数据模型类
  - 字段: id, stock_code, date, open, high, low, close, volume, timestamp
  - 方法: `to_dict()`, `calculate_returns()`

### models/user_indicator.py

- `UserIndicator` - 用户自定义指标关联模型
  - 字段: id, user_id, indicator_id, custom_parameters, is_active, created_at
  - 方法: `to_dict()`, `update_parameters()`

### models/watchlist.py

- `Watchlist` - 自选股列表模型类
  - 字段: id, user_id, name, stock_codes, created_at, updated_at
  - 方法: `to_dict()`, `add_stock()`, `remove_stock()`

---

## 3. 业务逻辑层 (services/)

### services/auth_service.py

- `register_user(username, email, password)` - 注册用户
- `login_user(username, password)` - 用户登录
- `logout_user(user_id)` - 用户登出
- `generate_token(user_id)` - 生成JWT令牌
- `verify_token(token)` - 验证JWT令牌
- `get_current_user(token)` - 获取当前用户信息
- `update_user_profile(user_id, profile_data)` - 更新用户资料
- `change_password(user_id, old_password, new_password)` - 修改密码

### services/indicator_service.py

- `create_indicator(user_id, name, description, formula, parameters)` - 创建新指标
- `get_indicator(indicator_id)` - 获取指标详情
- `get_user_indicators(user_id)` - 获取用户所有指标
- `update_indicator(indicator_id, update_data)` - 更新指标
- `delete_indicator(indicator_id)` - 删除指标
- `validate_formula(formula)` - 验证指标公式合法性
- `parse_parameters(parameters)` - 解析指标参数

### services/indicator_calculation_service.py

- `calculate_indicator(stock_code, indicator_name, parameters, start_date, end_date)` - 计算指定指标
- `calculate_multiple_indicators(stock_code, indicator_list, start_date, end_date)` - 批量计算多个指标
- `get_historical_data(stock_code, start_date, end_date)` - 获取历史行情数据
- `cache_indicator_result(cache_key, result, ttl)` - 缓存指标计算结果
- `get_cached_result(cache_key)` - 获取缓存的指标结果
- `clear_cache(pattern)` - 清除缓存

### services/stock_data_service.py

- `fetch_stock_data(stock_code, start_date, end_date)` - 从外部API获取股票数据
- `save_stock_data(stock_data_list)` - 保存股票数据到数据库
- `get_stock_data(stock_code, start_date, end_date)` - 查询股票数据
- `update_stock_data(stock_code)` - 更新最新股票数据
- `get_latest_price(stock_code)` - 获取最新价格
- `batch_fetch_data(stock_codes)` - 批量获取多只股票数据

### services/watchlist_service.py

- `create_watchlist(user_id, name, stock_codes)` - 创建自选股列表
- `get_watchlists(user_id)` - 获取用户所有自选股列表
- `get_watchlist(watchlist_id)` - 获取指定自选股列表
- `update_watchlist(watchlist_id, update_data)` - 更新自选股列表
- `delete_watchlist(watchlist_id)` - 删除自选股列表
- `add_stock_to_watchlist(watchlist_id, stock_code)` - 添加股票到自选列表
- `remove_stock_from_watchlist(watchlist_id, stock_code)` - 从自选列表移除股票
- `get_watchlist_indicators(watchlist_id)` - 获取自选股的指标数据

### services/alert_service.py

- `create_alert(user_id, stock_code, indicator_name, condition, threshold)` - 创建预警规则
- `get_user_alerts(user_id)` - 获取用户所有预警规则
- `update_alert(alert_id, update_data)` - 更新预警规则
- `delete_alert(alert_id)` - 删除预警规则
- `check_alerts()` - 检查所有预警条件
- `send_alert_notification(user_id, alert_info)` - 发送预警通知

---

## 4. 指标计算引擎 (indicators/)

### indicators/base_indicator.py

- `BaseIndicator` - 指标基类
  - 方法: `calculate(data, parameters)` - 计算指标（抽象方法）
  - 方法: `validate_parameters(parameters)` - 验证参数
  - 方法: `get_name()` - 获取指标名称
  - 方法: `get_description()` - 获取指标描述

### indicators/technical_indicators.py

- `MAIndicator` - 移动平均线指标
  - 方法: `calculate(data, period)` - 计算MA
- `EMAIndicator` - 指数移动平均线指标
  - 方法: `calculate(data, period)` - 计算EMA
- `MACDIndicator` - MACD指标
  - 方法: `calculate(data, fast_period, slow_period, signal_period)` - 计算MACD
- `RSIIndicator` - 相对强弱指标
  - 方法: `calculate(data, period)` - 计算RSI
- `BOLLIndicator` - 布林带指标
  - 方法: `calculate(data, period, std_dev)` - 计算布林带
- `KDJIndicator` - KDJ指标
  - 方法: `calculate(data, n, m1, m2)` - 计算KDJ

### indicators/custom_indicator_engine.py

- `CustomIndicatorEngine` - 自定义指标引擎
  - 方法: `register_indicator(name, formula_func)` - 注册自定义指标
  - 方法: `execute_formula(formula, data, parameters)` - 执行自定义公式
  - 方法: `validate_custom_formula(formula)` - 验证自定义公式安全性
  - 方法: `get_registered_indicators()` - 获取所有已注册指标

### indicators/indicator_registry.py

- `IndicatorRegistry` - 指标注册中心
  - 方法: `register(indicator_class)` - 注册指标类
  - 方法: `get_indicator(name)` - 获取指标实例
  - 方法: `get_all_indicators()` - 获取所有可用指标
  - 方法: `unregister(name)` - 注销指标

---

## 5. 控制器层 (controllers/)

### controllers/auth_controller.py

- `register(request)` - 处理用户注册请求
- `login(request)` - 处理用户登录请求
- `logout(request)` - 处理用户登出请求
- `get_profile(request)` - 获取用户资料
- `update_profile(request)` - 更新用户资料
- `change_password(request)` - 修改密码

### controllers/indicator_controller.py

- `create_indicator(request)` - 创建新指标
- `get_indicator(request, indicator_id)` - 获取指标详情
- `list_indicators(request)` - 获取指标列表
- `update_indicator(request, indicator_id)` - 更新指标
- `delete_indicator(request, indicator_id)` - 删除指标
- `calculate_indicator(request)` - 计算指标值
- `batch_calculate(request)` - 批量计算指标

### controllers/stock_controller.py

- `get_stock_data(request, stock_code)` - 获取股票数据
- `search_stocks(request)` - 搜索股票
- `get_stock_detail(request, stock_code)` - 获取股票详情
- `refresh_stock_data(request, stock_code)` - 刷新股票数据

### controllers/watchlist_controller.py

- `create_watchlist(request)` - 创建自选股列表
- `get_watchlists(request)` - 获取自选股列表
- `get_watchlist(request, watchlist_id)` - 获取指定自选股列表
- `update_watchlist(request, watchlist_id)` - 更新自选股列表
- `delete_watchlist(request, watchlist_id)` - 删除自选股列表
- `add_stock(request, watchlist_id)` - 添加股票
- `remove_stock(request, watchlist_id)` - 移除股票

### controllers/alert_controller.py

- `create_alert(request)` - 创建预警规则
- `get_alerts(request)` - 获取预警规则列表
- `update_alert(request, alert_id)` - 更新预警规则
- `delete_alert(request, alert_id)` - 删除预警规则
- `test_alert(request, alert_id)` - 测试预警规则

---

## 6. 路由层 (routes/)

### routes/auth_routes.py

- `register_auth_routes(app)` - 注册认证相关路由
  - POST /api/auth/register
  - POST /api/auth/login
  - POST /api/auth/logout
  - GET /api/auth/profile
  - PUT /api/auth/profile
  - PUT /api/auth/password

### routes/indicator_routes.py

- `register_indicator_routes(app)` - 注册指标相关路由
  - POST /api/indicators
  - GET /api/indicators
  - GET /api/indicators/<id>
  - PUT /api/indicators/<id>
  - DELETE /api/indicators/<id>
  - POST /api/indicators/calculate
  - POST /api/indicators/batch-calculate

### routes/stock_routes.py

- `register_stock_routes(app)` - 注册股票数据相关路由
  - GET /api/stocks/<code>
  - GET /api/stocks/search
  - GET /api/stocks/<code>/detail
  - POST /api/stocks/<code>/refresh

### routes/watchlist_routes.py

- `register_watchlist_routes(app)` - 注册自选股相关路由
  - POST /api/watchlists
  - GET /api/watchlists
  - GET /api/watchlists/<id>
  - PUT /api/watchlists/<id>
  - DELETE /api/watchlists/<id>
  - POST /api/watchlists/<id>/stocks
  - DELETE /api/watchlists/<id>/stocks/<code>

### routes/alert_routes.py

- `register_alert_routes(app)` - 注册预警相关路由
  - POST /api/alerts
  - GET /api/alerts
  - PUT /api/alerts/<id>
  - DELETE /api/alerts/<id>
  - POST /api/alerts/<id>/test

---

## 7. 中间件 (middleware/)

### middleware/auth_middleware.py

- `token_required(f)` - JWT令牌验证装饰器
- `admin_required(f)` - 管理员权限验证装饰器
- `extract_user_from_token(request)` - 从请求中提取用户信息

### middleware/error_handler.py

- `handle_validation_error(error)` - 处理验证错误
- `handle_authentication_error(error)` - 处理认证错误
- `handle_not_found_error(error)` - 处理404错误
- `handle_internal_error(error)` - 处理内部服务器错误
- `register_error_handlers(app)` - 注册错误处理器

### middleware/rate_limiter.py

- `rate_limit(limit, period)` - 速率限制装饰器
- `check_rate_limit(key, limit, period)` - 检查速率限制
- `reset_rate_limit(key)` - 重置速率限制

### middleware/request_logger.py

- `log_request(request)` - 记录请求日志
- `log_response(response, duration)` - 记录响应日志
- `register_logger_middleware(app)` - 注册日志中间件

---

## 8. 工具函数 (utils/)

### utils/response.py

- `success_response(data, message, status_code)` - 成功响应格式化
- `error_response(message, status_code, errors)` - 错误响应格式化
- `pagination_response(data, total, page, per_page)` - 分页响应格式化

### utils/validators.py

- `validate_email(email)` - 验证邮箱格式
- `validate_stock_code(code)` - 验证股票代码格式
- `validate_date_range(start_date, end_date)` - 验证日期范围
- `validate_indicator_parameters(parameters)` - 验证指标参数

### utils/cache.py

- `init_cache(config)` - 初始化缓存
- `get_cache(key)` - 获取缓存
- `set_cache(key, value, ttl)` - 设置缓存
- `delete_cache(key)` - 删除缓存
- `clear_pattern(pattern)` - 按模式清除缓存

### utils/logger.py

- `setup_logger(name, level)` - 设置日志器
- `get_logger(name)` - 获取日志器
- `log_api_call(endpoint, method, user_id)` - 记录API调用
- `log_indicator_calculation(indicator_name, duration)` - 记录指标计算

### utils/helpers.py

- `format_date(date_obj, format_str)` - 格式化日期
- `parse_query_params(request, schema)` - 解析查询参数
- `generate_cache_key(prefix, *args)` - 生成缓存键
- `async_wrapper(func)` - 异步函数包装器

---

## 9. 应用入口 (app.py)

### 主应用函数

- `create_app(config_name)` - 创建Flask应用实例
- `register_blueprints(app)` - 注册所有蓝图
- `register_extensions(app)` - 注册扩展（数据库、缓存等）
- `register_middlewares(app)` - 注册中间件
- `configure_cors(app)` - 配置CORS
- `setup_scheduler(app)` - 设置定时任务调度器

### 定时任务

- `schedule_stock_data_update()` - 定时更新股票数据
- `schedule_alert_check()` - 定时检查预警条件
- `schedule_cache_cleanup()` - 定时清理过期缓存

### 应用启动

- `run_development()` - 运行开发环境
- `run_production()` - 运行生产环境

---

## 核心设计原则

### 高内聚体现：

1. **每个模块职责单一**：config只负责配置，models只负责数据结构，services只负责业务逻辑
2. **指标计算独立封装**：indicators模块完全独立，可单独测试和扩展
3. **服务层细分**：auth、indicator、stock、watchlist、alert各自独立

### 低耦合体现：

1. **依赖注入**：通过参数传递依赖，而非硬编码
2. **接口抽象**：BaseIndicator提供统一接口，具体指标实现解耦
3. **注册中心模式**：IndicatorRegistry统一管理指标，避免直接依赖
4. **中间件分离**：认证、日志、限流等横切关注点独立
5. **路由与控制器分离**：routes只负责URL映射，controllers只负责请求处理

### 扩展性设计：

1. **新增指标**：只需继承BaseIndicator并注册
2. **新增功能模块**：添加新的service、controller、routes即可
3. **更换数据源**：只需修改stock_data_service的实现
4. **添加缓存策略**：通过cache工具函数统一处理

---

## 技术栈建议

- **Web框架**: Flask / FastAPI
- **数据库**: PostgreSQL / MySQL + SQLAlchemy ORM
- **缓存**: Redis
- **认证**: JWT
- **任务调度**: APScheduler / Celery
- **数据获取**: akshare / tushare / yfinance
- **部署**: Gunicorn + Nginx
