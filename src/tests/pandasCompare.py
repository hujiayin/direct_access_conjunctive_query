import pandas as pd

# Helper function for joining relations with projection
def pandas_join_relations(atoms, data, free_variables):
    """
    Join relations with algebraic projection to free_variables.
    Returns the joined DataFrame with duplicates removed.
    """
    df_result = None
    for rel_name, rel_vars in atoms:
        df_current = pd.DataFrame({var: data[rel_name][var] for var in rel_vars})

        if df_result is None:
            df_result = df_current
        else:
            common_vars = list(set(df_result.columns).intersection(set(df_current.columns)))
            if common_vars:
                df_result = df_result.merge(df_current, on=common_vars, how='inner')
            else:
                df_result['__tmp_key'] = 1
                df_current['__tmp_key'] = 1
                df_result = df_result.merge(df_current, on='__tmp_key').drop(columns='__tmp_key')
        
        # Algebraic projection operation: project to free_variables and remove duplicates
        projection_cols = [col for col in free_variables if col in df_result.columns]
        df_result = df_result[projection_cols].drop_duplicates().reset_index(drop=True)

    return df_result

# Lexicographic order join result: for reference
def pandas_join_lex(atoms, data, lex_order, free_variables, output_variables=None):
    df_result = pandas_join_relations(atoms, data, free_variables)

    if isinstance(lex_order, list):
        # List format: sort by columns in ascending order
        sort_cols = [v for v in lex_order if v in df_result.columns]
        df_result = df_result.sort_values(by=sort_cols).reset_index(drop=True)
    elif isinstance(lex_order, dict):
        # Dict format: 1 for ascending, -1 for descending
        sort_cols = [v for v in lex_order.keys() if v in df_result.columns]
        ascending_list = [lex_order[v] == 1 for v in sort_cols]
        df_result = df_result.sort_values(by=sort_cols, ascending=ascending_list).reset_index(drop=True)
    else:
        raise ValueError("Invalid lex_order format")
    
    # Select output_variables for final output
    if output_variables is None:
        output_variables = free_variables
    output_cols = [col for col in output_variables if col in df_result.columns]
    df_output = df_result[output_cols]
    return df_output

# SUM order join and sort result: for reference
def pandas_join_sum(atoms, data, sum_order, free_variables, output_variables=None):
    df_result = pandas_join_relations(atoms, data, free_variables)

    if isinstance(sum_order, list):
        sort_cols = [v for v in sum_order if v in df_result.columns]
        df_result['__sum'] = df_result[sort_cols].sum(axis=1)
        df_result = df_result.sort_values(by='__sum').reset_index(drop=True)
    elif isinstance(sum_order, dict):
        sort_cols = [v for v in sum_order if v in df_result.columns]
        df_result['__sum'] = df_result[list(sum_order.keys())].mul(list(sum_order.values()), axis=1).sum(axis=1)
        df_result = df_result.sort_values(by='__sum').reset_index(drop=True)
    else:
        # If sum_order is not a list or dict, throw error
        raise ValueError("Invalid sum_order format")
    
    # Select output_variables and sum for final output
    if output_variables is None:
        output_variables = free_variables
    output_cols = [col for col in output_variables if col in df_result.columns] + ['__sum']
    df_output = df_result[output_cols]
    return df_output

# verify direct access / single access results - LEX
# for LEX order, we compare the entire k-th row, we only check correctness ranked column(s) 
def verify_lex_k(pandas_df, access_result, lex_order, k):
    ranked_cols = [v for v in lex_order if v in pandas_df.columns and (lex_order[v] == 1 or lex_order[v] == -1)]
    pandas_res = pandas_df[ranked_cols].iloc[k].to_dict()  # Get k-th row as dictionary
    access_result = {col: access_result[col] for col in ranked_cols}
    assert pandas_res == access_result, f"LEX order verification FAILED for the {k} record."
    print(f"LEX order verification passed for the {k} record.")

def verify_lex_all(pandas_df, access_results, lex_order):
    assert len(pandas_df) == len(access_results), "Number of results mismatch between pandas and access results."
    for k, access_result in enumerate(access_results):
        verify_lex_k(pandas_df, access_result, lex_order, k)

# verify direct access / single access results - SUM
# for SUM order, we only check sum column correctness
def verify_sum_k(pandas_df, access_result, k):
    pandas_sum = pandas_df['__sum'].tolist()[k]
    access_sum = access_result['__sum']
    assert pandas_sum == access_sum, f"SUM order verification FAILED for the {k} record."
    print(f"SUM order verification passed for the {k} record.")

def verify_sum_all(pandas_df, access_results):
    assert len(pandas_df) == len(access_results), "Number of results mismatch between pandas and access results."
    for k, access_result in enumerate(access_results):
        verify_sum_k(pandas_df, access_result, k)




