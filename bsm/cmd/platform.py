import click

class Platform(object):
    def execute(self, config, config_version, output_all, output_title,
            output_arch, output_os, output_compiler, output_platform):
        if output_all:
            output_arch = True
            output_os = True
            output_compiler = True
            output_platform = True
        if not (output_arch or output_os or output_compiler or output_platform):
            output_platform = True

        output_final = ''
        output_items = ((output_arch, 'arch'), (output_os, 'os'), (output_compiler, 'compiler'), (output_platform, 'platform'))
        for o, v in output_items:
            if o:
                if output_title:
                    output_final += '{0:8} : '.format(v)
                output_final += config_version.config[v]
                output_final += '\n'

        click.echo(output_final, nl=False)
