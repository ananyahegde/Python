import os
from graph import Graph
from wal import WAL
from executor import Executor

WAL_PATH = "graphdb.wal"


def main():
    graph = Graph()
    wal = WAL(path=WAL_PATH, graph=graph)
    wal.open()
    executor = Executor(graph=graph, wal=wal)

    print("=== Graph DB Shell ===")
    print("Type EXIT to quit.\n")

    buffer = ""

    while True:
        try:
            prompt = "graphdb> " if not buffer else "       > "
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not line:
            continue

        if line.upper() == "EXIT":
            break

        # Accumulate multi-line queries (WHERE / RETURN on next lines)
        buffer = (buffer + " " + line).strip()

        # A query is complete when it doesn't end with a keyword
        # that expects continuation
        last_token = buffer.split()[-1].upper()
        if last_token in ("WHERE", "RETURN"):
            continue

        result = executor.run(buffer)
        print(result)
        buffer = ""

    wal.close()


if __name__ == "__main__":
    main()
