#!/usr/bin/env bash
# run_examples.sh

# Direct Access cases list
# Each case: "query_file data_dir k_list_file records_file"
CASES=(
  "examples/data2/query.json examples/data2 examples/data2/k_list.json examples/data2/records_directaccess.csv"
  "examples/data1/query.json examples/data1 examples/data1/k_list.json examples/data1/records_directaccess.csv"
)

for case in "${CASES[@]}"; do
  echo ">>> Running: $case"
  bash examples/template_directaccess.sh $case
done

# Select cases list
# Each case: "query_file data_dir k_list_file records_file"
CASES=(
  "examples/data2/query.json examples/data2 examples/data2/k_list.json examples/data2/records_select.csv"
  "examples/data1/query.json examples/data1 examples/data1/k_list.json examples/data1/records_select.csv"
)

for case in "${CASES[@]}"; do
  echo ">>> Running: $case"
  bash examples/template_select.sh $case
done