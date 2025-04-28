#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Prefect集成

此脚本测试使用Prefect执行工作流的功能。
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("prefect_integration_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PrefectIntegrationTest")

def test_prefect_workflow(workflow_file: str, mock_mode: bool = True) -> Dict[str, Any]:
    """
    测试使用Prefect执行工作流
    
    Args:
        workflow_file: 工作流JSON文件路径
        mock_mode: 是否使用模拟模式
        
    Returns:
        Dict: 测试结果
    """
    logger.info(f"测试使用Prefect执行工作流: {workflow_file} (模拟模式: {mock_mode})")
    
    try:
        # 导入Prefect工作流执行器
        from prefect_workflow_executor import PrefectWorkflowExecutor
        
        # 创建执行器
        executor = PrefectWorkflowExecutor(workflow_file=workflow_file, mock_mode=mock_mode)
        logger.info("成功创建Prefect工作流执行器")
        
        # 执行工作流
        result = executor.execute()
        logger.info(f"工作流执行结果: {result}")
        
        return {
            "status": "success",
            "message": "Prefect工作流测试成功",
            "result": result
        }
    except Exception as e:
        logger.error(f"Prefect工作流测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Prefect工作流测试失败: {str(e)}"
        }

def test_workflow_executor_with_prefect(workflow_file: str, mock_mode: bool = True) -> Dict[str, Any]:
    """
    测试使用WorkflowExecutor和Prefect执行工作流
    
    Args:
        workflow_file: 工作流JSON文件路径
        mock_mode: 是否使用模拟模式
        
    Returns:
        Dict: 测试结果
    """
    logger.info(f"测试使用WorkflowExecutor和Prefect执行工作流: {workflow_file} (模拟模式: {mock_mode})")
    
    try:
        # 导入工作流执行器
        from workflow_executor import WorkflowExecutor
        
        # 创建执行器
        executor = WorkflowExecutor(
            workflow_file=workflow_file,
            use_prefect=True,
            mock_mode=mock_mode
        )
        logger.info("成功创建WorkflowExecutor (使用Prefect)")
        
        # 执行工作流
        success = executor.execute_workflow()
        logger.info(f"工作流执行结果: {'成功' if success else '失败'}")
        
        return {
            "status": "success" if success else "error",
            "message": "WorkflowExecutor (使用Prefect) 测试成功" if success else "WorkflowExecutor (使用Prefect) 测试失败"
        }
    except Exception as e:
        logger.error(f"WorkflowExecutor (使用Prefect) 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"WorkflowExecutor (使用Prefect) 测试失败: {str(e)}"
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试Prefect集成")
    parser.add_argument("workflow_file", help="工作流JSON文件路径")
    parser.add_argument("--no-mock", action="store_true", help="不使用模拟模式（连接实际设备）")
    parser.add_argument("--direct", action="store_true", help="直接使用PrefectWorkflowExecutor而不是通过WorkflowExecutor")
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.isfile(args.workflow_file):
        logger.error(f"工作流文件不存在: {args.workflow_file}")
        sys.exit(1)
    
    # 执行测试
    if args.direct:
        result = test_prefect_workflow(args.workflow_file, mock_mode=not args.no_mock)
    else:
        result = test_workflow_executor_with_prefect(args.workflow_file, mock_mode=not args.no_mock)
    
    # 输出结果
    if result["status"] == "success":
        print(f"测试成功: {result['message']}")
        sys.exit(0)
    else:
        print(f"测试失败: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
