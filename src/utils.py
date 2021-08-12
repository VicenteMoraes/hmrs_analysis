def iter_map(map, levels):
    for key, value in map.items():
        if levels ==1:
            yield key, value
        else:
            for res in iter_map(value, levels-1):
                yield key, res
            