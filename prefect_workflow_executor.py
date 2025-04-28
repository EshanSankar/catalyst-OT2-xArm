#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prefect工作流执行器

此模块提供使用Prefect执行实验工作流的功能。
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

from prefect import Flow
from prefect.engine.state import State, Success, Failed

from json_to_prefect import JSONToPrefectConverter

# 配置日志
logger = logging.getLogger(__name__)

class PrefectWorkflowExecutor:
    """使用Prefect执行工作流"""
    
    def __init__(self, workflow_file: Union[str, Path], mock_mode: bool = False):
        """
        初始化Prefect工作流执行器
        
        Args:
            workflow_file: 工作流JSON文件路径
            mock_mode: 是否使用模拟模式（不连接实际设备）
        """
        self.workflow_file = workflow_file
        self.mock_mode = mock_mode
        self.converter = JSONToPrefectConverter(workflow_file, mock_mode=mock_mode)
        self.flow = None
    
    def prepare(self) -> Flow:
        """
        准备工作流
        
        Returns:
            Flow: Prefect工作流对象
        """
        logger.info(f"准备工作流: {self.workflow_file}")
        self.flow = self.converter.create_flow()
        return self.flow
    
    def execute(self) -> Dict[str, Any]:
        """
        执行工作流
        
        Returns:
            Dict: 执行结果
        """
        if not self.flow:
            self.prepare()
        
        logger.info(f"执行工作流: {self.workflow_file}")
        state = self.flow.run()
        
        # 处理执行结果
        if isinstance(state, Success):
            logger.info(f"工作流执行成功: {state.message}")
            return {
                "status": "success",
                "message": state.message,
                "result": state.result
            }
        else:
            logger.error(f"工作流执行失败: {state.message}")
            return {
                "status": "error",
                "message": state.message,
                "result": state.result if hasattr(state, 'result') else None
            }
    
    def register(self, project_name: str = "电化学实验") -> str:
        """
        注册工作流到Prefect服务器
        
        Args:
            project_name: Prefect项目名称
            
        Returns:
            str: 注册结果消息
        """
        if not self.flow:
            self.prepare()
        
        try:
            # 注册工作流
            flow_id = self.flow.register(project_name=project_name)
            logger.info(f"工作流已注册，ID: {flow_id}")
            return f"工作流已注册，ID: {flow_id}"
        except Exception as e:
            logger.error(f"工作流注册失败: {str(e)}")
            raise

# 辅助函数
def execute_workflow_with_prefect(workflow_file: Union[str, Path], mock_mode: bool = False) -> Dict[str, Any]:
    """
    使用Prefect执行工作流
    
    Args:
        workflow_file: 工作流JSON文件路径
        mock_mode: 是否使用模拟模式
        
    Returns:
        Dict: 执行结果
    """
    executor = PrefectWorkflowExecutor(workflow_file, mock_mode=mock_mode)
    return executor.execute()

# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("prefect_workflow.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="使用Prefect执行实验工作流")
    parser.add_argument("workflow_file", help="工作流JSON文件路径")
    parser.add_argument("--mock", action="store_true", help="使用模拟模式（不连接实际设备）")
    parser.add_argument("--register", action="store_true", help="注册工作流到Prefect服务器")
    parser.add_argument("--project", default="电化学实验", help="Prefect项目名称")
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.isfile(args.workflow_file):
        logger.error(f"工作流文件不存在: {args.workflow_file}")
        sys.exit(1)
    
    # 创建执行器
    executor = PrefectWorkflowExecutor(args.workflow_file, mock_mode=args.mock)
    
    # 注册或执行工作流
    if args.register:
        try:
            result = executor.register(project_name=args.project)
            print(f"工作流注册结果: {result}")
        except Exception as e:
            print(f"工作流注册失败: {str(e)}")
            sys.exit(1)
    else:
        # 执行工作流
        result = executor.execute()
        
        # 输出结果
        if result["status"] == "success":
            print(f"工作流执行成功: {result['message']}")
            sys.exit(0)
        else:
            print(f"工作流执行失败: {result['message']}")
            sys.exit(1)
