from cmd import Cmd
from random import shuffle
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Cli(Cmd):
  def __init__(self, completekey = "tab", stdin = None, stdout = None,
               player = None, playlist = None, default_actions = None,
               no_autostart = False, start_index = 0):
    super().__init__(completekey, stdin, stdout)
    self.player = player
    self.pl = playlist
    self.default_actions = default_actions or {}
    self.autostart = not no_autostart
    self.next_idx = start_index
    self.prev_idx = self.next_idx - 1
    self.save = True
    self.move = True
    if default_actions.get('start_randomized'):
      shuffle(self.pl)
    self.set_prompt()

  def do_q(self, _):
    '''Quit'''
    return True

  def do_l(self, _):
    '''List all entries in playlist'''
    num_width = len(str(len(self.pl)))
    for idx, item in enumerate(self.pl):
      prefix = '*' if self.next_idx == idx else ''
      print(f"{prefix:<1}{idx: >{num_width}} : {item.filename}")
    return False

  def do_z(self, _):
    '''Randomize playlist order'''
    shuffle(self.pl)
    self.set_index(0)
    return False

  def do_r(self, _):
    '''Replay playlist entry'''
    if self.next_idx > 0:
      self.set_index(self.next_idx - 1)
      return self.play_next()
    return False

  def do_p(self, _):
    '''Print out player options'''
    for key, val in self.player.get_args().items():
      print(f'{key:<10}{val}')
    return False

  def do_m(self, dest = None):
    '''Move previous file to dir'''
    self._move_file(dest)
    return self.play_next()

  def do_nm(self, _):
    '''Play next file without moving previous file'''
    return self.play_next()

  def do_nmq(self, _):
    '''Quit without moving previous file'''
    self.move = False
    return True

  def do_y(self, _):
    '''Delete file unless nodelete flag is set'''
    self._delete()
    return self.play_next()

  do_a = do_y

  def do_yq(self, _):
    '''Delete file unless nodelete flag is set'''
    self._delete()
    return self.do_nmq(_)

  def do_g(self, _):
    '''Move file to ./_gg/'''
    return self.do_m('_gg')

  def do_gq(self, _):
    '''Move file to ./._gg/ and quit'''
    self._move_file('_gg')
    return self.do_nmq(None)

  def do_ng(self, _):
    '''Move file to ./ngg/'''
    return self.do_m('ngg')

  def do_ngq(self, _):
    '''Move file to ./.ngg/ and quit'''
    self._move_file('ngg')
    return self.do_nmq(None)

  def do_details(self, _):
    '''Show details of file just played'''
    if self.previous_file():
      print(self.previous_file().details())
    return False
  
  def do_nosound(self, _):
    '''Toggle player audio on/off'''
    self.player.toggle_sound()
    return False

  def do_s(self, dest = ''):
    '''Save playlist to file'''
    import json
    dest = dest if dest else '__pl.json'
    pl = self.pl.export_playlist()
    pl['next_to_play'] = self.next_idx
    pl['next_filename'] = self.pl[self.next_idx].filename

    with open(dest, 'w') as fp:
      json.dump(pl, fp, indent=2)
    return False

  def do_sq(self, dest):
    '''Save playlist to file and quit'''
    self.do_s(dest)
    self.save = False
    return True

  def do_sort(self, _):
    '''Sort playlist'''
    self.pl.sort()
    self.set_index(0)
    return False

  def _delete(self):
    if not self.default_actions.get('nodelete'):
      self._move_file('.delete')
  
  def _move_file(self, dest = None, suffix = ''):
    if not (previous_file := self.previous_file()):
      return False
    new_filename  = previous_file.filename + suffix
    move_dir      = dest or (self.default_actions.get('move_file_dir') or 'sett')
    dest_dir      = Path(move_dir)
    dest_path     = dest_dir / new_filename
    src_file      = previous_file.fullpath

    logger.debug(f'{previous_file=}')
    logger.debug(f'{dest_dir=}')
    logger.debug(f'{dest_path=}')

    if dest_dir.exists() and not dest_dir.is_dir():
      print(f'\'{dest or "sett"}\' already exists and is not a directory!')
      print("Not moving the file!")
      return False
    else:
      dest_dir.mkdir(exist_ok = True)

    if dest_path.exists():
      from filecmp import cmp
      if cmp(src_file, dest_path, shallow = False):
        if dest == '.delete':
          print('File is already in .delete, removing!')
          src_file.unlink()
          self._remove_playlist_file(previous_file)
        else:
          print('File already exists and is the same! Moving file to .delete/')
          self._move_file('.delete')
      elif dest_path.suffix == '.notsame':
        suffixes = dest_path.suffixes
        num = int(suffixes[-2].strip('.')) + 1
        self._move_file(dest, f'.{num}.notsame')
      else:
        self._move_file(dest, '.0.notsame')
    else:
      print(f'Moving {previous_file.relpath} -> {dest_dir}')
      print('-'*20)
      src_file.rename(dest_path)
      self._remove_playlist_file(previous_file)
    return False

  def _remove_playlist_file(self, file):
    self.pl.remove(file)
    self.set_index(self.next_idx - 1)
    return None
    
  def set_index(self, next_idx):
    self.next_idx = next_idx
    self.prev_idx = next_idx - 1
    return next_idx

  def increment_index(self):
    return self.set_index(self.next_idx + 1)

  def next_file(self, increment = True):
    idx = self.next_idx
    next_file = None if idx >= len(self.pl) else self.pl[idx]
    if increment:
      self.increment_index()
    return next_file

  def previous_file(self):
    idx = self.prev_idx
    return None if (idx < 0 or idx >= len(self.pl)) else self.pl[idx]
  
  def play_next(self):
    next_file = self.next_file()
    if  next_file is None:
      print("No more files to play!")
      return True
    else:
      logger.debug(f'play_next(): {next_file}')
      print('-' * 20)
      print(f'Playing #{self.pl.index(next_file)}, "{next_file.filename}"')
      print()
      self.player.play(next_file.fullpath)
      logger.debug(f'play_next(): {next_file}')
    return False

  def emptyline(self):
    if self.default_actions.get('move_delete'):
      logger.info('Automatically moving file to ./.delete/')
      self._delete()
    elif self.default_actions.get('move_files'):
      logger.info('Automatically moving file to move directory')
      self._move_file()
    if self.next_idx >= len(self.pl):
      self.move = False
      self.save = False
    return self.play_next()

  def default(self, args):
    args = args.split(' ')
    arg = args[0]
    num = int(arg) if arg.lstrip('-+').isdecimal() else None
    logger.debug(f'{args=}')
    logger.debug(f'{arg=}')
    logger.debug(f'{num=}')
    if num is None:
      print(f'No such command: {arg}')
    elif num >= len(self.pl) or num < 0:
      print(f'No such index in playlist: {num}')
    else:
      self.set_index(num)
    return False

  def set_prompt(self):
    nf = self.next_file(increment = False)
    pf = self.previous_file()
    next_file = None if nf is None else nf.filename
    prev_file = None if pf is None else pf.filename
    prompt  = f'\nPrev: {prev_file}\n'
    prompt += f'Next: {next_file}\n'
    prompt += 'Do? '
    self.prompt = prompt
    return None
  
  def postcmd(self, stop, _):
    self.set_prompt()
    return stop

  def do_EOF(self, arg):
    '''EOF'''
    print()
    return True

  def preloop(self):
    if not self.pl:
      print('No files to play!')
      raise SystemExit()
    if self.autostart:
      self.play_next()
      self.set_prompt()
  
  def cmdloop(self):
    if self.default_actions.get('continuous'):
      while not self.play_next():
        pass
    else:
      return super().cmdloop()
  
  def postloop(self):
    if self.default_actions.get('move_delete') and self.move:
      self._delete()
    elif self.default_actions.get('move_files') and self.move:
      self._move_file()
    if self.default_actions.get('save_playlist') and self.save:
      self.do_s()
    print('Bye bye!')
