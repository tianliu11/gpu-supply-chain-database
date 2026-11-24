"""Claim-by-claim process validation. No source proves an entire GPU recipe."""
from additional_public_research import source, edge as register_edge, site, SOURCES

CLAIMS=[]
def edge(ids,sid,status,note):
    register_edge(ids,sid,status,note)
    for eid in ids.split():
        CLAIMS.append(dict(edge_id=eid,source_ids=sid,validation_status=status,claim_scope=note))

source('R5_SUMCO_PROCESS','SUMCO','Silicon wafer production processes',
 'https://www.sumcosi.com/english/products/process/',
 'CZ growth from polysilicon in a quartz crucible; slicing, alumina lapping, etching, colloidal-silica polishing and cleaning. Supports a representative process, not every consumable or commercial shipment.')
source('R5_MURATA_MLCC','Murata','May 2025 MLCC webinar, slide 13',
 'https://www.murata.com/-/media/webrenewal/campaign/events/asean/2025/may25_-mlcc-trouble-shoot/presentation-may-webinar-5may.ashx?cvid=20250508091321000000&la=en-sg',
 'Illustrates ceramic dielectric with barium titanate and nickel internal electrodes. Nickel sulfate is not the electrode metal; the combined input node must select its metal branch.')
source('R5_MURATA_INTERNAL','Murata','MLCC integrated production capability',
 'https://corporate.murata.com/en-eu/technology/technology-applications/ceramiccapacitor',
 'Documents in-house material formulation, paste development, manufacturing and inspection. Internal layers are not automatically separately purchased components.')
source('R5_MURATA_INDUCTOR','Murata','Power-inductor constructions',
 'https://www.murata.com/en-sg/products/inductor/power/overview/learn/basic_01',
 'Multilayer ferrite construction combines magnetic material and internal electrodes by lamination and sintering. Does not prove every ferrite is NiZn or every conductor silver.')
source('R5_ROHM_RESISTOR','ROHM','Current-sense resistor structures, January 2023',
 'https://www.rohm.com/documents/11303/7742701/Bodos_Power_0123_030123_Travis_Moench.pdf/9ccf4dd7-625d-b959-8af0-8f6560b562e7?t=1707983494603',
 'Contrasts thick-film ceramic-supported and metal-element resistors. Supports alumina substrate function, not a universal 96-percent composition or direct powder purchase.')
source('R5_WACKER_BURG','Wacker','Burghausen semiconductor-polysilicon line commissioned, July 2025',
 'https://www.wacker.com/cms/media/en/documents/pressrelease-pdf/pm2025/opening_etching_line_next.pdf',
 'Confirms semiconductor-grade polysilicon production and initial deliveries from Burghausen. Does not identify a particular wafer customer or transport corridor.')
source('R5_SUMCO_SITE','SUMCO','Corporate data and factory addresses',
 'https://www.sumcosi.com/english/corporate/profile.html',
 'Rechecks the Kyushu Nagahama factory address and wafer business; does not assign a GPU customer or verify a gate coordinate.')
source('R5_SHINKO_FLIP','Shinko Electric Industries','Molded underfill flip-chip package',
 'https://www.shinko.co.jp/english/product/package/assembly/muf.php',
 'Documents die/substrate assembly, solder-bump or copper-pillar options and resin underfill; not mandatory wire bonds and leadframe for this selected package option.')
source('R5_MURATA_SITES','Murata','Ceramic-capacitor production and supply locations',
 'https://www.murata.com/en-global/products/capacitor/ceramiccapacitor/overview/strength',
 'Product-specific supply network lists six named production entities and addresses. Supports capacitor class, not all R/C/L devices or GPU part qualification.')
for name,country,city,address in [
 ('Fukui Murata ceramic-capacitor plant','Japan','Echizen','1, 13-go, Okamotocho'),
 ('Izumo Murata ceramic-capacitor plant','Japan','Izumo','2308 Kaminaoe, Hikawa-cho'),
 ('Wuxi Murata ceramic-capacitor plant','China','Wuxi','6 Xingchuang 1st Road, Export Processing Zone B'),
 ('Murata Singapore ceramic-capacitor plant','Singapore','Singapore','200 Yishun Avenue 7'),
 ('Philippine Manufacturing Murata ceramic-capacitor plant','Philippines','Tanauan, Batangas','First Philippine Industrial Park, Barangay Pantay Bata'),
 ('Murata Thailand ceramic-capacitor plant','Thailand','Lamphun','63 Moo 4, Ban Klang, Northern Region Industrial Estate')]:
    site(name,'Murata',country,city,address,'R5_MURATA_SITES','SC-MLCC-BODY',
         operating_status='public_product_supply_location_listed;internal_body_not_separate_merchant_product')
