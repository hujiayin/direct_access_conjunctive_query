#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$SCRIPT_DIR"

RELATION_TYPE="path3"
PATTERN_NAME="path3_l_u_11_33_40"
QUERY_NAME="full_query"
# EXP_NAME="exp1_1000"
ITERS=5
K_FILE_NAME="median_list.json" 

while getopts "b:r:p:q:e:i:k:o:" opt; do
  case $opt in
    b) BASE_DIR="$OPTARG" ;;
    r) RELATION_TYPE="$OPTARG" ;;
    p) PATTERN_NAME="$OPTARG" ;;
    q) QUERY_NAME="$OPTARG" ;;
    e) EXP_NAME="$OPTARG" ;;
    i) ITERS="$OPTARG" ;;
    k) K_FILE_NAME="$OPTARG" ;;
    o) OUTPUT_MARK="$OPTARG" ;;

    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

source experiments/synthetic_exps/pg_config.sh


QUERY_FILE="$BASE_DIR/$RELATION_TYPE/$QUERY_NAME/query.json"
QUERY_DIR="$BASE_DIR/$RELATION_TYPE/$QUERY_NAME"

INPUT_DATASETS_DIR="$BASE_DIR/$RELATION_TYPE/input/$PATTERN_NAME"
if [ -n "$OUTPUT_MARK" ]; then
  OUTPUT_DIR="$BASE_DIR/$RELATION_TYPE/$QUERY_NAME/$PATTERN_NAME/$OUTPUT_MARK"
else
  OUTPUT_DIR="$BASE_DIR/$RELATION_TYPE/$QUERY_NAME/$PATTERN_NAME/$(basename "$K_FILE_NAME" .json)"
fi
echo "Output directory: $OUTPUT_DIR"

mkdir -p "$OUTPUT_DIR"

PROCESS_NAME="pg_query"

echo "exp_id,k,result" > "$OUTPUT_DIR/records_pg.csv"
echo "timestamp,exp_id,trial,process,k,duration_ms" > "$OUTPUT_DIR/timing_log_pg.csv" 

ROOT_DIR=$(pwd)

for DATASET_DIR in "$INPUT_DATASETS_DIR"/*/; do 
  
  EXP_ID=$(basename "$DATASET_DIR")
  K_FILE="$DATASET_DIR/$K_FILE_NAME"

  DB_NAME="${PATTERN_NAME}_${EXP_ID}"

  echo "Drop and recreate database: $DB_NAME..."
  dropdb --if-exists "$DB_NAME" -U "$PG_DB_USER"
  createdb "$DB_NAME" -U "$PG_DB_USER"

  DATA_DIR="$(realpath "$DATASET_DIR")"
  # DATA_DIR="$INPUT_DATASETS_DIR/$EXP_ID"
  echo "Data directory: $DATA_DIR"
  echo "Create tables and import data..."

  cd "$DATASET_DIR"
  psql -U "$PG_DB_USER" -d "$DB_NAME" \
        -v data_dir="$DATA_DIR" \
        -f "../../../$QUERY_NAME/create_tables.sql"

  cd "$ROOT_DIR"


  K_LIST=$(jq -r '.[]' "$K_FILE")

  echo "Run queries and explanations..."

  for k in $K_LIST; do
    echo "Running for k=$k"
    
    # Run query
    SQL=$(sed "s/{k}/$k/" "$QUERY_DIR/query_template.sql")
    echo "Executing SQL: $SQL"
    VALUE=$(psql -U "$PG_DB_USER" -d "$DB_NAME" -t -c "$SQL" | tr -d '[:space:]')
    echo "$EXP_ID,$k,$VALUE" >> "$OUTPUT_DIR/records_pg.csv"

    # Run explain multiple times
    for ((i=1; i<=$ITERS; i++)); do
      SQL_EXPLAIN=$(sed "s/{k}/$k/" "$QUERY_DIR/explain_template.sql")

      if [ "$i" -eq 1 ]; then
        EXPLAIN_OUTPUT_DIR="$OUTPUT_DIR/$EXP_ID"
        mkdir -p "$EXPLAIN_OUTPUT_DIR"
        EXPLAIN_OUTPUT_FILE="$EXPLAIN_OUTPUT_DIR/explain_offset${k}.txt"
        psql -U "$PG_DB_USER" -d "$DB_NAME" -c "$SQL_EXPLAIN" > "$EXPLAIN_OUTPUT_FILE"
        TIME_MS=$(grep "Execution Time" "$EXPLAIN_OUTPUT_FILE" | awk '{print $3}')
      else
        TIME_MS=$(psql -U "$PG_DB_USER" -d "$DB_NAME" -t -c "$SQL_EXPLAIN" \
          | grep "Execution Time" | awk '{print $3}')
      fi  
      echo "$(date +%s%3N),$EXP_ID,$i,$PROCESS_NAME,$k,$TIME_MS" >> "$OUTPUT_DIR/timing_log_pg.csv"
    done
  done

  dropdb --if-exists "$DB_NAME" -U "$PG_DB_USER"

done

echo "All done. Results saved to $OUTPUT_DIR"
