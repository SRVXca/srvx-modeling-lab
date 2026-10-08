"""Pin artifact hashes and confirm the unrelated weather change has remained byte-identical."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[2];BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'
clean=json.loads((BUNDLE/'audit/clean-copy.json').read_text())
weather=LAB/'repos/canmet-energy/h2k-hpxml/src/h2k_hpxml/utils/weather_files.py'
current=hashlib.sha256(weather.read_bytes()).hexdigest()
if current!=clean['sourceWeatherSha256']:raise RuntimeError('Original dirty weather_files.py changed')
resources=Path('/home/o/.local/share/OpenStudio-HPXML-v1.12.0/HPXMLtoOpenStudio/resources')
pins={'translatorCommit':clean['commit'],'sourceWeatherModificationPreservedSha256':current,
      'openstudio':'3.11.0+241b8abb4d','openstudioHpxml':'1.12.0','hpxmlSchema':'5.0',
      'consumerSourceSha256':{name:hashlib.sha256((resources/name).read_bytes()).hexdigest()
            for name in ['defaults.rb','hpxml.rb','hvac.rb','version.rb','hpxml_schema/HPXML.xsd','hpxml_schematron/EPvalidator.sch']}}
(BUNDLE/'audit/tool-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
files=sorted(p for p in BUNDLE.rglob('*') if p.is_file() and p.name!='ARTIFACTS.sha256')
(BUNDLE/'ARTIFACTS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(BUNDLE))+'\n' for p in files))
print(f'Pinned {len(files)} evidence artifacts; original weather modification unchanged')
