from dataclasses import dataclass, field
from collections import deque
import heapq


@dataclass
class Node:
    id: int
    label: str
    props: dict = field(default_factory=dict)

    def __repr__(self):
        return f"{self.label}#{self.id}"


@dataclass
class Edge:
    id: int
    type: str
    from_id: int
    to_id: int
    props: dict = field(default_factory=dict)

    def __repr__(self):
        return f"{self.type}#{self.id}"


class Graph:
    def __init__(self):
        self.nodes: dict[int, Node] = {}
        self.edges: dict[int, Edge] = {}

        self.out_adj: dict[int, list[int]] = {}
        self.in_adj: dict[int, list[int]] = {}

        self.indexes: dict[str, dict] = {}

        self._node_counter = 0
        self._edge_counter = 0

    def _next_node_id(self) -> int:
        """Auto incrememt node Id"""
        self._node_counter += 1
        return self._node_counter

    def _next_edge_id(self) -> int:
        """Auto incrememt edge Id"""
        self._edge_counter += 1
        return self._edge_counter

    def _index_node(self, node: Node):
        """hash index to look up nodes by their property for faster scans"""
        for prop, value in node.props.items():
            key = f"{node.label}.{prop}"
            if key not in self.indexes:
                self.indexes[key] = {}
            if value not in self.indexes[key]:
                self.indexes[key][value] = []
            self.indexes[key][value].append(node.id)

    def create_node(self, label: str, props: dict, node_id: int = None) -> Node:
        """Create Nodes"""
        nid = node_id if node_id is not None else self._next_node_id()

        if node_id is not None and node_id >= self._node_counter:
            self._node_counter = node_id

        node = Node(id=nid, label=label, props=props)
        self.nodes[nid] = node
        self.out_adj[nid] = []
        self.in_adj[nid] = []
        self._index_node(node)
        return node

    def create_edge(self, edge_type: str, from_id: int, to_id: int, props: dict, edge_id: int = None) -> Edge:
        """Create Edges"""
        if from_id not in self.nodes:
            raise ValueError(f"Node {from_id} does not exist")
        if to_id not in self.nodes:
            raise ValueError(f"Node {to_id} does not exist")

        eid = edge_id if edge_id is not None else self._next_edge_id()
        if edge_id is not None and edge_id >= self._edge_counter:
            self._edge_counter = edge_id

        edge = Edge(id=eid, type=edge_type, from_id=from_id, to_id=to_id, props=props)
        self.edges[eid] = edge
        self.out_adj[from_id].append(eid)
        self.in_adj[to_id].append(eid)
        return edge

    def get_nodes_by_label(self, label: str) -> list[Node]:
        return [n for n in self.nodes.values() if n.label == label]

    def find_nodes(self, label: str = None, prop: str = None, value=None) -> list[Node]:
        """
        Find nodes optionally filtered by label and/or a property value.
        Uses hash index when possible.
        """
        if label and prop and value is not None:
            key = f"{label}.{prop}"
            if key in self.indexes:
                ids = self.indexes[key].get(value, [])
                return [self.nodes[i] for i in ids if i in self.nodes]
            return [n for n in self.nodes.values() if n.label == label and n.props.get(prop) == value]

        if label:
            return self.get_nodes_by_label(label)

        return list(self.nodes.values())

    def get_outgoing_edges(self, node_id: int, edge_type: str = None) -> list[Edge]:
        eids = self.out_adj.get(node_id, [])
        edges = [self.edges[e] for e in eids if e in self.edges]
        if edge_type:
            edges = [e for e in edges if e.type == edge_type]
        return edges

    def match(self,
        start_label: str,
        start_filters: dict,
        hops: list[dict],
        where_filters: dict = None) -> list[dict]:
        """
        Full MATCH execution.

        start_label     : label of the first node in the pattern (e.g. "Person")
        start_filters   : property filters on the start node
        hops            : list of {"edge_type": ..., "node_label": ..., "node_filters": {...}}
        where_filters   : {"alias": {"prop": value}} applied after traversal
                          alias corresponds to position: 0 = start node, 1 = hop-1 node, etc.

        Returns list of dicts, each dict mapping hop index -> Node
        e.g. [{0: alice_node, 1: bob_node, 2: acme_node}, ...]
        """
        # seed: all nodes matching start
        candidates = self.find_nodes(label=start_label)
        for prop, val in start_filters.items():
            candidates = [n for n in candidates if n.props.get(prop) == val]

        # each "path" tracks the sequence of nodes matched so far
        paths = [{0: n} for n in candidates]

        for hop_index, hop in enumerate(hops):
            edge_type   = hop.get("edge_type")
            node_label  = hop.get("node_label")
            node_filters = hop.get("node_filters", {})
            next_paths = []

            for path in paths:
                current_node = path[hop_index]
                outgoing = self.get_outgoing_edges(current_node.id, edge_type=edge_type)

                for edge in outgoing:
                    neighbor = self.nodes.get(edge.to_id)
                    if neighbor is None:
                        continue
                    if node_label and neighbor.label != node_label:
                        continue
                    if not all(neighbor.props.get(p) == v for p, v in node_filters.items()):
                        continue
                    new_path = dict(path)
                    new_path[hop_index + 1] = neighbor
                    next_paths.append(new_path)

            paths = next_paths

        # Apply WHERE filters: where_filters = {alias_str -> {prop -> value}}
        if where_filters:
            filtered = []
            for path in paths:
                match = True
                for pos, filters in where_filters.items():
                    node = path.get(pos)
                    if node is None:
                        match = False
                        break
                    for prop, val in filters.items():
                        if node.props.get(prop) != val:
                            match = False
                            break
                if match:
                    filtered.append(path)
            paths = filtered

        return paths

    def shortest_path(self, from_id: int, to_id: int, max_hops: int = None) -> dict | None:
        """
        Dijkstra from from_id to to_id.
        Returns:
          {
            "nodes": [Node, ...],   # ordered list including start and end
            "edges": [Edge, ...],
            "length": int,          # number of hops
            "weight": float         # total weight
          }
        or None if no path found.
        BFS can also be used with the unweighted graph, since it guarantees shortest path.
        """
        if from_id not in self.nodes or to_id not in self.nodes:
            return None

        # (cost, node_id, path_nodes, path_edges)
        heap = [(0.0, from_id, [from_id], [])]
        visited = {}  # node_id -> best cost seen

        while heap:
            cost, node_id, path_nodes, path_edges = heapq.heappop(heap)

            if node_id in visited and visited[node_id] <= cost:
                continue
            visited[node_id] = cost

            if node_id == to_id:
                return {
                    "nodes": [self.nodes[n] for n in path_nodes],
                    "edges": [self.edges[e] for e in path_edges],
                    "length": len(path_edges),
                    "weight": cost
                }

            if max_hops is not None and len(path_edges) >= max_hops:
                continue

            for edge in self.get_outgoing_edges(node_id):
                neighbor_id = edge.to_id
                edge_weight = float(edge.props.get("weight", 1.0))
                new_cost = cost + edge_weight
                if neighbor_id not in visited or visited[neighbor_id] > new_cost:
                    heapq.heappush(heap, (
                        new_cost,
                        neighbor_id,
                        path_nodes + [neighbor_id],
                        path_edges + [edge.id]
                    ))

        return None

    def stats(self) -> dict:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "indexes": len(self.indexes),
            "index_keys": list(self.indexes.keys()),
        }
