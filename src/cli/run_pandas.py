import argparse
import csv
import json
from pathlib import Path
from select_k.PandasAccess import PandasAccess
from exp_timer.exp_timer import CONFIG, time_block, time_all_methods, TimerConfig, set_timer_context, timer_records
from exp_utils import parse_args, append_timing_records, append_result_records

def main():
    args = parse_args()

    query_file = Path(args.query_file).resolve()
    data_dir = Path(args.data_dir).resolve() if hasattr(args, "data_dir") else query_file.parent

    pa = PandasAccess(query_file, data_dir=data_dir)
    pa.smart_join_and_sort()

    records_file = getattr(args, "records_file", "records_pandas.csv")
    records_file = Path(records_file).resolve()
    pa.sorted_df.to_csv(records_file)


if __name__ == "__main__":
    main()
