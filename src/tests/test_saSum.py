# %%
from select_k.Query import ConjunctiveQuery
from select_k.Selection_Sum import Selection_Sum
from pandasCompare import pandas_join_sum, verify_sum_all

def sa_sum_getk(atoms, free_variables, sum_order, data, k): 
    cq = ConjunctiveQuery(atoms, free_variables, data = data, sum_order = sum_order)
    select_cq = Selection_Sum(cq)
    result = select_cq.select_k(k)
    return result

def sa_sum_getall(atoms, free_variables, sum_order, data):
    results = []
    k = 0
    while True:
        cq = ConjunctiveQuery(atoms, free_variables, data = data, sum_order = sum_order)
        try:
            select_cq = Selection_Sum(cq)
            result = select_cq.select_k(k)
            print("k =", k, "result =", result)
            results.append(result)
            k += 1
        except Exception as e:
            print("Exception occurred:", e)
            break
    return results

        
# %% 
"""
sum_order format
1. List: sort by the sum of variables in the list in ascending order
2. Dict: sort by the sum of variables in the list in ascending order, each one multiplied with the value in the dict
"""

# %%
# Case 1: 2 relations. 
atoms = [('P', ('a', 'b')), ('Q', ('b', 'c'))]

data = {
    'P': {
        'a': [1, 5, 2],
        'b': [1, 2, 1],
    },
    'Q': {
        'b': [2, 1, 2],
        'c': [1, 3, 2],
    },
}

# Case 1.1 all SUM order variables in free_variables, no disruptive trio
free_variables = ['a', 'b', 'c']
sum_order = {'c':-1, 'a':1, }

# Case 1.1 get single k
k = 1
result = sa_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

# Case 1.1 get all k
print("Case 1.1 results for all k:")
results = sa_sum_getall(atoms, free_variables, sum_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)
verify_sum_all(pandas_df, results)

# %%
atoms = [('P', ('a', 'b')), ('Q', ('c'))]

data = {
    'P': {
        'a': [1, 5, 2],
        'b': [1, 2, 1],
    },
    'Q': {
        'c': [1, 3, 2],
    },
}
free_variables = ['a', 'b', 'c']
sum_order = {'c':-1, 'a':1, }
k = 8
result = sa_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

results = sa_sum_getall(atoms, free_variables, sum_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)
verify_sum_all(pandas_df, results)

# %%
atoms = [('P', ('a', 'b')), ('Q', ('c')), ('R', ('d'))]

data = {
    'P': {
        'a': [1, 5, 2],
        'b': [1, 2, 1],
    },
    'Q': {
        'c': [1, 3, 2],
    },
    'R': {
        'd': [1, 2, 3],
    },
}
free_variables = ['a', 'b', 'c', 'd']
sum_order = {'c':-1, 'a':1, }
k = 9
result = sa_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

results = sa_sum_getall(atoms, free_variables, sum_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)
verify_sum_all(pandas_df, results)

# %%
atoms = [('P', ('a', 'b')), ('Q', ('c', 'd')), ('R', ('c','e'))]

data = {
    'P': {
        'a': [1, 5, 2],
        'b': [1, 2, 1],
    },
    'Q': {
        'c': [1, 3, 2, 5],
        'd': [1, 2, 3, 1],
    },
    'R': {
        'c': [1, 2, 3, 4],
        'e': [1, 2, 3, 1],
    },
}
free_variables = ['a', 'b', 'c', 'd' 'e']
sum_order = {'c':-1, 'a':1, }

k = 8
result = sa_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

results = sa_sum_getall(atoms, free_variables, sum_order, data)
print(results)

# verify with pandas
pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)
verify_sum_all(pandas_df, results)
# %%
atoms = [('P', ('a', 'b')), ('Q', ('b', 'c')), ('R', ('c','d'))]

data = {
    'P': {
        'a': [1, 5, 2],
        'b': [1, 2, 1],
    },
    'Q': {
        'b': [1, 1, 2],
        'c': [1, 2, 3],
    },
    'R': {
        'c': [1, 3, 2],
        'd': [1, 2, 3],
    },
}
free_variables = ['a', 'b', 'c', 'd']
sum_order = {'a':1, 'c':1, }

k = 2
result = sa_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

results = sa_sum_getall(atoms, free_variables, sum_order, data)
print(results)

pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)

verify_sum_all(pandas_df, results)

# %%
atoms = [('P', ('a', 'b')), ('Q', ('b', 'c')), ('R', ('c','d'))]

data = {
    'P': {
        'a': [1, 5, 2],
        'b': [1, 2, 1],
    },
    'Q': {
        'b': [1, 3, 2],
        'c': [1, 2, 3],
    },
    'R': {
        'c': [1, 2, 2],
        'd': [1, 2, 3],
    },
}
free_variables = ['a', 'b', 'c', 'd']
sum_order = {'a':1, 'b':1, 'c':1, }

k = 1
result = sa_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

results = sa_sum_getall(atoms, free_variables, sum_order, data)
print(results)

pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)

verify_sum_all(pandas_df, results)
# %%
atoms = [
    ('R', ('a', 'b')),
    ('S', ('a', 'c')),
    ('T', ('a', 'd')),
    ('U', ('a', 'e')),
]
data = {
    'R': {
        'a': [3, 3, 1, 2, 4, 5],
        'b': [1, 2, 3, 1, 4, 1],
    },
    'S': {
        'a': [3, 0, 1, 4, 5, 3],
        'c': [2, 3, 5, 1, 2, 4],
    },
    'T': {
        'a': [3, 3, 2, 1, 1, 5],
        'd': [1, 2, 3, 3, 1, 2],
    },
    'U': {
        'a': [3, 3, 2, 4, 5, 3],
        'e': [1, 2, 3, 1, 2, 4],
    }
}
free_variables = ['a', 'b', 'c', 'd', 'e']
sum_order = {'b': 1, 'c': 1}

k = 1
result = sa_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

results = sa_sum_getall(atoms, free_variables, sum_order, data)
print(results)

pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)

verify_sum_all(pandas_df, results)
# %%
# %%
atoms = [('P', ('a', 'b')), ('Q', ('b', 'c')), ('R', ('c','d'))]

data = {
    'P': {
        'a': [1, 5, 2],
        'b': [1, 2, 1],
    },
    'Q': {
        'b': [1, 3, 2],
        'c': [1, 2, 3],
    },
    'R': {
        'c': [1, 2, 2],
        'd': [1, 2, 3],
    },
}
free_variables = ['a', 'b', 'c', 'd']
sum_order = {'a':1, 'b':1}

k = 1
result = sa_sum_getk(atoms, free_variables, sum_order, data, k)
print("Case 1.1 result for k=", k)
print(result)

results = sa_sum_getall(atoms, free_variables, sum_order, data)
print(results)

pandas_df = pandas_join_sum(atoms, data, sum_order, free_variables)
print("Pandas result:")
print(pandas_df)

verify_sum_all(pandas_df, results)
# %%
