#!/usr/bin/env python3
"""Retain executed consumer results; model-default points are not source observations."""
import hashlib
import json
from pathlib import Path
from lxml import etree

ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[2];BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'
folders={'legacy-H2K':'consumer-baseline','current-OpenStudio-fallback':'consumer-current-defaults',
         'matched-equipment-17F-shape-plus-defaults':'consumer-samsung-17f','synthetic-detailed-control':'consumer-synthetic-detailed'}
profiles={}
for name,folder in folders.items():
    path=ROOT/'work'/folder/'run/in.xml'
    doc=etree.parse(str(path));hp=doc.xpath('//*[local-name()="HeatPump"]')[0]
    capacity=float(hp.findtext('{*}HeatingCapacity'))
    points=[]
    for p in hp.findall('{*}HeatingDetailedPerformanceData/{*}PerformanceDataPoint'):
        temperature=float(p.findtext('{*}OutdoorTemperature'))
        if temperature not in {47,17,5}:continue
        q=float(p.findtext('{*}Capacity'));cop=float(p.findtext('{*}Efficiency/{*}Value'))
        points.append({'temperatureF':temperature,'level':p.findtext('{*}CapacityDescription'),'capacityBtuH':q,
                       'fractionOfModelNominal':q/capacity,'cop':cop,'dataSource':p.get('dataSource'),
                       'evidenceKind':'SYNTHETIC_TEST_FIXTURE' if name=='synthetic-detailed-control' else 'MODELING_DEFAULT_OR_CALCULATED_CONSUMER_OUTPUT'})
    profiles[name]={'consumerInXmlSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'modelNominalBtuH':capacity,
                    'points':points,'equipmentAccuracyValidated':False,'consumerMeasureExecuted':True}
output={'consumerVersion':'1.12.0','openstudioVersion':'3.11.0','profiles':profiles,
        'runMethod':'Actual installed run_simulation.rb --skip-simulation; schema and Schematron enabled',
        'full47_17_5MatchedSamsungProjectionValidated':False,'syntheticDetailedMapAccepted':True}
(BUNDLE/'validation/executed-consumer-workflows.json').write_text(json.dumps(output,indent=2)+'\n')
simulation=ROOT/'work/simulation-samsung-17f/run'
end=simulation/'eplusout.end'
if not end.exists():end=simulation/'eplusout.end'
epw=Path('/home/o/.local/share/OpenStudio-HPXML-v1.12.0/weather/CAN_NB_Moncton.Intl.AP.717050_CWEC2020.epw')
report={'fullSimulationExecuted':end.exists(),'profile':'17F-only shape-transfer scenario, 5F performance remains consumer default',
        'outputDir':str(simulation),'endFile':end.read_text().strip() if end.exists() else None,
        'weatherFile':str(epw),'weatherSha256':hashlib.sha256(epw.read_bytes()).hexdigest(),'newDownloads':False,
        'equipmentInstalledPerformanceValidated':False,'matchedDetailed5FValidated':False,
        'interpretation':'Execution smoke test only; no energy-saving or physical-performance conclusion'}
(BUNDLE/'validation/simulation-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
print('Consumer profile summaries collected; simulation end:',report['endFile'])
