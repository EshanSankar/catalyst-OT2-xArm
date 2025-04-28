#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON到Prefect转换器

此模块负责将实验工作流JSON配置转换为Prefect工作流。
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

import prefect
from prefect import task, Flow, case, unmapped
from prefect.tasks.control_flow import merge
from prefect.engine.results import LocalResult
from prefect.engine.state import State, Success, Failed

# 配置日志
logger = logging.getLogger(__name__)

class JSONToPrefectConverter:
    """将实验JSON配置转换为Prefect工作流"""
    
    def __init__(self, json_file_path: Union[str, Path], mock_mode: bool = False):
        """
        初始化转换器
        
        Args:
            json_file_path: JSON工作流配置文件路径
            mock_mode: 是否使用模拟模式（不连接实际设备）
        """
        self.json_file_path = json_file_path
        self.mock_mode = mock_mode
        
        # 加载工作流配置
        with open(json_file_path, 'r') as f:
            self.workflow_config = json.load(f)
        
        # 导入后端类
        try:
            from backends import (
                BaseBackend, CVABackend, PEISBackend, OCVBackend, 
                CPBackend, LSVBackend
            )
            
            # 映射实验类型到后端类
            self.backend_classes = {
                "CVA": CVABackend,
                "PEIS": PEISBackend,
                "OCV": OCVBackend,
                "CP": CPBackend,
                "LSV": LSVBackend
            }
            
            # 后端实例将在任务中创建
            self.backend_instances = {}
            
        except ImportError as e:
            logger.error(f"无法导入后端类: {e}")
            raise
    
    def create_flow(self) -> Flow:
        """
        创建Prefect工作流
        
        Returns:
            Flow: Prefect工作流对象
        """
        # 创建工作流
        flow_name = self.workflow_config.get("name", "电化学实验工作流")
        with Flow(flow_name, result=LocalResult()) as flow:
            # 创建全局配置任务
            global_config = self.workflow_config.get("global_config", {})
            setup_result = self.create_setup_task(global_config)
            
            # 创建实验任务
            experiment_results = {}
            previous_result = setup_result
            
            # 按顺序创建和连接任务
            for exp_id in self.workflow_config.get("sequence", []):
                # 查找实验配置
                exp_config = None
                for exp in self.workflow_config.get("experiments", []):
                    if exp.get("id") == exp_id:
                        exp_config = exp
                        break
                
                if not exp_config:
                    raise ValueError(f"找不到ID为'{exp_id}'的实验配置")
                
                # 创建实验任务
                exp_result = self.create_experiment_task(
                    exp_config, 
                    upstream_result=previous_result
                )
                
                # 检查是否需要人工干预
                if exp_config.get("requires_human_check", False):
                    human_message = exp_config.get("human_message", f"请检查实验'{exp_id}'的结果")
                    human_check_result = self.create_human_intervention_task(
                        human_message,
                        upstream_result=exp_result
                    )
                    previous_result = human_check_result
                else:
                    previous_result = exp_result
                
                # 存储实验结果以供后续引用
                experiment_results[exp_id] = exp_result
                
                # 检查是否有条件执行
                if "condition" in exp_config:
                    condition_config = exp_config["condition"]
                    dependent_exp_id = condition_config.get("experiment_id")
                    
                    # 确保依赖的实验已经执行
                    if dependent_exp_id not in experiment_results:
                        raise ValueError(
                            f"实验'{exp_id}'依赖于尚未执行的实验'{dependent_exp_id}'"
                        )
                    
                    # 创建条件检查任务
                    condition_result = self.create_condition_check_task(
                        condition_config,
                        experiment_results[dependent_exp_id]
                    )
                    
                    # 使用条件分支
                    with case(condition_result, True):
                        # 条件为真时执行实验
                        exp_result = self.create_experiment_task(
                            exp_config, 
                            upstream_result=previous_result
                        )
                        previous_result = exp_result
            
            # 创建清理任务
            cleanup_result = self.create_cleanup_task(upstream_result=previous_result)
        
        return flow
    
    @task(name="环境设置", max_retries=3, retry_delay=prefect.tasks.core.constants.retry_delay(seconds=30))
    def create_setup_task(self, global_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建环境设置任务
        
        Args:
            global_config: 全局配置字典
            
        Returns:
            Dict: 设置结果
        """
        logger.info(f"设置实验环境，配置: {global_config}")
        
        try:
            # 这里可以实现实际的环境设置逻辑
            # 例如初始化OT-2、Arduino等设备
            
            if self.mock_mode:
                logger.info("使用模拟模式，跳过实际设备初始化")
                return {"status": "success", "message": "环境设置完成（模拟模式）"}
            
            # 实际设备初始化代码
            # ...
            
            return {
                "status": "success", 
                "message": "环境设置完成",
                "config": global_config
            }
            
        except Exception as e:
            logger.error(f"环境设置失败: {str(e)}")
            raise
    
    def create_experiment_task(self, experiment_config: Dict[str, Any], upstream_result: Optional[Any] = None):
        """
        创建实验执行任务
        
        Args:
            experiment_config: 实验配置字典
            upstream_result: 上游任务的结果
            
        Returns:
            Task: Prefect任务对象
        """
        uo_type = experiment_config.get("uo_type")
        exp_id = experiment_config.get("id", "unknown")
        
        @task(
            name=f"{uo_type}_{exp_id}",
            max_retries=experiment_config.get("retry_count", 2),
            retry_delay=prefect.tasks.core.constants.retry_delay(
                seconds=experiment_config.get("retry_delay", 60)
            ),
            timeout=experiment_config.get("timeout", 3600)  # 默认1小时超时
        )
        def run_experiment(config, upstream_data=None):
            logger.info(f"执行实验 {config.get('id')}, 类型: {config.get('uo_type')}")
            
            try:
                # 获取实验类型
                uo_type = config.get("uo_type")
                if uo_type not in self.backend_classes:
                    raise ValueError(f"未知的实验类型: {uo_type}")
                
                # 创建后端实例（如果尚未创建）
                if uo_type not in self.backend_instances:
                    backend_class = self.backend_classes[uo_type]
                    self.backend_instances[uo_type] = backend_class()
                
                backend = self.backend_instances[uo_type]
                
                # 准备实验参数
                uo = {
                    "uo_type": uo_type,
                    "parameters": config.get("parameters", {}),
                    "id": config.get("id")
                }
                
                # 执行实验
                if self.mock_mode:
                    logger.info(f"模拟执行实验: {uo}")
                    # 模拟结果
                    result = {
                        "status": "success",
                        "experiment_id": config.get("id"),
                        "uo_type": uo_type,
                        "results": {"message": "模拟执行成功"}
                    }
                else:
                    # 实际执行实验
                    result = backend.execute_experiment(uo)
                
                logger.info(f"实验 {config.get('id')} 执行完成，状态: {result.get('status')}")
                return result
                
            except Exception as e:
                logger.error(f"实验 {config.get('id')} 执行失败: {str(e)}")
                raise
        
        # 创建任务
        if upstream_result:
            return run_experiment(experiment_config, upstream_result)
        else:
            return run_experiment(experiment_config)
    
    def create_human_intervention_task(self, message: str, upstream_result: Any, timeout: int = 3600):
        """
        创建需要人工干预的任务
        
        Args:
            message: 人工干预提示信息
            upstream_result: 上游任务的结果
            timeout: 等待人工干预的超时时间（秒）
            
        Returns:
            Task: Prefect任务对象
        """
        @task(name="人工干预", timeout=timeout)
        def wait_for_human(result):
            logger.info(f"等待人工干预: {message}")
            logger.info(f"上游任务结果: {result}")
            
            # 这里可以实现等待人工确认的逻辑
            # 例如通过API轮询或者其他机制
            
            # 在实际实现中，这里可能会:
            # 1. 发送通知（邮件、Slack等）
            # 2. 等待用户通过API确认
            # 3. 超时后自动继续或失败
            
            # 模拟人工确认
            if self.mock_mode:
                logger.info("模拟模式：自动确认人工干预")
                return {"status": "confirmed", "message": "人工干预已确认（模拟）"}
            
            # 实际实现
            # ...
            
            return {"status": "confirmed", "message": "人工干预已确认", "original_result": result}
        
        return wait_for_human(upstream_result)
    
    def create_condition_check_task(self, condition_config: Dict[str, Any], experiment_result: Any):
        """
        创建条件检查任务
        
        Args:
            condition_config: 条件配置字典
            experiment_result: 依赖实验的结果
            
        Returns:
            Task: Prefect任务对象
        """
        @task(name="条件检查")
        def check_condition(result):
            logger.info(f"检查条件: {condition_config}")
            
            try:
                # 获取条件参数
                parameter = condition_config.get("parameter")
                operator = condition_config.get("operator")
                value = condition_config.get("value")
                
                # 从结果中提取参数值
                if isinstance(result, dict) and "results" in result:
                    actual_value = result["results"].get(parameter)
                else:
                    logger.warning(f"无法从结果中提取参数 {parameter}")
                    return False
                
                logger.info(f"条件检查: {actual_value} {operator} {value}")
                
                # 执行条件检查
                if operator == "==":
                    return actual_value == value
                elif operator == "!=":
                    return actual_value != value
                elif operator == ">":
                    return actual_value > value
                elif operator == "<":
                    return actual_value < value
                elif operator == ">=":
                    return actual_value >= value
                elif operator == "<=":
                    return actual_value <= value
                else:
                    logger.warning(f"未知的操作符: {operator}")
                    return False
                    
            except Exception as e:
                logger.error(f"条件检查失败: {str(e)}")
                return False
        
        return check_condition(experiment_result)
    
    @task(name="清理资源")
    def create_cleanup_task(self, upstream_result: Any = None):
        """
        创建资源清理任务
        
        Args:
            upstream_result: 上游任务的结果
            
        Returns:
            Dict: 清理结果
        """
        logger.info("清理资源...")
        
        try:
            # 断开所有设备连接
            for backend_type, backend in self.backend_instances.items():
                logger.info(f"断开 {backend_type} 后端连接")
                backend.disconnect_devices()
            
            return {"status": "success", "message": "资源清理完成"}
            
        except Exception as e:
            logger.error(f"资源清理失败: {str(e)}")
            raise

# 辅助函数
def run_workflow_with_prefect(json_file_path: Union[str, Path], mock_mode: bool = False) -> State:
    """
    使用Prefect执行工作流
    
    Args:
        json_file_path: JSON工作流配置文件路径
        mock_mode: 是否使用模拟模式
        
    Returns:
        State: Prefect执行状态
    """
    # 创建转换器
    converter = JSONToPrefectConverter(json_file_path, mock_mode=mock_mode)
    
    # 创建工作流
    flow = converter.create_flow()
    
    # 执行工作流
    state = flow.run()
    
    return state

# 示例用法
if __name__ == "__main__":
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python json_to_prefect.py <工作流JSON文件> [--mock]")
        sys.exit(1)
    
    # 解析参数
    json_file = sys.argv[1]
    mock_mode = "--mock" in sys.argv
    
    # 执行工作流
    print(f"使用Prefect执行工作流: {json_file} (模拟模式: {mock_mode})")
    state = run_workflow_with_prefect(json_file, mock_mode=mock_mode)
    
    # 输出结果
    if isinstance(state, Success):
        print(f"工作流执行成功: {state.message}")
        sys.exit(0)
    else:
        print(f"工作流执行失败: {state.message}")
        sys.exit(1)
