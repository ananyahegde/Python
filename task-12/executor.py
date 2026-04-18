import time
from graph import Graph, Node
from wal import WAL
from parser import parse, ParseError
from tabulate import tabulate


class ExecutorError(Exception):
    pass


class Executor:
    """
    Takes a parsed command dict and executes it against the graph.
    All mutations are logged to the WAL before being applied.
    Maintains an alias registry so CREATE NODE aliases can be referenced
    in subsequent CREATE EDGE and SHORTEST_PATH commands.
    """

    def __init__(self, graph: Graph, wal: WAL):
        self.graph = graph
        self.wal = wal
        # alias -> node_id, persists across commands in a session
        self.alias_map: dict[str, int] = {}

    def run(self, query: str) -> str:
        """
        Parse and execute a query string. Returns a result string to print.
        Catches parse and executor errors and returns them as error messages.
        """
        try:
            cmd = parse(query)
        except ParseError as e:
            return f"Parse error: {e}"

        try:
            return self._dispatch(cmd)
        except ExecutorError as e:
            return f"Error: {e}"

    def _dispatch(self, cmd: dict) -> str:
        op = cmd["cmd"]
        if op == "CREATE_NODE":
            return self._create_node(cmd)
        elif op == "CREATE_EDGE":
            return self._create_edge(cmd)
        elif op == "MATCH":
            return self._match(cmd)
        elif op == "SHORTEST_PATH":
            return self._shortest_path(cmd)
        elif op == "STATS":
            return self._stats()
        else:
            raise ExecutorError(f"Unknown command: {op}")

    # CREATE NODE
    def _create_node(self, cmd: dict) -> str:
        label = cmd["label"]
        props = cmd["props"]
        alias = cmd["alias"]

        node = self.graph.create_node(label=label, props=props)
        self.wal.log_create_node(label=label, props=props, node_id=node.id)
        self.alias_map[alias] = node.id

        return f"Node created: {label}#{node.id}"

    # CREATE EDGE
    def _create_edge(self, cmd: dict) -> str:
        from_alias = cmd["from_alias"]
        to_alias   = cmd["to_alias"]
        edge_type  = cmd["edge_type"]
        props      = cmd["props"]

        from_id = self.alias_map.get(from_alias)
        to_id   = self.alias_map.get(to_alias)

        if from_id is None:
            raise ExecutorError(f"Unknown alias '{from_alias}'. Create the node first.")
        if to_id is None:
            raise ExecutorError(f"Unknown alias '{to_alias}'. Create the node first.")

        edge = self.graph.create_edge(
            edge_type=edge_type,
            from_id=from_id,
            to_id=to_id,
            props=props
        )
        self.wal.log_create_edge(
            edge_type=edge_type,
            from_id=from_id,
            to_id=to_id,
            props=props,
            edge_id=edge.id
        )

        from_node = self.graph.nodes[from_id]
        to_node   = self.graph.nodes[to_id]
        return f"Edge created: {from_node} —{edge_type}-> {to_node}"

    # MATCH
    def _match(self, cmd: dict) -> str:
        start = time.perf_counter()

        paths = self.graph.match(
            start_label=cmd["start_label"],
            start_filters=cmd["start_filters"],
            hops=cmd["hops"],
            where_filters=cmd["where_filters"]
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        return_fields = cmd["return_fields"]

        if not paths:
            return "0 rows returned"

        if not return_fields:
            return f"{len(paths)} row(s) returned"

        # Count total nodes and edges touched across all paths
        total_nodes = len(paths) * (len(cmd["hops"]) + 1)
        total_edges = len(paths) * len(cmd["hops"])

        # Build result rows
        headers = [f"{f['alias']}.{f['prop']}" for f in return_fields]
        rows = []
        for path in paths:
            row = []
            for field in return_fields:
                node = path.get(field["pos"])
                value = node.props.get(field["prop"], "") if node else ""
                row.append(str(value))
            rows.append(row)

        table = tabulate(rows, headers=headers, tablefmt="psql")

        return (
            f"{table}\n"
            f"{len(rows)} row{'s' if len(rows) != 1 else ''} returned "
            f"(traversal: {total_nodes} nodes, {total_edges} edges) "
            f"in {elapsed_ms:.1f}ms"
        )

    # SHORTEST PATH
    def _shortest_path(self, cmd: dict) -> str:
        from_alias = cmd["from_alias"]
        to_alias = cmd["to_alias"]
        max_hops = cmd["max_hops"]

        from_id = self.alias_map.get(from_alias)
        to_id   = self.alias_map.get(to_alias)

        if from_id is None:
            raise ExecutorError(f"Unknown alias '{from_alias}'. Create the node first.")
        if to_id is None:
            raise ExecutorError(f"Unknown alias '{to_alias}'. Create the node first.")

        result = self.graph.shortest_path(from_id=from_id, to_id=to_id, max_hops=max_hops)

        if result is None:
            return f"No path found between {from_alias} and {to_alias}"

        nodes = result["nodes"]
        edges = result["edges"]

        path_parts = [nodes[0].props.get("name", str(nodes[0]))]
        for i, edge in enumerate(edges):
            path_parts.append(f"—{edge.type}->")
            path_parts.append(nodes[i + 1].props.get("name", str(nodes[i + 1])))

        path_str = " ".join(path_parts)
        return (
            f"Path: {path_str}\n"
            f"Length: {result['length']} hops | Total weight: {result['weight']}"
        )

    # STATS
    def _stats(self) -> str:
        s = self.graph.stats()
        index_list = ", ".join(s["index_keys"]) if s["index_keys"] else "none"
        wal_size   = self.wal.size_bytes()
        return (
            f"Nodes: {s['nodes']} | "
            f"Edges: {s['edges']} | "
            f"Indexes: {s['indexes']} ({index_list}) | "
            f"WAL size: {wal_size} bytes"
        )

