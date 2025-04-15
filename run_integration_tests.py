#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行dispatch模块集成测试的脚本。
可以直接运行此脚本来执行集成测试。
"""

import os
import sys
import unittest
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_dispatch_tests():
    """运行dispatch模块的集成测试"""
    # 确保tests目录在路径中
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    if not os.path.exists(tests_dir):
        logger.error(f"测试目录不存在: {tests_dir}")
        return False
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 只加载dispatch集成测试
    test_file = os.path.join(tests_dir, "test_dispatch_integration.py")
    if not os.path.exists(test_file):
        logger.error(f"测试文件不存在: {test_file}")
        return False
    
    # 加载并运行测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(tests_dir, pattern="test_dispatch_integration.py")
    
    # 运行测试
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # 返回结果
    return result.wasSuccessful()

if __name__ == "__main__":
    logger.info("开始运行dispatch模块集成测试...")
    success = run_dispatch_tests()
    
    if success:
        logger.info("✅ 所有测试通过!")
        sys.exit(0)
    else:
        logger.error("❌ 测试失败!")
        sys.exit(1) 
