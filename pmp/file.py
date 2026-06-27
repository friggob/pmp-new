import json
from pathlib import Path

class File(Path):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if self.is_file():
      self.fullpath = Path(self).resolve()
      self.filename = self.name
      self.dirname  = self.fullpath.parent
      self.relpath  = self.fullpath.relative_to(Path.cwd(), walk_up = True)
      self.mime     = None
      self.tags	    = []
    else:
      raise ValueError(f'Path "{self}" must point to a valid file!')

  def set_mime(self, mime: str = None):
    if mime:
      self.mime = mime

  def details(self):
    details = {
      'Full Path':     str(self.fullpath),
      'Filename':      str(self.filename),
      'Directory':     str(self.dirname),
      'Relative path': str(self.relpath),
      'Mime-type':     str(self.mime),
      'Tags':          self.tags
    }
    return json.dumps(details, indent=2)

  def as_dict(self):
    return {
      'fullpath': str(self.fullpath),
      'filename': str(self.filename),
      'dirname':  str(self.dirname),
      'relpath':  str(self.relpath),
      'mime':     str(self.mime),
      'tags':     self.tags
    }

  def add_tag(self, tag):
    if isinstance(tag, str):
      if tag not in self.tags:
        self.tags.append(tag)
    else:
      raise ValueError('Tag must be a string!')

  def remove_tag(self, tag):
    if tag in self.tags:
      self.tags.remove(tag)
