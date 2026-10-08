#!/usr/bin/env python3
"""Freeze one public source-shaped ENERGY STAR record and observations; preserve missing data."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sys
import jsonschema

LAB=Path(__file__).resolve().parents[3]
BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'
SNAPSHOT=Path('/home/o/nova-open/data/supply/air-source-heat-pump-v0.1')
from performance import positive, project_detailed, ProjectionBlocked


def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def main():
    source=json.loads((SNAPSHOT/'source.json').read_text())
    with gzip.open(SNAPSHOT/'metadata.json.gz','rt') as handle:metadata=json.load(handle)
    headers={c['fieldName']:c['name'] for c in metadata['columns']}
    with gzip.open(SNAPSHOT/'energy-star.csv.gz','rt') as handle:
        records=[r for r in csv.DictReader(handle) if r[headers['ahri_reference_number']]=='210448841']
    if len(records)!=1:raise ValueError('Expected one unambiguous exact AHRI record')
    record=records[0]
    frozen={'source':'EPA_ENERGY_STAR','datasetId':'83eb-xbyy','snapshotId':'2026-10-07',
            'sourceRecordId':record[headers['pd_id']],'sourceManifest':source,
            'sourceVocabulary':'Native CSV headers and scalar strings; no normalized fields injected',
            'snapshotCompressedSha256':hashlib.sha256((SNAPSHOT/'energy-star.csv.gz').read_bytes()).hexdigest(),
            'record':record}
    write(BUNDLE/'source-record/energy-star-2469692.json',frozen)
    points=[];observations=[]
    for temperature,field in [(47,'heating_capacity_at_47_f_btu_h'),(17,'heating_capacity_at_17_f_btu_h'),(5,'heating_capacity_at_5_f_btu_h')]:
        capacity=positive(record[headers[field]],field)
        # Rated 47F/17F reference follows AHRI H1Full/H3Full nomenclature; 5F level is not stated in this snapshot's data dictionary.
        level='nominal' if temperature in {47,17} else 'unspecified'
        cop=positive(record[headers['cop_at_5_f']],'COP at 5F') if temperature==5 else None
        fields=[field]+(['cop_at_5_f'] if temperature==5 else [])
        points.append({'outdoorTemperatureF':temperature,'operatingLevel':level,'capacityBtuH':capacity,
                       'inputPowerW':None,'cop':cop,'sourceFields':fields,'evidenceKind':'CERTIFICATION_REPORTED',
                       'ratingBasis':'ENERGY STAR/AHRI rated certificate fields; 5F compressor speed unspecified in saved dictionary'})
        for metric,value,unit,key in [('heating_capacity',capacity,'Btu/h',field)]+([('coefficient_of_performance',cop,'W/W','cop_at_5_f')] if cop else []):
            observations.append({'observationId':f'ENERGY_STAR:2469692:{key}','family':'air_source_heat_pump','contract':'HeatPumpPerformance',
                'equipmentIdentity':{'ahriReference':'210448841','outdoorModel':'AR12CSFCMWKX','indoorModel':'AR12CSFCMWKN','matchStatus':'SOURCE_ASSERTED'},
                'metric':metric,'value':value,'unit':unit,'conditions':{'outdoorTemperatureF':temperature,'operatingLevel':level},
                'ratingBasis':{'description':points[-1]['ratingBasis'],'nominalReferenceF':47},'evidenceKind':'CERTIFICATION_REPORTED',
                'source':{'datasetId':'83eb-xbyy','snapshotId':'2026-10-07','sourceRecordId':'2469692','sourceField':key,'retrievedAt':'2026-10-07'},
                'warnings':['Not an installed-system survey; H2K user capacity differs; missing COP/min/max are not filled']})
    schema=json.loads((LAB/'contracts/equipment-observation.v0.1.schema.json').read_text())
    for observation in observations:jsonschema.Draft202012Validator(schema).validate(observation)
    profile={'profileId':'ENERGY_STAR_AHRI_210448841','evidenceKind':'CERTIFICATION_REPORTED',
        'equipmentIdentity':observations[0]['equipmentIdentity'],'certificationBasis':'ENERGY STAR saved certificate field reporting',
        'sourceRecordPath':'source-record/energy-star-2469692.json',
        'nominalReference':{'outdoorTemperatureF':47,'operatingLevel':'nominal','capacityBtuH':12000.,'unit':'Btu/h'},
        'points':points,'observations':observations,'missing':['COP at 47F','COP at 17F','minimum/maximum curves','verified operating level at 5F','input power'],
        'sourceRecordIsNotObservation':True}
    write(BUNDLE/'observation/samsung-performance.json',profile)
    try:project_detailed(profile,'variable speed',47883.93)
    except ProjectionBlocked as error:
        write(BUNDLE/'projection/samsung-detailed-BLOCKED.json',{'status':'BLOCKED_SOURCE_INCOMPLETE','reason':str(error),
            'modelCapacityPreservedBtuH':47883.93,'shapeFractionsAvailable':{'47F':1.0,'17F':11/12,'5F_unspecified_speed':.825},
            'basisCompatible':True,'sourceValuesInvented':False,'upstreamPatchAllowed':False})
    print('Frozen real source record, four schema-validated observations; full detailed equipment projection blocked by missing source points')


if __name__=='__main__':main()
