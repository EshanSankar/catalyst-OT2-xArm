# Windows实验室机器设置指南

这个指南帮助你在Windows实验室机器上设置和运行Catalyst OT-2实验API。

## 🚀 快速开始

### 方法1: 使用批处理脚本（推荐）

1. **启动API服务器**
   ```cmd
   双击运行: start_api_windows.bat
   ```

2. **测试API功能**
   ```cmd
   双击运行: test_api_windows.bat
   ```

### 方法2: 手动命令行

1. **安装依赖**
   ```cmd
   python -m pip install litestar uvicorn pydantic aiohttp requests
   ```

2. **启动API服务器**
   ```cmd
   python start_api_server.py --host 127.0.0.1 --port 8000
   ```

3. **测试API**（在新的命令行窗口中）
   ```cmd
   python simple_api_test.py --wait
   ```

## 📋 系统要求

- Windows 10/11
- Python 3.7 或更高版本
- 网络连接（用于安装依赖）

## 🔧 详细设置步骤

### 1. 检查Python安装

打开命令提示符（cmd），运行：
```cmd
python --version
```

如果显示Python版本（如Python 3.9.x），则已安装。
如果提示"不是内部或外部命令"，需要安装Python。

### 2. 安装Python（如果需要）

1. 访问 https://www.python.org/downloads/
2. 下载最新的Python 3.x版本
3. 安装时**务必勾选"Add Python to PATH"**

### 3. 安装API依赖

```cmd
python -m pip install --upgrade pip
python -m pip install litestar uvicorn pydantic aiohttp requests
```

### 4. 配置硬件连接

编辑 `start_api_windows.bat` 文件，修改以下设置：

```batch
set OT2_IP=你的OT2机器人IP地址
set ARDUINO_PORT=你的Arduino串口（如COM3）
set MOCK_MODE=false
```

如果要使用模拟模式（不连接真实硬件）：
```batch
set MOCK_MODE=true
```

## 🧪 测试API功能

### 基本功能测试

1. **启动API服务器**
   ```cmd
   start_api_windows.bat
   ```

2. **运行测试**（在新窗口中）
   ```cmd
   python simple_api_test.py --wait
   ```

### 手动测试API端点

使用浏览器或curl测试：

1. **健康检查**
   ```
   http://127.0.0.1:8000/health
   ```

2. **API信息**
   ```
   http://127.0.0.1:8000/
   ```

3. **提交实验**（使用Postman或curl）
   ```cmd
   curl -X POST http://127.0.0.1:8000/experiments ^
     -H "Content-Type: application/json" ^
     -d "{\"uo_type\": \"CVA\", \"parameters\": {\"start_voltage\": \"-0.2V\", \"end_voltage\": \"1.0V\", \"scan_rate\": 0.05, \"cycles\": 1}}"
   ```

## 📡 发送实验配置

### 从远程计算机发送

如果API运行在IP地址为192.168.1.100的实验室机器上：

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

# 发送到实验室机器
response = requests.post(
    "http://192.168.1.100:8000/experiments",
    json=experiment
)

print(response.json())
```

### 使用客户端示例

```cmd
python api/client_example.py --url http://192.168.1.100:8000 --example single
```

## 🔍 故障排除

### 常见问题

1. **端口被占用**
   ```cmd
   netstat -ano | findstr :8000
   taskkill /PID <进程ID> /F
   ```

2. **Python不在PATH中**
   - 重新安装Python，确保勾选"Add to PATH"
   - 或手动添加Python到系统PATH

3. **依赖安装失败**
   ```cmd
   python -m pip install --upgrade pip
   python -m pip install --user litestar uvicorn pydantic
   ```

4. **防火墙阻止连接**
   - 在Windows防火墙中允许Python程序
   - 或临时关闭防火墙进行测试

5. **设备连接问题**
   - 检查OT-2 IP地址是否正确
   - 确认Arduino串口号（设备管理器中查看）
   - 使用MOCK_MODE=true进行测试

### 日志查看

API运行时会生成日志文件：
- `api_server.log` - API服务器日志
- 控制台输出 - 实时日志

### 网络配置

如果需要从其他机器访问API：

1. **修改启动配置**
   ```batch
   set API_HOST=0.0.0.0
   ```

2. **配置防火墙**
   - 允许端口8000的入站连接

3. **获取机器IP地址**
   ```cmd
   ipconfig
   ```

## 📊 性能监控

### 查看API状态
```cmd
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/experiments
```

### 监控实验执行
```python
import requests
import time

# 提交实验
response = requests.post("http://127.0.0.1:8000/experiments", json=experiment_data)
experiment_id = response.json()["experiment_id"]

# 监控状态
while True:
    status_response = requests.get(f"http://127.0.0.1:8000/experiments/{experiment_id}")
    status = status_response.json()["data"]["status"]
    print(f"实验状态: {status}")
    
    if status in ["completed", "failed"]:
        break
    
    time.sleep(5)
```

## 🚀 生产环境部署

### 作为Windows服务运行

1. 安装NSSM（Non-Sucking Service Manager）
2. 创建服务：
   ```cmd
   nssm install CatalystAPI python start_api_server.py
   nssm set CatalystAPI AppDirectory C:\path\to\catalyst-OT2
   nssm start CatalystAPI
   ```

### 开机自启动

将 `start_api_windows.bat` 添加到Windows启动文件夹：
```
Win+R -> shell:startup
```

## 📞 支持

如果遇到问题：

1. 检查日志文件 `api_server.log`
2. 运行 `python simple_api_test.py --wait` 进行诊断
3. 确认网络连接和硬件状态
4. 使用MOCK_MODE=true排除硬件问题
