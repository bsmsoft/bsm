from packaging import version

def run(version1, version2):
    ver1 = version.parse(version1)
    ver2 = version.parse(version2)
    if ver1 > ver2:
        return 1
    if ver1 < ver2:
        return -1
    return 0
