# %%
from select_k.Query import ConjunctiveQuery
from select_k.DirectAccessSum import DirectAccessSum
from pandasCompare import pandas_join_sum, verify_sum_all

def da_sum_getk(atoms, free_variables, sum_order, data, k): 
    cq = ConjunctiveQuery(atoms, free_variables, data = data, sum_order = sum_order)
    da_tree_sum = DirectAccessSum.create_and_prepare(cq)
    result = da_tree_sum.direct_access(k)
    return result

def da_sum_getall(atoms, free_variables, sum_order, data): 
    cq = ConjunctiveQuery(atoms, free_variables, sum_order = sum_order, data = data)
    da_tree_sum = DirectAccessSum.create_and_prepare(cq)
    result_ct = da_tree_sum.total_count
    results = []
    for k in range(result_ct):
        result = da_tree_sum.direct_access(k)
        results.append(result)
    return results
        
# %% 
"""
sum_order format
1. List: sort by the sum of variables in the list in ascending order
2. Dict: sort by the sum of variables in the list in ascending order, each one multiplied with the value in the dict
"""

# %%
# Case 1: 2 relations. 
atoms = [('P', ('a','b')), ('Q', ('b','c'))]
data = { 
        'P': { 
            'a': [2, 6, 1, 5, 1], 
            'b': [1, 2, 1, 2, 2], 
            }, 
        'Q': { 
            'b': [2, 1, 2, 1], 
            'c': [1, 2, 2, 3], 
            }, 
        }
# %%
# Case 1.1 all SUM order variables in free_variables, no disruptive trio
free_variables = ['a','b']
sum_order = {'a': 1, 'b': 1}

# Case 1.1 get single k
k = 1
result = da_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

# Case 1.1 get all k
print("Case 1.1 results for all k:")
results = da_sum_getall(atoms, free_variables, sum_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
verify_sum_all(pandas_df, results)

# %%
# Case: 2 relations with 3 variable
atoms = [('P', ('a','b','c')), ('Q', ('c','d'))]
data = { 
        'P': { 
            'a': [1, 2, 3, 1, 2], 
            'b': [1, 1, 2, 2, 2], 
            'c': [1, 2, 2, 3, 3],
            }, 
        'Q': { 
            'c': [2, 3], 
            'd': [1, 2], 
            }, 
        }

# Case: all free variables in one relation (P), SUM on subset
free_variables = ['a','b','c']
sum_order = {'a': 1, 'b': 1}

# Get single k
k = 1
result = da_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case (a,b,c)-(c,d) result for k=", k)
print(result)

# Get all k
print("Case (a,b,c)-(c,d) results for all k:")
results = da_sum_getall(atoms, free_variables, sum_order, data)
print(results)

# Verify with pandas
pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)
verify_sum_all(pandas_df, results)

# %%
# Case 3 : 2 relations with free variable in multiple relations
atoms = [('P', ('a','b','c')), ('Q', ('b','d'))]
data = { 
        'P': { 
            'a': [1, 2, 3, 1, 2], 
            'b': [1, 1, 2, 2, 3], 
            'c': [1, 2, 2, 3, 3],
            }, 
        'Q': { 
            'b': [2, 3, 4], 
            'd': [1, 2, 1], 
            }, 
        }

free_variables = ['a','b','c', 'd']
sum_order = {'a': 1, 'b': 1} 

# Get single k
k = 1
result = da_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case (a,b,c)-(c,d) result for k=", k)
print(result)

# Get all k
print("\nCase (a,b,c)-(c,d) with sum_order {'a': 1, 'b': 1}:")
results = da_sum_getall(atoms, free_variables, sum_order, data)
print(results)

# Verify with pandas
pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)
verify_sum_all(pandas_df, results)


# %%
