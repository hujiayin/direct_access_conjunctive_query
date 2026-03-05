import copy
import random
import numpy as np
from collections import defaultdict
from select_k.Query import ConjunctiveQuery
from select_k.JoinTreeNode import JoinTreeNode
from select_k.Relation import Relation
from exp_timer.exp_timer import timer


class Selection_Sum: 
    @timer(name="PrepareSelection", extra=lambda ctx: f"exp={ctx.exp_id}_trial={ctx.trial}" if hasattr(ctx, 'exp_id') and hasattr(ctx, 'trial') else None)
    def __init__(self, cq: ConjunctiveQuery):
        """
        Initialize Selection Class to determine if the selection is possible (in quasilinear time).
        """

        self.query = cq
        # assign each SUM variable to one of the 2 relations
        # sum_vars_1 and sum_vars_2 are lists that store (index of sum var, factor) for each of the 2 relations
        # sum_vars_1 refers to the root and sum_vars_2 refers to its first child
        # for sum_vars_2, flip the sign of the factors so that we can have the variables on each side of an inequality such as a + b < -c + pivot
        self.sum_vars_1 = []
        self.sum_vars_2 = []
        if not self.query.free_connex:
            raise Exception("NOT Tractable for Selection. The query is not free-connex.")
        elif self.query.is_sum_in_one_relation:
            self.root = ConjunctiveQuery.build_join_tree_given_root(self.query.atoms, self.query.sum_vars_relation)
            return
        elif len(self.query.atoms) <= 2:
            self.root = self.query.build_join_tree_arbitrary_root()
        else:
            pair = self.query.check_sum_vars_in_adjacent_nodes()
            if not pair:
                raise Exception("NOT Tractable for Selection. SUM variables are not contained in two adjacent nodes of the join tree.")
            else:
                self.root = ConjunctiveQuery.build_join_tree_given_root(self.query.atoms, pair[0])

                # print(self.root.children)
                
                # Ensure the first child is pair[1] (the relation with SUM variables)
                # Compare by relation name instead of object reference
                if self.root.children[0].relation.name != pair[1].name:
                    # Find pair[1] among children and swap with first child
                    found = False
                    for idx in range(1, len(self.root.children)):
                        if self.root.children[idx].relation.name == pair[1].name:
                            # print(f"Swapping child {idx} ({self.root.children[idx].relation.name}) with first child ({self.root.children[0].relation.name})")
                            self.root.children[0], self.root.children[idx] = self.root.children[idx], self.root.children[0]
                            found = True
                            break
                    if not found:
                        raise Exception(f"pair[1] relation {pair[1].name} not found among root's children")

            # print("Join tree built with root relation: ", self.root.relation.name)
            # print("first child relation: ", self.root.children[0].relation.name)
        for var in self.query.sum_order:
            if var in self.root.relation.variables:
                # print(f"SUM variable {var} found in root relation.")
                self.sum_vars_1.append((self.root.relation.variables.index(var), self.query.sum_order[var]))
            elif var in self.root.children[0].relation.variables:
                # print(f"SUM variable {var} found in first child relation.")
                self.sum_vars_2.append((self.root.children[0].relation.variables.index(var), -self.query.sum_order[var]))
            else: 
                raise Exception(f"SUM variable {var} not found in either of the 2 designated relations.")

    @timer(name="SelectK", extra=lambda ctx: f"exp={ctx.exp_id}_trial={ctx.trial}" if hasattr(ctx, 'exp_id') and hasattr(ctx, 'trial') else None)    
    def select_k(self, k:int, early_stopping:bool=False): 
        if self.query.is_sum_in_one_relation:
            return self.select_k_sum_in_one_relation(k)
        if len(self.query.atoms) <= 2:
            # ConjunctiveQuery.semi_join_bottom_up_count(self.root)
            return self.select_k_sum_two(k, early_stopping)
        else:
            return self.select_k_sum_more_than_two(k)

    def select_k_sum_two(self, k:int, early_stopping:bool=False): 
        """
        Select the k-th record according to the sum order.
        """

        current_root = self.root
        # print(current_root.select_count)

        if early_stopping:
            db_size = 0
            for rel in self.query.data.values():
                db_size += len(rel)

        while True:
            # Pick a good pivot (i.e., an answer that is relatively in the middle of the ranking)
            pivot, pivot_weight = self.pick_pivot(current_root, self.query.sum_order)

            remaining_answers = sum(current_root.select_count)
            # print("Remaining answers: ", remaining_answers)
            # print("Starting root: ", current_root.relation.instance_row)
            # print("Starting child: ", current_root.children[0].relation.instance_row)

            pivot_sum = sum(pivot[var] * weight for (var, weight) in self.query.sum_order.items())
            pivot['__sum'] = pivot_sum
            # print("Pivot selected: ", pivot)
            # print("Pivot weight: ", pivot_weight)

            # Create a new query (with a new database) that produces the answers that are smaller than the pivot
            # (satisfying the inequality SUM < pivot['__sum'])
            # For simplicity, we directly work on the join tree, not the query structure
            root_less_than = self.trim_lt_inequality(current_root, self.sum_vars_1, self.sum_vars_2, pivot_sum)
            ConjunctiveQuery.semi_join_bottom_up_count(root_less_than)
            count_less_than = sum(root_less_than.select_count)
            # print("Count less than pivot: ", count_less_than)
            # print("Root in less than vars: ", root_less_than.relation.variables)
            # print("Root in less than: ", root_less_than.relation.instance_row)
            # print("Child in less than vars: ", root_less_than.children[0].relation.variables)
            # print("Child in less than: ", root_less_than.children[0].relation.instance_row)

            root_greater_than = self.trim_gt_inequality(current_root, self.sum_vars_1, self.sum_vars_2, pivot_sum)
            ConjunctiveQuery.semi_join_bottom_up_count(root_greater_than)
            count_greater_than = sum(root_greater_than.select_count)
            # print("Count greater than pivot: ", count_greater_than)

            count_equal = remaining_answers - count_less_than - count_greater_than

            if k < count_less_than:
                current_root = root_less_than
                remaining_answers = count_less_than
            elif k < count_less_than + count_equal:
                remaining_k = k - count_less_than
                # We found the k-th answer
                # Return it after removing the auxiliary variables
                if '__lt_var' in pivot:
                    del pivot['__lt_var']
                if '__gt_var' in pivot:
                    del pivot['__gt_var']
                return pivot
            else:
                current_root = root_greater_than
                remaining_answers = count_greater_than
                k = k - count_less_than - count_equal

            if early_stopping and remaining_answers < db_size:
                # TODO: If the remaining answers are less than the database size, then perform the join
                # current_root is the current join tree which needs to be joined
                raise Exception("Early stopping not yet implemented.")
            
    def select_k_sum_more_than_two(self, k:int):
        """
        Select the k-th record according to the sum order. (more than two atoms case)
        Still we need to have the SUM variables contained in only two adjacent nodes of the join tree. 
        Currently, self.root is one of the relation with SUM variables, and its first child is the other relation with SUM variables. 
        We can extend the trimming procedure to work on a join tree with more than 2 nodes, as long as the SUM variables are contained in only 2 adjacent nodes. 
        We can enforce the inequality condition on the two nodes that contain the SUM variables, 
        and then do bottom-up counting to determine how many answers satisfy the condition. 
        The rest of the procedure is the same as in the two atoms case.
        """
        # 1. bottom-up count to get the total count for each relation with SUM variables
        # we need to seperate the tree into two subtrees: one with the root relation in the whole tree, 
        # and the other with the first child relation in the whole tree. 
        # then bottom-up count each subtree separately
        # but still we need to keep the original structure 

        # print('Starting select_k_sum_more_than_two with original tree structure.')
        
        current_root = self.root
        # Create subtree 1: root with all its children except the first child
        # This subtree will be used for counting tuples in the root relation
        subtree_root = copy.copy(current_root)
        subtree_root.children = [child for child in current_root.children[1:]]  # Exclude first child
        subtree_root.children_connection = {child: conn for child, conn in current_root.children_connection.items() 
                                           if child != current_root.children[0]}
        
        # Create subtree 2: first child with all its descendants
        # This subtree will be used for counting tuples in the first child relation
        subtree_first_child = current_root.children[0]
        
        # Perform bottom-up count on each subtree separately
        ConjunctiveQuery.semi_join_bottom_up_count(subtree_root)
        ConjunctiveQuery.semi_join_bottom_up_count(subtree_first_child)
        
        # Store the counts as the weights of the relations
        # self.root.relation.instance_w = subtree_root.select_count.copy()
        # self.root.children[0].relation.instance_w = subtree_first_child.select_count.copy()

        # 2. select_k_with_weights
        # Create a simplified tree with only the two relations that contain SUM variables
        # This tree is used for selection without interference from other relations
        simplified_root = JoinTreeNode(self.root.relation)
        simplified_root.instance_w = subtree_root.select_count.copy()
        simplified_child = JoinTreeNode(self.root.children[0].relation)
        simplified_child.instance_w = subtree_first_child.select_count.copy()
        simplified_root.children = [simplified_child]
        simplified_root.children_connection = {simplified_child: self.root.children_connection[self.root.children[0]]}
        simplified_child.parent = simplified_root
        simplified_child.parent_connection = self.root.children[0].parent_connection


        # Perform selection on the simplified tree
        top_result, remaining_k = self._select_k_with_weights_on_tree(simplified_root, k)

        # print('Selection on the two completed. Result: ', top_result)

        # 3. go along the join tree to find the tuple
        final_result = self.get_final_result(top_result)

        return final_result
    
    def select_k_sum_in_one_relation(self, k:int):
        """
        Select the k-th record according to the sum order when all SUM variables are in one relation.
        We can simply sort the tuples of that relation according to the sum order, and return the k-th one.
        """
        # count the total tuples in the relation with SUM 
        ConjunctiveQuery.semi_join_bottom_up_count(self.root)

        # sort the tuples according to the sum order
        self.root.relation.cal_sum_scores()

        sum_value, _, top_result_index = self.quick_select(self.root.relation.sum_score, self.root.select_count, k)

        top_result = {var: self.root.relation.instance_row[top_result_index][i] for i, var in enumerate(self.root.relation.variables)}
        top_result['__sum'] = sum_value

        final_result = self.get_final_result(top_result)

        return final_result
    
    @staticmethod
    def quick_select(sum_scores, weight, k):
        if k < 0:
            raise ValueError("k should be non-negative")

        items = [(score, w, idx) for idx, (score, w) in enumerate(zip(sum_scores, weight))]

        def quick_select_weighted(items, k, pre_weight): 
            # print(items, k)
            if not items:
                raise IndexError("k exceeds total weight")

            pivot_key = random.choice(items)[0]

            def compare(x):
                return x[0] < pivot_key

            L = [x for x in items if compare(x)] # left part
            E = [x for x in items if x[0] == pivot_key]
            R = [x for x in items if not compare(x) and x[0] != pivot_key]

            w_L = sum(w for _, w, _ in L)
            w_E = sum(w for _, w, _ in E)

            if k < w_L: 
                return quick_select_weighted(L, k, pre_weight)
            elif k < w_L + w_E: 
                # Pick concrete original index inside equal bucket by cumulative weight.
                target_in_e = k - w_L
                running = 0
                for score, w, original_idx in E:
                    running += w
                    if target_in_e < running:
                        return score, pre_weight + w_L, original_idx
                raise IndexError("k exceeds total weight")
            else: 
                return quick_select_weighted(R, k - w_L - w_E, pre_weight + w_L + w_E)

        return quick_select_weighted(items, k, 0)
    
    def get_final_result(self, top_result: dict):

        root = self.root

        # given a node, recursively find the tuple for its children according to the join condition
        def dfs(node, current_result):
            if set(self.query.free_vars) <= set(current_result.keys()):
                # Filter out auxiliary variables before returning
                
                return {var: val for var, val in current_result.items() if var in self.query.free_vars or var == '__sum'}

            if not node.children:
                return current_result

            accumulated_result = current_result
            for child, conn in node.children_connection.items():
                found_match = False

                # Greedy: pick the first tuple with positive count that satisfies joins and existing assignments
                for i, row in enumerate(child.relation.instance_row):
                    child_count = child.select_count[i] if child.select_count is not None else 1
                    if child_count <= 0:
                        continue

                    if conn and not all(
                        (join_var in accumulated_result) and
                        (row[child.relation.variables.index(join_var)] == accumulated_result[join_var])
                        for join_var in conn
                    ):
                        continue

                    consistent = True
                    next_result = accumulated_result.copy()
                    for j, var in enumerate(child.relation.variables):
                        val = row[j]
                        if var in next_result and next_result[var] != val:
                            consistent = False
                            break
                        next_result[var] = val

                    if not consistent:
                        continue

                    accumulated_result = dfs(child, next_result)
                    found_match = True
                    break

                if not found_match:
                    raise Exception("Failed to reconstruct a full free-variable assignment from top_result.")

            return accumulated_result

        final_result = dfs(root, top_result.copy())
        return {var: val for var, val in final_result.items() if var in self.query.free_vars or var == '__sum'}
    
    def _select_k_with_weights_on_tree(self, root: JoinTreeNode, k:int, early_stopping:bool=False):
        """
        Internal method to perform selection on a given tree structure.
        """
        current_root = root

        if early_stopping:
            db_size = 0
            for rel in self.query.data.values():
                db_size += len(rel)

        while True:
            # print("-----BEGINNING OF SELECTION WITH WEIGHTS ON TREE")
            # Pick a good pivot (i.e., an answer that is relatively in the middle of the ranking)
            pivot, pivot_weight = self.pick_pivot(current_root, self.query.sum_order)

            remaining_answers = sum(current_root.select_count)
            # print("Remaining answers: ", remaining_answers)
            # print("Starting root: ", current_root.relation.instance_row)
            # print("Starting child: ", current_root.children[0].relation.instance_row)
            # print("Pivot selected: ", pivot)
            # print("Pivot weight: ", pivot_weight)

            pivot_sum = sum(pivot[var] * weight for (var, weight) in self.query.sum_order.items())
            pivot['__sum'] = pivot_sum

            # Create a new query (with a new database) that produces the answers that are smaller than the pivot
            root_less_than = self.trim_lt_inequality(current_root, self.sum_vars_1, self.sum_vars_2, pivot_sum)
            ConjunctiveQuery.semi_join_bottom_up_count_weight(root_less_than)
            count_less_than = sum(root_less_than.select_count)

            root_greater_than = self.trim_gt_inequality(current_root, self.sum_vars_1, self.sum_vars_2, pivot_sum)
            ConjunctiveQuery.semi_join_bottom_up_count_weight(root_greater_than)
            count_greater_than = sum(root_greater_than.select_count)

            # print("Count less than pivot: ", count_less_than)
            # print("Count greater than pivot: ", count_greater_than)

            count_equal = remaining_answers - count_less_than - count_greater_than

            if k < count_less_than:
                current_root = root_less_than
                remaining_answers = count_less_than
            elif k < count_less_than + count_equal:
                remaining_k = k - count_less_than
                # if remaining_k <= pivot_weight:
                #     # We found the k-th answers' sum value
                #     # (there could be multiple answers with the same sum value as the pivot)
                #     # Return it after removing the auxiliary variables and adding tuple weights
                if '__lt_var' in pivot:
                    del pivot['__lt_var']
                if '__gt_var' in pivot:
                    del pivot['__gt_var']

                # print("FINAL PIVOT: ", pivot)
                # print("FINAL PIVOT weight: ", remaining_k)
                
                return pivot, remaining_k
            else:
                current_root = root_greater_than
                remaining_answers = count_greater_than
                k = k - count_less_than - count_equal

            if early_stopping and remaining_answers < db_size:
                raise Exception("Early stopping not yet implemented.")

    @staticmethod
    def trim_lt_inequality(root: JoinTreeNode, sum_vars_root: list, sum_vars_child: list, offset: float):
        return Selection_Sum.trim_inequality(root, sum_vars_root, sum_vars_child, offset, -1)

    @staticmethod
    def trim_gt_inequality(root: JoinTreeNode, sum_vars_root: list, sum_vars_child: list, offset: float):
        return Selection_Sum.trim_inequality(root, sum_vars_root, sum_vars_child, offset, 1)

    @staticmethod
    def trim_inequality(root: JoinTreeNode, sum_vars_root: list, sum_vars_child: list, offset: float, direction: int):
        """
        Assuming that the root and its first child contain all SUM variables, enforce the inequality SUM_root < -SUM_child + offset or SUM_root > -SUM_child + offset
        Returns a new join tree with modified relations (without destroying the original one)
        root: the root of the join tree
        sum_vars_root: a list of (index, factor) for the root variables
        sum_vars_child: a list of (index, factor) for the child variables, where the factors have been negated
        offset: float, the offset to apply
        direction: int, the direction of the inequality (1 for >, -1 for <)
        """

        # Initialize the new relations
        new_relation_root = copy.copy(root.relation)
        new_relation_root.instance_row = []
        new_relation_root.rowid = None
        new_relation_child = copy.copy(root.children[0].relation)
        new_relation_child.instance_row = []
        new_relation_child.rowid = None

        # Clone the join tree, with the same relation pointers
        # Since we will only modify the root node and its first child node, we can clone only those
        new_root = copy.copy(root)
        new_root.select_count = None
        new_root.pivots = None
        new_root.children = copy.copy(root.children)
        new_root.children_connection = copy.copy(root.children_connection)
        new_root.children[0] = copy.copy(root.children[0])
        new_root.children[0].select_count = None
        new_root.children[0].pivots = None
        new_root.children[0].parent_connection = copy.copy(root.children[0].parent_connection)

        # children_connection is a dict with join tree nodes as keys so we need to modify it now that we changed the child node
        del new_root.children_connection[root.children[0]]
        new_root.children_connection[new_root.children[0]] = copy.copy(root.children_connection[root.children[0]])

        new_root.relation = new_relation_root
        new_root.children[0].relation = new_relation_child


        # Create new auxiliary variables between the two relations that will encode the inequality condition
        # Also create a new columns that stores the sum of each tuple (needed for sorting)
        # (If such variables already exist, we reuse them)
        new_var_name = '__lt_var' if direction == -1 else '__gt_var'
        # root
        if new_var_name in new_relation_root.variables:
            # sum must also exist
            None
        else:
            if '__sum' in new_relation_root.variables:
                # sum exists at the end of the tuples because an iteration with a different inequality direction has occured
                # move the sum var to the end
                new_relation_root.variables = new_relation_root.variables[:-1] + (new_var_name,) + ('__sum',)
                new_relation_root.width += 1
                new_relation_child.variables = new_relation_child.variables[:-1] + (new_var_name,) + ('__sum',)
                new_relation_child.width += 1
            else:
                # Add both variables to the end
                new_relation_root.variables = new_relation_root.variables + (new_var_name,) + ('__sum',)
                new_relation_child.variables = new_relation_child.variables + (new_var_name,) + ('__sum',)
                new_relation_root.width += 2
                new_relation_child.width += 2

            # Adjust the connections of the root to the child, adding the new variable to the existing connection
            if new_root.children_connection[new_root.children[0]]:
                new_root.children_connection[new_root.children[0]].add(new_var_name)
            else:
                new_root.children_connection[new_root.children[0]] = {new_var_name}
            if new_root.children[0].parent_connection:
                new_root.children[0].parent_connection.add(new_var_name)
            else:
                new_root.children[0].parent_connection = {new_var_name}

        sum_var_root_idx = new_relation_root.variables.index('__sum')
        ineq_var_root_idx = new_relation_root.variables.index(new_var_name)
        sum_var_child_idx = new_relation_child.variables.index('__sum')
        ineq_var_child_idx = new_relation_child.variables.index(new_var_name)

        # Now we are ready to modify the data
        # Check if we need to handle weights
        has_weights = hasattr(root, 'instance_w') and root.instance_w is not None
        new_relation_root.instance_w = [] if hasattr(root, 'instance_w') else None
        new_relation_child.instance_w = [] if hasattr(root.children[0], 'instance_w') else None
        
        if has_weights:
            Selection_Sum.trim_data_inequality_with_weights(new_relation_root, new_relation_child, 
                                                    root, root.children[0], root.children_connection[root.children[0]],
                                                    ineq_var_root_idx, ineq_var_child_idx, sum_vars_root, sum_vars_child, offset, direction)
            new_root.instance_w = new_relation_root.instance_w
            new_root.children[0].instance_w = new_relation_child.instance_w
        else:
            Selection_Sum.trim_data_inequality(new_relation_root, new_relation_child, 
                                               root, root.children[0], root.children_connection[root.children[0]],
                                                ineq_var_root_idx, ineq_var_child_idx, sum_vars_root, sum_vars_child, offset, direction)

        return new_root
    
    @staticmethod
    def trim_data_inequality(new_parent: Relation, new_child: Relation, 
                                      parent: JoinTreeNode, child: JoinTreeNode, connection: list, \
                                ineq_var_parent_idx: int, ineq_var_child_idx: int, \
                                sum_vars_parent: list, sum_vars_child: list, \
                                offset: float, direction: int):
        """
        Enforce the inequality SUM_parent < -SUM_child + offset on the given relations.
        Populates new_parent and new_child with data.
        This version does NOT handle instance_w (weights).
        """
        new_var_value_id = 0

        def connect_tuples(parent_tuples, child_tuples):
            # Connects these groups of tuples by associating them with the same value for the inequality variable
            nonlocal new_var_value_id
            new_var_value_id += 1
            for parent_row in parent_tuples:
                # Set a common value for the inequality variable in this group of tuples, and remove the sum value at the end
                new_parent_row = parent_row[:ineq_var_parent_idx] + (new_var_value_id,) + parent_row[(ineq_var_parent_idx + 1):]
                new_parent.instance_row.append(new_parent_row)
                    
            for child_row in child_tuples:
                new_child_row = child_row[:ineq_var_child_idx] + (new_var_value_id,) + child_row[(ineq_var_child_idx + 1):]
                new_child.instance_row.append(new_child_row)

        def recursive_partitioning(parent_tuples_sorted, child_tuples_sorted, distinct_vals_sorted):
            num_distinct_vals = len(distinct_vals_sorted)
            # Base case
            if num_distinct_vals <= 1:
                # Inequality cannot be satisfied
                return
            # Recursive case
            # Split the distinct sums in half
            mid_distinct = num_distinct_vals // 2
            low_distinct_vals = distinct_vals_sorted[:mid_distinct]
            high_distinct_vals = distinct_vals_sorted[mid_distinct:]
            breakpoint_val = distinct_vals_sorted[mid_distinct] # Belongs to high

            # Partition the tuples on low/high
            parent_breakpoint = len(parent_tuples_sorted)
            for (i, tup) in enumerate(parent_tuples_sorted):
                if tup[-1] >= breakpoint_val:
                    parent_breakpoint = i # Index where high starts
                    break
            child_breakpoint = len(child_tuples_sorted)
            for (i, tup) in enumerate(child_tuples_sorted):
                if tup[-1] >= breakpoint_val:
                    child_breakpoint = i # Index where high starts
                    break
            parent_low = parent_tuples_sorted[:parent_breakpoint]
            parent_high = parent_tuples_sorted[parent_breakpoint:]
            child_low = child_tuples_sorted[:child_breakpoint]
            child_high = child_tuples_sorted[child_breakpoint:]

            if direction == -1:
                # Less than: Connect parent_low to child_high
                if len(parent_low) > 0 and len(child_high) > 0:
                    connect_tuples(parent_low, child_high)

                # Continue recursively in each low/high partition
                if len(parent_low) > 0 and len(child_low) > 0:
                    recursive_partitioning(parent_low, child_low, low_distinct_vals)
                if len(parent_high) > 0 and len(child_high) > 0:
                    recursive_partitioning(parent_high, child_high, high_distinct_vals)
            else:
                # Greater than: Connect parent_high to child_low
                if len(parent_high) > 0 and len(child_low) > 0:
                    connect_tuples(parent_high, child_low)

                # Continue recursively in each low/high partition
                if len(parent_low) > 0 and len(child_low) > 0:
                    recursive_partitioning(parent_low, child_low, low_distinct_vals)
                if len(parent_high) > 0 and len(child_high) > 0:
                    recursive_partitioning(parent_high, child_high, high_distinct_vals)

        # End of internal functions
        ################################################
        ################################################

        # First partition the rows of parent-child based on the equality condition, which is stored in the connection between them
        parent_partition = defaultdict(list)
        child_partition = defaultdict(list)

        # If the inequality variable was already in the connection, remove it when checking for equality
        # The reason is that we want to overwrite the variable with new values (the inequalities keep restricting the data)
        modified_connection = connection.copy() if connection else set()
        new_var_name = '__lt_var' if direction == -1 else '__gt_var'
        if new_var_name in modified_connection:
            modified_connection.remove(new_var_name)
            new_var_already_exists = True
        else:
            new_var_already_exists = False


        parent_key_idx = [parent.relation.variables.index(attr) for attr in modified_connection]
        child_key_idx = [child.relation.variables.index(attr) for attr in modified_connection]

        # TODO: handle the case of empty connection


        # Create copies of the tuples that contain (if they don't already):
        # 1) the new variable at the correct index and its value is 0
        # 2) the SUM value as the last element (this includes the offset for the child)
        # Then, partition the rows so that each partition has the rows that share the same join key
        # Parent
        for row in parent.relation.instance_row:
            sum_val = sum(row[indx] * factor for (indx, factor) in sum_vars_parent)
            new_row = row[:ineq_var_parent_idx] + (0,) + row[(ineq_var_parent_idx + 1):] + (sum_val,)
            key = tuple(row[i] for i in parent_key_idx)
            parent_partition.setdefault(key, []).append(new_row)
        # Child
        for row in child.relation.instance_row:
            sum_val = sum(row[indx] * factor for (indx, factor) in sum_vars_child) + offset
            new_row = row[:ineq_var_child_idx] + (0,) + row[(ineq_var_child_idx + 1):] + (sum_val,)
            key = tuple(row[i] for i in child_key_idx)
            child_partition.setdefault(key, []).append(new_row)


        for key in parent_partition.keys():
            if not child_partition[key]:
                continue
            parent_tuples = parent_partition[key]
            child_tuples = child_partition[key]

            # If the inequality variable already existed, we can have duplicate tuples
            if new_var_already_exists:
                parent_tuples = list(set(parent_tuples))
                child_tuples = list(set(child_tuples))

            # Sort each tuple set based on the sum value (the last element of each tuple)
            # This sorting is maintained across all recursive calls
            parent_tuples.sort(key=lambda x: x[-1])
            child_tuples.sort(key=lambda x: x[-1])

            # Put the distinct sum values in 1 common list
            distinct_sums = set()
            for tup in parent_tuples:
                distinct_sums.add(tup[-1])
            for tup in child_tuples:
                distinct_sums.add(tup[-1])
            distinct_sums_sorted = sorted(distinct_sums)

            recursive_partitioning(parent_tuples, child_tuples, distinct_sums_sorted)

            # TODO: Not sure if this is necessary
            new_parent.rowid = list(range(len(new_parent.instance_row)))
            new_child.rowid = list(range(len(new_child.instance_row)))

    @staticmethod
    def trim_data_inequality_with_weights(new_parent: Relation, new_child: Relation, 
                                      parent: JoinTreeNode, child: JoinTreeNode, connection: list, \
                                          ineq_var_parent_idx: int, ineq_var_child_idx: int, \
                                          sum_vars_parent: list, sum_vars_child: list, \
                                          offset: float, direction: int):
        """
        Enforce the inequality SUM_parent < -SUM_child + offset on the given relations.
        Populates new_parent and new_child with data.
        This version DOES handle instance_w (weights).
        """
        new_var_value_id = 0

        def connect_tuples(parent_tuples_with_weights, child_tuples_with_weights):
            # Connects these groups of tuples by associating them with the same value for the inequality variable
            nonlocal new_var_value_id
            new_var_value_id += 1
            for parent_row, parent_weight in parent_tuples_with_weights:
                # Set a common value for the inequality variable in this group of tuples, and remove the sum value at the end
                new_parent_row = parent_row[:ineq_var_parent_idx] + (new_var_value_id,) + parent_row[(ineq_var_parent_idx + 1):]
                new_parent.instance_row.append(new_parent_row)
                if new_parent.instance_w is not None:
                    new_parent.instance_w.append(parent_weight)
                    
            for child_row, child_weight in child_tuples_with_weights:
                new_child_row = child_row[:ineq_var_child_idx] + (new_var_value_id,) + child_row[(ineq_var_child_idx + 1):]
                new_child.instance_row.append(new_child_row)
                if new_child.instance_w is not None:
                    new_child.instance_w.append(child_weight)

        def recursive_partitioning(parent_tuples_sorted, child_tuples_sorted, distinct_vals_sorted):
            # parent_tuples_sorted and child_tuples_sorted are lists of (tuple, weight)
            num_distinct_vals = len(distinct_vals_sorted)
            # Base case
            if num_distinct_vals <= 1:
                # Inequality cannot be satisfied
                return
            # Recursive case
            # Split the distinct sums in half
            mid_distinct = num_distinct_vals // 2
            low_distinct_vals = distinct_vals_sorted[:mid_distinct]
            high_distinct_vals = distinct_vals_sorted[mid_distinct:]
            breakpoint_val = distinct_vals_sorted[mid_distinct] # Belongs to high

            # Partition the tuples on low/high
            parent_breakpoint = len(parent_tuples_sorted)
            for (i, (tup, w)) in enumerate(parent_tuples_sorted):
                if tup[-1] >= breakpoint_val:
                    parent_breakpoint = i # Index where high starts
                    break
            child_breakpoint = len(child_tuples_sorted)
            for (i, (tup, w)) in enumerate(child_tuples_sorted):
                if tup[-1] >= breakpoint_val:
                    child_breakpoint = i # Index where high starts
                    break
            parent_low = parent_tuples_sorted[:parent_breakpoint]
            parent_high = parent_tuples_sorted[parent_breakpoint:]
            child_low = child_tuples_sorted[:child_breakpoint]
            child_high = child_tuples_sorted[child_breakpoint:]

            # print("======== Rec Part =========")
            # print("Distinct vals:", distinct_vals_sorted)
            # print("Breakpoint val:", breakpoint_val)
            # print("Parent:", parent_tuples_sorted)
            # print("Parent breakpoint:", parent_breakpoint)
            # print("Parent low:", parent_low)
            # print("Parent high:", parent_high)
            # print("Child:", child_tuples_sorted)
            # print("Child breakpoint:", child_breakpoint)
            # print("Child low:", child_low)
            # print("Child high:", child_high)
            # print("=================")

            if direction == -1:
                # Less than: Connect parent_low to child_high
                if len(parent_low) > 0 and len(child_high) > 0:
                    connect_tuples(parent_low, child_high)

                # Continue recursively in each low/high partition
                if len(parent_low) > 0 and len(child_low) > 0:
                    recursive_partitioning(parent_low, child_low, low_distinct_vals)
                if len(parent_high) > 0 and len(child_high) > 0:
                    recursive_partitioning(parent_high, child_high, high_distinct_vals)
            else:
                # Greater than: Connect parent_high to child_low
                if len(parent_high) > 0 and len(child_low) > 0:
                    connect_tuples(parent_high, child_low)

                # Continue recursively in each low/high partition
                if len(parent_low) > 0 and len(child_low) > 0:
                    recursive_partitioning(parent_low, child_low, low_distinct_vals)
                if len(parent_high) > 0 and len(child_high) > 0:
                    recursive_partitioning(parent_high, child_high, high_distinct_vals)

        # End of internal functions
        ################################################
        ################################################

        # First partition the rows of parent-child based on the equality condition, which is stored in the connection between them
        parent_partition = defaultdict(list)
        child_partition = defaultdict(list)

        # If the inequality variable was already in the connection, remove it when checking for equality
        # The reason is that we want to overwrite the variable with new values (the inequalities keep restricting the data)
        modified_connection = connection.copy() if connection else set()
        new_var_name = '__lt_var' if direction == -1 else '__gt_var'
        if new_var_name in modified_connection:
            modified_connection.remove(new_var_name)
            new_var_already_exists = True
        else:
            new_var_already_exists = False


        parent_key_idx = [parent.relation.variables.index(attr) for attr in modified_connection]
        child_key_idx = [child.relation.variables.index(attr) for attr in modified_connection]

        # TODO: handle the case of empty connection


        # Create copies of the tuples that contain (if they don't already):
        # 1) the new variable at the correct index and its value is 0
        # 2) the SUM value as the last element (this includes the offset for the child)
        # Then, partition the rows so that each partition has the rows that share the same join key
        # Store tuples with their weights as (tuple, weight) pairs
        # Parent
        for i, row in enumerate(parent.relation.instance_row):
            sum_val = sum(row[indx] * factor for (indx, factor) in sum_vars_parent)
            new_row = row[:ineq_var_parent_idx] + (0,) + row[(ineq_var_parent_idx + 1):] + (sum_val,)
            weight = parent.instance_w[i] if parent.instance_w is not None else 1
            key = tuple(row[i] for i in parent_key_idx)
            parent_partition.setdefault(key, []).append((new_row, weight))
        # Child
        for i, row in enumerate(child.relation.instance_row):
            sum_val = sum(row[indx] * factor for (indx, factor) in sum_vars_child) + offset
            new_row = row[:ineq_var_child_idx] + (0,) + row[(ineq_var_child_idx + 1):] + (sum_val,)
            weight = child.instance_w[i] if child.instance_w is not None else 1
            key = tuple(row[i] for i in child_key_idx)
            child_partition.setdefault(key, []).append((new_row, weight))


        for key in parent_partition.keys():
            if not child_partition[key]:
                continue
            parent_tuples_with_weights = parent_partition[key]
            child_tuples_with_weights = child_partition[key]

            # If the inequality variable already existed, we can have duplicate tuples
            if new_var_already_exists:
                parent_tuples_with_weights = list(set(parent_tuples_with_weights))
                child_tuples_with_weights = list(set(child_tuples_with_weights))

            # Sort each tuple set based on the sum value (the last element of each tuple)
            # This sorting is maintained across all recursive calls
            parent_tuples_with_weights.sort(key=lambda x: x[0][-1])
            child_tuples_with_weights.sort(key=lambda x: x[0][-1])

            # Put the distinct sum values in 1 common list
            distinct_sums = set()
            for tup, w in parent_tuples_with_weights:
                distinct_sums.add(tup[-1])
            for tup, w in child_tuples_with_weights:
                distinct_sums.add(tup[-1])
            distinct_sums_sorted = sorted(distinct_sums)

            recursive_partitioning(parent_tuples_with_weights, child_tuples_with_weights, distinct_sums_sorted)


    @staticmethod
    def pick_pivot(root, sum_order):

        # To calculate the correct SUMs we need to assign each SUM variable to a specific join tree node
        # (Otherwise, we would for example double-count b in R(a, b), S(b, c))
        # However, double-counting does not influence the relative position of the tuples
        # So, it is fine to skip that step and double-count some variables

        def bottom_up_pivot(node:JoinTreeNode): 

            # Compute for each tuple:
            # 1) the count of the answers in the subtree
            # Use tuple weights (instance_w) as initial count, representing tuple repetitions
            if hasattr(node, 'instance_w'):
                node.select_count = np.array(node.instance_w, dtype=int)
            else:
                node.select_count = np.ones(len(node.relation.instance_row), dtype=int)
            # 2) a pivot for its subtree as the union of its values together with the pivots of its children
            # a pivot is represented as a dict from variable names to their values (all variables, not just those in the sum)
            node.pivots = np.empty(len(node.relation.instance_row), dtype=object)
            for i in range(len(node.pivots)):
                node.pivots[i] = {}
            # For all the tuples of the relation, we need to calculate the SUM
            # For that, we need the indexes of the SUM variables in the current relation, together with the factors we multiply them
            sum_indexes, factors = zip(*[(node.relation.variables.index(var), weight) for var, weight in sum_order.items() if var in node.relation.variables])
            for i, tup in enumerate(node.relation.instance_row):
                for j, var in enumerate(node.relation.variables):
                    node.pivots[i][var] = tup[j]
                # Calculate the SUM value of the tuple, taking into account the constant factors stored in the sum_order dict
                node.pivots[i]['__sum'] = sum(tup[j] * weight for j, weight in zip(sum_indexes, factors))

            if node.children:
                for child, conn in node.children_connection.items(): 
                    bottom_up_pivot(child) 
                    
                    # the pivot of a child is calulated as the weighted median of the pivots of the connecting tuples

                    if not conn:
                        # no connections
                        # calculate the counts
                        total_weight = np.sum(child.select_count)
                        # node.select_count *= total_weight
                        # calculate the weighted median of the child
                        child_pivot,_ = weighted_median_linear(child.pivots, child.select_count, total_weight)
                        for ii in range(len(node.pivots)):
                            node.pivots[ii].update(child_pivot)
                        node.select_count *= total_weight
                        # node.pivots[i].update(child_pivot)
                        continue

                    parent_key_idx = [node.relation.variables.index(attr) for attr in conn]
                    child_key_idx = [child.relation.variables.index(attr) for attr in conn]

                    # Each bucket has the pivots that share the same join key together with their weights
                    child_buckets = defaultdict(list)
                    for tup, w, p in zip(child.relation.instance_row, child.select_count, child.pivots):
                        key = tuple(tup[i] for i in child_key_idx)
                        child_buckets.setdefault(key, []).append((p, w))
                    # The messages sent from a child contain a tuple of aggregates for each join key (weighted median for pivots, sum for counts)
                    child_messages = {}
                    for key, bucket in child_buckets.items():
                        child_pivots, child_weights = zip(*bucket)
                        total_bucket_weight = sum(child_weights)
                        child_messages[key] = (weighted_median_linear(child_pivots, child_weights, total_bucket_weight)[0], total_bucket_weight)

                    for i, (tup, w, p) in enumerate(zip(node.relation.instance_row, node.select_count, node.pivots)):
                        key = tuple(tup[i] for i in parent_key_idx)
                        (child_pivot, child_weight) = child_messages.get(key, (None, 0))
                        ## TODO: Maybe that's the place we should delete a tuple if it doesn't join (the weight map returns 0)
                        node.select_count[i] = w * child_weight
                        if child_pivot is not None:
                            node.pivots[i].update(child_pivot)
            

        # Compute a pivot for each tuple (corresponding to its joining subtree)
        bottom_up_pivot(root)

        # Take the weighted median of the pivots of the root, ignoring those that don't join
        root_pivots = [p for p, w in zip(root.pivots, root.select_count) if w > 0]
        root_weights = [w for w in root.select_count if w > 0]
        final_pivot, final_weight = weighted_median_linear(root_pivots, root_weights, sum(root_weights))
        # print("final_pivot: ", final_pivot)
        # print("final_weight: ", final_weight)
        return final_pivot, final_weight


