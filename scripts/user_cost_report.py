#!/usr/bin/env python3
"""用户Token消耗统计报表脚本

用法:
    python scripts/user_cost_report.py
    python scripts/user_cost_report.py --start-date 2026-03-01 --end-date 2026-03-18
    python scripts/user_cost_report.py --format csv --output report.csv
"""

import argparse
import csv
import sys
from pathlib import Path


def format_number(num: int) -> str:
    """格式化数字，添加千位分隔符"""
    return f"{num:,}"


def print_table(headers: list[str], rows: list[list[str]], title: str = ""):
    """打印表格"""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")

    if not rows:
        print("  无数据")
        return

    # 计算每列的最大宽度
    all_rows = [headers] + rows
    col_widths = [
        max(len(str(row[i])) for row in all_rows) for i in range(len(headers))
    ]

    # 打印表头
    header_line = "  |  ".join(
        f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers))
    )
    print(f"  {header_line}")
    print(f"  {'-' * len(header_line)}")

    # 打印数据行
    for row in rows:
        row_line = "  |  ".join(f"{row[i]:<{col_widths[i]}}" for i in range(len(row)))
        print(f"  {row_line}")


def print_summary(summary: dict):
    """打印汇总信息"""
    print(f"\n{'=' * 60}")
    print("  Token消耗汇总")
    print(f"{'=' * 60}")
    print(f"  总输入Token数:  {format_number(summary['total_input_tokens']):>15}")
    print(f"  总输出Token数:  {format_number(summary['total_output_tokens']):>15}")
    print(f"  总Token数:      {format_number(summary['total_tokens']):>15}")
    print(f"  总调用次数:     {format_number(summary['total_calls']):>15}")


def print_type_summary(type_stats: list[dict]):
    """打印按类型汇总信息"""
    print(f"\n{'=' * 60}")
    print("  按类型Token消耗汇总")
    print(f"{'=' * 60}")

    if not type_stats:
        print("  无数据")
        return

    for stat in type_stats:
        type_name = "主助手" if stat["type"] == "assistant" else "对话压缩"
        print(f"  {type_name:12}  输入: {format_number(stat['total_input_tokens']):>12}  "
              f"输出: {format_number(stat['total_output_tokens']):>12}  "
              f"总计: {format_number(stat['total_tokens']):>12}  "
              f"调用: {format_number(stat['total_calls']):>8}")


def generate_console_report(report: dict):
    """生成控制台报表"""
    summary = report["summary"]
    type_stats = report["by_type"]
    user_stats = report["by_user"]
    model_stats = report["by_model"]
    user_model_stats = report["by_user_model"]
    daily_stats = report["by_day"]

    # 打印汇总
    print_summary(summary)

    # 按类型统计
    print_type_summary(type_stats)

    # 按天统计
    daily_rows = [
        [
            stat["date"],
            format_number(stat["total_input_tokens"]),
            format_number(stat["total_output_tokens"]),
            format_number(stat["total_tokens"]),
            format_number(stat["call_count"]),
        ]
        for stat in daily_stats
    ]
    print_table(
        ["日期", "输入Token", "输出Token", "总Token", "调用次数"],
        daily_rows,
        "按天统计",
    )

    # 按用户统计
    user_rows = [
        [
            stat["user_id"],
            format_number(stat["total_input_tokens"]),
            format_number(stat["total_output_tokens"]),
            format_number(stat["total_tokens"]),
            format_number(stat["call_count"]),
        ]
        for stat in user_stats
    ]
    print_table(
        ["用户ID", "输入Token", "输出Token", "总Token", "调用次数"],
        user_rows,
        "按用户统计",
    )

    # 按模型统计
    model_rows = [
        [
            stat["model_key"],
            format_number(stat["total_input_tokens"]),
            format_number(stat["total_output_tokens"]),
            format_number(stat["total_tokens"]),
            format_number(stat["call_count"]),
        ]
        for stat in model_stats
    ]
    print_table(
        ["模型", "输入Token", "输出Token", "总Token", "调用次数"],
        model_rows,
        "按模型统计",
    )

    # 按用户和模型统计
    user_model_rows = [
        [
            stat["user_id"],
            stat["model_key"],
            format_number(stat["total_input_tokens"]),
            format_number(stat["total_output_tokens"]),
            format_number(stat["total_tokens"]),
            format_number(stat["call_count"]),
        ]
        for stat in user_model_stats
    ]
    print_table(
        ["用户ID", "模型", "输入Token", "输出Token", "总Token", "调用次数"],
        user_model_rows,
        "按用户和模型统计",
    )

    print(f"\n{'=' * 60}\n")


