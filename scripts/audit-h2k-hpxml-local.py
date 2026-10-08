#!/usr/bin/env python3
"""Read-only local H2K/HPXML candidate discovery.

Outputs filenames, XML element/attribute *names*, and translator code keyword hits.
Never emits model values, changes source, runs simulations, or asserts H2K field equivalence.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

CANDIDATE_TERMS = re.compile(
 r"air.?condit|cool|heat.?pump|furnace|boiler|water.?heat|hot.?water|domestic|geotherm|ground|heating|primary|secondary|hspf|seer|afue|cop|eer|capacity|efficiency|fuel|performance|energy.?factor|storage|tank|type1|type2|type3|type4",
 re.I,
)
COMPONENT_NAMES = [
 'system_air_conditioning.py', 'system_heat_pumps.py',
 'system_heating_primary.py','system_heating_secondary.py','system_hot_water.py',
 'system_coordinator.py','system_hvac_distribution.py',
]
CSV_FIELDS=['file','element_path','attributes','occurrences','evidence_level']
HITS_FIELDS=['file','line','matched_tokens','code_excerpt','evidence_level']

def save_csv(path, fields, records):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as fd:
        w=csv.DictWriter(fd,fieldnames=fields);w.writeheader();w.writerows(records)

def local_tag(tag):
    return tag.rsplit('}',1)[-1]

def xml_candidate_paths(file):
    # xml.etree avoids network schema fetches; values never leave this function.
    root=ET.parse(file).getroot()
    count=Counter()
    attrs={}
    def walk(node,parent,depth=0):
        if depth>30:return
        segment=local_tag(node.tag)
        path=f'{parent}/{segment}'
        if CANDIDATE_TERMS.search(path) or any(CANDIDATE_TERMS.search(a) for a in node.attrib):
            count[path]+=1
            attrs.setdefault(path,set()).update(local_tag(k) for k in node.attrib)
        for child in node:
            walk(child,path,depth+1)
    walk(root,'')
    return [(path,';'.join(sorted(attrs.get(path,set()))),n) for path,n in count.items()]

def build_report(root,out,max_xml):
    root=root.resolve()
    translator=root/'repos/canmet-energy/h2k-hpxml/src/h2k_hpxml/components'
    source_candidates=[]
    for filename in COMPONENT_NAMES:
        path=translator/filename
        if path.is_file():source_candidates.append(path)
    hits=[]
    for path in source_candidates:
        for line_no,line in enumerate(path.read_text(encoding='utf-8',errors='replace').splitlines(),1):
            matches=sorted({m.group().lower() for m in CANDIDATE_TERMS.finditer(line)})
            if matches:
                hits.append({'file':str(path.relative_to(root)), 'line':line_no,
                             'matched_tokens':';'.join(matches),
                             'code_excerpt':line.strip()[:220],
                             'evidence_level':'CODE_KEYWORD_HIT_ONLY'})
    # Read only bounded examples from known H2K/translator areas; large datasets excluded.
    search_dirs=[
      root/'repos/canmet-energy/h2k-hpxml/tests',
      root/'repos/canmet-energy/h2k-hpxml/src/h2k_hpxml/examples',
      root/'contributions/h2k-hpxml-issue-19/tests',
      root/'fixtures/buildings',
    ]
    xml_files=[]
    for directory in search_dirs:
        if directory.is_dir():
            for candidate in directory.rglob('*'):
                if len(xml_files)>=max_xml:break
                if candidate.is_file() and candidate.suffix.lower() in ('.h2k','.xml') and candidate.stat().st_size < 2_000_000:
                    xml_files.append(candidate)
    rows=[];failed=[]
    for path in xml_files:
        try:
            for element,attributes,n in xml_candidate_paths(path):
                rows.append({'file':str(path.relative_to(root)),'element_path':element,
                             'attributes':attributes,'occurrences':n,
                             'evidence_level':'OBSERVED_XML_TAG_NOT_VALIDATED_TARGET_MAPPING'})
        except (ET.ParseError,ValueError,OSError,RecursionError) as ex:
            failed.append({'file':str(path.relative_to(root)),'reason':type(ex).__name__})
    save_csv(out/'h2k-xml-candidate-paths.csv',CSV_FIELDS,rows)
    save_csv(out/'h2k-translator-keyword-evidence.csv',HITS_FIELDS,hits)
    summary={'status':'LOCAL_DISCOVERY_ONLY', 'h2k_candidate_paths':len(rows),
        'translator_keyword_hits':len(hits), 'translator_files_found':len(source_candidates),
        'xml_files_scanned':len(xml_files), 'xml_failures':failed,
        'warning':'No H2K fields verified by this script: a human must compare parser source + actual H2K schema + target converter output.'}
    (out/'audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print('H2K candidate audit:',json.dumps(summary))
    print('Output directory:',out)
    return summary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out',type=Path)
    parser.add_argument('--max-xml',type=int,default=60)
    args=parser.parse_args()
    if args.max_xml<1 or args.max_xml>300:parser.error('max-xml must be between 1 and 300')
    root=args.root.resolve()
    out=(args.out or root/'var/modeling-audit/h2k-hpxml-v0.1').resolve()
    if not root.is_dir():parser.error(f'root not found: {root}')
    build_report(root,out,args.max_xml)
if __name__=='__main__':main()
