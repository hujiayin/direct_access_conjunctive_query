# %%
from select_k.LayeredAlgorithm import LayeredJoinTree
from select_k.Query import ConjunctiveQuery
from pandasCompare import pandas_join_lex, verify_lex_all

# %%
def da_lex_getk(atoms, free_variables, lex_order, data, k): 
    cq = ConjunctiveQuery(atoms, free_variables, lex_order = lex_order, data = data)
    da_tree = LayeredJoinTree.create_and_prepare(cq)
    result = da_tree.direct_access(k)
    return result

def da_lex_getall(atoms, free_variables, lex_order, data): 
    cq = ConjunctiveQuery(atoms, free_variables, lex_order = lex_order, data = data)
    da_tree = LayeredJoinTree.create_and_prepare(cq)
    result_ct = da_tree.direct_access_tree[1].buckets[()]['weight']
    results = []
    for k in range(result_ct):
        result = da_tree.direct_access(k)
        results.append(result)
    return results

# %%
# Case 1: 2 relations. 
atoms = [('P', ('a','b')), ('Q', ('b','c'))]
data = { 
        'P': { 
            'a': [2, 6, 1, 5], 
            'b': [1, 2, 1, 2], 
            }, 
        'Q': { 
            'b': [2, 1, 2, 1], 
            'c': [1, 2, 2, 3], 
            }, 
        }
# %%
# Case 1.1 full lex order, no disruptive trio
free_variables = ['a','b','c']
lex_order = {'a': 1, 'b': 1, 'c': 1}

# Case 1.1 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

# Case 1.1 get all k
print("Case 1.1 results for all k:")
results = da_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
verify_lex_all(pandas_df, results, lex_order)


# %%
# Case 1.2 full lex order, no disruptive trio
free_variables = ['a','b','c']
lex_order = {'b': 1, 'a': 1, 'c': 1}

# Case 1.2 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 1.2 result for k=", k)
print(result)

# Case 1.2 get all k
print("Case 1.2 results for all k:")
results = da_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 1.3 full lex order, with disruptive trio
free_variables = ['a','b','c']
lex_order = {'a': 1, 'c': 1, 'b': 1} # {'c': 1, 'a': 1, 'b': 1}

# Case 1.3 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
# case raises error due to disruptive trio

# %%
# Case 1.4 partial lex order, no disruptive trio
free_variables = ['a','b','c']
lex_order = {'a': 1, 'b': 1}

# Case 1.4 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 1.4 result for k=", k)
print(result)

# Case 1.4 get all k
results = da_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(lex_order)
verify_lex_all(pandas_df, results, lex_order)


# %%
# Case 1.4 full lex order, not L-connex
free_variables = ['a','b','c']
lex_order = {'a': 1, 'c': 1}

# Case 1.4 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
# case raises error due to not L-connex order
# %%
# Case 2: 3 relations - path.
atoms = [
    ('P', ('a', 'b')),
    ('Q', ('b', 'c')),
    ('R', ('c', 'd')),
]
data = {
    'P': {
        'a': [1, 2, 3, 3],
        'b': [1, 1, 2, 3],
    },
    'Q': {
        'b': [1, 2, 2, 3],      
        'c': [10, 20, 30, 30], 
    },
    'R': {
        'c': [10, 20, 30, 30, 31], 
        'd': [7,  8,  9,  10, 11],
    },
}

# %%
# Case 2.1 full lex order, no disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': -1, 'b': -1, 'c': -1, 'd': -1}
# Case 2.1 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.1 result for k=", k)
print(result)

# Case 2.1 get all k
results = da_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(lex_order)
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 2.2 full lex order, with disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': 1, 'c': 1, 'b': 1, 'd': 1}
# Case 2.2 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)

# %%
# Case 2.3.1 partial lex order, no disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': -1, 'b': -1, 'c': -1}
# Case 2.3 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.3 result for k=", k)
print(result)

# Case 2.3 get all k
results = da_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(lex_order)
verify_lex_all(pandas_df, results, lex_order)

# %%
# %%
# Case 2.3.2 partial lex order, no disruptive trio, fewer free variables
free_variables = ['a', 'b', 'c']
lex_order = {'a': -1, 'b': -1, 'c': -1}
# Case 2.3 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.3 result for k=", k)
print(result)

# Case 2.3 get all k
results = da_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(lex_order)
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 2.4 partial lex order, no disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': -1, 'b': -1, 'd': -1}
# Case 2.4 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.4 result for k=", k)
print(result)

# %%
# %%
# Case 3: 3 relations - star.
atoms = [
    ('P', ('a', 'b')),
    ('Q', ('b', 'c')),
    ('R', ('b', 'd')),
]
data = {
    'P': {
        'a': [1, 2, 3, 1],
        'b': [1, 1, 2, 2],
    },
    'Q': {
        'b': [1, 1, 2, 1],
        'c': [10, 11, 20, 20], 
    },
    'R': {
        'b': [1, 2, 1, 2],
        'd': [7,  8,  9,  9],  
    },
}
# %%
# Case 3.1 full lex order, no disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'b': -1, 'a': -1, 'c': -1, 'd': -1}
# Case 3.1 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 3.1 result for k=", k)
print(result)

# Case 3.1 get all k
results = da_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(lex_order)
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 3.2 full lex order, with disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': 1, 'c': 1, 'b': 1, 'd': 1}
# Case 3.2 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)

# %%
# Case 3.3 full lex order, not L-connex
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': 1, 'b': 1, 'd': 1}
# Case 3.3 get single k
k = 1
result = da_lex_getk(atoms, free_variables, lex_order, data, k)
# case raises error due to not L-connex order

