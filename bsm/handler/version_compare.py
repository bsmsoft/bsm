from packaging import version

def run(ver1, ver2):
    v1 = version.parse(ver1)
    v2 = version.parse(ver2)
    if v1 > v2:
        return 1
    if v1 < v2:
        return -1
    return 0
