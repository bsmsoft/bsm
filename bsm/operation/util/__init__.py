import re

from bsm.operation import Base

from bsm.git import Git
from bsm.git import GitNotFoundError
from bsm.git import GitEmptyUrlError

from bsm.logger import get_logger
_logger = get_logger()

def list_versions(release_repo, version_pattern, git_temp=None):
    try:
        if git_temp:
            git = Git(git_temp=git_temp)
        else:
            git = Git()
        tags = git.ls_remote_tags(release_repo)
    except GitNotFoundError:
        _logger.error('Git is not found. Please install "git" first')
        raise
    except GitEmptyUrlError:
        _logger.error('No release repository found. Please setup "release_repo" first')
        raise

    versions = {}

    pattern = re.compile(version_pattern)
    for tag in tags:
        m = pattern.match(tag)
        if not m:
            continue
        groups = m.groups()
        if len(groups) == 0:
            continue
        version = groups[0]
        if version in versions:
            _logger.warn('Duplicated version "{0}" found for tag "{1}", please check the version pattern "{2}"'.format(version, tag, version_pattern))
            continue
        versions[version] = tag

    return versions
