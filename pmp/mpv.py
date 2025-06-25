import subprocess
import logging

logger = logging.getLogger(__name__)

class Mpv:
  __match_flags = {
    'nosound': '--no-audio',
    'verbose': '-v',
    'stereo': '--audio-channels=stereo'
  }

  def __init__(self, args: dict = None):
    self.args = {}
    for key in Mpv.__match_flags:
      self.args[key] = False
    if args is not None:
      self.args.update(args)

  def get_args(self):
    return self.args.copy()

  def set_args(self, args: dict = None):
    if args:
      self.args.update(args)

  def toggle_sound(self):
    self.args['nosound'] = not self.args['nosound']

  def play(self, file: str = None):
    if not file:
      raise ValueError('No file to play!')
    cmd = ['/usr/bin/env', 'mpv', '--fs']
    flags = Mpv.__match_flags
    for key, value in self.args.items():
      if key in flags:
        _ = cmd.append(flags[key]) if value else None
      else:
        _ = cmd.append(f'--{key}={value}') if value else None

    cmd.append(file)
    logger.debug(f'{cmd=}')
    subprocess.run(cmd, check = False)
