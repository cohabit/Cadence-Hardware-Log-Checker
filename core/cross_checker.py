# -*- coding: utf-8 -*-
"""
多源参数交叉比对核验引擎 (Testability Cross-Checker Engine)
将 Cadence 硬件实测参数与知识库理论规程阈值进行自动化语义对齐与越限核验，输出违规缺陷清单。
"""
import pandas as pd
from typing import List, Dict, Any
from .knowledge_base import TestabilityKnowledgeBase


class TestabilityCrossChecker:
    def __init__(self, kb: TestabilityKnowledgeBase = None, rule_snapshot: Dict[str, Any] = None):
        self.kb = kb or TestabilityKnowledgeBase()
        self.rule_snapshot = rule_snapshot or {}

    def run_check(self, df_components: pd.DataFrame) -> Dict[str, Any]:
        """
        批量核验元器件降额裕度与电气安全间隙
        """
        violations = []
        passed_count = 0
        checked_dimensions = set()

        for _, row in df_components.iterrows():
            ref_des = row["ref_des"]
            comp_type = row["comp_type"]
            net_name = row["net_name"]
            op_v = row["operating_voltage"]
            rated_v = row["rated_voltage"]
            clearance = row["clearance_mm"]

            is_valid = True

            # 1. 降额耐压应力比核验 (Voltage Stress Ratio)
            if rated_v > 0:
                stress_ratio = op_v / rated_v
                limit_ratio = self.kb.get_derating_limit(comp_type)
                checked_dimensions.add("voltage_derating")
                
                if stress_ratio > limit_ratio:
                    is_valid = False
                    violations.append({
                        "rule_id": f"DERATING-{comp_type}",
                        "ref_des": ref_des,
                        "comp_type": comp_type,
                        "net_name": net_name,
                        "violation_type": "降额应力超标 (Over-Stress)",
                        "severity": "CRITICAL",
                        "measured_value": f"工作比: {stress_ratio*100:.1f}% ({op_v}V/{rated_v}V)",
                        "standard_limit": f"上限: {limit_ratio*100:.1f}%",
                        "recommendation": f"建议更换耐压更高规格型号（如 >= {op_v / limit_ratio:.1f}V）"
                    })

            # 2. 空间爬电间距核验 (Clearance Check)
            min_clearance = self.kb.get_min_clearance(net_name, op_v)
            checked_dimensions.add("clearance")
            if clearance < min_clearance:
                is_valid = False
                violations.append({
                    "rule_id": "CLEARANCE-HIGH" if min_clearance >= 0.25 else "CLEARANCE-NORMAL",
                    "ref_des": ref_des,
                    "comp_type": comp_type,
                    "net_name": net_name,
                    "violation_type": "间距违规 (Clearance Violation)",
                    "severity": "WARNING",
                    "measured_value": f"{clearance}mm",
                    "standard_limit": f"下限: {min_clearance}mm",
                    "recommendation": "优化 PCB 布线走线间距，防止高压拉弧击穿"
                })

            if is_valid:
                passed_count += 1

        total = len(df_components)
        pass_rate = round((passed_count / total * 100), 2) if total > 0 else 100.0

        summary = {
            "total_inspected_components": total,
            "passed_components": passed_count,
            "violations_found": len(violations),
            "pass_rate_pct": pass_rate,
            "coverage_rate_pct": round(len(checked_dimensions) / 2 * 100, 2),
            "checked_dimensions": sorted(checked_dimensions),
            "rule_snapshot_version": self.rule_snapshot.get("version", "embedded-demo-rules"),
        }

        print(f"[CrossChecker] 交叉比对核验完成！核查元器件: {total} 个, 发现缺陷: {len(violations)} 处, 合规率: {pass_rate}%。")
        return {
            "summary": summary,
            "violations": violations
        }
