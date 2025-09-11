#!/usr/bin/env bash
# set -euo pipefail

RELATION_TYPE="path3_2"
NUM_ROWS_LIST_CSV="100,300,1000,3000,10000,30000,100000,300000,1000000"
# NUM_ROWS_LIST_CSV="20,50"
SEED_LIST_CSV="11,33,40" 
QUERY_NAME="full_query"
ITERS="5"
K_FILE_NAME="median_list.json"
OUTPUT_MARK="median"
EXTRA=""

BASE_DIR="experiments/synthetic_exps/exp1_median"
PARAMS_FILE="${1:-experiments/synthetic_exps/exp1_params.csv}"
RUN_SCRIPT="${RUN_SCRIPT:-experiments/synthetic_exps/run_klist.sh}"

tail -n +2 "$PARAMS_FILE" | tr -d '\r' | \
while IFS=, read -r DIST_TYPE DIST_PARAMS DOMAIN_TYPE; do
  DIST_TYPE="$(echo -n "${DIST_TYPE:-}" | xargs)"
  DIST_PARAMS="$(echo -n "${DIST_PARAMS:-}" | xargs)"
  DOMAIN_TYPE="$(echo -n "${DOMAIN_TYPE:-}" | xargs)"
  [[ -z "$DIST_TYPE$DIST_PARAMS$DOMAIN_TYPE" ]] && continue

  ts="$(date +%Y%m%d-%H%M%S)"
  tag="dist=${DIST_TYPE}_param=${DIST_PARAMS:-EMPTY}_domain=${DOMAIN_TYPE}"

  echo "BASE_DIR=$BASE_DIR"

  echo "[RUN ] $tag"
  BASE_DIR="$BASE_DIR" \
  RELATION_TYPE="$RELATION_TYPE" \
  NUM_ROWS_LIST_CSV="$NUM_ROWS_LIST_CSV" \
  SEED_LIST_CSV="$SEED_LIST_CSV" \
  QUERY_NAME="$QUERY_NAME" \
  ITERS="$ITERS" \
  K_FILE_NAME="$K_FILE_NAME" \
  OUTPUT_MARK="$OUTPUT_MARK" \
  EXTRA="$EXTRA" \
  DOMAIN_TYPE="$DOMAIN_TYPE" DIST_TYPE="$DIST_TYPE" DIST_PARAMS="$DIST_PARAMS" \
  RUN_PGSQL=true \
    bash "$RUN_SCRIPT" 
done