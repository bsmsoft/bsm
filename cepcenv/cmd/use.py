import os
import click

from cepcenv.use import Use as CepcenvUse

class Use(object):
    def execute(self, config, config_version, config_release, shell):
        script = ''


        script += shell.unset_env('CEPCSOFT_VERSION')

        if 'CEPCENV_ENV_LIST' in os.environ:
            for k in os.environ['CEPCENV_ENV_LIST'].split():
                script += shell.unset_env(k)
            script += shell.unset_env('CEPCENV_ENV_LIST')

        old_path = {}
        if 'CEPCENV_PATH_LIST' in os.environ:
            for k in os.environ['CEPCENV_PATH_LIST'].split():
                if k in os.environ:
                    old_path[k] = os.environ[k].split(os.pathsep)
                else:
                    old_path[k] = []

                if ('CEPCENV_'+k) in os.environ:
                    old_val = os.environ['CEPCENV_'+k].split(os.pathsep)
                    for v in old_val:
                        if v in old_path[k]:
                            old_path[k].remove(v)

                    if old_path[k]:
                        script += shell.set_env(k, os.pathsep.join(old_path[k]))
                    else:
                        script += shell.unset_env(k)

                    script += shell.unset_env('CEPCENV_'+k)

            script += shell.unset_env('CEPCENV_PATH_LIST')


        obj = CepcenvUse(config, config_release)
        path, env = obj.run()


        path_list = []
        env_list = []

        for k, v in path.items():
            if not v:
                continue

            val = os.pathsep.join(v)
            script += shell.set_env('CEPCENV_'+k, val)

            if k in old_path and old_path[k]:
                val += (os.pathsep + os.pathsep.join(old_path[k]))
            elif k in os.environ and os.environ[k]:
                val += (os.pathsep + os.environ[k])
            script += shell.set_env(k, val)

            path_list.append(k)

        for k, v in env.items():
            script += shell.set_env(k, v)
            env_list.append(k)

        script += shell.set_env('CEPCENV_PATH_LIST', ' '.join(path_list))
        script += shell.set_env('CEPCENV_ENV_LIST', ' '.join(env_list))

        script += shell.set_env('CEPCSOFT_VERSION', config_version.config['version'])

        click.echo(script, nl=False)
