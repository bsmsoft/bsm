from packaging import version

def run(pkg1, pkg2):
    v1 = version.parse(pkg1.get('version', ''))
    v2 = version.parse(pkg2.get('version', ''))
    if v1 > v2:
        return 1
    if v1 < v2:
        return -1
    return 0
