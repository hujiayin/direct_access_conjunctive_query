#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$SCRIPT_DIR"


RELATION_TYPE="path3"
PATTERN_NAME="path3_l_u_11_33_40"
QUERY_NAME="full_query"
# EXP_NAME="exp1_1000"
ITERS=5
TIMER_ENABLED=true
K_FILE_NAME="median_list.json" 
# K_LIST=(1)

while getopts "b:r:p:q:e:i:k:l:o:" opt; do
  case $opt in
    b) BASE_DIR="$OPTARG" ;;
    r) RELATION_TYPE="$OPTARG" ;;
    p) PATTERN_NAME="$OPTARG" ;;
    q) QUERY_NAME="$OPTARG" ;;
    e) EXP_NAME="$OPTARG" ;;
    i) ITERS="$OPTARG" ;;
    k) K_FILE_NAME="$OPTARG" ;;
    l) K_LIST=($OPTARG) ;;  # when calling, use: -l "${k_list[*]}" 
    o) OUTPUT_MARK="$OPTARG" ;;

    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

QUERY_FILE="$BASE_DIR/$RELATION_TYPE/$QUERY_NAME/query.json"

INPUT_DATASETS_DIR="$BASE_DIR/$RELATION_TYPE/input/$PATTERN_NAME"
if [ -n "$OUTPUT_MARK" ]; then
  OUTPUT_DIR="$BASE_DIR/$RELATION_TYPE/$QUERY_NAME/$PATTERN_NAME/$OUTPUT_MARK"
else
  OUTPUT_DIR="$BASE_DIR/$RELATION_TYPE/$QUERY_NAME/$PATTERN_NAME/$(basename "$K_FILE_NAME" .json)"
fi
echo "Output directory: $OUTPUT_DIR"

# output directory
mkdir -p "$OUTPUT_DIR"

SLT_EXPERIMENT_FILE="src/cli/select_klist.py"

TIMER_LOG="$OUTPUT_DIR/timing_log_select.log"
TIME_DATA_FILE="$OUTPUT_DIR/timing_log_select.csv"
RECORDS_FILE="$OUTPUT_DIR/records_select.csv"

for f in "$TIMER_LOG" "$TIME_DATA_FILE" "$RECORDS_FILE"; do
  if [ -f "$f" ]; then
    echo "Deleting existing file: $f"
    rm -f "$f"
  fi
done


echo "Starting batch experiments..." > "$TIMER_LOG"

for DATASET_DIR in "$INPUT_DATASETS_DIR"/*/; do 
 
  EXP_ID=$(basename "$DATASET_DIR")
  echo "[+] Running dataset: $EXP_ID"

  if [ ${#K_LIST[@]} -gt 0 ]; then
    K_FILE=""
  else
    K_FILE="$DATASET_DIR/$K_FILE_NAME"
  fi 

  for i in $(seq 1 $ITERS); do
    echo " -------- Trial $i"

    python3 "$SLT_EXPERIMENT_FILE" \
      --query_file "$QUERY_FILE" \
      --data_dir "$DATASET_DIR" \
      --k_file "$K_FILE" \
      --k_list "${K_LIST[@]}" \
      --timer_enabled True \
      --timer_log "$TIMER_LOG" \
      --time_data_file "$TIME_DATA_FILE" \
      --trial "$i" \
      --exp_id "$EXP_ID" \
      --records_file "$RECORDS_FILE"
  done
done