import json
import logging
from pathlib import Path
from mimetypes import guess_type
from multiprocessing import Pool

import magic

from .playlist import PlayList

logger = logging.getLogger(__name__)

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

def create_file(filename: str  = None):
  filetypes = ['video/', 'audio/']
  logger.debug(f'create_file({filename=})')
  if not filename or not Path(filename).is_file():
    return None
  mime_type = get_mime(filename)
  logger.debug(f'{mime_type=}')

  if any(x in mime_type for x in filetypes):
    ret_dict = {'fullpath': filename, 'mime': mime_type}
    logger.debug(f'{ret_dict=}')
    return ret_dict
  return None

def create_file_list_dict(files: list = None):
  if files is None:
    print('No files given!')
    return None

  if '__pl.json' in files:
    with open('__pl.json', encoding="UTF-8") as f:
      pl_dict = json.load(f)
    files.remove('__pl.json')
  else:
    pl_dict = PlayList().playlist_format()
  logger.debug(f'{pl_dict=}')

  with Pool(10) as p:
    pl_dict['list'].extend(list(filter(None,p.map(create_file, files))))
  logger.debug(f'{pl_dict=}')
  return pl_dict
