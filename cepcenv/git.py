import subprocess


class GitError(Exception):
    pass


class Git(object):
    def __init__(self, repo_path):
        self.__repo_path = repo_path

    def __git_cmd(self, cmd, *args):
        full_cmd = ['git', cmd] + list(args)
        try:
            p = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.__repo_path)
            out, err = p.communicate()
            out = out.decode()
            err = err.decode()
            ret = p.returncode
        except Exception as e:
            raise GitError('Exception while running git command "{0}": {1}'.format(cmd, e))

        if ret != 0:
            raise GitError('Git command "{0}" failed with exit code {1}: {2}'.format(' '.join(full_cmd), ret, err))

        return out

    def clone(self, remote_path):
        out = self.__git_cmd('clone', remote_path, self.__repo_path)

    def checkout(self, branch):
        out = self.__git_cmd('checkout', branch)

    def __list_ref(self, ref):
        ref_prefix = 'refs/' + ref
        out = self.__git_cmd('for-each-ref', '--format=%(refname)', ref_prefix)
        items = []
        for i in out.splitlines():
            i = i.strip()
            i = i[len(ref_prefix)+1:]
            if i:
                items.append(i)
        return items

    def list_branch(self):
        return self.__list_ref('heads')

    def list_tag(self):
        return self.__list_ref('tags')
