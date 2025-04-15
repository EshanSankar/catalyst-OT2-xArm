#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用于测试的模拟解析模块。
提供 parse_experiment_parameters 函数来模拟实际解析操作。
"""

from typing import Dict, Any


def parse_experiment_parameters(uo: Dict[str, Any]) -> Dict[str, Any]:
    """
    模拟解析实验参数的函数。
    在实际代码中，这个函数会执行更复杂的解析和验证逻辑。
    
    Args:
        uo: 包含实验参数的单元操作字典
        
    Returns:
        解析后的单元操作字典
    """
    # 创建解析后的副本，避免修改原始字典
    parsed_uo = uo.copy()
    
    # 确保必要的字段存在
    if "uo_type" not in parsed_uo:
        raise ValueError("Missing required field: uo_type")
    
    if "parameters" not in parsed_uo:
        parsed_uo["parameters"] = {}
    
    # 根据实验类型执行特定的解析逻辑
    uo_type = parsed_uo["uo_type"]
    
    if uo_type == "CVA":
        # 转换电压单位，移除单位后缀
        if "start_voltage" in parsed_uo["parameters"]:
            start_v = parsed_uo["parameters"]["start_voltage"]
            if isinstance(start_v, str) and start_v.endswith("V"):
                parsed_uo["parameters"]["start_voltage"] = float(start_v.rstrip("V"))
        
        if "end_voltage" in parsed_uo["parameters"]:
            end_v = parsed_uo["parameters"]["end_voltage"]
            if isinstance(end_v, str) and end_v.endswith("V"):
                parsed_uo["parameters"]["end_voltage"] = float(end_v.rstrip("V"))
    
    elif uo_type == "PEIS":
        # 转换频率单位
        if "frequency_high" in parsed_uo["parameters"]:
            freq_high = parsed_uo["parameters"]["frequency_high"]
            if isinstance(freq_high, str) and freq_high.endswith("Hz"):
                parsed_uo["parameters"]["frequency_high"] = float(freq_high.split()[0])
        
        if "frequency_low" in parsed_uo["parameters"]:
            freq_low = parsed_uo["parameters"]["frequency_low"]
            if isinstance(freq_low, str) and freq_low.endswith("Hz"):
                parsed_uo["parameters"]["frequency_low"] = float(freq_low.split()[0])
    
    return parsed_uo 
