"""
兼容层文件。

按当前项目约定，本文件仅保留 HFSS 连接与参数读写相关能力，
优化流程统一走 optimizer/bayesian.py + orchestrator/pipeline.py。
"""

from simulator.hfss_client import (
    get_hfss_parameters,
    open_hfss,
    parse_value_with_units,
    run_analysis,
    run_and_extract_metric,
    set_hfss_parameters,
)

__all__ = [
    "open_hfss",
    "parse_value_with_units",
    "get_hfss_parameters",
    "set_hfss_parameters",
    "run_analysis",
    "run_and_extract_metric",
]
