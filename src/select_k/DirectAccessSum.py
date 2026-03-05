from select_k.Query import ConjunctiveQuery
from select_k.JoinTreeNode import JoinTreeNode
from select_k.Relation import Relation

class DirectAccessSum:
    def __init__(self, cq: ConjunctiveQuery):
        """
        Initialize DirectAccessSum Class to determine if it is possible. 
        Variables in SUM are in the same relation. 
        The implementation supports DirectAccess for SUM order for the following conditions:
            1. All free variables are in SUM relation; or
            2. Some variables are not in SUM relation. 
        """
        self.query = cq
        if self.query.sum_order.keys() - set(self.query.free_vars) != set(): 
            raise Exception("NOT Supported: Some SUM variables are not free variables.")
        # check tractability: free-connex and all variables in SUM are from the same relation. 
        if self.query.free_connex and self.query.is_sum_in_one_relation: 
            print('Tractable for Direct Access for SUM order.') 
        else: 
            raise Exception("NOT Tractable for Direct Access for SUM order.")
        self.root = None
        self.preprocess_results = None
        self.direct_access_tree = {}
        self.quick_access = False
        self.post_order = None
        self.total_count = None

    # def preprocess_only_sum_var(self):
    #     """
    #     Preprocess the Join Tree for Direct Access for SUM order. 
    #     Case 1: Var_free - Var_sum = empty
    #         1. bottom-up semi-join reduction;
    #         2. calculate SUM of free variables on the root node. 
    #         3. Sort by SUM. 
    #     # return a list of (projected_dict, SUM) sorted by SUM
    #     """
    #     # bottom-up semi-join reduction
    #     ConjunctiveQuery.semi_join_bottom_up(self.root) 

    #     var_map = {v: self.root.variables.index(v) for v in self.query.sum_order.keys()}

        
        
    #     sum_results = project_sort_weighted(self.root.instance_row, self.root.variables, self.query.sum_order)

    #     return sum_results
    
    # Helper function to project and sort by weighted sum
    # def project_sort_weighted(instance_row, variables, sum_order):
    #     var_info = [(var, variables.index(var), weight) for var, weight in sum_order.items()]

    #     # project to score variables and remove duplicates
    #     unique_proj = {
    #         tuple(row[i] for _, i, _ in var_info) for row in instance_row
    #     }

    #     result = []
    #     for proj in unique_proj:
    #         proj_dict = {var: proj[idx] for idx, (var, _, _) in enumerate(var_info)}
    #         score = sum(proj_dict[var] * weight for var, _, weight in var_info)
    #         result.append((proj_dict, score))

    #     result.sort(key=lambda pair: pair[1])
    #     return result

    def preprocess(self): 
        # free variables at least include those in SUM
        sum_set = set(self.query.sum_order.keys())
        free_set = set(self.query.free_vars)
        atoms = self.query.atoms
        free_set_candidates = list(filter(lambda r: free_set.issubset(r.variables), atoms))
        sum_order = self.query.sum_order

        
        # 1. Free variables are equal to sum_vars
        # find the root with sum variables with the smallest width
        # bottom-up semi-join reduction and sort by SUM
        # 2. Free variables include sum_vars
        # if we can find a node contains all free variables, then sort in that node
        if free_set_candidates: # all free variables are in one relation
            # print('quick access for SUM order.')
            self.quick_access = True
            root_cand = min(free_set_candidates, key=lambda r: len(r.variables))
            self.root = ConjunctiveQuery.build_join_tree_given_root(atoms, root_cand)
            ConjunctiveQuery.semi_join_bottom_up(self.root)
            self.root.relation.cal_sum_scores()
            self.root.relation.sum_sort()
            self.total_count = len(self.root.relation.rowid)

        else: 
            # some free variables are not in SUM relation
            sum_set_candidates = list(filter(lambda r: sum_set.issubset(r.variables), atoms))
            root_cand = max(sum_set_candidates, key=lambda r: len(r.variables))
            self.root = ConjunctiveQuery.build_join_tree_given_root(atoms, root_cand)
            self.root.relation.cal_sum_scores()
            self.root.relation.sum_sort()

            self.post_order = self.root.post_order_traversal() 

            for node in self.post_order:
                node.preprocess_buckets_sum()

            self.total_count = self.root.buckets[()]['weight']
    
    def direct_access(self, k): 
        """
        Direct Access for SUM order query with k. 
        Return the k-th tuple (projected_dict, SUM)
        """
        if self.quick_access:
            chosen = self.root.relation.rowid[k]
            data_tuple = self.root.relation.instance_row[chosen]
            result_dict = {var: data_tuple[self.root.relation.variables.index(var)] for var in self.query.free_vars}
            result_dict['__sum'] = self.root.relation.sum_score[chosen]
        
        else: 
            # print('Direct Access for SUM with free variables not all in one relation.')
            current_k = k
            root_bucket = self.root.buckets[()]
            if current_k < 0 or current_k >= root_bucket['weight']:
                raise IndexError("k exceeds total number of results.")
            
            factor = root_bucket['weight']
            result_dict = {}
            buckets_dict = {}

            for current_node in reversed(self.post_order):
                if current_node == self.root:
                    current_bucket = root_bucket
                else:
                    current_bucket = buckets_dict[current_node]

                factor = factor / current_bucket['weight']

                # binary search to find the bucket that k should contain in. t.start_index <= k < t.end_index
                data = current_bucket['data']
                left, right = 0, len(data) - 1
                chosen = None
                while left <= right:
                    mid = (left + right) // 2
                    _, _, s, e = data[mid]
                    if s * factor <= current_k < e * factor:
                        chosen = data[mid]
                        break
                    elif current_k < s * factor:
                        right = mid - 1
                    else:
                        left = mid + 1

                if chosen is None:
                    raise RuntimeError("Binary search failed.")
                
                row_id, weight, start, end = chosen
                current_k -= start * factor
                

                data_tuple = current_node.relation.instance_row[row_id]
                for var in self.query.free_vars:
                    if var in current_node.relation.variables and var not in result_dict:
                        if current_node == self.root: 
                            result_dict['__sum'] = self.root.relation.sum_score[row_id]
                        result_dict[var] = data_tuple[current_node.relation.variables.index(var)]

                # construct the prefix for next layer
                for child, connection in current_node.children_connection.items(): 
                    next_prefix = tuple(result_dict[attr] for attr in connection)
                    buckets_dict[child] = child.buckets[next_prefix]
                    factor = factor * child.buckets[next_prefix]['weight']

        return result_dict
    

    @classmethod
    def create_and_prepare(cls, cq: ConjunctiveQuery):
        da_tree_sum = cls(cq)
        da_tree_sum.preprocess()
        return da_tree_sum