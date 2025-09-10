#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$SCRIPT_DIR"

RELATION_TYPE="path3_2"
PATTERN_NAME="path3_2_l_u_1"
QUERY_NAME="full_query"
TIMER_ENABLED=true

while getopts "b:r:p:" opt; do
  case $opt in
    b) BASE_DIR="$OPTARG" ;;
    r) RELATION_TYPE="$OPTARG" ;;
    p) PATTERN_NAME="$OPTARG" ;;

    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

QUERY_FILE="$BASE_DIR/$RELATION_TYPE/$QUERY_NAME/query.json"

INPUT_DATASETS_DIR="$BASE_DIR/$RELATION_TYPE/input/$PATTERN_NAME"

CT_EXPERIMENT_FILE="src/cli/exp_count.py"

for DATASET_DIR in "$INPUT_DATASETS_DIR"/*/; do 

  EXP_ID=$(basename "$DATASET_DIR")

  echo "[+] Running dataset: $EXP_ID"

    python3 "$CT_EXPERIMENT_FILE" \
      --query_file "$QUERY_FILE" \
      --data_dir "$DATASET_DIR" 
 
done
