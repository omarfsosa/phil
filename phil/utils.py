def group(lst, n):
    """Yield successive n-sized groups from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def argmin(seq):
    """
    The index of the smallest element in the sequence.
    """
    return min(range(len(seq)), key=seq.__getitem__)