source('R5_BASF_PU','BASF','Polyurethane chemistry FAQ',
 'https://chemicals.basf.com/north-america/en/Monomers/isocyanates-and-polyols/resources/faqs',
 'Polyols and polyisocyanates are the immediate reactive material classes for polyurethane; formulation additives and precise pad grades not specified.')
source('R5_EPA_PEROXIDE','US EPA','Hydrogen peroxide supply-chain profile, December 2022',
 'https://www.epa.gov/system/files/documents/2023-03/Hydrogen%20Peroxide%20Supply%20Chain%20Profile.pdf',
 'Describes the anthraquinone hydrogenation/oxidation cycle and water extraction. General chemical route, not semiconductor purity or current transport authorization.')
SOURCES[-1]['reliability']='Government technical profile; historical factory counts and water-treatment grade not used as current semiconductor evidence'
edge('E0163 E0164 E0165','R5_EPA_PEROXIDE','supported_process_input',
 'Hydrogen and oxygen feed the anthraquinone cycle, with water extraction. Not a direct gas-mixing recipe; electronic-grade purification remains unspecified.')
source('R5_DOE_NITRIC','US Department of Energy','Chemical industry profile: nitric-acid manufacturing',
 'https://www1.eere.energy.gov/manufacturing/resources/chemicals/pdfs/profile_chap5.pdf',
 'Documents ammonia oxidation, subsequent nitrogen-oxide oxidation and water absorption. Historical technical reference, not current suppliers, capacity or semiconductor purity.')
SOURCES[-1]['reliability']='Government technical process reference; historical industry statistics excluded'
source('R5_DOE_ACID_ROUTES','US Department of Energy','Chemical industry profile: sections 5.1.1, 5.1.6 and 5.1.7',
 'https://www1.eere.energy.gov/manufacturing/resources/chemicals/pdfs/profile_chap5.pdf',
 'Historical technical reference for ammonia synthesis, sulfuric-acid contact processing and thermal versus wet phosphoric-acid routes. No current market shares, factories or electronic-grade claims adopted.')
SOURCES[-1]['reliability']='Government technical process reference; historical market statistics excluded'
edge('E0192 E0193','R5_DOE_ACID_ROUTES','supported_process_input',
 'Hydrogen and nitrogen feed ammonia synthesis. Aggregate process only; semiconductor purification and supplier qualification remain unverified.')
edge('E0259 E0261','R5_DOE_ACID_ROUTES','supported_process_input',
 'Contact processing uses selected sulfur-bearing feed and air/oxygen. Elemental sulfur and pyrite are alternatives; no direct shipment established.')
edge('E0260','R5_DOE_ACID_ROUTES','supported_upstream_process_not_direct_input',
 'Refinery sulfur recovery can precede sulfuric-acid manufacture; crude petroleum is not an immediate acid reactant or mandatory source.')
edge('E0273 E0274','R5_DOE_ACID_ROUTES','supported_process_input',
 'Elemental phosphorus and air/oxygen belong to the thermal route. Wet-process feedstocks are an alternative, not additional mandatory inputs.')
edge('E0262 E0275','R5_DOE_ACID_ROUTES','water_role_requires_definition_review',
 'Process water is documented, but the submitted node is coolant. Cooling utility and chemical-process water must not be treated as the same qualified input.')
edge('E0265 E0266 E0267','R5_DOE_NITRIC','supported_process_input',
 'Ammonia, oxygen/air and water participate in staged oxidation/absorption. This aggregate process edge does not establish direct oxygen cylinders, semiconductor grade or a one-step reaction.')
