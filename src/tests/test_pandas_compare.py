# %%
from tests.pandasCompare import pandas_join_lex, pandas_join_sum

# %%
# Test 1: Basic join with 2 relations
free_variables = ['a', 'b', 'c']
output_variables = ['a', 'b', 'c']
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

# Test 1 LEX - lexicographic order
lex_order = {'c': 1, 'a': 1}  # Sort by c ascending, then a ascending
df_result_lex = pandas_join_lex(atoms, data, lex_order, free_variables, output_variables)
print("Test 1 LEX - Basic join with dict lex_order:", lex_order)
print(df_result_lex)
print()

# Test 1 SUM - Using sum_order
sum_order = {'c':1, 'a':1, }
df_result_sum = pandas_join_sum(atoms, data, sum_order, free_variables, output_variables)
print("Test 1 - Basic join with dict sum_order:", sum_order)
print(df_result_sum)
print()

# %%
# Test 2: Using list order
print("Test 2 - List order:")
free_variables = ['a', 'b', 'c']
output_variables = ['a', 'c']
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

# Test 2 LEX - lexicographic order
lex_order = ['a', 'c']  # Sort by a, then c (all ascending)
df_result_lex = pandas_join_lex(atoms, data, lex_order, free_variables, output_variables)
print("Test 2 LEX - List lex_order:", lex_order)
print(df_result_lex)
print()

# Test 2 SUM - Using sum_order
sum_order = ['a', 'c']
df_result_sum = pandas_join_sum(atoms, data, sum_order, free_variables, output_variables)
print("Test 2 SUM - List sum_order:", sum_order)
print(df_result_sum)
print()

# %%
# Test 3: Testing projection with duplicates removal
print("Test 3 - Projection with duplicate removal:")
free_variables = ['a', 'c']  # Projecting out variable 'b'
output_variables = ['a', 'c']
atoms = [('P', ('a', 'b')), ('Q', ('b', 'c'))]

data = {
    'P': {
        'a': [1, 1, 2],  # Note: repeated 'a' values
        'b': [1, 2, 1],
    },
    'Q': {
        'b': [1, 2, 1],
        'c': [3, 3, 2],  # Note: repeated 'c' values
    },
}

# Test 3 LEX - Same data, lexicographic order
lex_order = {'a': 1, 'c': 1}  # Sort by a ascending, then c ascending
df_result_lex = pandas_join_lex(atoms, data, lex_order, free_variables, output_variables)
print("Test 3 LEX - Projection with duplicate removal:", lex_order)
print(df_result_lex)
print()

# Test 3 SUM - Using sum_order
sum_order = {'a': 1, 'c': 1} # sort by a+c
df_result_sum = pandas_join_sum(atoms, data, sum_order, free_variables, output_variables)
print("Test 3 SUM - Projection with duplicate removal:", sum_order)
print(df_result_sum)
print()

# %%
# Test 4: Three-way join
print("Test 4 - Three-way join:")
free_variables = ['a', 'b', 'c', 'd']
output_variables = ['a', 'b', 'c', 'd']
atoms = [('P', ('a', 'b')), ('Q', ('b', 'c')), ('R', ('c', 'd'))]

data = {
    'P': {
        'a': [1, 2, 3],
        'b': [1, 1, 2],
    },
    'Q': {
        'b': [1, 2],
        'c': [1, 1],
    },
    'R': {
        'c': [1, 2],
        'd': [5, 6],
    },
}

# Test 4 LEX - lexicographic order
lex_order = {'a': 1, 'd': 1}  # Sort by a ascending, then d ascending
df_result_lex = pandas_join_lex(atoms, data, lex_order, free_variables, output_variables)
print("Test 4 LEX - Three-way join:", lex_order)
print(df_result_lex)
print()

# Test 4 SUM - Using sum_order
sum_order = {'a': 2, 'd': 1} # sort by 2*a + d
df_result_sum = pandas_join_sum(atoms, data, sum_order, free_variables, output_variables)
print("Test 4 SUM - Three-way join:", sum_order)
print(df_result_sum)
print()

# %%
# Test 5: Cartesian product (no common variables)
print("Test 5 - Cartesian product (no join keys):")
free_variables = ['a', 'c']
output_variables = ['a', 'c']
atoms = [('P', ('a',)), ('Q', ('c',))]

data = {
    'P': {
        'a': [1, 2],
    },
    'Q': {
        'c': [3, 4],
    },
}

# Test 5 LEX - lexicographic order
lex_order = ['a', 'c']  # Sort by a, then c
df_result_lex = pandas_join_lex(atoms, data, lex_order, free_variables, output_variables)
print("Test 5 LEX - Cartesian product (no join keys):", lex_order)
print(df_result_lex)
print()

# Test 5 SUM - Using sum_order
sum_order = ['a', 'c'] # sort by a+c
df_result_sum = pandas_join_sum(atoms, data, sum_order, free_variables, output_variables)
print("Test 5 SUM - Cartesian product (no join keys):", sum_order)
print(df_result_sum)
print()

# %%
