#!/usr/bin/env python

import os
import datetime
import argparse as argp
import logging
from mimetypes import guess_type
from pathlib import Path
import magic
from pmp._version import __version__
from pmp.playlist import PlayList
from pmp.mpv import Mpv
from pmp.cli import Cli

logger = logging.getLogger(__name__)

def main():
  logging.basicConfig(level = os.environ.get('LOGLEVEL', 'WARNING'))
  args = parse_args_setup()
  logger.debug(f'{args=}')

  pl = PlayList()
  player = setup_player(args)
  start = datetime.datetime.now()

  file_list = args.files if args.files else []
  logger.debug(f'{args.text_file=}')
  if args.text_file:
    for file in args.text_file:
      with open(file[0], 'r', encoding = 'UTF-8') as f:
        for line in f.readlines():
          file_list.append(line.strip('\n'))

  pl.load_playlist(create_file_list_dict(file_list))

  logger.debug(f'{pl=}')
  logger.info(f' Time used: {datetime.datetime.now() - start}')

  cli_args = setup_cli_args(args)
  prompt = Cli(playlist = pl, player = player, default_actions = cli_args,
               no_autostart = args.no_autostart)
  try:
    prompt.cmdloop()
  except KeyboardInterrupt:
    prompt.do_EOF(None)
    prompt.postloop()

def create_file_list_dict(files: list = None):
  if files is None:
    print('No files given!')
    return None

  pl_dict = PlayList().playlist_format()
  logger.debug(f'{pl_dict=}')

  for f in files:
    fi = create_file(f)
    if fi:
      pl_dict['list'].append(fi)
  logger.debug(f'{pl_dict=}')
  return pl_dict

def setup_cli_args(args):
  cli_args = {
    'nodelete': args.no_delete,
    'continuous': args.no_wait,
    'move_files': args.move_files,
    'move_delete': args.move_delete,
    'save_playlist': args.save_playlist,
    'move_file_dir': args.move_file_dir if args.move_file_dir else None,
    'start_randomized': args.randomize
  }
  return cli_args

def setup_player(args):
  player = Mpv()
  player_args = player.get_args()
  player_args['nosound'] = args.nosound
  player_args['cache']   = args.cache
  player_args['verbose'] = args.verbose
  player_args['stereo']  = args.stereo
  _ = player_args.update({'slang': args.subtitle_language}) if args.subtitle_language else None
  _ = player_args.update({'alang': args.audio_language}) if args.audio_language else None
  _ = player_args.update({'sid': args.subtitle_id}) if args.subtitle_id else None
  _ = player_args.update({'aid': args.audio_id}) if args.audio_id else None
  player.set_args(player_args)

  return player

def create_file(filename: str  = None):
  filetypes = ['video/', 'audio/']
  if not filename:
    return None
  mime_type = get_mime(filename)
  logger.debug(f'{mime_type=}')

  if any(x in mime_type for x in filetypes):
    ret_dict = {'fullpath': filename, 'mime': mime_type}
    logger.debug(f'{ret_dict=}')
    return ret_dict
  return None

def get_mime(filename: str = None):
  if filename is None:
    return None
  suffix = Path(filename).suffix.split('.')[-1]
  deep_check = False
  decs = ['text/', 'model/']
  mime_type = guess_type(filename)[0]

  if mime_type is None:
    deep_check = True
  elif any(x in mime_type for x in decs):
    deep_check = True
  if suffix.isdecimal() and 1 <= int(suffix) <= 9:
    deep_check = True

  if deep_check:
    logger.debug('Doing deep mime check')
    mime_type = magic.detect_from_filename(filename).mime_type
  return mime_type

def parse_args_setup():
  p = argp.ArgumentParser(description = 'Playlist player')
  p.add_argument('files', metavar = '<files>', nargs='*',
                 help = 'Media or playlist files to play')
  p.add_argument('-n', '--nosound', action = 'store_true', default = False,
                 help = 'Play files without sound')
  p.add_argument('-z', '--randomize', action = 'store_true', default = False,
                 help = 'Randomize playlist at start')
  p.add_argument('-x', '--save-playlist', action = 'store_true', default = False,
                 help = 'Save playlist after playing each entry')
  p.add_argument('-d', '--move-delete', action = 'store_true', default = False,
                 help = 'Move file to ./.delete after playing by default')
  p.add_argument('-m', '--move-files', action = 'store_true', default = False,
                 help = 'Move files to ./sett after playing by default')
  p.add_argument('-M', '--move-file-dir', metavar = '<dir to automove to>', type = str,
                 help = 'Set default dir to move files after playing')
  p.add_argument('-D', '--no-delete', action = 'store_true', default = False,
                 help = 'Do not delete files no matter what we say')
  p.add_argument('-c', '--cache', metavar = '<kBytes>', type = int,
                 help = 'Size of mpv cache in kBytes')
  p.add_argument('-q', '--no-wait', action = 'store_true', default = False,
                 help = 'Do not wait for action between files')
  p.add_argument('-s', '--stereo', action = 'store_true', default = False,
                 help = "Force mpv to use stereo audio")
  p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                 help = 'Make player output more verbose')
  p.add_argument('-#', '--start-at', default = None, type = int,
                 help = "Start playing at numbered playlist postition")
  p.add_argument('-t', '--text-file', metavar = '<filename>', nargs = 1, action='append',
                 type = str,
                 help = 'Pass a text file with path to files to play, one on each line')
  p.add_argument('-j', '--subtitle-language', default = None, type = str,
                 help = 'Set mpv subtitle language by subtitle language code')
  p.add_argument('-J', '--subtitle-id', default = None, type = int,
                 help = 'Set mpv subtitle language by subtitle language id')
  p.add_argument('-l', '--audio-language', default = None, type = str,
                 help = 'Set mpv audio language by audio language code')
  p.add_argument('-L', '--audio-id', default = None, type = int,
                 help = 'Set mpv audio language by audio language id')
  p.add_argument('-a', '--no-autostart', action = 'store_true', default = False,
                 help = 'Do not automatically start playing')
  p.add_argument('-V', '--version', action = 'version', version = f'%(prog)s {__version__}',
                 help = 'Show program version')
  return p.parse_args()

if __name__ == "__main__":
  main()