source('R5_SHINETSU_MASK','Shin-Etsu Chemical','Photomask blank construction',
 'https://www.shinetsu.co.jp/en/products/electronics-materials/photomask-blanks/',
 'Synthetic-quartz substrate with conventional chromium or MoSi films. These are alternative transmissive-mask constructions, not a complete EUV stack.')
source('R5_AGC_EUV','AGC Electronics America','EUV mask blank construction',
 'https://www.agcem.com/products/euv-mask-blanks/',
 'Low-thermal-expansion glass with multilayer optical coating is patterned into EUV masks. Manufacturer is AGC; the US distribution office is not a blank factory.')
source('R5_MITSUI_PELLICLE','Mitsui Chemicals','Pellicle dust-proof membrane',
 'https://us.mitsuichemicals.com/service/product/pellicle/index.htm',
 'Pellicle is a mask protective accessory; membrane/thickness depend on exposure. Does not establish universal aluminium frames or fluoropolymer for EUV.')
edge('E0295 E0296','R5_SHINETSU_MASK','supported_product_class',
 'Supports quartz plus Cr-or-MoSi transmissive mask blanks, not a universal EUV recipe. Reviewed view separates the technologies.')
edge('E0297','R5_MITSUI_PELLICLE','supported_product_class',
 'Pellicle protective function supported. Exposure-specific accessory, not part of the etched circuit or interchangeable across wavelengths.')
source('R5_PGMEA_PROCESS','US Treasury / IRS','Production-route description in 2025-14705, section XI, pages 30-31',
 'https://public-inspection.federalregister.gov/2025-14705.pdf',
 'Describes PGME from methanol/propylene oxide, PGMEA from PGME/acetic acid, and the chlorohydrin route for propylene oxide. Used for chemistry, not legal advice or a universal route.')
SOURCES[-1]['reliability']='Government published process description based on producer petition; chosen route, not every commercial process'
edge('E0289 E0290','R5_PGMEA_PROCESS','supported_upstream_process_not_direct_input',
 'Propylene and methanol are upstream of PGMEA through propylene oxide and PGME; reviewed graph introduces intermediates.')
edge('E0291','R5_PGMEA_PROCESS','supported_process_input','Acetic acid reacts with PGME in the selected esterification route; electronic-grade purification is additional.')
edge('E0177 E0178','R5_BASF_PU','upstream_lineage_requires_process_evidence',
 'Do not treat benzene or propylene as immediate PU reactants. Immediate classes are polyols/polyisocyanates; commodity-to-monomer routes need their own evidence.')

edge('E0219 E0220','R4_WACKER_SEED','supported_process_input',
 'Wacker explicitly describes converting metallurgical silicon with hydrogen chloride to trichlorosilane, then distillation. Exact reactor configuration and purity are not established by this citation.')
edge('E0080 E0081','R4_WACKER_SEED','supported_upstream_process_not_direct_input',
 'Seed rods and TCS feed polysilicon deposition; the reviewed view routes these to deposition, not directly to a wafer.')
edge('E0082 E0083','R5_SUMCO_PROCESS','supported_process_input',
 'SUMCO documents dopant selection and quartz-crucible use in crystal growth. Category alternatives are not all simultaneously required; crucible is process tooling.')
edge('E0092 E0093','R5_SUMCO_PROCESS','supported_consumable_use',
 'Alumina is used in wafer lapping and colloidal silica in polishing in the documented process. Both are consumables, not constituents to be added to the silicon die.')
edge('E0594','R5_MURATA_MLCC','supported_product_class',
 'Barium titanate dielectric in the documented MLCC class; dielectric grade and device qualification remain design-specific.')
edge('E0595','R5_MURATA_MLCC','supported_product_class',
 'Nickel metal internal electrode supported, not nickel sulfate. Metal must be processed into the appropriate electrode formulation.')
edge('E0605','R5_ROHM_RESISTOR','supported_upstream_process_not_direct_input',
 'Alumina substrate is supported; calcined powder must first become a ceramic substrate. Exact 96-percent specification is not established.')
edge('E0585','R5_MURATA_INDUCTOR','supported_product_class',
 'Ferrite body is supported for multilayer ferrite inductors; this source alone does not establish NiZn composition.')
edge('E0044 E0045','R5_SHINKO_FLIP','supported_category_membership',
 'Substrate and underfill/mould resin belong to the documented flip-chip process; the precise resin grade and assembly design are not assigned.')
