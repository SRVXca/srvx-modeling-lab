require 'json'
require '/home/o/.local/share/OpenStudio-HPXML-v1.12.0/HPXMLtoOpenStudio/measure.rb'
input,output=ARGV
hpxml=HPXML.new(hpxml_path:input)
raise hpxml.errors.join('; ') unless hpxml.errors.empty?
hp=hpxml.buildings[0].heat_pumps.find { |p| p.id=='HeatPump1' }
before=hp.heating_detailed_performance_data.map do |dp|
  {'temperatureF'=>dp.outdoor_temperature,'level'=>dp.capacity_description,'fraction'=>dp.capacity_fraction_of_nominal,'cop'=>dp.efficiency_cop,'capacity'=>dp.capacity}
end
raise 'Expected nine supplied control points' unless before.size==9
raise 'Legacy fraction conflicts with supplied details' unless hp.heating_capacity_fraction_17F.nil? && hp.heating_capacity_17F.nil?
capacity=hp.heating_capacity
Defaults.expand_detailed_performance_data(:htg,hp)
Defaults.set_heat_pump_heating_capacity_17F(hp)
after=hp.heating_detailed_performance_data.map do |dp|
  {'temperatureF'=>dp.outdoor_temperature,'level'=>dp.capacity_description,'fraction'=>dp.capacity_fraction_of_nominal,'cop'=>dp.efficiency_cop,'capacity'=>dp.capacity}
end
before.zip(after).each do |a,b|
  raise 'COP was replaced' unless a['cop']==b['cop']
  raise 'Capacity-description changed' unless a['level']==b['level']
  raise 'Fraction not consumed' unless b['capacity']==(a['fraction']*capacity).round
end
raise 'Nominal model capacity replaced' unless capacity==hp.heating_capacity
report={'consumerVersion'=>Version::OS_HPXML_Version,'openstudioVersion'=>OpenStudio.openStudioVersion,
        'input'=>input,'evidenceKind'=>'SYNTHETIC_TEST_FIXTURE','parsedPoints'=>before,'expandedPoints'=>after,
        'heatingCapacityBefore'=>capacity,'heatingCapacityAfter'=>hp.heating_capacity,
        'defaultedHeatingCapacity17F'=>hp.heating_capacity_17F,
        'legacyFractionAbsent'=>hp.heating_capacity_fraction_17F.nil?,
        'copValuesPreserved'=>true,'normalizedCapacityAccepted'=>true,'capacityDescriptionPreserved'=>true,
        'matchedEquipmentValidated'=>false,'fullSimulationExecuted'=>false}
File.write(output,JSON.pretty_generate(report)+"\n")
puts "Pinned consumer parsed and expanded 9 synthetic points at 47F/17F/5F; retained #{capacity} Btu/h nominal size"
