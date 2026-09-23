# -*- coding: utf-8 -*-
"""
Cadence EDA 硬件日志流式解析器 (Cadence Log Stream Parser)
针对十万行级 EDA 导出的固定包头、变长表格与多源异构网表日志进行毫秒级正则与流式结构化清洗。
"""
import re
import time
import pandas as pd
from typing import List, Dict, Any, Generator


class CadenceLogParser:
    def __init__(self):
        # 匹配元器件电气参数行（支持空格对齐与制表符混合文本）
        # 格式示例: C102  CAP_CERAMIC  0603  VCC_3V3  3.3V  6.3V  0.22mm  PASS
        self.comp_pattern = re.compile(
            r'^\s*([CRULDQJ]\d+)\s+([A-Z0-9_\-]+)\s+([A-Z0-9_\-]+)\s+([A-Z0-9_]+)\s+([\d\.]+V?)\s+([\d\.]+V?)\s+([\d\.]+mm)\s*.*$',
            re.IGNORECASE
        )
        self.last_stats = {}

    def parse_stream(self, lines: Generator[str, None, None]) -> pd.DataFrame:
        """
        流式逐行解析，自动过滤固定包头、授权声明与分隔符
        """
        records = []
        in_data_table = False
        skipped_headers = 0
        malformed_rows = 0
        line_number = 0

        for line_number, line in enumerate(lines, 1):
            line_str = line.strip()
            
            # 检测数据表头起始标记
            if not in_data_table:
                if line_str.startswith("REF_DES") or "COMPONENT DETAILS LIST" in line_str or line_str.startswith("------"):
                    in_data_table = True
                else:
                    skipped_headers += 1
                continue

            # 忽略空行与页尾总结
            if not line_str or line_str.startswith("===") or "TOTAL COMPONENTS" in line_str:
                continue

            # 正则解析单行元器件特征
            match = self.comp_pattern.match(line_str)
            if match:
                ref_des, comp_type, package, net_name, op_v, rated_v, clearance = match.groups()
                
                # 数值清洗
                op_v_num = float(op_v.replace("V", "").replace("v", ""))
                rated_v_num = float(rated_v.replace("V", "").replace("v", ""))
                clearance_num = float(clearance.replace("mm", ""))

                records.append({
                    "ref_des": ref_des.upper(),
                    "comp_type": comp_type.upper(),
                    "package": package.upper(),
                    "net_name": net_name.upper(),
                    "operating_voltage": op_v_num,
                    "rated_voltage": rated_v_num,
                    "clearance_mm": clearance_num
                    ,"source_line": line_number
                })
            elif line_str and not line_str.startswith("-"):
                malformed_rows += 1

        df = pd.DataFrame(records)
        self.last_stats = {
            "parsed_rows": len(records),
            "skipped_headers": skipped_headers,
            "malformed_rows": malformed_rows,
            "total_lines": line_number,
        }
        return df

    def parse_file(self, file_path: str) -> pd.DataFrame:
        """
        读取并解析 Cadence 硬件日志文件
        """
        start_t = time.time()
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            df = self.parse_stream(f)
        cost_ms = (time.time() - start_t) * 1000
        print(f"[CadenceParser] 解析 {len(df)} 条元器件记录，耗时 {cost_ms:.1f}ms，异常行 {self.last_stats.get('malformed_rows', 0)}。")
        return df
