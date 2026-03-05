import json
from pathlib import Path
from select_k.Query import ConjunctiveQuery
from select_k.LayeredAlgorithm import LayeredJoinTree
from cli.exp_utils import parse_args, append_timing_records, append_result_records

def main():
    args = parse_args()
    exp_id = getattr(args, "exp_id", "exp01")
    trial = getattr(args, "trial", None) or 1

    # Load k_list from file if provided
    k_values = None
    k_path = Path(args.k_file).resolve()
    if k_path.exists():
        try:
            k_json = json.loads(k_path.read_text())
            if isinstance(k_json, dict) and "k_list" in k_json:
                k_values = k_json["k_list"]
            elif isinstance(k_json, list):
                k_values = k_json
        except Exception as e:
            print(f"Error when reading {k_path}: {e}")

    # if invalid k_file use args.k_list
    if not k_values:
        k_values = args.k_list

    result_list = []
    query_file = Path(args.query_file).resolve()
    data_dir = Path(args.data_dir).resolve() if hasattr(args, "data_dir") else query_file.parent

    cq = ConjunctiveQuery.from_query_file(query_file=query_file, data_dir=data_dir)
    tree = LayeredJoinTree(cq)
    tree.build_layered_join_tree()
    tree.direct_access_preprocessing()

    for k in k_values:
        result = tree.direct_access(k) 
        print(f"Direct access result for k={k}: {result}")
        if trial == 1:
            result_list.append({
                "exp_id": exp_id,
                "k": k,
                "result": result
            })

    # append timing records to the output file
    if trial == 1:
        records_file = getattr(args, "records_file")
        if records_file:
            records_file = Path(records_file).resolve()
        else: 
            records_file = data_dir / "records_directaccess.csv"
        append_result_records(result_list, records_file)

if __name__ == "__main__":
    main()
    