for ids, sid, note in [
 ('E0743 E0747 E0755','R5_MURATA_MLCC','MLCC body belongs to capacitor branch, not a combined R/C/L device.'),
 ('E0744 E0748 E0756','R5_ROHM_RESISTOR','Thick-film body belongs to resistor branch, not capacitor or inductor.'),
 ('E0742 E0746','R5_MURATA_INDUCTOR','Ferrite internal structure belongs to an inductor/filter branch; exact electrical function still depends on part selection.')]:
    edge(ids,sid,'supported_component_family',note+' Presence and counts in the submitted board are not confirmed.')

# Existing site records are updated, not duplicated or counted as new factories.
SITE_UPDATES = {
 'UP_WACKER_BURG':dict(source_ids='SRC_WACKER_POLY;SRC_OSM;R5_WACKER_BURG',
    operating_status='semiconductor_polysilicon_production_confirmed_2025_07',
    site_evidence_level='Official commissioning and deliveries confirm product class at site; customer allocation unverified'),
 'UP_SUMCO_IMARI':dict(source_ids='SRC_SUMCO_PLANTS;SRC_OSM;R5_SUMCO_SITE',
    operating_status='factory_publicly_listed_rechecked_2026_11_24',
    site_evidence_level='Official factory address rechecked; exact product/diameter/customer allocation requires further evidence')}

# Reroutes apply only to the separate reviewed structure. Unsupported ancestry
# remains visible but is excluded from direct-process calculations.
REROUTES = {
 'E0163':('REVIEW:peroxide_process','hydrogenation_feed','R5_EPA_PEROXIDE'),
 'E0164':('REVIEW:peroxide_process','oxidation_feed','R5_EPA_PEROXIDE'),
 'E0165':('REVIEW:peroxide_process','extraction_water','R5_EPA_PEROXIDE'),
 'E0295':('REVIEW:transmissive_blank','transmissive_mask_substrate','R5_SHINETSU_MASK'),
 'E0296':('REVIEW:transmissive_blank','selected_Cr_or_MoSi_film','R5_SHINETSU_MASK'),
 'E0289':('REVIEW:propylene_oxide','selected_chlorohydrin_route_feed','R5_PGMEA_PROCESS'),
 'E0290':('REVIEW:pgme','alkoxylation_feed','R5_PGMEA_PROCESS'),
 'E0080':('REVIEW:poly_deposition','process_seed','R4_WACKER_SEED'),
 'E0081':('REVIEW:poly_deposition','chemical_feed','R4_WACKER_SEED'),
 'E0082':('REVIEW:crystal_growth','selected_dopant_family','R5_SUMCO_PROCESS'),
 'E0083':('REVIEW:crystal_growth','process_tooling','R5_SUMCO_PROCESS'),
 'E0092':('REVIEW:wafer_finishing','lapping_consumable','R5_SUMCO_PROCESS'),
 'E0093':('REVIEW:wafer_finishing','polishing_consumable','R5_SUMCO_PROCESS')}

