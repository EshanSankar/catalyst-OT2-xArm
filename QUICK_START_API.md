# Catalyst OT-2 实验API - 快速启动指南

这个API解决了：**从remote监听并接收实时发送过来的JSON文件**。

## 🚀 快速开始

### Windows实验室机器（推荐）

```cmd
# 双击运行批处理脚本
start_api_windows.bat

# 测试API功能
test_api_windows.bat
```

### Linux/Mac或手动安装

```bash
# 安装API所需的依赖
pip install -r requirements-api.txt
# 或者
python install_api_dependencies.py
```

### 2. 启动API服务器

```bash
# 启动服务器（默认端口8000）
python start_api_server.py

# 或者自定义端口
python start_api_server.py --port 8080 --host 0.0.0.0
```

### 3. 测试API功能

```bash
# 运行API测试
python test_api.py --wait
```

## 📡 发送实验配置

### 方法1: 使用客户端示例

```bash
# 发送单个实验
python api/client_example.py --example single

# 发送批量实验
python api/client_example.py --example batch
```

### 方法2: 使用curl命令

```bash
# 发送CVA实验配置
curl -X POST http://localhost:8000/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "uo_type": "CVA",
    "parameters": {
      "start_voltage": "-0.2V",
      "end_voltage": "1.0V",
      "scan_rate": 0.05,
      "cycles": 3,
      "arduino_control": {
        "base0_temp": 25.0,
        "pump0_ml": 0.0,
        "ultrasonic0_ms": 0
      }
    }
  }'
```

### 方法3: 使用Python脚本

```python
import requests
import json

# 实验配置
experiment = {
    "uo_type": "CVA",
    "parameters": {
        "start_voltage": "-0.2V",
        "end_voltage": "1.0V",
        "scan_rate": 0.05,
        "cycles": 3,
        "arduino_control": {
            "base0_temp": 25.0,
            "pump0_ml": 0.0,
            "ultrasonic0_ms": 0
        }
    }
}

# 发送到API
response = requests.post(
    "http://localhost:8000/experiments",
    json=experiment
)

if response.status_code == 200:
    result = response.json()
    experiment_id = result['experiment_id']
    print(f"实验已提交，ID: {experiment_id}")
else:
    print(f"提交失败: {response.text}")
```

## 🔍 监控实验状态

```bash
# 查看特定实验状态
curl http://localhost:8000/experiments/{experiment_id}

# 查看所有实验
curl http://localhost:8000/experiments

# 健康检查
curl http://localhost:8000/health
```

## 📋 支持的实验类型

### CVA (循环伏安法)
```json
{
  "uo_type": "CVA",
  "parameters": {
    "start_voltage": "-0.2V",
    "end_voltage": "1.0V",
    "scan_rate": 0.05,
    "cycles": 3
  }
}
```

### PEIS (电化学阻抗谱)
```json
{
  "uo_type": "PEIS",
  "parameters": {
    "frequency_range": [0.1, 100000],
    "amplitude": 0.01,
    "dc_voltage": 0.0
  }
}
```

### OCV (开路电压)
```json
{
  "uo_type": "OCV",
  "parameters": {
    "duration": 300,
    "sampling_rate": 1.0
  }
}
```

### CP (恒电流)
```json
{
  "uo_type": "CP",
  "parameters": {
    "current": "1.0mA",
    "duration": 600
  }
}
```

### LSV (线性扫描伏安法)
```json
{
  "uo_type": "LSV",
  "parameters": {
    "start_voltage": "0.0V",
    "end_voltage": "1.0V",
    "scan_rate": 0.1
  }
}
```

## 🔧 配置选项

### 环境变量配置
```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export OT2_IP=100.67.89.154
export ARDUINO_PORT=COM3
export LOG_LEVEL=INFO
export MOCK_MODE=false
```

### 配置文件
```bash
# 创建配置模板
python api/config.py --create-template config.json

# 验证配置
python api/config.py --validate config.json
```

## 🐳 Docker部署

```bash
# 构建并启动
docker-compose -f docker-compose.api.yml up -d

# 查看日志
docker-compose -f docker-compose.api.yml logs -f
```

## 🔄 与现有代码的集成

这个API完全兼容现有的`dispatch.py`和后端代码：

1. **ExperimentDispatcher**: API使用相同的调度器
2. **后端类**: 支持所有现有的实验类型（CVA, PEIS, OCV, CP, LSV）
3. **参数格式**: 使用相同的JSON参数格式
4. **结果保存**: 使用相同的结果保存机制

## 🚨 故障排除

### 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8000

# 使用不同端口
python start_api_server.py --port 8080
```

### 依赖安装失败
```bash
# 手动安装关键依赖
pip install litestar uvicorn pydantic aiohttp

# 检查Python版本（需要3.7+）
python --version
```

### 设备连接问题
```bash
# 使用mock模式测试
export MOCK_MODE=true
python start_api_server.py
```

## 📊 API端点总览

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API信息 |
| `/health` | GET | 健康检查 |
| `/experiments` | POST | 提交单个实验 |
| `/experiments` | GET | 列出所有实验 |
| `/experiments/{id}` | GET | 获取实验状态 |
| `/experiments/batch` | POST | 批量提交实验 |

## 🎯 下一步

1. **启动API服务器**: `python start_api_server.py`
2. **测试基本功能**: `python test_api.py --wait`
3. **发送第一个实验**: `python api/client_example.py --example single`
4. **集成到你的工作流**: 使用HTTP POST发送JSON配置

现在可以从任何远程系统发送JSON实验配置到这个API，它会自动处理并执行实验！🎉
