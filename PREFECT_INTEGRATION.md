# Prefect集成指南

本文档介绍如何使用Prefect来管理和执行电化学实验工作流。

## 概述

Prefect是一个强大的工作流管理系统，它提供了以下优势：

1. **任务管理和监控**：
   - 可视化界面跟踪实验进度
   - 详细的任务执行历史
   - 错误通知和报告

2. **错误处理**：
   - 自动重试失败的任务
   - 条件分支处理不同情况
   - 人工干预机制

3. **灵活性**：
   - 支持复杂的工作流，如条件执行、并行任务等
   - 可以在不同环境（本地、AWS、Kubernetes等）运行

## 安装

1. 安装Prefect：

```bash
pip install prefect
```

2. （可选）启动Prefect服务器：

```bash
prefect server start
```

## 使用方法

### 1. 使用工作流执行器

最简单的方法是使用现有的`WorkflowExecutor`类，并启用Prefect支持：

```bash
python workflow_executor.py example_workflow.json --prefect
```

参数说明：
- `--prefect`：启用Prefect执行模式
- `--mock`：使用模拟模式（不连接实际设备）
- `--register`：注册工作流到Prefect服务器
- `--project`：指定Prefect项目名称（默认为"电化学实验"）

### 2. 直接使用Prefect执行器

也可以直接使用`PrefectWorkflowExecutor`类：

```bash
python prefect_workflow_executor.py example_workflow.json
```

参数说明：
- `--mock`：使用模拟模式（不连接实际设备）
- `--register`：注册工作流到Prefect服务器
- `--project`：指定Prefect项目名称（默认为"电化学实验"）

### 3. 测试Prefect集成

使用测试脚本测试Prefect集成：

```bash
python test_prefect_integration.py example_workflow.json
```

参数说明：
- `--no-mock`：不使用模拟模式（连接实际设备）
- `--direct`：直接使用PrefectWorkflowExecutor而不是通过WorkflowExecutor

## 工作流JSON格式

Prefect集成支持扩展的工作流JSON格式，增加了以下功能：

1. **实验序列**：
   ```json
   "sequence": ["ocv_experiment", "cva_experiment", "peis_experiment"]
   ```

2. **重试配置**：
   ```json
   "retry_count": 2,
   "retry_delay": 30
   ```

3. **人工干预**：
   ```json
   "requires_human_check": true,
   "human_message": "请检查CVA实验结果，确认是否继续执行PEIS实验"
   ```

4. **条件执行**：
   ```json
   "condition": {
     "type": "result_check",
     "experiment_id": "cva_experiment",
     "parameter": "peak_current",
     "operator": ">",
     "value": 0.001
   }
   ```

## 示例工作流

查看`example_workflow.json`文件，了解完整的工作流示例。

## Prefect UI

启动Prefect服务器后，可以通过浏览器访问Prefect UI：

```
http://localhost:4200
```

在UI中可以：
- 查看工作流执行状态
- 监控任务执行
- 重试失败的任务
- 查看日志和错误信息

## 故障排除

1. **导入错误**：
   - 确保已安装Prefect：`pip install prefect`
   - 确保所有Python文件都在同一目录或Python路径中

2. **连接错误**：
   - 使用`--mock`参数测试工作流，不连接实际设备
   - 检查设备连接配置

3. **执行错误**：
   - 查看日志文件：`prefect_integration_test.log`
   - 检查Prefect UI中的任务状态和错误信息
