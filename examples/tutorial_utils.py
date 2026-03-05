"""
Utility functions for the Algorithm Tutorial.

This module provides helper functions for loading and displaying datasets
in the tutorial notebooks.
"""

import pandas as pd
from pathlib import Path


def load_dataset(dir_path, atoms, show_data=True):
    """
    Load dataset from a given directory path.
    Read all CSV files in the directory and save to dictionary as the given atoms format.
    
    Parameters:
    -----------
    dir_path : str
        Path to the directory containing CSV files
    atoms : list of tuples
        List of (relation_name, tuple_of_column_names)
        Example: [('R', ('a', 'b')), ('S', ('b', 'c')), ('T', ('a', 'b', 'c'))]
    show_data : bool, default=True
        Whether to display the loaded data
    
    Returns:
    --------
    dict
        Dictionary mapping relation names to data dictionaries
        Example: {'R': {'a': [1,2,3], 'b': [4,5,6]}}
    """
    data = {}
    for atom_name, columns in atoms:
        file_path = Path(dir_path) / f"{atom_name}.csv"
        if file_path.exists():
            # Support any number of columns
            df = pd.read_csv(file_path, header=None, names=columns)
            data[atom_name] = {col: df[col].tolist() for col in columns}
        else:
            print(f"Warning: {file_path} does not exist.")
    
    if show_data:
        show_sample_data(data)
    return data


def show_sample_data(data):
    """
    Display sample data from the loaded dataset.
    
    Parameters:
    -----------
    data : dict
        Dictionary mapping relation names to data dictionaries
    """
    from IPython.display import display
    
    for atom_name, columns in data.items():
        print(f"\nAtom: {atom_name}")
        df = pd.DataFrame(columns)
        display(df)
