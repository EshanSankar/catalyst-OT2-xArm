# Catalyst OT-2 项目结构

这个文档描述了清理后的项目结构和各个组件的作用。

## 📁 核心目录结构

```
catalyst-OT2/
├── 📁 api/                          # 新的API系统
│   ├── litestar_app.py              # 主要的Litestar API应用
│   ├── simple_test_app.py           # 简化测试版本
│   ├── client_example.py            # 客户端使用示例
│   ├── config.py                    # API配置管理
│   └── README.md                    # API详细文档
│
├── 📁 backends/                     # 实验后端系统（正在使用）
│   ├── __init__.py                  # 包初始化文件
│   ├── base.py                      # 基础后端类
│   ├── cva_backend.py               # 循环伏安法后端
│   ├── peis_backend.py              # 电化学阻抗谱后端
│   ├── ocv_backend.py               # 开路电压后端
│   ├── cp_backend.py                # 恒电流后端
│   ├── lsv_backend.py               # 线性扫描伏安法后端
│   └── README.md                    # 后端系统文档
│
├── 📁 config/                       # 配置文件
│   ├── default_config.json          # 默认配置
│   ├── logging_config.yaml          # 日志配置
│   └── parameter_limits.json        # 参数限制
│
├── 📁 utils/                        # 工具模块
│   ├── data_processing.py           # 数据处理工具
│   ├── utils.py                     # 通用工具函数
│   └── validation.py                # 参数验证
│
├── 📁 tests/                        # 测试文件
│   ├── test_backends/               # 后端测试
│   ├── test_hardware/               # 硬件测试
│   ├── test_utils/                  # 工具测试
│   └── test_dispatch_integration.py # 集成测试
│
├── 📁 docs/                         # 文档
│   ├── api_reference.md             # API参考
│   ├── hardware_setup.md            # 硬件设置
│   └── installation.md              # 安装指南
│
├── 📁 labware/                      # 实验器具定义
│   ├── nis_15_wellplate_3895ul.json
│   ├── nis_2_wellplate_30000ul.json
│   ├── nis_8_reservoir_25000ul.json
│   └── nistall_4_tiprack_1ul.json
│
├── 📁 data/                         # 实验数据
│   ├── 20250419_000/
│   ├── 20250419_001/
│   └── 20250419_002/
│
└── 📁 scripts/                      # 脚本文件
    └── install.sh
```

## 🚀 核心文件

### 主要执行文件
- `dispatch.py` - 实验调度器（核心组件）
- `run_experiment.py` - 单个实验执行
- `run_workflow.py` - 工作流执行
- `start_api_server.py` - API服务器启动脚本

### API系统文件
- `start_api_windows.bat` - Windows一键启动脚本
- `test_api_windows.bat` - Windows测试脚本
- `simple_api_test.py` - 简单API测试
- `test_api.py` - 完整API测试

### 硬件控制文件
- `opentronsHTTPAPI_clientBuilder.py` - OT-2机器人控制
- `ot2-arduino.py` / `ot2_arduino.py` - Arduino控制
- `mock_opentrons.py` - 模拟硬件（测试用）

### 工作流和配置
- `json_to_prefect.py` - JSON到Prefect工作流转换
- `workflow_executor.py` - 工作流执行器
- `parsing.py` - 参数解析
- `generate_workflow.py` - 工作流生成
- `validate_workflow.py` - 工作流验证

### 示例和模板
- `cva_experiment.json` - CVA实验示例
- `electrochemical_workflow.json` - 电化学工作流示例
- `example_workflow.json` - 通用工作流示例
- `deck_configuration.json` - 甲板配置

### 依赖和部署
- `requirements.txt` - 完整依赖列表
- `requirements-api.txt` - API最小依赖
- `Dockerfile` / `Dockerfile.api` - Docker配置
- `docker-compose.api.yml` - Docker Compose配置
- `setup.py` / `setup.cfg` - Python包配置

## 📚 文档文件

### 快速开始指南
- `QUICK_START_API.md` - API快速开始
- `WINDOWS_SETUP_GUIDE.md` - Windows设置指南
- `README.md` - 项目主要说明

### 详细指南
- `WORKFLOW_GUIDE.md` - 工作流指南
- `OT2_WORKFLOW_GUIDE.md` - OT-2工作流指南
- `LABWARE_README.md` - 实验器具说明
- `DECK_CONFIGURATION_GUIDE.md` - 甲板配置指南

### 测试和开发
- `TEST_INSTRUCTIONS.md` - 测试说明
- `DEVICE_TESTING.md` - 设备测试
- `OT2_TESTING.md` - OT-2测试
- `PREFECT_INTEGRATION.md` - Prefect集成

## 🔧 已删除的重复文件

为了保持项目结构整洁，已删除以下重复或过时的文件：

### 旧的后端目录
- `backend/` - 旧的后端实现（已被 `backends/` 替代）

### 重复的运行脚本
- `run_demo_workflow*.py` - 演示脚本
- `run_workflow_*.py` - 各种工作流运行脚本

### 重复的测试文件
- `test_connections.py`
- `test_device_*.py`
- `test_real_*.py`
- `test_mock_workflow.py`

### 重复的配置文件
- `updated_*.json` - 更新版本的配置文件
- `canvas_ot2_workflow_*.json` - Canvas工作流文件
- `standard_*.json` - 标准配置文件

### 临时和备份文件
- `check_file_content.py`
- `test_import.py`
- `progress.md`
- `instruction.md`

## 🎯 使用建议

### 开发环境
1. 使用 `backends/` 目录中的后端类
2. 通过 `dispatch.py` 调度实验
3. 使用 `api/` 目录中的API系统接收远程JSON

### 生产环境
1. 在Windows实验室机器上运行 `start_api_windows.bat`
2. 使用 `simple_api_test.py` 验证功能
3. 通过HTTP POST发送JSON实验配置

### 测试
1. 使用 `tests/` 目录中的测试文件
2. 运行 `test_device_functionality.py` 测试硬件
3. 使用 `mock_opentrons.py` 进行模拟测试

这个清理后的结构更加清晰，避免了重复文件，便于维护和使用。
