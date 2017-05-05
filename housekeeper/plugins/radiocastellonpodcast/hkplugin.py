from . import rcpodcast
from housekeeper import pluginlib


class RadioCastellonPodcastCommand(pluginlib.Command):
    __extension_name__ = 'radiocastellon'

    HELP = 'Generate custom podcast for «Radio Castellón»'
    ARGUMENTS = (
        pluginlib.argument(
            '--data-dir'
        ),
        pluginlib.argument(
            '--podcast-url'
        ),
        pluginlib.argument(
            '--audio-url'
        ),
        pluginlib.argument(
            '--program',
            action='append'
        ),
    )

    def execute(self, app, arguments):
        kwargs_keys = 'data_dir', 'podcast_url', 'audio_url', 'program'

        kwargs = {k: getattr(arguments, k, None) for k in kwargs_keys}
        kwargs['programs'] = kwargs.pop('program')
        kwargs = {k: v for (k, v) in kwargs.items() if v}

        print(repr(kwargs))
        # rcp = rcpodcast.RadioCastellonCustomPodcast(**kwargs)
