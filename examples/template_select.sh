#!/usr/bin/env bash
# template_selection.sh

# default parameters (can be override to run any experiments)
QUERY_FILE="examples/data2/query.json"
DATA_DIR="examples/data2"
K_FILE="examples/data2/k_list.json"
RECORDS_FILE="examples/data2/records_select.csv"

if [ $# -eq 4 ]; then
  QUERY_FILE=$1
  DATA_DIR=$2
  K_FILE=$3
  RECORDS_FILE=$4
fi

python src/cli/run_select.py \
  --query_file "$QUERY_FILE" \
  --data_dir "$DATA_DIR" \
  --k_file "$K_FILE" \
  --records_file "$RECORDS_FILE"