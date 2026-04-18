# wal.py
import json
import os
from graph import Graph


class WAL:
    """
    Write-Ahead Log for the graph database.
    
    Every mutation (CREATE NODE, CREATE EDGE) is serialized as a JSON line
    and fsynced to disk before being applied in memory. On startup, if a
    WAL file exists, it is replayed line by line to reconstruct graph state.
    """

    def __init__(self, path: str, graph: Graph):
        self.path = path
        self.graph = graph
        self._file = None

    def open(self):
        """Open the WAL file, replaying existing entries if the file exists."""
        if os.path.exists(self.path):
            self._replay()
        self._file = open(self.path, "a", encoding="utf-8")

    def close(self):
        """Flush and close the WAL file."""
        if self._file:
            self._file.flush()
            self._file.close()
            self._file = None

    def log_create_node(self, label: str, props: dict, node_id: int):
        """Append a CREATE_NODE entry to the WAL and fsync."""
        entry = {"op": "CREATE_NODE", "id": node_id, "label": label, "props": props}
        self._append(entry)

    def log_create_edge(self, edge_type: str, from_id: int, to_id: int, props: dict, edge_id: int):
        """Append a CREATE_EDGE entry to the WAL and fsync."""
        entry = {"op": "CREATE_EDGE", "id": edge_id, "type": edge_type,
                 "from_id": from_id, "to_id": to_id, "props": props}
        self._append(entry)

    def size_bytes(self) -> int:
        """Return current size of the WAL file in bytes."""
        if os.path.exists(self.path):
            return os.path.getsize(self.path)
        return 0

    def _append(self, entry: dict):
        """Serialize entry as a JSON line, write, and fsync to disk."""
        line = json.dumps(entry) + "\n"
        self._file.write(line)
        self._file.flush()
        os.fsync(self._file.fileno())

    def _replay(self):
        """
        Read every line in the WAL file and re-apply each operation
        to the graph. Called once on startup before opening for append.
        """
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                op = entry["op"]

                if op == "CREATE_NODE":
                    self.graph.create_node(
                        label=entry["label"],
                        props=entry["props"],
                        node_id=entry["id"]
                    )
                elif op == "CREATE_EDGE":
                    self.graph.create_edge(
                        edge_type=entry["type"],
                        from_id=entry["from_id"],
                        to_id=entry["to_id"],
                        props=entry["props"],
                        edge_id=entry["id"]
                    )
