from bsm.util import call_and_log

def run(param):
    package_dir = param['pkg_info']['dir']['package']
    cwd = param['action_param'].get('cwd', package_dir)

    cmd = param['action_param']['cmd']
    if not isinstance(cmd[0], list):
        cmd = [cmd]

    env = param.get('env')
    env_cmd = env.copy()
    for k, v in param['action_param'].get('env', {}).items():
        env_cmd[k] = v.format(**param['pkg_dir_list'])

    ret = 0
    with open(param['log_file'], 'w') as f:
        for c in cmd:
            ret = call_and_log(c, log=f, cwd=package_dir, env=env)
            if ret != 0:
                return {'success': False, 'message': 'Command "{0}" failed with exit code: {0}'.format(c, ret)}

    return {'success': ret==0, 'message': 'Command exit code: {0}'.format(ret)}
