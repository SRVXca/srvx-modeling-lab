#!/usr/bin/env python3
"""Real limited candidate and distinct synthetic consumer control, with exact field diffs."""
from copy import deepcopy
import json
from pathlib import Path
from lxml import etree
from performance import project_17f, project_detailed, synthetic_control

LAB=Path(__file__).resolve().parents[3]
BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'


def read(path):return json.loads(path.read_text())
def write(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def clean_parse(path):return etree.parse(str(path),etree.XMLParser(remove_blank_text=True))
def same(a,b):return etree.tostring(a,method='c14n')==etree.tostring(b,method='c14n')


def mutate_detailed(tree,points):
    model=deepcopy(tree);root=model.getroot();ns=etree.QName(root).namespace
    hp=model.xpath('//*[local-name()="HeatPump"]')[0]
    for field in ['HeatingCapacity17F','HeatingDetailedPerformanceData']:
        for element in hp.findall('{*}'+field):hp.remove(element)
    extension=hp.find('{*}extension')
    if extension is not None:
        for name in ['HeatingCapacityFraction17F','HeatingCapacityRetention']:
            for element in extension.findall('{*}'+name):extension.remove(element)
        if len(extension)==0:hp.remove(extension);extension=None
    detail=etree.Element('{'+ns+'}HeatingDetailedPerformanceData')
    for point in points:
        element=etree.SubElement(detail,'{'+ns+'}PerformanceDataPoint')
        for name in ['OutdoorTemperature','CapacityFractionOfNominal','CapacityDescription']:
            etree.SubElement(element,'{'+ns+'}'+name).text=str(point[name])
        if point.get('Efficiency'):
            efficiency=etree.SubElement(element,'{'+ns+'}Efficiency')
            for name in ['Units','Value']:etree.SubElement(efficiency,'{'+ns+'}'+name).text=str(point['Efficiency'][name])
    hp.insert(hp.index(extension) if extension is not None else len(hp),detail)
    return model


def main():
    baseline=clean_parse(BUNDLE/'model/MURB-baseline.xml')
    hp=baseline.xpath('//*[local-name()="HeatPump"]')[0]
    capacity=float(hp.findtext('{*}HeatingCapacity'))
    profile=read(BUNDLE/'observation/samsung-performance.json')
    scalar=project_17f(profile,capacity)
    write(BUNDLE/'projection/samsung-17f.json',scalar)
    candidate=deepcopy(baseline)
    fraction=candidate.xpath('//*[local-name()="HeatPump"]/*[local-name()="extension"]/*[local-name()="HeatingCapacityFraction17F"]/*[local-name()="Fraction"]')[0]
    old=float(fraction.text);fraction.text=str(scalar['HeatingCapacityFraction17F'])
    candidate.write(str(BUNDLE/'model/MURB-samsung-17f.xml'),encoding='utf-8',xml_declaration=True,pretty_print=True)
    fallback=deepcopy(baseline)
    fallback_hp=fallback.xpath('//*[local-name()="HeatPump"]')[0]
    extension=fallback_hp.find('{*}extension')
    extension.remove(extension.find('{*}HeatingCapacityFraction17F'))
    if len(extension)==0:fallback_hp.remove(extension)
    fallback.write(str(BUNDLE/'model/MURB-current-downstream-defaults-COMPARISON.xml'),encoding='utf-8',xml_declaration=True,pretty_print=True)
    expected=deepcopy(baseline)
    expected.xpath('//*[local-name()="HeatingCapacityFraction17F"]/*[local-name()="Fraction"]')[0].text=fraction.text
    assert same(expected,candidate)
    write(BUNDLE/'validation/exact-diff-samsung-17f.json',{'passed':True,'allowedChangesOnly':True,
        'changes':[{'path':'HeatPump[SystemIdentifier/@id=HeatPump1]/extension/HeatingCapacityFraction17F/Fraction','before':old,'after':scalar['HeatingCapacityFraction17F']}],
        'HeatingCapacityBefore':capacity,'HeatingCapacityAfter':float(candidate.xpath('//*[local-name()="HeatPump"]/*[local-name()="HeatingCapacity"]')[0].text),
        'fiveDegreePerformanceInstalled':False,'physicalInstalledSystemVerified':False})
    control=synthetic_control();write(BUNDLE/'projection/synthetic-consumer-control.json',control)
    projection=project_detailed(control,'variable speed',capacity)
    write(BUNDLE/'projection/synthetic-detailed-projection.json',projection)
    detailed=mutate_detailed(baseline,projection['points'])
    detailed.write(str(BUNDLE/'model/MURB-synthetic-detailed-control.xml'),encoding='utf-8',xml_declaration=True,pretty_print=True)
    actual=clean_parse(BUNDLE/'model/MURB-synthetic-detailed-control.xml')
    assert same(mutate_detailed(baseline,projection['points']),actual)
    write(BUNDLE/'validation/exact-diff-synthetic-control.json',{'passed':True,'allowedChangesOnly':True,
        'removed':['HeatPump1/extension/HeatingCapacityFraction17F','empty HeatPump1/extension'],
        'added':['HeatPump1/HeatingDetailedPerformanceData (nine SYNTHETIC_TEST_FIXTURE points)'],
        'originalHeatingCapacityPreserved':True,'proof':'Independent allowed-subtree reconstruction plus canonical XML equality',
        'equipmentEvidence':False})
    # Negative consumer evidence: show why three capacity fields alone cannot validate variable-speed details.
    insufficient=[]
    for point in profile['points']:
        out={'OutdoorTemperature':point['outdoorTemperatureF'],'CapacityFractionOfNominal':point['capacityBtuH']/12000,
             'CapacityDescription':'nominal'}
        if point['cop'] is not None:out['Efficiency']={'Units':'COP','Value':point['cop']}
        insufficient.append(out)
    negative=mutate_detailed(baseline,insufficient)
    negative.write(str(BUNDLE/'model/MURB-incomplete-detail-NEGATIVE-TEST.xml'),encoding='utf-8',xml_declaration=True,pretty_print=True)
    write(BUNDLE/'projection/incomplete-detail-negative-test.json',{'status':'DELIBERATELY_INVALID_CONSUMER_TEST',
        'equipmentProjection':False,'unsupportedAssumption':'5F speed forced nominal ONLY to exercise consumer rejection; not accepted source interpretation',
        'expectedFailures':['missing minimum/maximum points','missing COP at 47F and 17F'], 'points':insufficient})
    print('Built real 17F-only scenario, separate synthetic nine-point consumer control, and deliberately invalid negative test')


if __name__=='__main__':main()
