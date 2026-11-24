#!/usr/bin/env python3
"""Explain unresolved supplier nodes without treating missing evidence as absence.

This is a research queue, not a replacement BOM or a supplier qualification model.
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / 'data/clean'

GROUPS = [
 ('1 1.2 1.4 6 8 8.2', 'assembly_or_function_not_single_material',
  'The node groups several child parts or a function. A board assembler, chip packager and component manufacturer are not interchangeable supplier roles.',
  'Specify purchased assembly versus in-house assembly, then research that role; keep child suppliers separate.'),
 ('4', 'integrated_feature_not_separate_connector',
  'PCIe edge contacts are a feature of the card PCB. A motherboard PCIe socket vendor would be the wrong match.',
  'Link the PCB maker and contact-finishing process after confirming the intended node semantics.'),
 ('1.5 3 7', 'custom_mechanical_part_research_open',
  'A material mill or cooler vendor does not establish manufacture of this custom bracket, backplate or shroud.',
  'Find stamped/machined/moulded-part manufacturing capability and a production address; exact GPU contract may remain undisclosed.'),
 ('5', 'connector_assembly_definition_needed',
  'Auxiliary power connector can mean the board receptacle, cable or complete assembly. These have different suppliers.',
  'Choose the interface and purchased unit; use its manufacturer drawing rather than infer from a child contact.'),
 ('LD:interconnect_materials LD:basic_acidic_chemical_inputs LD:dopants', 'broad_material_family',
  'The label spans multiple materials, grades or alternative chemistries. One supplier cannot be inherited across all branches.',
  'Use the existing child definitions where possible and seek evidence for each missing grade or species.'),
 ('LD:plastic_substrate', 'substrate_definition_needed',
  'Plastic substrate is too broad to identify a qualified electronics product or its manufacturing site.',
  'Specify polymer, form and application; do not substitute a general plastics producer for a package substrate manufacturer.'),
 ('LD:sic_lapping_slurry', 'abrasive_versus_workpiece_ambiguity',
  'A product advertised for polishing SiC does not prove its abrasive is SiC. The Entegris lead was not admitted as a match.',
  'Confirm abrasive chemistry and the workpiece in a technical datasheet before selecting vendors.'),
 ('LD:deionized_water_coolant SC-DI-WATER', 'local_purification_or_working_fluid',
  'Water-treatment equipment vendors are not necessarily sellers of the specified water. On-site production and sealed working-fluid fill are different cases.',
  'Specify on-site purification versus purchased fluid, purity, degassing and supply boundary.'),
 ('LD:polysilicon_starter_rods', 'specialised_intermediate_research_open',
  'Polysilicon production capability alone does not prove separately sold high-purity slim rods.',
  'Find an explicit slim-rod product and production location or document captive production; further research is possible.'),
 ('LD:polyurethane_matrix LD:polyester_felt_backing', 'pad_layer_not_finished_pad',
  'A finished polishing-pad supplier does not prove independent sale of its matrix or felt layer.',
  'Find specified foam/felt intermediate products, or model the layers as internal transformations within the pad plant.'),
 ('PM-ACRYLIC-PU PM-REFINED-AU', 'promising_official_lead_access_blocked',
  'Official indexed product leads exist, but this pass could not inspect the full source: Covestro returned HTTP 403 and Umicore HTTP 402 through the research service.',
  'Manually obtain current manufacturer datasheets. Do not interpret an access failure as evidence the supplier does not exist.'),
 ('DC-SINTER-BOAT', 'shape_and_composition_not_yet_matched',
  'YSZ material capability or a YSZ coating on a setter plate does not establish a bulk YSZ setter plate matching this node.',
  'Verify bulk material versus coating, shape and application in a manufacturer datasheet before adding a vendor.'),
 ('SC-PBT-GF30 SC-LCP-GF SC-PPA-REFLECTOR', 'compound_versus_moulded_part',
  'A resin compound maker is not necessarily the producer of the moulded fan, connector insulator or LED reflector.',
  'Separate compound supply from moulding responsibility and verify each product-to-site mapping.'),
 ('SC-FE-POWDER-CORE SC-FERRITE-BODY SC-RES-BODY SC-SMD-TERM SC-CU-TERMINAL', 'internal_component_or_specialised_intermediate',
  'A finished inductor/resistor/capacitor maker does not prove an independently sold internal body, core or termination.',
  'Seek explicit intermediate-product evidence or document an internal factory process; do not create false independent backups.'),
 ('SC-FBGA-SUB', 'technology_and_grade_allocation_open',
  'BT and ABF denote different substrate technologies. General package-substrate capability does not prove the exact FBGA design or plant.',
  'Verify substrate technology, dimensions and package application, then research site-specific production.'),
]

def main():
    with (CLEAN/'full_supply_chain_vendor_coverage.csv').open() as f:
        coverage = list(csv.DictReader(f))
    lookup = {nid: (status, issue, action) for ids, status, issue, action in GROUPS for nid in ids.split()}
    unresolved = []
    for row in coverage:
        if int(row['vendor_count']):
            continue
        treatment = row['procurement_treatment']
        if treatment == 'process_stage_no_material_vendor':
            disposition = ('process_stage', 'This node represents an operation, not a material to buy.', 'Research process operators and facilities, not a commodity vendor.')
        elif treatment == 'category_expand_children':
            disposition = ('category', 'This is a grouping node; missing a category-level vendor is not necessarily a data defect.', 'Review the child materials and their supplier/site evidence.')
        elif treatment == 'local_resource_or_utility':
            disposition = ('utility_resource', 'Ambient air and local water are not globally interchangeable component purchases.', 'Choose the actual facility and local intake, utility or treatment boundary.')
        else:
            disposition = lookup.get(row['node_id'], ('further_supplier_research_open',
                'No sufficiently scoped supplier record has been accepted. This is unfinished research, not proof that evidence cannot be found.',
                'Continue official product, technical-datasheet and manufacturing-location research; confirm grade and product form.'))
        status, issue, action = disposition
        unresolved.append(dict(node_id=row['node_id'], node_name=row['node_name'], status=status,
            issue=issue, next_action=action, evidence_absence_claim=False))
    payload = dict(reviewed_on='2026-11-24',
        interpretation='Unresolved is not unavailable. This diagnostic distinguishes source access, product definition, internal manufacture and research still open.',
        newly_supplier_mapped_nodes=['PM-WC-COBALT', 'DC-PET-LINER', 'DC-TIN-PLATE'],
        counts=dict(Counter(r['status'] for r in unresolved)), unresolved_nodes=unresolved,
        access_blocked_leads=[
          dict(node_id='PM-REFINED-AU', supplier='Umicore', url='https://mds.umicore.com/en/electroplating/products/product-finder/potassium-gold-cyanide-68-2', status='official_indexed_lead_full_page_and_datasheet_fetch_failed_HTTP_402', caveat='68.2% gold content of a salt is not 99.99% elemental-gold purity; combined node needs branch separation.'),
          dict(node_id='PM-ACRYLIC-PU', supplier='Covestro', url='https://www.covestro.com/en/product-technology/waterborne-coatings-and-paint', status='official_indexed_lead_full_page_fetch_failed_HTTP_403', caveat='PU/polyacrylate resin family is not a fully verified electronics coating or photoresist recipe.')],
        rejected_automatic_matches=[
          dict(node_id='LD:sic_lapping_slurry', url='https://www.entegris.com/shop/en/USD/products/chemistries/specialty-chemicals/slurries/Silicon-Carbide-(SiC)-Slurries/p/SiliconCarbideSiCSlurries', issue='For-SiC application is not proof of SiC abrasive composition.'),
          dict(node_id='DC-SINTER-BOAT', url='https://www.coatingsolutions.saint-gobain.com/applications/performance-industrial/metal-industry/reaction-barrier-coatings-setter-plates', issue='Coating capability is not evidence of a complete bulk-YSZ setter plate.')],
        cross_cutting_gaps=[
          'All manufacturing sites: current subset is incomplete; product-to-plant evidence is often narrower than the company portfolio.',
          'Top-ten/market-share claims: current product capability evidence does not establish comparable segment/year rankings.',
          'Shipping: nearest-hub distance is not a freight route; cargo acceptance, access, schedules and hazardous-material restrictions remain unverified.',
          'Times: manufacturing lead time requires queue, batch size and process assumptions or observations; one operation duration is not total lead time.',
          'Redundancy: qualified alternatives, independent ownership, capacity and AND/OR dependency rules remain to be validated.'
        ])
    (CLEAN/'full_supply_chain_gap_diagnosis.json').write_text(json.dumps(payload, indent=2)+'\n')
    lines=['WHY SOME DATA REMAIN INCOMPLETE', '', payload['interpretation'], '',
        'This pass added three previously unmapped material nodes. It did not fill gaps with assumed suppliers or times.', '',
        f'Unresolved supplier nodes: {len(unresolved)} (including categories, stages and utilities).', '']
    for row in unresolved:
        lines += [f"{row['node_id']} | {row['node_name']} | {row['status']}", row['issue'], 'Next: '+row['next_action'], '']
    lines += ['OTHER PROJECT GAPS']+payload['cross_cutting_gaps']
    (ROOT/'GAP_DIAGNOSIS.txt').write_text('\n'.join(lines)+'\n')
    print(f'Wrote a reason and next action for all {len(unresolved)} unresolved supplier nodes.')

if __name__ == '__main__':
    main()
