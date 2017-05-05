from urllib import request
import xml.etree.ElementTree
import copy
import re
import hashlib
from pydub import AudioSegment
import os
import logging


class RadioCastellonCustomPodcast:
    SOURCE_PODCAST_URL = 'http://recursosweb.prisaradio.com/podcasts/634p.xml'

    def __init__(self, base_url, datadir, programs=None):
        self.logger = logging.getLogger()
        self.root = xml.etree.ElementTree.fromstring(fetch(self.SOURCE_PODCAST_URL))
        self.programs = programs
        self.datadir = datadir
        os.makedirs(datadir, exist_ok=True)
        self.process()

    def process(self):
        channel = self.root.find('./channel')
        items = channel.findall('./item')

        for item in items:
            self._append_a_quien_corresponda(channel, item)

            if not self._is_interesting(item):
                channel.remove(item)
                continue

    def tostring(self):
        return xml.etree.ElementTree.tostring(self.root, encoding='unicode')

    def _append_a_quien_corresponda(self, channel, item):
        title = item.find('title').text.lower().strip()

        if not title.startswith('hoy por hoy castellón ('):
            return

        clone = copy.deepcopy(item)

        date = re.search(r'\((.+)\)$', title).group(1)
        clone_title = 'A quien corresponda ({date})'.format(date=date)
        clone.find('title').text = clone_title

        media_url = clone.find('./enclosure').attrib['url']
        digest = hashlib.md5()
        digest.update(media_url.encode('utf-8'))
        digest = digest.hexdigest()

        output_filename = self.datadir + '/' + digest + '.mp3'
        crop_audio(media_url, output_filename, start=45*60*1000, end=55*60*1000)
        import ipdb; ipdb.set_trace(); pass

        channel.append(clone)

        import ipdb; ipdb.set_trace(); pass

    def _is_interesting(self, item):
        if not self.programs:
            return True

        programs = [x.lower().strip() + ' (' for x in self.programs]

        title = item.find('title').text.lower().strip()
        for prog in programs:
            if title.startswith(prog):
                return True

        return False


def fetch(url):
    with request.urlopen(url) as fh:
        return fh.read()


def crop_audio(url, output_filename, start, end, format='mp3', tmp_suffix='.tmp'):
    if os.path.exists(output_filename):
        raise FileExistsError(output_filename)

    tmp_filename = output_filename + tmp_suffix
    req = request.urlopen(url)
    audio = AudioSegment.from_file(req, format=format)
    audio[start:end].export(tmp_filename, format=format)
    os.rename(tmp_filename, output_filename)


PROGRAMS = [
    'A quien corresponda',
    'Hoy por hoy Castellón',
    'La tertulia de Radio Castellón'
]


if __name__ == '__main__':
    print(RadioCastellonCustomPodcast(programs=PROGRAMS, datadir='./data', base_url='http://cuarentaydos.com/_/podcasts').tostring())
