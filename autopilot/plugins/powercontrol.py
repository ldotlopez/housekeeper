from autopilot import pluginlib


import os
import subprocess


import requests


def get_api(method, **params):
    if 'key' in params:
        params['key'] = os.path.expanduser(params['key'])

    if method == 'ssh':
        return SSHAPI(**params)

    elif method == 'ddwrt':
        return DDWRT(**params)

    else:
        raise NotImplementedError()


class API:
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.args = args
        self.kwargs = kwargs

    def shutdown(self):
        pass

    def reboot(self):
        pass


class APIError(Exception):
    pass


class SSHAPI(API):
    def build_cmdl(self, action, ssh_cmd=None, key=None, user=None,
                   sudo=False):
        if ssh_cmd:
            cmdl = [x.strip() for x in ssh_cmd.split()]
        else:
            cmdl = ['ssh']

        if key:
            cmdl.extend(['-i', key])

        # Set ssh options
        cmdl.extend(['-oPasswordAuthentication=No'])

        # Set user
        if user:
            cmdl.append('-oUser={}'.format(user))

        # Connect to host
        cmdl.append(self.host)

        # non-interactive sudo
        if sudo:
            cmdl.append('sudo -n ')
        else:
            cmdl.append('')

        cmdl[-1] += action

        return cmdl

    def execute(self, cmdl):
        try:
            subprocess.check_output(cmdl)
        except subprocess.CalledProcessError as e:
            if e.returncode == 255:
                pass
            else:
                raise pluginlib.PluginError(code=e.returncode, output=e.output) \
                    from e

    def shutdown(self):
        self.execute(self.build_cmdl('/sbin/poweroff', **self.kwargs))

    def reboot(self):
        self.execute(self.build_cmdl('/sbin/reboot', **self.kwargs))


class DDWRT(API):
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def shutdown(self):
        raise NotImplementedError()

    def reboot(self):
        # http://192.168.1.2/apply.cgi
        # import ipdb; ipdb.set_trace(); pass
        pass


class PowerControl(pluginlib.Command):
    ARGUMENTS = (
        pluginlib.argument(
            '--host', type=str,
            required=True
        ),
    )

    def execute(self, app, arguments):
        host = arguments.host
        conf = app.settings.get('powercontrol', {})

        if host not in conf:
            msg = 'Unknow host «{host}»'
            msg = msg.format(host=host)
            raise pluginlib.ConfigurationError(msg)

        if not isinstance(conf[host], dict):
            msg = "Invalid configuration for host {host}"
            msg = msg.format(host=host)
            raise pluginlib.ConfigurationError(msg)

        if isinstance(self, (Shutdown, Poweroff)):
            get_api(**conf[host]).shutdown()

        elif isinstance(self, Reboot):
            get_api(**conf[host]).reboot()

        else:
            raise pluginlib.ArgumentError('Unknow command')


class Poweroff(PowerControl):
    __extension_name__ = 'poweroff'
    HELP = 'poweroff remote stuff'


class Reboot(PowerControl):
    __extension_name__ = 'reboot'
    HELP = 'reboot remote stuff'


class Shutdown(PowerControl):
    __extension_name__ = 'shutdown'
    HELP = 'shutdown remote stuff'


__autopilot_extensions__ = [
    Poweroff,
    Shutdown,
    Reboot
]
