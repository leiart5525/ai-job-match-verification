#!/usr/bin/env python3
import argparse, shutil
from pathlib import Path
p=argparse.ArgumentParser(description='Install skill without overwriting existing files');p.add_argument('--dest',required=True);a=p.parse_args()
src=Path(__file__).resolve().parent/'skills/ai-job-match-verification';dest=Path(a.dest).expanduser()/src.name
if dest.exists():p.error(f'Already exists: {dest}; choose another directory or manage existing installation explicitly.')
shutil.copytree(src,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc','node_modules'))
print(f'Installed: {dest}')