def expand_structure(nodes, edges, decisions):
    added=[]
    def node(nid,name,kind,sid,description):
        nodes[nid]=dict(id=nid,name=name,node_type=kind,original_node_ids=[],
            vendor_candidates=[],component_definition=dict(formal_definition=description,
            project_interpretation='Added technical process node; no assumed factory, time or customer.',source_ids=sid))
    for args in [
      ('REVIEW:poly_deposition','Polysilicon deposition and purification','process','R4_WACKER_SEED','Deposition on seed rods followed by breaking and cleaning for semiconductor feedstock.'),
      ('REVIEW:polysilicon','Semiconductor-grade polysilicon','material','R4_WACKER_SEED','Purified polycrystalline silicon feedstock for crystal growth.'),
      ('REVIEW:crystal_growth','CZ single-crystal growth','process','R5_SUMCO_PROCESS','Growth of a single-crystal silicon ingot from a doped melt in a quartz crucible.'),
      ('REVIEW:ingot','Single-crystal silicon ingot','material','R5_SUMCO_PROCESS','Single-crystal silicon stock before wafer forming.'),
      ('REVIEW:wafer_finishing','Wafer slicing, lapping, etching, polishing and cleaning','process','R5_SUMCO_PROCESS','Grouped wafer-forming operations, separate from semiconductor device fabrication.'),
      ('REVIEW:passive_R','Finished thick-film chip resistor','component','R5_ROHM_RESISTOR','A resistive device, distinct from capacitor and inductor families.'),
      ('REVIEW:passive_C','Finished multilayer ceramic capacitor','component','R5_MURATA_MLCC','A ceramic dielectric device with internal electrodes and device-specific external terminations.'),
      ('REVIEW:passive_L','Finished multilayer ferrite inductor/filter','component','R5_MURATA_INDUCTOR','A magnetic multilayer device; electrical rating and filter/inductor selection are design-dependent.')]: node(*args)
    for args in [
      ('REVIEW:polyol','Polyol formulation for polyurethane','material_family','R5_BASF_PU','Hydroxyl-functional material class; selected grade and additives require pad specifications.'),
      ('REVIEW:polyisocyanate','Polyisocyanate for polyurethane','material_family','R5_BASF_PU','Isocyanate-functional reactive material class; individual species are alternatives, not all required.'),
      ('REVIEW:propylene_oxide','Propylene oxide intermediate','chemical','R5_PGMEA_PROCESS','Intermediate in the selected PGME manufacturing route; chlorohydrin route is a scenario choice.'),
      ('REVIEW:pgme','Propylene glycol methyl ether intermediate','chemical','R5_PGMEA_PROCESS','Alcohol-ether intermediate esterified with acetic acid to produce PGMEA.')]: node(*args)
    for args in [
      ('REVIEW:transmissive_blank','Transmissive photomask blank','component','R5_SHINETSU_MASK','Synthetic quartz and selected chromium or MoSi film, before circuit patterning.'),
      ('REVIEW:transmissive_mask','Patterned transmissive photomask','process_output','R5_SHINETSU_MASK','Patterned mask for its specified optical exposure technology.'),
      ('REVIEW:euv_blank','Reflective EUV mask blank','component','R5_AGC_EUV','Low-expansion glass with multilayer optical coating; detailed stack is not expanded here.'),
      ('REVIEW:euv_mask','Patterned reflective EUV mask','process_output','R5_AGC_EUV','Patterned reflective mask for EUV exposure; not interchangeable with transmissive masks.')]: node(*args)
    node('REVIEW:anthraquinone','Anthraquinone working carrier','process_material','R5_EPA_PEROXIDE','Regenerated working carrier in the selected peroxide cycle; make-up consumption differs from stoichiometric reactant consumption.')
    node('REVIEW:peroxide_process','Anthraquinone-cycle peroxide production and extraction','process','R5_EPA_PEROXIDE','Grouped hydrogenation, oxidation and aqueous extraction; purity upgrading is not established.')
    def link(a,b,relation,sid,note):
        eid='RV'+str(len(added)+1).zfill(4)
        e=dict(edge_id=eid,source_node_id=a,target_node_id=b,
            validation_status='supported_process_stage',source_ids=sid,
            audit_note=note,review_note=note,reviewed_relation=relation,
            observed_shipping_edge=False,enabled_in_reviewed_view=True,
            evidence_scope='scoped_primary_source_process',analysis_use='technical_dependency_not_observed_shipment')
        edges.append(e);added.append(e)
    for a,b,sid in [
      ('REVIEW:poly_deposition','REVIEW:polysilicon','R4_WACKER_SEED'),
      ('REVIEW:polysilicon','REVIEW:crystal_growth','R5_SUMCO_PROCESS'),
      ('REVIEW:crystal_growth','REVIEW:ingot','R5_SUMCO_PROCESS'),
      ('REVIEW:ingot','REVIEW:wafer_finishing','R5_SUMCO_PROCESS'),
      ('REVIEW:wafer_finishing','LD:wafer','R5_SUMCO_PROCESS')]:
        link(a,b,'process_sequence',sid,'Documented representative sequence; not evidence these stages share a supplier or shipping route.')
    family={'SC-RES-BODY':('REVIEW:passive_R','R5_ROHM_RESISTOR'),
            'SC-MLCC-BODY':('REVIEW:passive_C','R5_MURATA_MLCC'),
            'SC-FERRITE-BODY':('REVIEW:passive_L','R5_MURATA_INDUCTOR')}
    changes={}
    for e in edges[:]:
        eid=e['edge_id']
        if eid in REROUTES:
            target,relation,sid=REROUTES[eid]
            e.update(target_node_id=target,reviewed_relation=relation,source_ids=sid,
                review_note='Rerouted to the documented intermediate or operation; not a shortcut to the final product.')
        elif e['target_node_id'] in ('1.4.3','1.6','8.2.3') and e['source_node_id'] in family:
            old=e['source_node_id']; replacement,sid=family[old]
            e.update(source_node_id=replacement,reviewed_relation='selected_component_family',
                review_note='Board group contains distinct finished device families, not one composite R/C/L product. Counts and actual part selections unverified.')
        elif e['target_node_id']=='LD:wafer' and eid.startswith('E'):
            e.update(reviewed_relation='upstream_or_optional_process_context',
                review_note='Not admitted as a direct requirement in the documented wafer-process backbone; chemistry or process option needs additional evidence.')
        if eid.startswith('E'):
            changes[eid]=e
            e['analysis_use']='context_only' if e['reviewed_relation'] in ('upstream_or_optional_process_context','dependency_or_ancestry_requires_process_review','category_or_family_membership','device_specific_internal_structure') else 'technical_dependency_not_observed_shipment'
            e['audit_note']=e['review_note']+' Source scope: '+e.get('audit_note','')
    for body,(finished,sid) in family.items():
        link(body,finished,'internal_structure',sid,'Body is an internal manufacturing intermediate; do not infer a separate commercial supplier or shipment.')
        link('SC-SMD-TERM',finished,'device_specific_termination','R4_ROHM_TERMINATIONS;R5_MURATA_MLCC;R5_MURATA_INDUCTOR','Device-specific termination function; universal Cu/Ni/Sn composition is explicitly NOT established.')
        edges[-1]['validation_status']='candidate_design_option'
        edges[-1]['analysis_use']='context_only'
    for a,b,sid in [
      ('REVIEW:polyol','LD:polyurethane_matrix','R5_BASF_PU'),
      ('REVIEW:polyisocyanate','LD:polyurethane_matrix','R5_BASF_PU'),
      ('REVIEW:propylene_oxide','REVIEW:pgme','R5_PGMEA_PROCESS'),
      ('REVIEW:pgme','LD:pgmea_casting_solvent','R5_PGMEA_PROCESS'),
      ('LD:chlorine','REVIEW:propylene_oxide','R5_PGMEA_PROCESS'),
      ('LD:sodium_hydroxide','REVIEW:propylene_oxide','R5_PGMEA_PROCESS')]:
        link(a,b,'selected_chemical_process_input',sid,'Supported material-class reaction in the selected process; purification, catalyst, grade and capacity are not specified.')
    for a,b,sid in [
      ('REVIEW:transmissive_blank','REVIEW:transmissive_mask','R5_SHINETSU_MASK'),
      ('REVIEW:euv_blank','REVIEW:euv_mask','R5_AGC_EUV'),
      ('REVIEW:transmissive_mask','LD:photomasks','R5_SHINETSU_MASK'),
      ('REVIEW:euv_mask','LD:photomasks','R5_AGC_EUV')]:
        link(a,b,'technology_specific_mask_route',sid,'Select exposure technology per lithography layer. Different mask types are not freely interchangeable backups; both may occur on different layers.')
    link('REVIEW:anthraquinone','REVIEW:peroxide_process','regenerated_process_carrier','R5_EPA_PEROXIDE','Carrier is regenerated; do not model full replacement for every unit of product.')
    link('REVIEW:peroxide_process','LD:hydrogen_peroxide','process_output','R5_EPA_PEROXIDE','General peroxide product; semiconductor-grade purification and qualification need separate specifications.')
    for d in decisions:
        if d['edge_id'] in changes:
            e=changes[d['edge_id']]
            d.update(reviewed_source=e['source_node_id'],reviewed_target=e['target_node_id'],relation=e['reviewed_relation'],decision=e['review_note'],source_ids=e['source_ids'])
    return added
