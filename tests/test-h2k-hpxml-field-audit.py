#!/usr/bin/env python3
"""Run the standalone candidate matrix checks. No additional dependencies."""
import csv
import json
from pathlib import Path
import tempfile
import subprocess
import sys

BUNDLE = Path(__file__).resolve().parents[1]

def check_matrix(root):
    f=root/'registry/h2k-hpxml-field-matrix.v0.1.csv'
    with f.open(newline='',encoding='utf-8') as infile:
        rows=list(csv.DictReader(infile))
    assert len(rows)>=60, f'Expected broad mapping inventory, got {len(rows)}'
    families={r['family'] for r in rows}
    assert len(families)==6, families
    assert all(r['h2k_verification']=='PENDING_LOCAL_XML_TRANSLATOR_AUDIT' for r in rows)
    assert all(r['mapping'] and r['hpxml_element'] for r in rows)
    # Ensure differentiating observed equipment from building/scenario inputs.
    assert {r['scope'] for r in rows}=={'EQUIPMENT_EVIDENCE','SCENARIO_ASSEMBLY'}
    assert not any(r['metric']=='heatingInputCapacity' and r['hpxml_target_field']=='HeatingCapacity' and r['hpxml_element']=='HeatingSystem' for r in rows), 'Input was incorrectly mapped as output!'
    assert any(r['metric']=='heatingInputCapacity' and r['hpxml_element']=='WaterHeatingSystem' and r['hpxml_target_field']=='HeatingCapacity' for r in rows), 'Water heater special case missing'
    if (root/'registry/technical-contracts.v0.1.json').exists():
        registry=json.loads((root/'registry/technical-contracts.v0.1.json').read_text())['contracts']
        for row in rows:
            if row['scope']!='EQUIPMENT_EVIDENCE': continue
            assert row['contract'] in registry,row
            assert row['metric'] in registry[row['contract']]['fields'],row
    print(f'PASS matrix: {len(rows)} rows, {len(families)} families; no premature H2K claims')

def check_scanner():
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)
        components=root/'repos/canmet-energy/h2k-hpxml/src/h2k_hpxml/components'
        components.mkdir(parents=True)
        (components/'system_heat_pumps.py').write_text('capacity = heat_pump.get("HeatingCapacity")\n')
        fixtures=root/'fixtures/buildings';fixtures.mkdir(parents=True)
        (fixtures/'test.h2k').write_text('<House><Systems><HeatPump capacity="12" /></Systems></House>')
        out=root/'audit'
        cmd=[sys.executable,str(BUNDLE/'scripts/audit-h2k-hpxml-local.py'),'--root',str(root),'--out',str(out)]
        subprocess.run(cmd,check=True,capture_output=True,text=True)
        a=json.loads((out/'audit-summary.json').read_text())
        assert a['translator_files_found']==1
        assert a['translator_keyword_hits']>=1
        assert a['h2k_candidate_paths']>=1
        paths=(out/'h2k-xml-candidate-paths.csv').read_text()
        assert '/House/Systems/HeatPump' in paths
        assert '12' not in paths, 'No model values should be exported.'
        print('PASS scanner: extracted candidate field names without model values')

if __name__=='__main__':
    check_matrix(BUNDLE)
    check_scanner()
