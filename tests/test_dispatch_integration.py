#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
集成测试模块，用于测试experiment dispatch功能。
使用模拟(mock)对象来模拟硬件交互，验证dispatch.py的功能。
"""

import os
import sys
import json
import logging
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

# 添加项目根目录和测试目录到Python路径，确保可以导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 模拟boto3模块
sys.modules['boto3'] = MagicMock()
import boto3

# 导入测试用的模拟解析模块
import parsing

from dispatch import (
    ExperimentDispatcher, 
    LocalResultUploader, 
    S3ResultUploader, 
    validate_workflow_json,
    ResultUploader
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 捕获日志输出进行验证
class LogCapture:
    def __init__(self):
        self.handler = None
        self.log_output = StringIO()
    
    def __enter__(self):
        self.handler = logging.StreamHandler(self.log_output)
        logging.getLogger().addHandler(self.handler)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.handler:
            logging.getLogger().removeHandler(self.handler)
    
    def get_logs(self):
        return self.log_output.getvalue()


# 模拟后端类
class MockBackend:
    def __init__(self, config_path=None, result_uploader=None):
        self.config_path = config_path
        self.result_uploader = result_uploader
        self.device_connected = True
    
    def execute_experiment(self, uo):
        """模拟执行实验并返回结果"""
        experiment_id = uo.get('experiment_id', 'test_id')
        uo_type = uo.get('uo_type', 'UNKNOWN')
        
        # 根据实验类型返回不同的模拟结果
        if uo_type == "CVA":
            return {
                "status": "success",
                "data": {
                    "voltage": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                    "current": [0.001, 0.002, 0.003, 0.004, 0.005, 0.006]
                },
                "metadata": {
                    "cycles": uo.get("parameters", {}).get("cycles", 1),
                    "scan_rate": uo.get("parameters", {}).get("scan_rate", 0.05),
                }
            }
        elif uo_type == "PEIS":
            return {
                "status": "success",
                "data": {
                    "frequency": [100000, 10000, 1000, 100, 10, 1],
                    "z_real": [10, 15, 25, 50, 100, 200],
                    "z_imag": [-5, -10, -15, -20, -30, -40]
                }
            }
        else:
            return {
                "status": "success",
                "data": {"message": f"执行了 {uo_type} 实验"}
            }
    
    def disconnect_devices(self):
        """模拟断开设备连接"""
        self.device_connected = False
        return True


class TestExperimentDispatcher(unittest.TestCase):
    """ExperimentDispatcher的集成测试类"""
    
    def setUp(self):
        """每个测试前的设置"""
        # 创建临时目录用于存储结果
        self.temp_dir = tempfile.TemporaryDirectory()
        self.results_dir = self.temp_dir.name
        
        # 创建测试使用的上传器
        self.local_uploader = LocalResultUploader(self.results_dir)
        
        # 模拟实验参数
        self.test_experiment = {
            "uo_type": "CVA",
            "parameters": {
                "start_voltage": "0.0V",
                "end_voltage": "1.0V",
                "scan_rate": 0.05,
                "cycles": 3
            }
        }
    
    def tearDown(self):
        """每个测试后的清理"""
        self.temp_dir.cleanup()
    
    @patch('importlib.import_module')
    def test_experiment_execution(self, mock_import):
        """测试实验执行流程"""
        # 配置模拟导入模块，替换为我们的MockBackend
        mock_module = MagicMock()
        mock_module.CVABackend = MockBackend
        mock_import.return_value = mock_module
        
        # 创建带有本地上传器的调度器
        dispatcher = ExperimentDispatcher(
            result_uploader=self.local_uploader
        )
        
        # 使用日志捕获器记录日志输出
        with LogCapture() as log_capture:
            # 执行实验
            result = dispatcher.execute_experiment(self.test_experiment)
            
            # 验证结果
            self.assertEqual(result["status"], "success")
            self.assertIn("data", result)
            self.assertIn("voltage", result["data"])
            self.assertIn("current", result["data"])
            self.assertEqual(len(result["data"]["voltage"]), 6)
            self.assertEqual(len(result["data"]["current"]), 6)
            
            # 验证元数据
            self.assertIn("experiment_id", result)
            self.assertIn("uo_type", result)
            self.assertEqual(result["uo_type"], "CVA")
            self.assertIn("timestamp", result)
            
            # 验证日志输出
            logs = log_capture.get_logs()
            self.assertIn("Executing CVA experiment", logs)
            self.assertIn("Saved results to", logs)
            
            # 验证结果文件是否已创建
            result_dir = os.path.join(self.results_dir, result["experiment_id"])
            result_file = os.path.join(result_dir, "results.json")
            self.assertTrue(os.path.exists(result_dir))
            self.assertTrue(os.path.exists(result_file))
            
            # 验证保存的结果文件内容
            with open(result_file, 'r') as f:
                saved_result = json.load(f)
                self.assertEqual(saved_result["status"], "success")
        
        # 测试清理功能
        dispatcher.cleanup()
    
    @patch('importlib.import_module')
    def test_multiple_experiment_types(self, mock_import):
        """测试多种实验类型的执行"""
        # 配置模拟导入模块
        mock_module_cva = MagicMock()
        mock_module_cva.CVABackend = MockBackend
        
        mock_module_peis = MagicMock()
        mock_module_peis.PEISBackend = MockBackend
        
        # 不同的导入返回不同的模块
        def side_effect(name):
            if name == "cva_backend":
                return mock_module_cva
            elif name == "peis_backend":
                return mock_module_peis
            else:
                raise ImportError(f"No module named '{name}'")
        
        mock_import.side_effect = side_effect
        
        # 创建调度器
        dispatcher = ExperimentDispatcher(
            result_uploader=self.local_uploader
        )
        
        # 测试CVA实验
        cva_result = dispatcher.execute_experiment(self.test_experiment)
        self.assertEqual(cva_result["uo_type"], "CVA")
        
        # 测试PEIS实验
        peis_experiment = {
            "uo_type": "PEIS",
            "parameters": {
                "frequency_high": "100000 Hz",
                "frequency_low": "1 Hz",
                "points_per_decade": 10,
                "amplitude": "10 mV"
            }
        }
        
        peis_result = dispatcher.execute_experiment(peis_experiment)
        self.assertEqual(peis_result["uo_type"], "PEIS")
        self.assertIn("frequency", peis_result["data"])
        
        # 验证后端实例被重用
        self.assertEqual(len(dispatcher.backend_instances), 2)
        self.assertIn("CVA", dispatcher.backend_instances)
        self.assertIn("PEIS", dispatcher.backend_instances)
    
    def test_s3_result_uploader(self):
        """测试S3结果上传器"""
        # S3客户端已经被全局模拟，直接使用
        s3_client = boto3.client('s3')
        s3_client.put_object = MagicMock()
        
        # 创建S3上传器
        s3_uploader = S3ResultUploader(
            bucket="test-bucket",
            prefix="test-experiments"
        )
        
        # 模拟实验结果
        test_results = {
            "status": "success",
            "data": {"test": "data"},
            "experiment_id": "test_experiment"
        }
        
        # 测试上传
        result = s3_uploader.upload(test_results, "test_experiment")
        
        # 验证
        self.assertTrue(result)
        s3_client.put_object.assert_called_once()
        call_args = s3_client.put_object.call_args[1]
        self.assertEqual(call_args["Bucket"], "test-bucket")
        self.assertEqual(call_args["Key"], "test-experiments/test_experiment/results.json")
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"schema": "test"}')
    @patch('jsonschema.validate')
    def test_workflow_validation(self, mock_validate, mock_file):
        """测试工作流验证功能"""
        # 测试有效的工作流
        result = validate_workflow_json("valid_workflow.json")
        self.assertTrue(result)
        mock_validate.assert_called_once()
    
    def test_workflow_validation_missing_file(self):
        """测试工作流文件不存在的情况"""
        # 模拟open函数在打开工作流文件时抛出FileNotFoundError
        with patch('builtins.open') as mock_open:
            # 第一次调用open（打开schema文件）返回mock文件对象
            # 第二次调用open（打开工作流文件）抛出FileNotFoundError
            mock_open.side_effect = [
                mock_open().return_value,  # 返回模拟的schema文件
                FileNotFoundError("No such file or directory")  # 工作流文件不存在
            ]
            
            # 模拟json.load返回一个schema对象
            with patch('json.load', return_value={"schema": "test"}):
                # 验证应该抛出ValueError
                with self.assertRaises(ValueError) as context:
                    validate_workflow_json("missing_workflow.json")
                
                # 验证错误信息内容
                self.assertIn("Workflow file", str(context.exception))
                self.assertIn("not found", str(context.exception))
    
    @patch('jsonschema.validate')
    def test_workflow_validation_invalid(self, mock_validate):
        """测试无效工作流验证"""
        # 配置模拟验证函数抛出异常
        from jsonschema.exceptions import ValidationError
        mock_validate.side_effect = ValidationError("Invalid workflow: missing required field")
        
        # 使用当前目录下的测试文件
        test_file = os.path.join(os.path.dirname(__file__), "invalid_workflow.json")
        test_schema = os.path.join(os.path.dirname(__file__), "workflow_schema.json")
        
        # 确保测试文件存在
        self.assertTrue(os.path.exists(test_file), f"测试文件不存在: {test_file}")
        self.assertTrue(os.path.exists(test_schema), f"Schema文件不存在: {test_schema}")
        
        # 模拟打开文件和加载JSON
        with patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}'):
            with patch('json.load', return_value={"test": "data"}):
                # 验证应该失败并抛出ValueError
                with self.assertRaises(ValueError) as context:
                    validate_workflow_json(test_file, test_schema)
                
                # 验证错误信息
                self.assertIn("Validation error", str(context.exception))
    
    @patch('importlib.import_module')
    def test_error_handling(self, mock_import):
        """测试错误处理"""
        # 模拟导入错误
        mock_import.side_effect = ImportError("Module not found")
        
        # 创建调度器
        dispatcher = ExperimentDispatcher()
        
        # 测试不存在的实验类型
        invalid_experiment = {
            "uo_type": "INVALID_TYPE",
            "parameters": {}
        }
        
        result = dispatcher.execute_experiment(invalid_experiment)
        self.assertEqual(result["status"], "error")
        self.assertIn("message", result)
        self.assertIn("Unknown experiment type", result["message"])
        
        # 测试有效类型但后端模块不存在
        valid_experiment = {
            "uo_type": "CVA",
            "parameters": {}
        }
        
        result = dispatcher.execute_experiment(valid_experiment)
        self.assertEqual(result["status"], "error")
        self.assertIn("message", result)
    
    def test_parsing_integration(self):
        """测试与解析模块的集成"""
        # 测试CVA参数解析
        cva_experiment = {
            "uo_type": "CVA",
            "parameters": {
                "start_voltage": "0.5V",
                "end_voltage": "1.2V"
            }
        }
        
        parsed = parsing.parse_experiment_parameters(cva_experiment)
        self.assertEqual(parsed["parameters"]["start_voltage"], 0.5)
        self.assertEqual(parsed["parameters"]["end_voltage"], 1.2)
        
        # 测试PEIS参数解析
        peis_experiment = {
            "uo_type": "PEIS",
            "parameters": {
                "frequency_high": "10000 Hz",
                "frequency_low": "0.1 Hz"
            }
        }
        
        parsed = parsing.parse_experiment_parameters(peis_experiment)
        self.assertEqual(parsed["parameters"]["frequency_high"], 10000.0)
        self.assertEqual(parsed["parameters"]["frequency_low"], 0.1)
    
    @patch('importlib.import_module')
    def test_custom_result_uploader(self, mock_import):
        """测试自定义结果上传器"""
        # 创建自定义上传器
        mock_uploader = MockResultUploader()
        
        # 配置模拟模块
        mock_module = MagicMock()
        mock_module.CVABackend = MockBackend
        mock_import.return_value = mock_module
            
        # 创建调度器
        dispatcher = ExperimentDispatcher(
            result_uploader=mock_uploader
        )
            
        # 执行实验
        result = dispatcher.execute_experiment(self.test_experiment)
            
        # 验证上传器被调用
        self.assertEqual(len(mock_uploader.uploaded_results), 1)
        uploaded_result, experiment_id = mock_uploader.uploaded_results[0]
            
        # 验证上传的结果
        self.assertEqual(uploaded_result["status"], "success")
        self.assertEqual(uploaded_result["uo_type"], "CVA")
        self.assertIn("experiment_id", uploaded_result)
        self.assertEqual(experiment_id, uploaded_result["experiment_id"])


# 自定义结果上传器用于测试
class MockResultUploader(ResultUploader):
    def __init__(self):
        self.uploaded_results = []
    
    def upload(self, results, experiment_id):
        self.uploaded_results.append((results, experiment_id))
        return True


# 如果直接运行此文件则执行测试
if __name__ == "__main__":
    unittest.main() 
