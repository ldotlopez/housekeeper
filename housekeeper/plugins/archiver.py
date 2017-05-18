from housekeeper import (
    kit,
    pluginlib
)
from housekeeper.lib import hkfilesystem, hkdatetime


def archive(source, delta, destination=None, dry_run=False):
    source = hkfilesystem.pathname_normalize(source)

    if destination is None:
        destination = source + ' (Archive)'
    else:
        destination = hkfilesystem.pathname_normalize(destination)

    delta = hkdatetime.parse_timespan(delta)

    ret = hkfilesystem.archive(
        source,
        destination,
        diff=delta,
        filter_func=is_archivable_filter,
        dry_run=dry_run)

    if dry_run:
        for (op, *args) in ret:
            if op == hkfilesystem.Operations.MOVE:
                print("mv '{}' '{}'".format(*args))

            elif op == hkfilesystem.Operations.UNLINK:
                print("rm '{}'".format(*args))


def is_archivable_filter(dirpath, dirnames, filenames):
    # Skip .sync dir
    try:
        dirnames.remove('.sync')
    except ValueError:
        pass

    # Skip hidden files
    hidden = [x for x in filenames if x[0] == '.']
    for x in hidden:
        filenames.remove(x)


class ArchiveCommand(pluginlib.Applet):
    __extension_name__ = 'archive'
    HELP = 'Archive stuff'

    PARAMETERS = (
        pluginlib.Parameter('from', abbr='f', required=True),
        pluginlib.Parameter('to', abbr='t', required=False),
        pluginlib.Parameter('delta', abbr='d', required=True),
        pluginlib.Parameter('dry-run', abbr='n', action='store_true', required=False)
    )
    # PARAMETERS = (
    #     pluginlib.argument(
    #         '-f', '--from',
    #         dest='src',
    #         required=True
    #     ),
    #     pluginlib.argument(
    #         '-t', '--to',
    #         dest='dst',
    #         required=False
    #     ),
    #     pluginlib.argument(
    #         '-d', '--delta',
    #         required=True
    #     ),
    #     pluginlib.argument(
    #         '-n', '--dry-run',
    #         action='store_true',
    #         required=False
    #     )
    # )

    # def execute(self, app, arguments):
    #     archive(source=arguments.src,
    #             destination=arguments.dst,
    #             delta=arguments.delta,
    #             dry_run=arguments.dry_run)

    def main(self, source, delta, destination=None, dry_run=False):
        return archive(
            source=source,
            destination=destination,
            delta=delta,
            dry_run=True)


class CronTask(pluginlib.Task):
    __extension_name__ = 'archive'
    INTERVAL = '1H'

    def execute(self, core):
        for params in core.settings.get('archive', []):
            archive(**params)


__housekeeper_extensions__ = [
    ArchiveCommand,
    CronTask
]