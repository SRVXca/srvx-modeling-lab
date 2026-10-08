#!/usr/bin/env python3
"""Pinned HPXML XSD/Schematron comparison with baseline, including an expected rejection."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from lxml import etree,isoschematron

LAB=Path(__file__).resolve().parents[3];BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'
RESOURCES=Path('/home/o/.local/share/OpenStudio-HPXML-v1.12.0/HPXMLtoOpenStudio/resources')
xsd=RESOURCES/'hpxml_schema/HPXML.xsd';rules=RESOURCES/'hpxml_schematron/EPvalidator.sch'
schema=etree.XMLSchema(etree.parse(str(xsd)))
validator=isoschematron.Schematron(etree.parse(str(rules)),store_report=True)
svrl={'s':'http://purl.oclc.org/dsdl/svrl'}
models=['MURB-baseline','MURB-samsung-17f','MURB-synthetic-detailed-control','MURB-incomplete-detail-NEGATIVE-TEST']
report={}
for name in models:
    doc=etree.parse(str(BUNDLE/'model'/f'{name}.xml'))
    passed=schema.validate(doc);xsderrors=[e.message for e in schema.error_log]
    validator.validate(doc)
    errors=[{'test':e.get('test'),'location':e.get('location'),'message':e.xpath('string(s:text)',namespaces=svrl)}
            for e in validator.validation_report.xpath('//s:failed-assert',namespaces=svrl)]
    report[name]={'xsdPass':passed,'xsdErrors':xsderrors,'schematronPass':not errors,'schematronErrors':errors}
    validator.validation_report.write(str(BUNDLE/'validation'/f'{name}.svrl.xml'),encoding='utf-8',pretty_print=True)
baseline=Counter(json.dumps(e,sort_keys=True) for e in report['MURB-baseline']['schematronErrors'])
for name,r in report.items():
    r['newSchematronFailures']=sum((Counter(json.dumps(e,sort_keys=True) for e in r['schematronErrors'])-baseline).values())
for name in models[:3]:assert report[name]['xsdPass'] and report[name]['newSchematronFailures']==0
assert report[models[-1]]['newSchematronFailures']>0,'Incomplete details unexpectedly accepted'
output={'pinnedConsumerVersion':'1.12.0','pinnedHpXmlVersion':'5.0','namespace':'http://hpxmlonline.com/2025/12',
    'schemaPath':str(xsd),'schemaSha256':hashlib.sha256(xsd.read_bytes()).hexdigest(),
    'rulesPath':str(rules),'rulesSha256':hashlib.sha256(rules.read_bytes()).hexdigest(),'results':report,
    'matched47_17_5EquipmentProjectionValidated':False,'syntheticCompleteConsumerControlValidated':True}
(BUNDLE/'validation/schema-consumer-rules.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({n:{k:r[k] for k in ['xsdPass','schematronPass','newSchematronFailures']} for n,r in report.items()},indent=2))
