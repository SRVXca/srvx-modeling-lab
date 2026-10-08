#!/usr/bin/env python3
"""Separate published constants, current-data aggregate reconstruction and equipment observations."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from statistics import mean
import sys

LAB=Path(__file__).resolve().parents[3];BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'
RESEARCH=LAB/'contributions/h2k-hpxml-issue-19/analysis/addendum82-populations'
NEEP=LAB/'contributions/h2k-hpxml-issue-19/source-study/neep'
sys.path.insert(0,str(RESEARCH));sys.path.insert(0,str(NEEP))
from run import A82,metrics,number,identity_key
from neep_hp_xlsx_adapter import iter_neep_hp_source_rows
from neep_hp_source_record import NEEP_HP_SOURCE_HEADERS


def write(name,value):
    (BUNDLE/'comparison'/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def evaluate(rows):
    values=[metrics(row) for row in rows]
    coefficients={key:mean(v[key] for v in values) for key in A82}
    errors={key:abs(coefficients[key]/A82[key]-1) for key in A82}
    return {'N':len(rows),'coefficients':coefficients,'meanRelativeError':mean(errors.values()),'maxMetricError':max(errors.values())}


def scale_capacity(coefficients,retention_17):
    # Qr means relative to same-temperature maximum, not relative to nominal 47F.
    max47=1/coefficients['Qr47full'];min47=coefficients['Qr47min']*max47
    max17=retention_17/coefficients['Qr17full'];min17=coefficients['Qr17min']*max17
    max5=coefficients['Qm5max']*max17
    return {'47F':{'minimum':min47,'nominal':1.,'maximum':max47},
            '17F':{'minimum':min17,'nominal':retention_17,'maximum':max17},
            '5F':{'minimum':coefficients['Qr5min']*max5,'nominal':coefficients['Qr5full']*max5,'maximum':max5}}


def main():
    published={'referenceId':'RESNET_ADDENDUM_82_PUBLISHED','evidenceKind':'EXTERNAL_PUBLISHED_REFERENCE',
        'sourceUrl':'https://www.resnet.us/wp-content/uploads/Addendum-82-HPAC-Modeling.pdf',
        'approvalDate':'2025-12-17','section':'C.6.7 variable capacity mean coefficients, pages 6–7',
        'coefficients':dict(A82),'normalization':'Qr = relative to maximum at same temperature; Qm = maintenance relative to next less extreme temperature',
        'immutableReference':True,'scopeCaveat':'Published scope excludes multi-splits; applicability to the two-head MURB input is not established'}
    write('resnet-addendum-82-published.json',published)
    selected=[];outdoor_seen=set();outdoor=[];baseline_counts=Counter();cap17=[];cap5=[];source_count=0;ahri_matches=0
    for row in iter_neep_hp_source_rows():
        source_count+=1;raw={header:row.record[key] for key,header in NEEP_HP_SOURCE_HEADERS.items()}
        if str(raw.get('AHRI Certified Reference Number⁺'))=='210448841':ahri_matches+=1
        if raw['Status']!='Live' or raw['Variable Capacity?'] is not True:continue
        baseline_counts['Live variable-capacity']+=1
        q47=number(raw['Rated Capacity 47°F⁺']);q17=number(raw['Rated Capacity 17°F⁺']);q5=number(raw['Rated Capacity 5°F - Optional⁺'])
        if q47 and q17:cap17.append(q17/q47)
        if q47 and q5:cap5.append(q5/q47)
        if raw['Ducting Configuration']!='Singlezone Non-Ducted, Ceiling Placement' or raw['ENERGY STAR Cold Climate Certified'] is not False:continue
        if q47 is None or q47<18000 or not all(v is not None for v in metrics(raw).values()):continue
        selected.append(raw)
        key=identity_key(raw,'outdoor',row.source_row)
        if key not in outdoor_seen:outdoor.append(raw);outdoor_seen.add(key)
    fields=sorted({f for r in outdoor for f in r})
    raw_fields=[field for field in fields if any(x in field.casefold() for x in ['capacity','power','cop','seer2','hspf2','eer2'])
                and not any(x in field.casefold() for x in ['model','brand','manufacturer','ahri','series','date'])
                and sum(number(r.get(field)) is not None for r in outdoor)>=30]
    clones={}
    for row in outdoor:
        fingerprint=tuple(number(row.get(field)) for field in raw_fields)
        clones.setdefault(fingerprint,row)
    reference={'referenceId':'SRVX_A82_RESEARCH_2026_10_08','evidenceKind':'CALCULATED','status':'EXPERIMENTAL_CURRENT_DATA_RECONSTRUCTION_NOT_OFFICIAL_ADDENDUM_82',
        'sourcePath':str(NEEP/'neep_air_source_heat_pump_2026-10-07.xlsx'),
        'snapshotSha256':hashlib.sha256((NEEP/'neep_air_source_heat_pump_2026-10-07.xlsx').read_bytes()).hexdigest(),
        'sourceRows':source_count,'rawSelectedRows':len(selected),'fingerprintFieldCount':len(raw_fields),
        'population':'Live; variable capacity; Singlezone Non-Ducted, Ceiling Placement; non-cold-climate; rated Q47>=18000; all 15 metrics complete',
        'outdoorWeighted':evaluate(outdoor),'exactPerformanceCloneCollapse':evaluate(list(clones.values())),
        'historicalPopulationRecovered':False,'upstreamDefault':False,'publicationRights':'No raw NEEP records copied; source notice does not establish permission to publish data extracts'}
    write('srvx-current-data-reconstruction.json',reference)
    neep_reference={'source':'NEEP ccASHP Product List','snapshotId':'2026-10-07',
        'sourceRecordShape':'87 fields, source-native vocabulary retained by existing adapter',
        'localSnapshotPath':reference['sourcePath'],'snapshotSha256':reference['snapshotSha256'],
        'schemaPath':str(NEEP/'hp-source-schema.json'),'schemaSha256':hashlib.sha256((NEEP/'hp-source-schema.json').read_bytes()).hexdigest(),
        'sourceStudyPath':str(NEEP/'SOURCE-STUDY.md'),'sourceAdapterPath':str(NEEP/'neep_hp_xlsx_adapter.py'),
        'usageNotice':'Downloaded export says not for commercial use; no assumption of permission to redistribute raw data or publish extracts',
        'payloadIncluded':False,'sourceRecordNormalizedIntoCanonicalTruth':False,'matchedSamsungAhriCount':ahri_matches}
    (BUNDLE/'source-record/neep-local-snapshot-reference.json').write_text(json.dumps(neep_reference,indent=2)+'\n')
    write('neep-population-summary.json',{'evidenceKind':'CALCULATED_POPULATION_AGGREGATE','sourceRows':source_count,
        'liveVariableCapacityCount':baseline_counts['Live variable-capacity'],'matchedSamsungAhriCount':ahri_matches,
        'rawRowWeightedRated17Over47':{'N':len(cap17),'mean':mean(cap17)},'rawRowWeightedRated5Over47':{'N':len(cap5),'mean':mean(cap5)},
        'warning':'Row-weighted population statistics are neither matched-equipment evidence nor fallback recommendations; optional rated 5F completeness changes population'})
    nominal17=11/12
    write('capacity-profile-comparison.json',{'unit':'fraction of source/model nominal 47F capacity',
        'anchor17Over47':nominal17,'anchorStatus':'Explicit common illustrative comparison anchor; not recovered official population or universal retention',
        'publishedDerived':scale_capacity(A82,nominal17),'reconstructionDerived':scale_capacity(reference['outdoorWeighted']['coefficients'],nominal17),
        'matchedEquipment':{'47F':{'nominal':1.},'17F':{'nominal':nominal17},'5F':{'unspecified_operating_level':.825,'COP':2.}},
        'legacyH2K':{'47F_direct_multiplier':1.004770666,'17F_direct_multiplier':.563635566,'5F_direct_multiplier':.440489640,
                     '17Over47_normalized':.560959416,'5Over47_normalized':.438398189},
        'openstudioFallback17Over47':{'singleStage':.626,'twoStage':.626,'variableSpeed':.69},
        'COPComparison':'Actual Samsung COP only at 5F; published/reconstructed EIR coefficients have different denominators and are not absolute COP. Executed model-default profiles are retained separately.',
        'notUsedAsUpstreamDefaults':True})
    print(json.dumps({'sourceRows':source_count,'outdoor':reference['outdoorWeighted'],'clones':reference['exactPerformanceCloneCollapse']},indent=2))


if __name__=='__main__':main()
