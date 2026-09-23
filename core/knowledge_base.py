# -*- coding: utf-8 -*-
"""
硬件测试性与可靠性规程知识库 (Hardware Testability Knowledge Base)
固化军用/工业电子装备硬件元器件降额设计准则 (GJB/Z 35)、爬电安全距离与测试点覆盖率规范。
"""
from typing import Dict, Any, List


class TestabilityKnowledgeBase:
    def __init__(self):
        # 降额规范：工作参数 / 额定参数 的最大允许比例
        self.derating_standards = {
            "CAPACITOR": {"max_voltage_ratio": 0.70, "desc": "电容一级降额：工作电压不应超过额定耐压的 70%"},
            "RESISTOR": {"max_power_ratio": 0.60, "desc": "电阻一级降额：工作功耗不应超过额定功率的 60%"},
            "IC": {"max_voltage_ratio": 0.85, "desc": "集成电路电压稳态波动降额上限 85%"}
        }

        # 空间布线间距规范 (Clearance Rules)
        self.clearance_standards = {
            "HIGH_VOLTAGE": {"min_clearance_mm": 0.25, "desc": "高压网络 (>=24V) 导线与焊盘间距必须 >= 0.25mm，防止击穿拉弧"},
            "NORMAL_VOLTAGE": {"min_clearance_mm": 0.15, "desc": "常规低压网络导线与焊盘间距必须 >= 0.15mm"}
        }

    def get_derating_limit(self, comp_type: str) -> float:
        for k, v in self.derating_standards.items():
            if k in comp_type.upper():
                return v["max_voltage_ratio"]
        return 0.80

    def export_rules(self) -> dict:
        return {
            "version": "demo-1.0",
            "rules": [
                {
                    "rule_id": f"DERATING-{name}",
                    "comp_type": name,
                    "max_voltage_ratio": data["max_voltage_ratio"],
                    "min_clearance_mm": None,
                    "description": data["desc"],
                }
                for name, data in self.derating_standards.items()
            ]
        }

    def get_min_clearance(self, net_name: str, op_volt: float) -> float:
        if op_volt >= 24.0 or "HIGH" in net_name.upper() or "48V" in net_name.upper():
            return self.clearance_standards["HIGH_VOLTAGE"]["min_clearance_mm"]
        return self.clearance_standards["NORMAL_VOLTAGE"]["min_clearance_mm"]
