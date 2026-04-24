# 个人看盘指标系统 - 后端框架

## 项目概述

这是一个高内聚低耦合的后端框架，用于个人看盘指标网站。提供了完整的RESTful API接口，支持用户管理、技术指标计算、自选股管理、预警系统等功能。

## 项目结构

```
backend/
├── config/              # 配置模块
│   ├── database.py      # 数据库配置
│   └── settings.py      # 应用配置
├── models/              # 数据模型层
│   ├── user.py          # 用户模型
│   ├── indicator.py     # 指标模型
│   ├── stock_data.py    # 股票数据模型
│   ├── user_indicator.py # 用户指标关联模型
│   └── watchlist.py     # 自选股模型
├── services/            # 业务逻辑层
│   ├── auth_service.py           # 认证服务
│   ├── indicator_service.py      # 指标管理服务
│   ├── indicator_calculation_service.py  # 指标计算服务
│   ├── stock_data_service.py     # 股票数据服务
│   ├── watchlist_service.py      # 自选股服务
│   └── alert_service.py          # 预警服务
├── controllers/         # 控制器层
│   ├── auth_controller.py        # 认证控制器
│   ├── indicator_controller.py   # 指标控制器
│   ├── stock_controller.py       # 股票控制器
│   ├── watchlist_controller.py   # 自选股控制器
│   └── alert_controller.py       # 预警控制器
├── routes/              # 路由层
│   ├── auth_routes.py            # 认证路由
│   ├── indicator_routes.py       # 指标路由
│   ├── stock_routes.py           # 股票路由
│   ├── watchlist_routes.py       # 自选股路由
│   └── alert_routes.py           # 预警路由
├── middleware/          # 中间件
│   ├── auth_middleware.py        # 认证中间件
│   ├── error_handler.py          # 错误处理
│   ├── rate_limiter.py           # 速率限制
│   └── request_logger.py         # 请求日志
├── utils/               # 工具函数
│   ├── response.py      # 响应格式化
│   ├── validators.py    # 数据验证
│   ├── cache.py         # 缓存操作
│   ├── logger.py        # 日志工具
│   └── helpers.py       # 辅助函数
├── indicators/          # 指标计算引擎
│   ├── base_indicator.py         # 指标基类
│   ├── technical_indicators.py   # 技术指标实现
│   ├── custom_indicator_engine.py # 自定义指标引擎
│   └── indicator_registry.py     # 指标注册中心
├── app.py               # 应用入口
└── requirements.txt     # 依赖包列表
```

## 核心特性

### 1. 高内聚设计

- **模块化分层**：config、models、services、controllers、routes各司其职
- **指标引擎独立**：indicators模块完全封装，支持扩展
- **服务细分**：auth、indicator、stock、watchlist、alert独立服务

### 2. 低耦合架构

- **依赖注入**：通过参数传递依赖
- **接口抽象**：BaseIndicator提供统一接口
- **注册中心模式**：IndicatorRegistry统一管理指标
- **中间件分离**：横切关注点独立

### 3. 可扩展性

- **新增指标**：继承BaseIndicator并注册即可
- **新增模块**：添加service + controller + routes
- **更换数据源**：只修改stock_data_service
- **缓存策略**：通过utils/cache统一处理

## 技术栈

- **Web框架**: Flask
- **数据库**: PostgreSQL / MySQL + SQLAlchemy ORM
- **缓存**: Redis
- **认证**: JWT (PyJWT)
- **任务调度**: APScheduler
- **数据获取**: akshare / tushare / yfinance
- **部署**: Gunicorn + Nginx

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建`.env`文件：

```env
# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=stock_indicator
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password

# 应用配置
SECRET_KEY=your-secret-key
FLASK_ENV=development

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. 初始化数据库

```python
from config.database import create_engine_instance
from models.user import User
from models.indicator import Indicator
# ... 导入其他模型

# 创建所有表
engine = create_engine_instance()
Base.metadata.create_all(engine)
```

### 4. 运行应用

```bash
python app.py
```

开发服务器将在 `http://localhost:5000` 启动

## API接口文档

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户资料
- `PUT /api/auth/profile` - 更新用户资料
- `PUT /api/auth/password` - 修改密码

### 指标接口

- `POST /api/indicators` - 创建新指标
- `GET /api/indicators` - 获取指标列表
- `GET /api/indicators/<id>` - 获取指标详情
- `PUT /api/indicators/<id>` - 更新指标
- `DELETE /api/indicators/<id>` - 删除指标
- `POST /api/indicators/calculate` - 计算指标值
- `POST /api/indicators/batch-calculate` - 批量计算指标

### 股票接口

- `GET /api/stocks/<code>` - 获取股票历史数据
- `GET /api/stocks/search` - 搜索股票
- `GET /api/stocks/<code>/detail` - 获取股票详情
- `POST /api/stocks/<code>/refresh` - 刷新股票数据

### 自选股接口

- `POST /api/watchlists` - 创建自选列表
- `GET /api/watchlists` - 获取所有自选列表
- `GET /api/watchlists/<id>` - 获取指定自选列表
- `PUT /api/watchlists/<id>` - 更新自选列表
- `DELETE /api/watchlists/<id>` - 删除自选列表
- `POST /api/watchlists/<id>/stocks` - 添加股票
- `DELETE /api/watchlists/<id>/stocks/<code>` - 移除股票
- `GET /api/watchlists/<id>/with-indicators` - 获取带指标的自选列表

### 预警接口

- `POST /api/alerts` - 创建预警规则
- `GET /api/alerts` - 获取所有预警规则
- `PUT /api/alerts/<id>` - 更新预警规则
- `DELETE /api/alerts/<id>` - 删除预警规则
- `POST /api/alerts/<id>/test` - 测试预警规则

## 开发指南

### 添加新的技术指标

1. 在`indicators/technical_indicators.py`中创建新类：

```python
class MyCustomIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(name="MYINDICATOR", description="我的自定义指标")

    def calculate(self, data, parameters):
        # 实现计算逻辑
        pass
```

2. 在`indicators/indicator_registry.py`的`initialize_default_indicators()`中注册：

```python
registry.register(MyCustomIndicator)
```

### 添加新的业务模块

1. 创建服务层：`services/new_module_service.py`
2. 创建控制器：`controllers/new_module_controller.py`
3. 创建路由：`routes/new_module_routes.py`
4. 在`app.py`的`register_blueprints()`中注册路由

### 实现具体功能

每个函数都包含详细的docstring说明，包括：

- 参数说明（Args）
- 返回值说明（Returns）
- 异常说明（Raises）
- 注意事项（Note）

你只需要将`pass`替换为具体实现即可。

## 注意事项

1. **安全性**：
   - 所有密码必须哈希存储
   - 使用HTTPS生产环境
   - 实施速率限制防止滥用
   - 验证所有用户输入

2. **性能优化**：
   - 使用缓存减少重复计算
   - 批量操作数据库
   - 异步处理耗时任务
   - 定期清理过期数据

3. **错误处理**：
   - 统一的错误响应格式
   - 详细的日志记录
   - 优雅的错误恢复

4. **代码规范**：
   - 遵循PEP 8编码规范
   - 使用类型注解（可选）
   - 编写单元测试
   - 保持函数单一职责

## 许可证

本项目仅供个人学习和使用。

## 联系方式

如有问题或建议，欢迎反馈。
