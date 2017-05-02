from autopilot import pluginlib
from autopilot import tools
from autopilot.plugins.sync import sync


class Task(pluginlib.Task):
    __extension_name__ = 'sync'
    INTERVAL = '0'

    def __init__(self, settings):
        super().__init__(settings)

        # Parse options
        self.api = sync.SyncAPI(
            exclude=settings.get('plugins.sync.exclude', default=[])
        )

    def get_syncs(self):
        syncs = self.settings.get('syncs', default=[])

        for (id_, opts) in tools.walk_collection(syncs):
            genname = opts.pop('generator')
            genopts = {}

            if isinstance(genname, dict):
                genname, genopts = genname.pop('name'), genname

            gen = sync.generator_factory(genname, **genopts)
            try:
                tools.validate_mapping(opts,
                                       required=['source', 'destination'],
                                       optional=['hardlink', 'exclude'])
            except tools.MappingValidationError as e:
                print(repr(e))
                continue

            yield sync.SyncOperation(generator=gen, **opts)

    def execute(self, app):
        for op in self.get_syncs():
            self.api.sync(op)
