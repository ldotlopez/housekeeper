from urllib import request
import xml.etree.ElementTree
import copy
import re
import hashlib
from pydub import AudioSegment
import os


def hexdigest(buff, algorithm):
    try:
        obj = getattr(hashlib, algorithm)()
    except AttributeError as e:
        raise ValueError(algorithm) from e

    obj.update(buff)
    return obj.hexdigest()


class RadioCastellonCustomPodcast:
    SOURCE_PODCAST_URL = 'http://recursosweb.prisaradio.com/podcasts/634p.xml'
    NAMESPACES = {
        'ns0': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'ns1': 'http://www.w3.org/2005/Atom'
    }

    def __init__(self, data_dir, podcast_url, audio_url, programs=None):
        """
        datadir: Where to store generated audio
        podcast_url: Where is going to be published the generated podcast
        audio_url: Where is going to be published the generated audio
        programs: Filter some programs
        """
        for x in data_dir, podcast_url, audio_url:
            if not x.endswith('/'):
                raise ValueError(x)

        # FIXME: Implement storage interface
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.podcast_url = podcast_url
        self.audio_url = audio_url

        self.programs = programs

        buff = fetch(self.SOURCE_PODCAST_URL)
        self.root = xml.etree.ElementTree.fromstring(buff)
        self.process()

    def process(self):
        channel = self.root.find('./channel')
        items = channel.findall('./item')

        for item in items:
            if not self._is_interesting(item):
                channel.remove(item)
                continue

            self._replace_enclosure(item)

            if self._is_hoy_x_hoy_castellon(item):
                new_item = self._generate_a_quien_corresponda(channel, item)
                channel.append(new_item)

    def tostring(self):
        return xml.etree.ElementTree.tostring(self.root, encoding='unicode')

    def _replace_enclosure(self, item):
        enclosure = item.find('enclosure')

        x = re.search(
            r'/(\d+/\d+/\d+/\d+_\d+\.mp3)',
            enclosure.attrib['url']
        ).group(1)

        enclosure.attrib['url'] = 'http://sdmedia.playser.cadenaser.com/' + x

    def _is_hoy_x_hoy_castellon(self, item):
        title = item.find('title').text.lower().strip()
        return title.startswith('hoy por hoy castellón (')

    def _generate_a_quien_corresponda(self, channel, item, start=50*60,
                                      length=10*60):
        # Fetch and crop enclosure audio
        enclosure_url = item.find('./enclosure').attrib['url']

        digest = hexdigest(enclosure_url.encode('utf-8'), 'md5')
        output_filename = self.data_dir + '/' + digest + '.mp3'

        try:
            crop_audio(enclosure_url, output_filename,
                       start=start*1000, end=(start + length)*1000)
        except FileExistsError:
            pass

        clone = copy.deepcopy(item)

        # Rewrite title
        title = item.find('title').text.lower().strip()
        date = re.search(r'\((.+)\)$', title).group(1)
        clone_title = 'A quien corresponda ({date})'.format(date=date)
        clone.find('title').text = clone_title

        # Rewrite enclosure related tags
        clone.find('enclosure').attrib['url'] = (
            self.audio_url + digest + '.mp3')
        clone.find('guid').text = self.audio_url + digest + '.mp3'
        clone.find('enclosure').attrib['length'] = str(
            os.stat(output_filename).st_size)
        clone.find('ns0:duration', self.NAMESPACES).text = str(
            length)

        # Insert the new node
        return clone

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


def crop_audio(url, output_filename, start, end, format='mp3',
               tmp_suffix='.tmp'):
    if os.path.exists(output_filename):
        raise FileExistsError(output_filename)

    tmp_filename = output_filename + tmp_suffix
    req = request.urlopen(url)
    audio = AudioSegment.from_file(req, format=format)
    audio[start:end].export(tmp_filename, format=format)
    os.rename(tmp_filename, output_filename)


if __name__ == '__main__':
    obj = RadioCastellonCustomPodcast(
        data_dir='./storage/podcasts/audio/',
        podcast_url='http://cuarentaydos.com/_/podcasts/',
        audio_url='http://cuarentaydos.com/_/podcasts/audio/',
        programs=[
            'A quien corresponda',
            'Hoy por hoy Castellón',
            'La tertulia de Radio Castellón'
        ])

    with open('./storage/podcasts/radiocastellon.xml', 'w') as fh:
        fh.write(obj.tostring())
