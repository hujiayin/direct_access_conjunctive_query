import argparse
import os
from pathlib import Path
import random
import numpy as np
from math import sqrt
import pandas as pd
import json
import csv

## use to check the distribution of generated plot
# def plot_hist(rel_data): 
#     import matplotlib.pyplot as plt
#     data_array = np.array(rel_data)
#     fig, axes = plt.subplots(1, 5, figsize=(20,4))
#     bin_num = min(100, data_array.shape[0] // 10)
#     for i in range(data_array.shape[1]):
#         axes[i].hist(data_array[:,i], bins=bin_num, color="skyblue", edgecolor="black")
#         axes[i].set_title(f"Column {i+1}")
#         axes[i].set_xlabel("Value")
#         axes[i].set_ylabel("Frequency")

#     plt.tight_layout()
#     plt.show()


def sample_value(domain_values, dist_type, dist_params): 
    if dist_type == 'uniform':
        return random.choice(domain_values)
    
    # elif dist_type == 'zipf':
    #     while True:
    #         zipf_param = dist_params[0] if dist_params else 1.000001 # Zipf distribution parameter: > 1, larger: more skewed, smaller: more flat
    #         i = np.random.zipf(zipf_param) - 1 # np.random.zipf generates value in [1, inf), we shift to [0, inf)
    #         if i < len(domain_values): # truncate
    #             return domain_values[i]
            
    elif dist_type == 'normal':
        sigma_factor = dist_params[0] if dist_params else 6 # 6: simulate standard normal distribution
        mu = (len(domain_values) - 1) / 2
        sigma = len(domain_values) / sigma_factor
        for _ in range(10):
            i = int(np.random.normal(mu, sigma))
            if 0 <= i < len(domain_values):
                return domain_values[i]
        return random.choice(domain_values)
    
    else:
        raise ValueError(f"Unsupported dist_type: {dist_type}")
    
def fast_truncated_zipf(N, a, size):
    ks = np.arange(0, N)
    weights = 1 / (ks + 1)**a
    probs = weights / weights.sum()
    return np.random.choice(ks, size=size, p=probs)

# generate non-duplicate tuples with the identical distribution
def generate_relation_data(variables, domain_size, num_row, dist_type, dist_params):
    rel_data = []
    seen = set()
    
    attempts = 0
    max_attempts = 10 * num_row

    # try to keep unique tuples
    if dist_type == "normal" or dist_type == "uniform": 
        domain_values = [i for i in range(domain_size)]

        rel_data = []
        while len(rel_data) < num_row and attempts < max_attempts:

            tup = tuple(
                sample_value(domain_values, dist_type, dist_params)
                for var in variables
            )
            if tup not in seen:
                seen.add(tup)
                rel_data.append(tup)
            attempts += 1

    # may result large duplicates
    elif dist_type == "zipf": 
        batch = max(num_row // 10, 1000) * 2  
        zipf_param = dist_params[0] if dist_params else 1.000001
        for _ in range(max_attempts):
            X = np.column_stack([fast_truncated_zipf(domain_size, zipf_param, size=batch) 
                                 for var in variables])
            for row in map(tuple, X):
                if row not in seen:
                    seen.add(row)
                    rel_data.append(row)
                    if len(rel_data) >= num_row:
                        return rel_data
        # zipf_param = dist_params[0] if dist_params else 1.000001
        # def fast_truncated_zipf(N, a, size, seed=None):
        #     ks = np.arange(0, N)
        #     weights = 1 / (ks + 1)**a
        #     probs = weights / weights.sum()
        #     return np.random.choice(ks, size=size, p=probs)
        # var_num = len(variables)
        # rel_data = fast_truncated_zipf(domain_size, a=zipf_param, size=(num_row, var_num))
    else:
        raise ValueError(f"Unsupported dist_type: {dist_type}")
    
    return rel_data

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic data based on given parameters.")
    parser.add_argument("--query_file", type=str, default="query.json", help="Path to the query JSON file")
    parser.add_argument("--relation_type", type=str, help="Type of the relation to generate")
    parser.add_argument("--num_rows", type=int, nargs="*", required=True, help="Number of rows per relation.")
    parser.add_argument("--domain_type", type=str, choices=["large", "small", "half", "twice", 'q', 'four', 'x', 'ten', 'eight'], required=True, help="Type of domain size relative to num_rows.")
    parser.add_argument("--dist_type", type=str, required=True) 
    parser.add_argument("--dist_params", type=int, nargs="*", required=False, help="Parameters for the distribution types, if applicable.")
    parser.add_argument("--save_dir", type=str, required=False, help="Directory to save the generated data).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--extra", type=str, default='', help="Extra identifier for data generation.")
    args = parser.parse_args()

    # Load query configuration
    json_path = Path(args.query_file).resolve()
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file {json_path} does not exist.")


    json_obj = json.loads(json_path.read_text())
    relations = json_obj["query"]
    relation_type = args.relation_type if args.relation_type else json_path.parent.parent.name
    num_rows_list = args.num_rows 
    domain_type = args.domain_type
    dist_type = args.dist_type
    dist_params = args.dist_params if args.dist_params else []
    seed = args.seed 
    dist_str = f'{dist_type[0]}{dist_params}' if dist_params else dist_type[0]
    extra_str = f'_{args.extra}' if args.extra else ''
    data_dir_name = f'{relation_type}_{domain_type[0]}_{dist_str}_{seed}{extra_str}'
    data_dir = Path(args.save_dir).resolve() if args.save_dir else json_path.parent / data_dir_name
    if not data_dir.exists():
        os.makedirs(data_dir, exist_ok=True)

    random.seed(seed)
    np.random.seed(seed)

    for i, num_row in enumerate(num_rows_list): 
        
        data_dir_i = data_dir / f"{seed}_exp{i+1}_{num_row}"
        if not data_dir_i.exists():
            os.makedirs(data_dir_i, exist_ok=True)
        generate_data(
                                        relations=relations,
                                        num_row=num_row,
                                        domain_type=domain_type,
                                        dist_type=dist_type,
                                        dist_params=dist_params,
                                        data_dir=data_dir_i
                                    )
        

def generate_data(relations, num_row, domain_type, dist_type, dist_params, data_dir):
    if domain_type == "large": 
        # domain_size = num_row
        domain_size = int(num_row / 10)
    elif domain_type == "small": 
        # domain_size = int(sqrt(num_row)) + 1 
        domain_size = int(sqrt(num_row)) * 2
    # elif domain_type == "q": 
    #     domain_size = int(sqrt(num_row)) * 2
    # elif domain_type == "ten":
    #     domain_size = int(num_row / 10)
    else: 
        raise ValueError("Not supported domain type.")

    for rel in relations:
        rel_name = rel["relation_name"]
        rel_schema = rel["relation_schema"]
        has_header = rel.get("has_header", False)
        file_path = data_dir / rel["file_name"]

        rel_data = generate_relation_data(rel_schema, domain_size, 
                                          num_row, dist_type, dist_params)

        # Save the relation data to a CSV file
        df = pd.DataFrame(rel_data, columns=rel_schema if has_header else None)
        df.to_csv(file_path, index=False, header=has_header)

if __name__ == "__main__":
    main()

# Call main function
# python synthetic_data/data_generator.py --query_file synthetic_data/input/path3_full_smallds/full_query.json --num_rows 1000 1000 1000 --domain_type 'n_row' --dist_type 'uniform' --seed 123