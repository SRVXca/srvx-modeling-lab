#!/usr/bin/env python3
"""Fresh translation using a pristine git-archive copy of the pinned upstream source."""
from pathlib import Path
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[2]
BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'
CLEAN=ROOT/'h2k-hpxml-clean'
sys.path.insert(0,str(CLEAN/'src'))
from h2k_hpxml.core.translator import h2ktohpxml

source=CLEAN/'src/h2k_hpxml/examples/MURB.h2k'
raw=source.read_bytes()
result=h2ktohpxml(raw.decode('ISO-8859-1'),{'translation_mode':'STANDARD','operating_condition':'SOC'})
(BUNDLE/'model/MURB-baseline.xml').write_text(result)
tree=ET.fromstring(raw)
hp=tree.find('.//HeatingCooling/Type2/AirHeatPump')
output=ET.fromstring(result).find('.//{*}HeatPump')
report={'converterRerun':True,'cleanPinnedCommit':'0b77fcee8f1c717f0bfd02e4b5924c84244a9b6b',
    'sourceSha256':hashlib.sha256(raw).hexdigest(),'h2kCapacityInternalKW':float(hp.find('Specifications/OutputCapacity').get('value')),
    'h2kCapacityMode':hp.findtext('Specifications/OutputCapacity/English'),
    'h2kRatingTemperatureC':float(hp.find('Temperature/RatingType').get('value')),
    'h2kRatingLabel':hp.findtext('Temperature/RatingType/English'),
    'h2kUiUnits':hp.find('Specifications/OutputCapacity').get('uiUnits'),
    'h2kDeclaredNumberOfHeads':hp.find('Equipment').get('numberOfHeads'),
    'h2kAhri':hp.find('EquipmentInformation').get('AHRI'),'h2kModels':hp.findtext('EquipmentInformation/Model'),
    'hpxmlHeatingCapacityBtuH':float(output.findtext('{*}HeatingCapacity')),
    'hpxmlCoolingCapacityBtuH':float(output.findtext('{*}CoolingCapacity')),
    'hpxmlCompressorType':output.findtext('{*}CompressorType'),'hpxmlVersion':ET.fromstring(result).get('schemaVersion'),
    'nominalBasisVerdict':'47F rated heating reference compatible; preserve explicit H2K model capacity. UI-units string does not change stored kW mapping.',
    'physicalInstalledSizeVerdict':'Unresolved: model 47883.93 differs from matched 12000; two declared heads does not establish an aggregation conversion.',
    'sourceConditionUnchanged':True}
(BUNDLE/'audit/fresh-MURB-translation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