def weighted_median_linear(elements, weights, total_weight):
    """
    Compute the weighted median in expected linear time using Quickselect.
    elements: each element is a dict that contains a key '__sum'. This is what we compare with.
    weights: the number of times each element appears, same length as values
    total_weight: float, the total weight of all tuples
    """
    def weighted_select_linear(elements, weights, total_weight, k):
        elements = np.array(elements, dtype=object)  # Enable boolean indexing
        weights = np.asarray(weights)
        # print("elements: ", elements)
        # print("weights: ", weights)
        assert len(elements) == len(weights)

        if len(elements) == 1:
            return elements[0], weights[0]
        pivot_idx = np.random.randint(len(elements))
        pivot = elements[pivot_idx]
        pivot_weight = weights[pivot_idx]
        left_mask = np.array([t['__sum'] < pivot['__sum'] for t in elements])
        right_mask = np.array([t['__sum'] > pivot['__sum'] for t in elements])
        eq_mask = np.array([t['__sum'] == pivot['__sum'] for t in elements])

        w_left = weights[left_mask].sum()
        w_eq = weights[eq_mask].sum()
        if k < w_left:
            return weighted_select_linear(elements[left_mask], weights[left_mask], w_left, k)
        elif k < w_left + w_eq:
            return pivot, pivot_weight
        else:
            return weighted_select_linear(elements[right_mask], weights[right_mask], total_weight - w_left - w_eq, k - w_left - w_eq)

    return weighted_select_linear(elements, weights, total_weight, len(elements) // 2)