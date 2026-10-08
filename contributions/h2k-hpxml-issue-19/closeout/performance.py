"""Lab-only performance observations and guarded HPXML projection; no catalog lookup or defaults."""
import math


class ProjectionBlocked(ValueError):
    pass


def positive(value, label):
    if isinstance(value,bool):
        raise ProjectionBlocked(f'{label}: expected a finite positive number')
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ProjectionBlocked(f'{label}: expected a finite positive number') from error
    if not math.isfinite(number) or number <= 0:
        raise ProjectionBlocked(f'{label}: expected a finite positive number')
    return number


def validate_observation(profile):
    reference = profile.get('nominalReference', {})
    if reference.get('outdoorTemperatureF') != 47 or reference.get('operatingLevel') != 'nominal':
        raise ProjectionBlocked('Nominal reference must be rated 47F, nominal operating level')
    if reference.get('unit') != 'Btu/h':
        raise ProjectionBlocked('Nominal reference unit must be Btu/h')
    qref = positive(reference.get('capacityBtuH'), 'nominal reference capacity')
    seen = set()
    for point in profile['points']:
        temperature = float(point['outdoorTemperatureF'])
        if not math.isfinite(temperature) or not (temperature in {47,17,5} or temperature < 5):
            raise ProjectionBlocked('Unsupported temperature')
        level = point['operatingLevel']
        if level not in {'minimum','nominal','maximum','unspecified'}:
            raise ProjectionBlocked('Unknown operating-level vocabulary')
        identity = (temperature, level)
        if identity in seen:
            raise ProjectionBlocked('Duplicate/conflicting performance point')
        seen.add(identity)
        capacity = positive(point['capacityBtuH'], 'point capacity')
        if identity == (47,'nominal') and abs(capacity/qref-1) > 1e-9:
            raise ProjectionBlocked('Conflicting nominal basis')
        if point.get('cop') is not None:
            positive(point['cop'],'COP')
        if point.get('inputPowerW') is not None:
            positive(point['inputPowerW'],'input power')
        if not point.get('sourceFields') or not point.get('evidenceKind'):
            raise ProjectionBlocked('Missing field-level provenance')
    return qref


def project_17f(profile, model_capacity):
    """Project only a rated 17F/47F shape, preserving the independent model size."""
    if profile is None:
        return {'status':'NO_EXTERNAL_PERFORMANCE','changedFields':[]}
    qref = validate_observation(profile)
    if model_capacity is not None:
        positive(model_capacity,'model capacity')
    point = next((p for p in profile['points'] if p['outdoorTemperatureF']==17 and p['operatingLevel']=='nominal'),None)
    if point is None:
        raise ProjectionBlocked('Missing nominal 17F point')
    ratio = point['capacityBtuH']/qref
    return {'status':'PARTIAL_17F_PROJECTION','HeatingCapacityFraction17F':ratio,
            'modelHeatingCapacityBtuH':model_capacity,'referenceCapacityBtuH':qref,
            'formula':'source nominal capacity at 17F / source nominal capacity at 47F',
            'modelSizeChanged':False,'fiveDegreeDataProjected':False,
            'basis':'47F nominal heating reference matches H2K RatingType and HPXML consumer reference',
            'physicalInstalledCombinationVerified':False}


def project_detailed(profile, compressor_type, model_capacity=None):
    """Require actual complete points; never pad missing operating levels, COPs or nominal basis."""
    qref=validate_observation(profile)
    if model_capacity is not None:positive(model_capacity,'model capacity')
    points={(float(p['outdoorTemperatureF']),p['operatingLevel']):p for p in profile['points']}
    temperatures=sorted({key[0] for key in points},reverse=True)
    if 47 not in temperatures or 17 not in temperatures:
        raise ProjectionBlocked('Detailed consumer requires 47F and 17F data')
    required_levels={'single stage':['nominal'],'two stage':['minimum','nominal'],
                     'variable speed':['minimum','maximum']}[compressor_type]
    missing=[]
    for t in temperatures:
        for level in required_levels + (['nominal'] if compressor_type=='variable speed' and t in {47,17} else []):
            if (t,level) not in points:missing.append(f'{t:g}F {level}')
    if any(p['operatingLevel']=='unspecified' for p in profile['points']):missing.append('unverified operating level')
    if any(p.get('cop') is None for p in profile['points']):missing.append('COP missing at supplied points')
    if missing:raise ProjectionBlocked('Incomplete detailed performance: '+', '.join(missing))
    output=[]
    for point in profile['points']:
        output.append({'OutdoorTemperature':point['outdoorTemperatureF'],
                       'CapacityFractionOfNominal':point['capacityBtuH']/qref,
                       'CapacityDescription':point['operatingLevel'],'Efficiency':{'Units':'COP','Value':point['cop']}})
    for t in temperatures:
        at=[p for p in output if p['OutdoorTemperature']==t]
        ordered=sorted(at,key=lambda p:['minimum','nominal','maximum'].index(p['CapacityDescription']))
        fractions=[p['CapacityFractionOfNominal'] for p in ordered]
        powers=[p['CapacityFractionOfNominal']/p['Efficiency']['Value'] for p in ordered]
        if fractions!=sorted(fractions) or powers!=sorted(powers):
            raise ProjectionBlocked('Capacity/input-power order inconsistent with operating levels')
    return {'status':'DETAILED_PROJECTION','points':output,'removeFields':['HeatingCapacity17F','extension/HeatingCapacityFraction17F','extension/HeatingCapacityRetention'],
            'referenceCapacityBtuH':qref,'modelHeatingCapacityBtuH':model_capacity,'modelSizeChanged':False,
            'evidenceKind':profile['evidenceKind'],'profileId':profile['profileId']}


def synthetic_control():
    """Consumer regression input only; no invented values are represented as source evidence."""
    reference=12000.
    definitions={47:[('minimum',.25,4.0),('nominal',1.,3.5),('maximum',1.2,3.2)],
                 17:[('minimum',.2,3.1),('nominal',11/12,2.5),('maximum',1.1,2.3)],
                 5:[('minimum',.15,2.5),('nominal',.825,2.0),('maximum',.95,1.9)]}
    return {'profileId':'SYNTHETIC_CONSUMER_CONTROL','evidenceKind':'SYNTHETIC_TEST_FIXTURE',
            'publicationAllowedAsEquipmentEvidence':False,'equipmentIdentity':{'matchStatus':'UNVERIFIED'},
            'nominalReference':{'outdoorTemperatureF':47,'operatingLevel':'nominal','capacityBtuH':reference,'unit':'Btu/h'},
            'points':[{'outdoorTemperatureF':t,'operatingLevel':level,'capacityBtuH':fraction*reference,
                       'inputPowerW':None,'cop':cop,'sourceFields':['synthetic_control definition'],
                       'evidenceKind':'SYNTHETIC_TEST_FIXTURE','ratingBasis':'NONE; generated regression input'}
                      for t,values in definitions.items() for level,fraction,cop in values]}
