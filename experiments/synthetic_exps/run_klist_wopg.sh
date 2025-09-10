#!/bin/bash
# set -e
# set -euo pipefail

# SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# BASE_DIR="$SCRIPT_DIR"

# RELATION_TYPE="path3_3"
# # NUM_ROWS_LIST=(100 1000 10000 20000 50000 80000 100000 200000 300000 400000 500000 600000 700000 800000 900000 1000000)
NUM_ROWS_LIST=(10000 20000 50000 80000 100000)
SEED_LIST=(2)

# DOMAIN_TYPE="large" 
# DIST_TYPE="zipf"
# DIST_PARAMS=""

# QUERY_NAME="full_query"
# ITERS=5
# K_FILE_NAME="quartile_list.json" 
# OUTPUT_MARK="quartiles"
# EXTRA=""
: "${BASE_DIR:=experiments/synthetic_exps}"
: "${RELATION_TYPE:=path3_3}"
: "${NUM_ROWS_LIST:=(10000 20000 50000 80000 100000)}"
: "${SEED_LIST:=(5)}"
: "${DOMAIN_TYPE:=large}"
: "${DIST_TYPE:=zipf}"
: "${DIST_PARAMS:=}"
: "${QUERY_NAME:=full_query}"
: "${ITERS:=5}"
: "${K_FILE_NAME:=quartile_list.json}"
: "${OUTPUT_MARK:=}"
: "${EXTRA:=}"

echo "Base directory: $BASE_DIR"

if [[ -n "${NUM_ROWS_LIST_CSV:-}" ]]; then
  IFS=',' read -r -a NUM_ROWS_LIST <<< "$NUM_ROWS_LIST_CSV"
fi

if [[ -n "${SEED_LIST_CSV:-}" ]]; then
  IFS=',' read -r -a SEED_LIST <<< "$SEED_LIST_CSV"
fi

domain_initial="${DOMAIN_TYPE:0:1}"
dist_initial="${DIST_TYPE:0:1}"
if [ -n "$DIST_PARAMS" ]; then
  dist_str="${dist_initial}${DIST_PARAMS}"
else
  dist_str="$dist_initial"
fi
if [ -n "$EXTRA" ]; then
  extra_str="_${EXTRA}"
else
  extra_str=""
fi

if [ -n "$SEED" ]; then
  seed_str="$SEED"
elif [ -n "$SEED_LIST" ]; then
  echo "1"
  seed_str=$(IFS=_; echo "${SEED_LIST[*]}")
else
  echo "No seed provided"
  exit 1
fi

PATTERN_NAME="${RELATION_TYPE}_${domain_initial}_${dist_str}_${seed_str}${extra_str}"

echo "Save directory: $PATTERN_NAME"

# # run generator
# if [ -n "$SEED_LIST" ]; then

#   for seed in "${SEED_LIST[@]}"; do
#     echo "Using seed: $seed"

#     bash experiments/synthetic_exps/run_generator.sh -b "$BASE_DIR" -r "$RELATION_TYPE" -n "$(IFS=,; echo "${NUM_ROWS_LIST[*]}")" -d "$DOMAIN_TYPE" -t "$DIST_TYPE" -s "$seed" -x "$EXTRA" -p "$PATTERN_NAME"

#   done

# elif [ -n "$SEED" ]; then

#   echo "Using single seed: $SEED"
#   bash experiments/synthetic_exps/run_generator.sh -b "$BASE_DIR" -r "$RELATION_TYPE" -n "$(IFS=,; echo "${NUM_ROWS_LIST[*]}")" -d "$DOMAIN_TYPE" -t "$DIST_TYPE" -s "$SEED" -x "$EXTRA" -p "$PATTERN_NAME"

# fi

# run count
bash experiments/synthetic_exps/run_count.sh -b "$BASE_DIR" -r "$RELATION_TYPE" -p "$PATTERN_NAME"

# bash experiments/synthetic_exps/run_da.sh -b "$BASE_DIR" -r "$RELATION_TYPE" -p "$PATTERN_NAME" -q "$QUERY_NAME" -i "$ITERS" -k "$K_FILE_NAME" -o "$OUTPUT_MARK"
# bash experiments/synthetic_exps/run_select.sh -b "$BASE_DIR" -r "$RELATION_TYPE" -p "$PATTERN_NAME" -q "$QUERY_NAME" -i "$ITERS" -k "$K_FILE_NAME" -o "$OUTPUT_MARK"


