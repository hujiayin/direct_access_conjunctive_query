# %%
from select_k.Selection import Selection
from select_k.Query import ConjunctiveQuery
from pandasCompare import pandas_join_lex, verify_lex_all, verify_lex_k


# %%
def sa_lex_getk(atoms, free_variables, lex_order, data, k): 
    cq = ConjunctiveQuery(atoms, free_variables, lex_order = lex_order, data = data)
    result = Selection.get_selectk_result(cq, k)
    return result

def sa_lex_getall(atoms, free_variables, lex_order, data):
    results = []
    k = 0
    while True:
        cq = ConjunctiveQuery(atoms, free_variables, lex_order = lex_order, data = data)
        try:
            result = Selection.get_selectk_result(cq, k)
            results.append(result)
            k += 1
        except Exception:
            break
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
k = 0
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

# Case 1.1 get all k
print("Case 1.1 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)


# %%
# Case 1.2 full lex order, no disruptive trio
free_variables = ['a','b','c']
lex_order = {'b': 1, 'a': 1, 'c': 1}

# Case 1.2 get single k
k = 5
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 1.2 result for k=", k)
print(result)

# Case 1.2 get all k
print("Case 1.2 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)


# %%
# Case 1.3 full lex order, with disruptive trio
free_variables = ['a','b','c']
lex_order = {'a': 1, 'c': 1, 'b': 1} # {'c': 1, 'a': 1, 'b': 1}

# Case 1.3 get single k
k = 2
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 1.3 result for k=", k)
print(result)

# Case 1.3 get all k
print("Case 1.3 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 1.4 partial lex order, no disruptive trio
free_variables = ['a','b','c']
lex_order = {'a': 1, 'b': 1}

# Case 1.4 get single k
k = 2
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 1.4 result for k=", k)
print(result)

# Case 1.4 get all k
print("Case 1.4 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)
# %%
# Case 1.5 full lex order, not L-connex
free_variables = ['a','b','c']
lex_order = {'a': 1, 'c': 1}

# Case 1.5 get single k
k = 0
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 1.5 result for k=", k)
print(result)

print("Case 1.5 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)


# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)
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
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.1 result for k=", k)
print(result)

results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)

# verify all 
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 2.2 full lex order, with disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': 1, 'c': 1, 'b': 1, 'd': 1}
# Case 2.2 get single k
k = 1
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.2 result for k=", k)
print(result)

results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)

# verify all 
verify_lex_all(pandas_df, results, lex_order)
# %%
# Case 2.3.1 partial lex order, no disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': -1, 'b': -1, 'c': -1}
# Case 2.3 get single k
k = 1
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.3 result for k=", k)
print(result)

# Case 2.3 get all k
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)

verify_lex_all(pandas_df, results, lex_order)

# %%
# %%
# Case 2.3.2 partial lex order, no disruptive trio, fewer free variables
free_variables = ['a', 'b', 'c']
lex_order = {'a': -1, 'b': -1, 'c': -1}
# Case 2.3 get single k
k = 1
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.3 result for k=", k)
print(result)

# Case 2.3 get all k
results = sa_lex_getall(atoms, free_variables, lex_order, data)
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
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 2.4 result for k=", k)
print(result)

results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)

# verify all 
verify_lex_all(pandas_df, results, lex_order)


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
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 3.1 result for k=", k)
print(result)

# Case 3.1 get all k
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 3.2 full lex order, with disruptive trio
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': 1, 'c': 1, 'b': 1, 'd': 1}
# Case 3.2 get single k
k = 1
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 3.2 result for k=", k)
print(result)

# Case 3.2 get all k
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 3.3 full lex order, not L-connex
free_variables = ['a', 'b', 'c', 'd']
lex_order = {'a': 1, 'b': 1, 'd': 1}
# Case 3.3 get single k
k = 1
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)

# Case 3.3 get all k
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
verify_lex_all(pandas_df, results, lex_order)


# %%
# Case 4: 2 relations, cartesian product. 
atoms = [('P', ('a','b')), ('Q', ('c','d'))]
data = { 
        'P': { 
            'a': [2, 6, 1, 5], 
            'b': [1, 2, 1, 2], 
            }, 
        'Q': { 
            'c': [2, 1, 2, 1], 
            'd': [1, 2, 2, 3], 
            }, 
        }
# %%
# Case 4.1 full lex order, no disruptive trio
free_variables = ['a','b','c','d']
lex_order = {'a': 1, 'b': 1, 'c': 1, 'd': 1}

# Case 4.1 get single k
k = 2
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 4.1 result for k=", k)
print(result)

# %%

# Case 4.1 get all k
print("Case 4.1 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)


# %%
# Case 4.2 full lex order, no disruptive trio
free_variables = ['a','b','c','d']
lex_order = {'b': 1, 'a': 1, 'c': 1, 'd': 1}

# Case 4.2 get single k
k = 5
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 4.2 result for k=", k)
print(result)

# Case 4.2 get all k
print("Case 4.2 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)
# %%
# Case 4.3 partial lex order, with disruptive trio
free_variables = ['a','b','c']
lex_order = {'a': 1, 'c': 1, 'b': 1} # {'c': 1, 'a': 1, 'b': 1}

# Case 4.3 get single k
k = 2
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 4.3 result for k=", k)
print(result)

# Case 4.3 get all k
print("Case 4.3 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)

# %%
# Case 4.4 partial lex order, no disruptive trio
free_variables = ['a','b','c','d']
lex_order = {'a': 1, 'd': 1}

# Case 4.4 get single k
k = 2
result = sa_lex_getk(atoms, free_variables, lex_order, data, k)
print("Case 4.4 result for k=", k)
print(result)

# Case 4.4 get all k
print("Case 4.4 results for all k:")
results = sa_lex_getall(atoms, free_variables, lex_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_lex(atoms, data, lex_order, free_variables)
print(pandas_df)
verify_lex_all(pandas_df, results, lex_order)
# %%