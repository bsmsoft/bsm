from bsm.cmd import Base


class LsAvail(Base):
    def execute(self, list_all, tag):
        versions = self._bsm.ls_avail(list_all)
        if not tag:
            version_names = list(versions.keys())
            version_names.sort()
            return version_names
        return versions
