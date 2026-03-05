from select_k.Relation import Relation
from collections import deque, defaultdict

class JoinTreeNode:
    """
    Node of the Join Tree, covering part of the variables
    edges: save the neighbor node
    """
    def __init__(self, relation:Relation, layer=None, parent=None, parent_connection=None, 
                 children=None, children_connection=None, aux = False):
        self.relation = relation
        self.parent = parent
        self.parent_connection = parent_connection
        self.children = children if children else []
        self.children_connection = children_connection if children_connection else {}
        self.layer = layer 
        self.aux = aux
        self.buckets = None # for direct access 
        self.select_count = None # for selection
        self.pivots = None # for SUM selection

    def __repr__(self):
        return f"Node - Layer {self.layer} {self.relation.name}: {self.relation.variables}"
    
    @classmethod
    def from_node(cls, original: 'JoinTreeNode', layer=None, parent=None, parent_connection=None, 
                  children=None, children_connection=None, aux=None):
        """
        Create a new JoinTreeNode as a copy of the original JoinTreeNode.
        
        """
        # Copy the relation
        copied_relation = Relation.from_relation(original.relation)
        
        # Use provided values or copy from original
        new_layer = layer if layer is not None else original.layer
        new_parent = parent if parent is not None else original.parent
        new_parent_connection = parent_connection if parent_connection is not None else original.parent_connection
        new_children = children if children is not None else original.children.copy() if original.children else []
        new_children_connection = children_connection if children_connection is not None else original.children_connection.copy() if original.children_connection else {}
        new_aux = aux if aux is not None else original.aux
        
        return cls(
            relation=copied_relation,
            layer=new_layer,
            parent=new_parent,
            parent_connection=new_parent_connection,
            children=new_children,
            children_connection=new_children_connection,
            aux=new_aux
        )
    
    
    def bfs_get_relations(self): 
        relations = []
        if self is None:
            print("No subtree")
            return relations
        queue = deque([self])
        while queue:
            node = queue.popleft()
            relations.append(node.relation)
            
            if node.children:      
                for child in node.children:
                    queue.append(child)

        return relations
    
    
    def preprocess_buckets(self): 

        data = self.relation.instance_row
        row_id = self.relation.rowid
        # table_dict = table.cols

        parent_attrs = self.parent_connection
        is_leaf = not bool(self.children)

        n_rows = len(row_id)
        var_pos = {v:i for i, v in enumerate(self.relation.variables)}
        prefix_mapping = defaultdict(list)

        # with time_block(f"attribute mapping, {n_rows}"):
        if parent_attrs: 
            parent_pos = tuple(var_pos[a] for a in parent_attrs)
            # attr_map = [self.relation.variables.index(attr) for attr in parent_attrs]
            # prefix_keys = []
            # bucket_start_positions = []
            
            for i in range(n_rows): 
                idx = row_id[i]
                key_tup = tuple(data[idx][p] for p in parent_pos)
                # key_tup = tuple(data[idx][attr] for attr in attr_map)
                prefix_mapping[key_tup].append(idx)

        else:
            # parent_attrs is empty. prefix_key=()
            prefix_mapping [()] = row_id

        buckets = {}
        # with time_block(f"establish buckets"):
        for current_prefix, idx_list in prefix_mapping.items():
            start = 0  # start_index of record
            count_wb = 0  # weight of the total bucket 
            bucket_data = []
    
            for idx in idx_list: 
                wgt = 1 # inital weight of the data tuple

                # calculate weight for tuple in one prefix 
                if not is_leaf: 
                    for child in self.children: 
                        if child.parent_connection:
                            
                            child_attr_map = [self.relation.variables.index(attr) for attr in child.parent_connection]
                            child_key = tuple(data[idx][attr] for attr in child_attr_map) 
                            child_bucket_weight = child.buckets.get(child_key, {'weight': 0})['weight'] 

                        else:
                            # no parent_attrs in children
                            child_bucket_weight = child.buckets.get((), {'weight': 0})['weight']

                        if child_bucket_weight == 0:
                            wgt = 0
                            break

                        wgt *= child_bucket_weight

                end = start + wgt
                bucket_data.append((idx, wgt, start, end)) 

                start += wgt 
                count_wb += wgt

            buckets[current_prefix] = {
                'weight': count_wb,
                'data': bucket_data
            } 
        

        self.buckets = buckets


        

    def add_child(self, child, connection):
        self.children.append(child)
        self.children_connection[child] = connection
        child.parent = self
        child.parent_connection = connection

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            self.children_connection.pop(child, None)
            child.parent = None
            child.parent_connection = None

    @staticmethod
    def reroot_tree(new_root): 
        # new_root is the original root
        if not new_root.parent: 
            return
        
        visited = set()

        def dfs(node, parent, conn_to_parent=None):
            visited.add(node)

            # Collect neighbors (both parent and children)
            neighbors = []

            if node.parent and node.parent not in visited:
                neighbors.append((node.parent, node.parent_connection))

            for child in node.children:
                if child not in visited:
                    neighbors.append((child, node.children_connection[child]))

            # Clear current children and parent — will be rebuilt
            node.children = []
            node.children_connection = {}
            node.parent = parent 
            node.parent_connection = conn_to_parent

            for neighbor, conn in neighbors:
                # Attach current node as parent
                if node not in neighbor.children:
                    neighbor.children = [c for c in neighbor.children if c != node]
                    neighbor.children_connection.pop(node, None)

                # Recursively rewire
                dfs(neighbor, node, conn)
                node.children.append(neighbor)
                node.children_connection[neighbor] = conn

        def reverse_conn(parent, child):
            # Connection from parent to child → now used as child → parent
            if child in parent.children_connection:
                return parent.children_connection[child]
            return child.parent_connection

        dfs(new_root, None)


    @staticmethod
    def detach_subtree(node):
        if node.parent:
            parent = node.parent
            parent.children.remove(node)
            parent.children_connection.pop(node, None)
            node.parent = None
            node.parent_connection = None

    @staticmethod
    def attach_node(new_parent, node, connection_info):
        node.parent = new_parent
        node.parent_connection = connection_info
        new_parent.children.append(node)
        new_parent.children_connection[node] = connection_info

    @staticmethod
    def find_node_with_var_bfs(root, variable):
        """
        Perform BFS from the root to find the first node that contains the given variable.
        """
        queue = deque([root])

        while queue:
            node = queue.popleft()
            if variable in node.relation.variables:
                return node
            queue.extend(node.children)

        return None
    
    def post_order_traversal(self):
        post_order = []
        # iterate through children first
        for child in self.children:
            post_order.extend(child.post_order_traversal())
        post_order.append(self)
        return post_order
    
    def preprocess_buckets_sum(self): 

        data = self.relation.instance_row
        row_id = self.relation.rowid

        parent_attrs = self.parent_connection
        is_leaf = not bool(self.children)

        n_rows = len(row_id)
        var_pos = {v:i for i, v in enumerate(self.relation.variables)}
        prefix_mapping = defaultdict(list)

        if parent_attrs: # non-root nodes
            parent_pos = tuple(var_pos[a] for a in parent_attrs)
            
            for i in range(n_rows): 
                idx = row_id[i]
                key_tup = tuple(data[idx][p] for p in parent_pos)
                prefix_mapping[key_tup].append(idx)

        else: # root node
            prefix_mapping [()] = row_id

        buckets = {}
        for current_prefix, idx_list in prefix_mapping.items():
            start = 0  # start_index of record
            count_wb = 0  # weight of the total bucket 
            bucket_data = []
    
            for idx in idx_list: 
                wgt = 1 # inital weight of the data tuple

                # calculate weight for tuple in one prefix 
                if not is_leaf: 
                    for child in self.children: 
                        if child.parent_connection:
                            
                            child_attr_map = [self.relation.variables.index(attr) for attr in child.parent_connection]
                            child_key = tuple(data[idx][attr] for attr in child_attr_map) 
                            child_bucket_weight = child.buckets.get(child_key, {'weight': 0})['weight'] 

                        else:
                            # no parent_attrs in children
                            child_bucket_weight = child.buckets.get((), {'weight': 0})['weight']

                        if child_bucket_weight == 0:
                            wgt = 0
                            break

                        wgt *= child_bucket_weight

                end = start + wgt
                bucket_data.append((idx, wgt, start, end)) 

                start += wgt 
                count_wb += wgt

            buckets[current_prefix] = {
                'weight': count_wb,
                'data': bucket_data
            } 
        

        self.buckets = buckets