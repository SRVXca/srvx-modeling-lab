"""Create a clean copy from a pinned git archive without touching the original repository metadata."""
import io
from pathlib import Path
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[2]
destination=ROOT/'h2k-hpxml-clean'
if destination.exists():raise RuntimeError('Existing clean copy must be inspected before recreation')
archive=subprocess.check_output(['git','-C',str(LAB/'repos/canmet-energy/h2k-hpxml'),'archive','0b77fcee8f1c717f0bfd02e4b5924c84244a9b6b'])
destination.mkdir()
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(destination,filter='data')
print(destination)
