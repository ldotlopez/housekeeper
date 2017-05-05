from autopilot import pluginlib


from appkit import application, network


import falcon


class AemetAPI:
    def __init__(self, location):
        self.location = location

    @property
    def xml_url(self):
        base = 'http://www.aemet.es/xml/municipios/localidad_{location}.xml'
        return base.format(location=self.location)

    def get(self, key):
        parts = key.split('.')

        if parts[0] == 'rain':
            if parts[1] == 'today':
                pass

            if parts[1] == 'tomorrow':
                pass

        else:
            raise ValueError(key)



class AemetEndPoint(pluginlib.APIEndPoint):
    __extension_name__ = 'aemet'

    def on_get(self, req, resp):
        when = req.params.get('when') or 'today'

        api = AemetAPI(location=12040)
        api.get('rain.tomorrow')

        resp.status = falcon.HTTP_200
        resp.context['result'] = {
            'url': api.xml_url
        }


class AemetCommand(pluginlib.Command):
    HELP = 'aemet'
    ARGUMENTS = (
        pluginlib.cliargument(
            'when',
            help='keywords')
    )

    def execute(self, app, arguments):
        print(repr(arguments))


__autopilot_extensions__ = [
    AemetCommand,
    AemetEndPoint
]


if __name__ == '__main__':
    application.execute(AemetCommand)
