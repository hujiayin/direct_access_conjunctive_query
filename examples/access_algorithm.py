"""
Unified interface for Direct Access and Single Access algorithms.

This module provides the AccessAlgorithm class that wraps all access algorithms
for both LEX and SUM ordering with Direct and Single access methods.
"""

from select_k.LayeredAlgorithm import LayeredJoinTree
from select_k.DirectAccessSum import DirectAccessSum
from select_k.Selection import Selection
from select_k.Selection_Sum import Selection_Sum
from select_k.Query import ConjunctiveQuery


class AccessAlgorithm:
    """
    Unified interface for Direct Access and Single Access algorithms.
    
    Supports:
    - Direct Access: LEX order, SUM order
    - Single Access: LEX order, SUM order
    
    Usage Examples:
    ---------------
    # Direct Access with LEX order
    algo = AccessAlgorithm(atoms, data, free_variables, 
                           order_type='lex', lex_order={'a': 1, 'b': 1},
                           access_type='direct')
    result = algo.get_k(5)
    total = algo.get_total_count()
    all_results = algo.get_all()
    
    # Single Access with SUM order
    algo = AccessAlgorithm(atoms, data, free_variables,
                           order_type='sum', sum_order={'a': 1, 'b': -1},
                           access_type='single')
    result = algo.get_k(10)
    first_n = algo.get_all(limit=10)
    """
    
    def __init__(self, atoms, data, free_variables, 
                 order_type='lex', lex_order=None, sum_order=None,
                 access_type='direct'):
        """
        Initialize the algorithm wrapper.
        
        Parameters:
        -----------
        atoms : list of tuples
            List of (relation_name, tuple_of_variables)
            Example: [('R', ('a', 'b')), ('S', ('b', 'c'))]
            
        data : dict
            Dictionary mapping relation names to data
            Example: {'R': {'a': [1,2,3], 'b': [4,5,6]}}
            
        free_variables : list
            List of free variables
            Example: ['a', 'b', 'c']
            
        order_type : str, default='lex'
            Type of ordering: 'lex' or 'sum'
            
        lex_order : dict/list, optional
            Lexicographic order specification
            Example: {'a': 1, 'b': 1, 'c': -1} (1=ascending, -1=descending)
            
        sum_order : dict, optional
            Sum order specification with weights
            Example: {'a': 1, 'b': -1}
            
        access_type : str, default='direct'
            Type of access: 'direct' or 'single'
        """
        self.atoms = atoms
        self.data = data
        self.free_variables = free_variables
        self.order_type = order_type.lower()
        self.access_type = access_type.lower()
        self.lex_order = lex_order
        self.sum_order = sum_order
        
        # Validate inputs
        if self.order_type not in ['lex', 'sum']:
            raise ValueError("order_type must be 'lex' or 'sum'")
        if self.access_type not in ['direct', 'single']:
            raise ValueError("access_type must be 'direct' or 'single'")
        if self.order_type == 'lex' and lex_order is None:
            raise ValueError("lex_order must be provided when order_type='lex'")
        if self.order_type == 'sum' and sum_order is None:
            raise ValueError("sum_order must be provided when order_type='sum'")
            
        # Preprocessing for direct access
        self.preprocessed = None
        if self.access_type == 'direct':
            self._preprocess()
    
    def _preprocess(self):
        """Preprocess data structure for direct access."""
        if self.order_type == 'lex':
            # Direct Access LEX
            cq = ConjunctiveQuery(self.atoms, self.free_variables, 
                                lex_order=self.lex_order, data=self.data)
            self.preprocessed = LayeredJoinTree.create_and_prepare(cq)
        else:
            # Direct Access SUM
            cq = ConjunctiveQuery(self.atoms, self.free_variables,
                                sum_order=self.sum_order, data=self.data)
            self.preprocessed = DirectAccessSum.create_and_prepare(cq)
    
    def get_k(self, k):
        """
        Get the k-th result (0-indexed).
        
        Parameters:
        -----------
        k : int
            The index of the result to retrieve (0-indexed)
            
        Returns:
        --------
        dict
            The k-th result as a dictionary mapping variables to values
        """
        if self.access_type == 'direct':
            return self._direct_access_k(k)
        else:
            return self._single_access_k(k)
    
    def _direct_access_k(self, k):
        """Direct access for k-th result."""
        if self.preprocessed is None:
            raise RuntimeError("Preprocessing failed")
        return self.preprocessed.direct_access(k)
    
    def _single_access_k(self, k):
        """Single access for k-th result."""
        if self.order_type == 'lex':
            # Single Access LEX
            cq = ConjunctiveQuery(self.atoms, self.free_variables,
                                lex_order=self.lex_order, data=self.data)
            return Selection.get_selectk_result(cq, k)
        else:
            # Single Access SUM
            cq = ConjunctiveQuery(self.atoms, self.free_variables,
                                sum_order=self.sum_order, data=self.data)
            select_cq = Selection_Sum(cq)
            return select_cq.select_k(k)
    
    def get_all(self, limit=None):
        """
        Get all results (or up to limit).
        
        Parameters:
        -----------
        limit : int, optional
            Maximum number of results to retrieve
            
        Returns:
        --------
        list of dict
            List of all results
        """
        results = []
        k = 0
        
        # Determine total count for direct access
        if self.access_type == 'direct':
            if self.order_type == 'lex':
                total_count = self.preprocessed.direct_access_tree[1].buckets[()]['weight']
            else:
                total_count = self.preprocessed.total_count
            max_k = min(total_count, limit) if limit else total_count
        else:
            max_k = limit if limit else float('inf')
        
        while k < max_k:
            try:
                result = self.get_k(k)
                results.append(result)
                k += 1
            except Exception as e:
                # No more results
                break
                
        return results
    
    def get_total_count(self):
        """
        Get total number of results (only for direct access).
        
        Returns:
        --------
        int
            Total count of results
            
        Raises:
        -------
        NotImplementedError
            If called on single access algorithm
        """
        if self.access_type != 'direct':
            raise NotImplementedError("Total count only available for direct access")
            
        if self.order_type == 'lex':
            return self.preprocessed.direct_access_tree[1].buckets[()]['weight']
        else:
            return self.preprocessed.total_count
