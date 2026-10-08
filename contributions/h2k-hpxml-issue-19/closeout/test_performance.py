#!/usr/bin/env python3
"""Meaningful projection and real-model regression checks; no upstream checkout mutation."""
from copy import deepcopy
import io
import json
from pathlib import Path
import unittest
from lxml import etree
from performance import ProjectionBlocked, project_17f, project_detailed, synthetic_control, validate_observation
from build_models import same, clean_parse, mutate_detailed

LAB=Path(__file__).resolve().parents[3];BUNDLE=LAB/'evidence-core/heat-pump/issue-19-v0.1'


class PerformanceTests(unittest.TestCase):
    def setUp(self):
        self.actual=json.loads((BUNDLE/'observation/samsung-performance.json').read_text())
        self.control=synthetic_control()

    def test_no_external_performance_retains_fallback(self):
        result=project_17f(None,47883.93)
        self.assertEqual(result,{'status':'NO_EXTERNAL_PERFORMANCE','changedFields':[]})

    def test_17_only_without_47_reference_blocked(self):
        p=deepcopy(self.actual);p['points']=p['points'][1:2];p['nominalReference']={}
        with self.assertRaisesRegex(ProjectionBlocked,'Nominal reference'):project_17f(p,47883.93)

    def test_47_17_ratio_preserves_explicit_h2k_size(self):
        p=deepcopy(self.actual);p['points']=p['points'][:2]
        result=project_17f(p,47883.93)
        self.assertAlmostEqual(result['HeatingCapacityFraction17F'],11/12)
        self.assertEqual(result['modelHeatingCapacityBtuH'],47883.93)
        self.assertFalse(result['modelSizeChanged'])

    def test_47_17_5_equipment_fields_do_not_fake_complete_map(self):
        self.assertEqual([p['capacityBtuH'] for p in self.actual['points']],[12000,11000,9900])
        self.assertEqual([p['cop'] for p in self.actual['points']],[None,None,2])
        with self.assertRaisesRegex(ProjectionBlocked,'Incomplete detailed'):project_detailed(self.actual,'variable speed',47883.93)

    def test_min_nom_max_at_each_temperature_and_cop(self):
        result=project_detailed(self.control,'variable speed',47883.93)
        self.assertEqual(len(result['points']),9)
        self.assertEqual({p['OutdoorTemperature'] for p in result['points']},{47,17,5})
        self.assertEqual({p['CapacityDescription'] for p in result['points']},{'minimum','nominal','maximum'})
        self.assertTrue(all(p['Efficiency']['Units']=='COP' for p in result['points']))
        self.assertTrue(any(p['CapacityFractionOfNominal']>1 for p in result['points']))

    def test_autosized_model_uses_fraction_without_replacing_size(self):
        result=project_detailed(self.control,'variable speed',None)
        self.assertIsNone(result['modelHeatingCapacityBtuH'])
        self.assertTrue(all('Capacity' not in p for p in result['points']))

    def test_explicit_h2k_capacity_not_certificate_capacity(self):
        result=project_detailed(self.control,'variable speed',47883.93)
        self.assertEqual(result['referenceCapacityBtuH'],12000)
        self.assertEqual(result['modelHeatingCapacityBtuH'],47883.93)

    def test_invalid_negative_nonfinite_capacity_and_cop(self):
        for value in [0,-1,float('nan'),float('inf'),'not-a-number',True]:
            p=deepcopy(self.control);p['points'][0]['capacityBtuH']=value
            with self.subTest(value=value),self.assertRaises(ProjectionBlocked):validate_observation(p)
            p=deepcopy(self.control);p['points'][0]['cop']=value
            with self.subTest(cop=value),self.assertRaises(ProjectionBlocked):validate_observation(p)

    def test_conflicting_nominal_basis(self):
        p=deepcopy(self.control);next(x for x in p['points'] if x['outdoorTemperatureF']==47 and x['operatingLevel']=='nominal')['capacityBtuH']=6000
        with self.assertRaisesRegex(ProjectionBlocked,'Conflicting nominal'):project_detailed(p,'variable speed')

    def test_duplicates_and_unverified_levels(self):
        p=deepcopy(self.control);p['points'].append(deepcopy(p['points'][0]))
        with self.assertRaisesRegex(ProjectionBlocked,'Duplicate'):validate_observation(p)
        p=deepcopy(self.control);p['points'][0]['operatingLevel']='unspecified'
        with self.assertRaisesRegex(ProjectionBlocked,'unverified operating'):project_detailed(p,'variable speed')

    def test_missing_cop_blocks(self):
        p=deepcopy(self.control);p['points'][0]['cop']=None
        with self.assertRaisesRegex(ProjectionBlocked,'COP missing'):project_detailed(p,'variable speed')

    def test_inconsistent_power_order_blocks(self):
        p=deepcopy(self.control);p['points'][0]['cop']=.01
        with self.assertRaisesRegex(ProjectionBlocked,'input-power order'):project_detailed(p,'variable speed')

    def test_unsupported_temperature_and_units(self):
        p=deepcopy(self.control);p['points'][0]['outdoorTemperatureF']=30
        with self.assertRaisesRegex(ProjectionBlocked,'Unsupported temperature'):validate_observation(p)
        p=deepcopy(self.control);p['nominalReference']['unit']='kW'
        with self.assertRaisesRegex(ProjectionBlocked,'unit'):validate_observation(p)

    def test_single_and_two_stage_completeness(self):
        p=deepcopy(self.control);p['points']=[x for x in p['points'] if x['operatingLevel']=='nominal']
        self.assertEqual(len(project_detailed(p,'single stage')['points']),3)
        with self.assertRaisesRegex(ProjectionBlocked,'minimum'):project_detailed(p,'two stage')

    def test_fresh_real_baseline_and_size_basis(self):
        audit=json.loads((BUNDLE/'audit/fresh-MURB-translation.json').read_text())
        self.assertTrue(audit['converterRerun'])
        self.assertAlmostEqual(audit['h2kRatingTemperatureC'],8.3333)
        self.assertEqual(audit['hpxmlHeatingCapacityBtuH'],47883.93)
        self.assertEqual(audit['h2kDeclaredNumberOfHeads'],'2')

    def test_real_scalar_exact_diff(self):
        baseline=clean_parse(BUNDLE/'model/MURB-baseline.xml');actual=clean_parse(BUNDLE/'model/MURB-samsung-17f.xml')
        baseline.xpath('//*[local-name()="HeatingCapacityFraction17F"]/*[local-name()="Fraction"]')[0].text=str(11/12)
        self.assertTrue(same(baseline,actual))
        actual.xpath('//*[local-name()="HeatPump"]/*[local-name()="CoolingCapacity"]')[0].text='12000'
        self.assertFalse(same(baseline,actual),'Unrelated capacity drift must fail exact diff')

    def test_complete_control_exact_diff(self):
        baseline=clean_parse(BUNDLE/'model/MURB-baseline.xml');actual=clean_parse(BUNDLE/'model/MURB-synthetic-detailed-control.xml')
        projection=project_detailed(self.control,'variable speed',47883.93)
        self.assertTrue(same(mutate_detailed(baseline,projection['points']),actual))

    def test_xsd_and_schematron_baseline_candidates_negative(self):
        r=json.loads((BUNDLE/'validation/schema-consumer-rules.json').read_text())['results']
        for name in ['MURB-baseline','MURB-samsung-17f','MURB-synthetic-detailed-control']:
            self.assertTrue(r[name]['xsdPass']);self.assertEqual(r[name]['newSchematronFailures'],0)
        self.assertGreater(r['MURB-incomplete-detail-NEGATIVE-TEST']['newSchematronFailures'],0)

    def test_actual_consumer_acceptance_is_distinct_from_equipment_validity(self):
        r=json.loads((BUNDLE/'validation/detailed-consumer-control.json').read_text())
        self.assertTrue(r['normalizedCapacityAccepted'] and r['copValuesPreserved'] and r['legacyFractionAbsent'])
        self.assertEqual(r['heatingCapacityBefore'],r['heatingCapacityAfter'])
        self.assertEqual(len(r['parsedPoints']),9)
        self.assertFalse(r['matchedEquipmentValidated'])


if __name__=='__main__':
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PerformanceTests))
    print(stream.getvalue(),end='')
    (BUNDLE/'validation/unit-tests.txt').write_text(stream.getvalue())
    (BUNDLE/'validation/unit-tests.json').write_text(json.dumps({'passed':result.wasSuccessful(),'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
