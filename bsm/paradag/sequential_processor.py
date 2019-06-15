class SequentialProcessor(object):
    def process(self, vertice, executor):
        results = []
        for vertex in vertice:
            result = executor.execute(executor.param(vertex))
            results.append((vertex, result))
        return results
