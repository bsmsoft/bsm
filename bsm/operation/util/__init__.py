import re

from bsm.logger import get_logger
_logger = get_logger()


def list_versions(release_repo, version_pattern, git):
    tags = git.ls_remote_tags(release_repo)

    versions = {}

    pattern = re.compile(version_pattern)
    for tag in tags:
        m = pattern.match(tag)
        if not m:
            continue
        groups = m.groups()
        if not groups:
            continue
        version = groups[0]
        if version in versions:
            _logger.warning(
                'Duplicated version "%s" found for tag "%s", please check the version pattern "%s"',
                version, tag, version_pattern)
            continue
        versions[version] = tag

    return versions