def generate_csv_report(report: dict, output_path: str):
    """生成CSV报表"""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # 写入汇总
        writer.writerow(["Token消耗统计报表"])
        writer.writerow([])
        writer.writerow(["汇总"])
        writer.writerow(["总输入Token数", report["summary"]["total_input_tokens"]])
        writer.writerow(["总输出Token数", report["summary"]["total_output_tokens"]])
        writer.writerow(["总Token数", report["summary"]["total_tokens"]])
        writer.writerow(["总调用次数", report["summary"]["total_calls"]])
        writer.writerow([])

        # 按类型统计
        writer.writerow(["按类型统计"])
        writer.writerow(["类型", "输入Token", "输出Token", "总Token", "调用次数"])
        for stat in report["by_type"]:
            writer.writerow(
                [
                    stat["type"],
                    stat["total_input_tokens"],
                    stat["total_output_tokens"],
                    stat["total_tokens"],
                    stat["call_count"],
                ]
            )
        writer.writerow([])

        # 按天统计
        writer.writerow(["按天统计"])
        writer.writerow(["日期", "输入Token", "输出Token", "总Token", "调用次数"])
        for stat in report["by_day"]:
            writer.writerow(
                [
                    stat["date"],
                    stat["total_input_tokens"],
                    stat["total_output_tokens"],
                    stat["total_tokens"],
                    stat["call_count"],
                ]
            )
        writer.writerow([])

        # 按用户统计
        writer.writerow(["按用户统计"])
        writer.writerow(["用户ID", "输入Token", "输出Token", "总Token", "调用次数"])
        for stat in report["by_user"]:
            writer.writerow(
                [
                    stat["user_id"],
                    stat["total_input_tokens"],
                    stat["total_output_tokens"],
                    stat["total_tokens"],
                    stat["call_count"],
                ]
            )
        writer.writerow([])

        # 按模型统计
        writer.writerow(["按模型统计"])
        writer.writerow(["模型", "输入Token", "输出Token", "总Token", "调用次数"])
        for stat in report["by_model"]:
            writer.writerow(
                [
                    stat["model_key"],
                    stat["total_input_tokens"],
                    stat["total_output_tokens"],
                    stat["total_tokens"],
                    stat["call_count"],
                ]
            )
        writer.writerow([])

        # 按用户和模型统计
        writer.writerow(["按用户和模型统计"])
        writer.writerow(
            ["用户ID", "模型", "输入Token", "输出Token", "总Token", "调用次数"]
        )
        for stat in report["by_user_model"]:
            writer.writerow(
                [
                    stat["user_id"],
                    stat["model_key"],
                    stat["total_input_tokens"],
                    stat["total_output_tokens"],
                    stat["total_tokens"],
                    stat["call_count"],
                ]
            )

    print(f"报表已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="用户Token消耗统计报表",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/user_cost_report.py
  python scripts/user_cost_report.py --start-date 2026-03-01 --end-date 2026-03-18
  python scripts/user_cost_report.py --format csv --output report.csv
        """,
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="开始日期（格式：YYYY-MM-DD）",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="结束日期（格式：YYYY-MM-DD）",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件路径（仅CSV格式有效）",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["table", "csv"],
        default="table",
        help="输出格式（默认：table）",
    )

    args = parser.parse_args()

    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # 延迟导入（避免在--help时加载依赖）
    from src.user.user_cost.user_cost_manager import user_cost_manager  # noqa: E402

    # 处理日期范围（直接使用日期字符串，因为表结构按天统计）
    start_date = args.start_date
    end_date = args.end_date

    # 获取报表数据
    report = {
        "summary": {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "total_calls": 0,
        },
        "by_type": user_cost_manager.get_type_cost_stats(start_date, end_date),
        "by_user": user_cost_manager.get_user_cost_stats(start_date, end_date),
        "by_model": user_cost_manager.get_model_cost_stats(start_date, end_date),
        "by_user_model": [],
        "by_day": [],
    }

    # 获取每个用户的模型统计并合并
    for user_stat in report["by_user"]:
        user_id = user_stat["user_id"]
        user_model_stats = user_cost_manager.get_user_model_cost_stats(
            user_id, start_date, end_date
        )
        for stat in user_model_stats:
            report["by_user_model"].append({"user_id": user_id, **stat})

    # 计算汇总数据
    for stat in report["by_type"]:
        report["summary"]["total_input_tokens"] += stat["total_input_tokens"]
        report["summary"]["total_output_tokens"] += stat["total_output_tokens"]
        report["summary"]["total_tokens"] += stat["total_tokens"]
        report["summary"]["total_calls"] += stat["total_calls"]

    # 生成报表
    if args.format == "csv":
        output_path = args.output or "user_cost_report.csv"
        generate_csv_report(report, output_path)
    else:
        generate_console_report(report)


if __name__ == "__main__":
    main()
