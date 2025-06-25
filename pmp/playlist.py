from .file import File
import logging

logger = logging.getLogger(__name__)

class PlayList(list):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @staticmethod
  def playlist_format():
    return {
      'type': 'Fredriks playlist format',
      'next_to_play': 0,
      'next_filename': "",
      'list': []
    }

  def load_playlist(self, playlist: dict = None):
    if playlist is None:
      raise ValueError('Playlist is None!')
    data = playlist.get('list') or playlist.get('data') or []
    logger.debug(f'{data=}')
    if not isinstance(data, list):
      raise ValueError('Data is not a list!')

    for e in data:
      f = File(e['fullpath'])
      f.set_mime(e['mime'])
      if f not in self:
        self.append(f)

  def export_playlist(self):
    jpl = self.playlist_format()
    for i in self:
      jpl['list'].append(i.as_dict())
    return jpl
