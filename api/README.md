# Catalyst OT-2 Experiment API

这是一个基于Litestar的实时实验控制API，用于接收和处理从远程发送的JSON实验配置文件。

## 功能特性

- **实时JSON接收**: 从远程源接收实验配置JSON文件
- **异步实验执行**: 支持并发执行多个实验
- **状态监控**: 实时查询实验执行状态
- **批量处理**: 支持批量提交多个实验
- **结果管理**: 自动保存和管理实验结果
- **错误处理**: 完善的错误处理和日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 启动API服务器

```bash
# 使用默认设置启动
python start_api_server.py

# 自定义端口和主机
python start_api_server.py --host 0.0.0.0 --port 8080

# 开发模式（自动重载）
python start_api_server.py --reload --log-level DEBUG
```

### 2. 发送实验配置

使用客户端示例发送实验：

```bash
# 发送单个实验
python api/client_example.py --example single

# 发送批量实验
python api/client_example.py --example batch

# 查看实验状态
python api/client_example.py --example status
```

### 3. 直接使用HTTP API

#### 提交单个实验

```bash
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

#### 查询实验状态

```bash
curl http://localhost:8000/experiments/{experiment_id}
```

#### 列出所有实验

```bash
curl http://localhost:8000/experiments
```

## API端点

### POST /experiments
提交单个实验配置

**请求体**:
```json
{
  "uo_type": "CVA|PEIS|OCV|CP|LSV",
  "parameters": {
    // 实验参数
  },
  "metadata": {
    // 可选的元数据
  }
}
```

**响应**:
```json
{
  "status": "success",
  "experiment_id": "uuid",
  "message": "Experiment submitted successfully"
}
```

### GET /experiments/{experiment_id}
获取特定实验的状态

**响应**:
```json
{
  "status": "success",
  "experiment_id": "uuid",
  "data": {
    "status": "pending|running|completed|failed",
    "created_at": "2024-01-01T00:00:00",
    "completed_at": "2024-01-01T01:00:00",
    "result": {
      // 实验结果
    }
  }
}
```

### GET /experiments
列出所有实验

### POST /experiments/batch
批量提交多个实验

### GET /health
健康检查端点

## 实验类型和参数

### CVA (循环伏安法)
```json
{
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
    },
    "ot2_actions": [
      {
        "action": "pick_up_tip",
        "labware": "electrode_tip_rack",
        "well": "A1"
      }
    ]
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
    "dc_voltage": 0.0,
    "arduino_control": {
      "base0_temp": 30.0,
      "pump0_ml": 1.0,
      "ultrasonic0_ms": 2000
    }
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

## 配置管理

### 创建配置模板
```bash
python api/config.py --create-template config.json
```

### 验证配置文件
```bash
python api/config.py --validate config.json
```

### 环境变量配置
```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export OT2_IP=192.168.1.100
export ARDUINO_PORT=/dev/ttyUSB0
export LOG_LEVEL=DEBUG
export MOCK_MODE=false
```

## 开发和测试

### 运行测试
```bash
pytest tests/
```

### 代码格式化
```bash
black api/
isort api/
```

### 类型检查
```bash
mypy api/
```

## 部署

### Docker部署
```bash
# 构建镜像
docker build -t catalyst-ot2-api .

# 运行容器
docker run -p 8000:8000 catalyst-ot2-api
```

### 生产环境
```bash
# 使用多个worker进程
python start_api_server.py --workers 4 --host 0.0.0.0 --port 8000
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :8000
   # 或使用不同端口
   python start_api_server.py --port 8080
   ```

2. **设备连接失败**
   - 检查OT-2 IP地址是否正确
   - 确认Arduino串口连接
   - 使用mock模式进行测试

3. **实验执行失败**
   - 查看日志文件 `api_server.log`
   - 检查实验参数格式
   - 验证设备状态

### 日志查看
```bash
# 实时查看日志
tail -f api_server.log

# 查看错误日志
grep ERROR api_server.log
```

## 贡献

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

MIT License
