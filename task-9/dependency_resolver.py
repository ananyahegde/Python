def resolve(plugins: list[PluginBase]) -> list[PluginBase]:
    """
    Takes a list of plugin objects and returns them in activation order.
    Raises an error if a circular dependency is detected.
    Uses topological sorting algorithm.
    """

    graph = {p.name: p.dependencies for p in plugins}
    plugin_map = {p.name: p for p in plugins}
    visited = set()
    result = []

    def dfs(name, visiting=None):
        if visiting is None:
            visiting = set()
        if name in visiting:
            raise Exception(f"Circular dependency detected: {name}")
        if name in visited:
            return
        visiting.add(name)

        for dep in graph[name]:
            dfs(dep, visiting)

        visiting.remove(name)
        visited.add(name)
        result.append(plugin_map[name])

    for plugin in plugins:
        dfs(plugin.name)

    return result
