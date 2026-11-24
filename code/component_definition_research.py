"""Scoped technical definitions and public evidence for the submitted hierarchy.

Definitions describe product classes. Project interpretations and exact grade
requirements are separate from facts established by the cited sources.
"""
from additional_public_research import source, vendor, site, edge, SOURCES

DEFINITIONS = {}
def define(ids, name, kind, definition, sources, decision):
    for nid in ids.split():
        DEFINITIONS[nid] = dict(node_id=nid, preferred_name=name, semantic_kind=kind,
            formal_definition=definition, source_ids=sources,
            project_interpretation=decision, definition_status='technical_class_definition_with_explicit_project_scope', evidence_scope='References support class terminology; project-specific material, geometry, grade and procurement choices are not thereby verified.')

source('R4_TORAY_PBT','Toray','Reinforced PBT technical properties',
 'https://www.plastics.toray/technical/toraycon/tec_003.html',
 'Lists glass-fibre reinforced PBT grades; does not verify a particular GPU fan moulding or reinforcement percentage.')
source('R4_AL_ROLLING','The Aluminum Association','Aluminium processing: sheet and plate',
 'https://www.aluminum.org/processing-101',
 'Describes rolled plate, subsequent machining and sheet production. Does not establish the alloy or dimensions of a GPU backplate.')
source('R4_IPS_SETTER','IPS Ceramics','Kiln setters, supports and cranks',
 'https://ipsceramics.com/kiln-furniture/setters-supports-cranks/',
 'Defines the firing support function. Does not establish bulk YSZ composition or electronics suitability.')
source('R4_SHINETSU_REFLECTOR','Shin-Etsu Chemical','LED reflector material announcement, 2009',
 'https://www.shinetsu.co.jp/jp/news/other/shin-etsu-chemical-develops-a-silicone-reflector-material-for-high-brightness-leds-and-transparent-protective-film/',
 'Explains reflector function and historical PPA use; proposes silicone alternatives. Not a current GPU-specific recipe.')
source('R4_MOLEX_LCP','Molex','Impact connector technical drawing',
 'https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/765/76530/765303047_sd.pdf',
 'Documents a glass-filled LCP connector body. This is not a DisplayPort drawing and supports only the material-class definition.')
source('R4_TECHNIC_GOLD','Technic','Gold plating technical presentation, 2014',
 'https://www.technic.com/sites/default/files/resources/SUR-FIN%20pres%200614.pdf',
 'Discusses potassium gold cyanide plating chemistry. Used only to distinguish plating salt from elemental gold, not current sales/site evidence.')

source('R4_AMKOR_FLIP','Amkor','Flip-chip assembly technology sheet',
 'https://amkor.com/wp-content/uploads/2018/02/Flip_Chip_TS102.pdf',
 'Describes bumped die attachment to substrate and underfill. Supports the distinction between bare die, packaging operation and packaged output; not an NVIDIA supplier assignment.')
source('R4_SHINKO_PBGA','Shinko Electric Industries','Organic plastic BGA substrates',
 'https://www.shinko.co.jp/english/product/package/substrate/pbga.php',
 'Organic prepreg substrates for logic and memory; through-hole and build-up options. BT/ABF grade and exact GDDR package are not established.')
source('R4_COILCRAFT_VRM','Coilcraft','Magnetics in multiphase voltage regulators',
 'https://www.coilcraft.com/en-us/resources/application-notes/tlvr-multiphase-magnetics/',
 'Interleaved buck-converter phases use individual inductors; TLVR is a distinct architecture. Phase count and exact board BOM remain design choices.')
source('R4_SIERRA_EDGE','Sierra Circuits','PCB gold fingers',
 'https://www.protoexpress.com/kb/gold-fingers/',
 'PCB edge-contact terminology and fabrication context; a card edge is different from its mating board socket.')
source('R4_ROHM_TERMINATIONS','ROHM','Chip resistor FAQ, 2012, question 5',
 'https://fscdn.rohm.com/en/products/databook/operation/passive/resistor/common/faq.pdf',
 'Documents silver-based inner termination, nickel barrier and tin outer layer for the described chip resistors. Counters treating copper/nickel/tin as universal for every passive component; dated factory claims not used as current site evidence.')
source('R4_ROHM_BODY','ROHM','Chip resistor construction and use notes',
 'https://fscdn.rohm.com/en/products/databook/operation/passive/resistor/common/r_siyoujou.pdf',
 'Technical construction reference for ceramic thick-film resistor bodies; the specified recipe does not cover every resistor technology.')
source('R4_MURATA_INDUCTOR','Murata','Power inductor structures',
 'https://www.murata.com/en-global/products/inductor/power/overview/feature/power',
 'Distinguishes wire-wound and multilayer inductors; magnetic core, winding and resin construction depend on the product family.')
source('R4_ACT_WATER','Advanced Cooling Technologies','Heat pipe fundamentals',
 'https://www.1-act.com/thermal-solutions/passive/heat-pipes/heat-pipes-101/',
 'Two-phase heat transfer and copper/water compatibility. Does not establish a specific degassing or impurity specification for a GPU cooler.')
source('R4_LAPMASTER_SIC','Lapmaster Wolters','Premixed abrasive slurries',
 'https://www.lapmaster-wolters.com/pre-mixed-abrasive-slurries.html',
 'Explicitly offers slurries containing silicon-carbide abrasive powder. Wafer suitability, particle distribution and carrier purity require qualification.')
vendor('Lapmaster Wolters','R4_LAPMASTER_SIC','LD:sic_lapping_slurry',
 'SiC-containing lapping slurry; semiconductor wafer grade and water-carrier specification unconfirmed')
edge('E0250','R4_LAPMASTER_SIC','supported_product_class','SiC powder can be the abrasive in a lapping slurry; no universal wafer-process requirement is implied.')
source('R4_WACKER_SEED','Wacker','Siemens deposition on seed rods, annual report 2022',
 'https://reports.wacker.com/2022/annual-report/sustainable-solutions/purity-is-our-recipe-for-success.html',
 'Trichlorosilane deposits silicon on seed rods to produce polysilicon before crystal growth. Seed rods are not themselves fabricated GPU wafers; merchant slim-rod sales not established.')
source('R4_KURITA_WATER','Kurita','Ultrapure water supply service',
 'https://www.kurita-water.com/en/solution/watersupply.html',
 'Documents installation and operation of water-treatment systems plus supply of UPW itself. Facility-specific service contracts and cooling-fluid suitability are not established.')
vendor('Kurita','R4_KURITA_WATER','LD:deionized_water_coolant',
 'On-site ultrapure-water supply service capability; coolant formulation and customer/site contract not established',
 'utility_service_not_shipped_commodity;coolant_application_unqualified')
source('R4_HYDRO_AL','Hydro','High-purity aluminium for electronics',
 'https://www.hydro.com/en/global/aluminium/products/casthouse-products/high-purity-aluminium/',
 'High-purity aluminium feedstock and semiconductor sputtering applications; numeric purity range is reported separately from inconsistent N shorthand on the page.')
vendor('Hydro','R4_HYDRO_AL','LD:aluminum','High-purity aluminium feedstock for electronics; finished sputtering-target dimensions and qualification unconfirmed')
source('R4_HYDRO_GREVEN','Hydro','High Purity GmbH production location',
 'https://www.hydro.com/en/global/about-hydro/hydro-worldwide/europe/germany/grevenbroich/hydro-aluminium-high-purity-gmbh/',
 'Identifies ultra-pure aluminium production business and Grevenbroich address; specific customer qualification not established.')
site('Hydro Grevenbroich high-purity aluminium plant','Hydro','Germany','Grevenbroich','Aluminiumstrasse 2, D-41515 Grevenbroich','R4_HYDRO_GREVEN','LD:aluminum')
source('R4_TAYA_WIRE','Taya Group','Polyimide-enamelled copper wire catalog',
 'https://www.taya.com.tw/en/enamel-wire',
 'Explicit PI-enamelled copper wire product. Oxygen-free conductor grade and GPU fan winding use remain unconfirmed.')
vendor('Taya Group','R4_TAYA_WIRE','SC-MAGNET-WIRE','Polyimide-enamelled copper wire; oxygen-free grade, wire diameter and winding qualification unconfirmed')
source('R4_MITSUI_CORE','Mitsui High-tec','Electrical-steel motor-core manufacture',
 'https://www.mitsui-high-tec.com/technology/',
 'Manufacturer describes stacking electrical steel to make motor cores for automotive and household equipment. GPU-fan dimensions and suitability not established.')
vendor('Mitsui High-tec','R4_MITSUI_CORE','SC-SILICON-STEEL','Electrical-steel motor-core product class; miniature fan geometry and grade unqualified')
source('R4_MITSUI_SITES','Mitsui High-tec Canada','Group manufacturing network',
 'https://mht-canada.com/global-network/',
 'Lists named motor-core plants and addresses. Office-only and placeholder under-construction entries excluded; this is a documented subset.')
for name,country,city,address in [
 ('Brantford motor-core plant','Canada','Brantford, Ontario','60 Fen Ridge Court'),
 ('Gifu motor-core plant','Japan','Kani','675-35 Kakida'),
 ('Shanghai motor-core and leadframe plant','China','Shanghai','2001 Xinjinqiao Road'),
 ('Ayutthaya motor-core plant','Thailand','Bang Pa-in','125 Moo 1, Hi-tech Industrial Estate, Baan Lane'),
 ('Guangdong motor-core and leadframe plant','China','Dongguan','10 Lian Xin Road, Shang Jiao Village, Chang An')]:
    site('Mitsui High-tec '+name,'Mitsui High-tec',country,city,address,'R4_MITSUI_SITES','SC-SILICON-STEEL')
source('R4_MYLAR_INSULATION','Mylar Specialty Films','Polyester electrical insulation films',
 'https://mylar.com/market-areas-for-mylar-specialty-films-range/mylar-polyester-film-for-electrical-insulation/',
 'Names insulation film and manufacturing in Dumfries and Hopewell. Film supply is distinct from die-cut finished liners; no finished-liner vendor mapping is inferred.')
source('R4_USGS_AS','USGS','Arsenic commodity overview',
 'https://www.usgs.gov/centers/national-minerals-information-center/arsenic-statistics-and-information',
 'Arsenic recovery can use arsenopyrite or smelter byproducts. An arsenopyrite mine is not universally necessary for arsine or GaAs manufacture.')
SOURCES[-1]['reliability']='US geological agency commodity reference; not a supplier contract or mine allocation'
source('R4_VAC_LAMINATION','Vacuumschmelze','Laminated magnetic cores',
 'https://www.vacuumschmelze.com/products/soft-magnetic-materials-and-stamped-parts/lamination-stacks',
 'Explains insulated sheet stacks and eddy-current control; its cobalt/nickel iron products are not accepted as silicon-steel substitutes.')
source('R4_NORDSON_COAT','Nordson','Conformal coating material families',
 'https://www.nordson.com/en/divisions/electronics-solutions/your-process/fluid-types/conformal-coating-materials',
 'Distinguishes acrylic, polyurethane and hybrid formulations. This does not establish one shared formulation for photoresist, pressure-sensitive adhesive and motor lamination varnish.')
source('R4_TI_RGB','Texas Instruments','Microcontroller RGB LED reference design',
 'https://www.ti.com/tool/TIDM-G2XXSWRGBLED',
 'Documents PWM control of red, green and blue LED channels using a microcontroller; this supports a circuit function, not a mandatory standalone GPU daughterboard.')
source('R4_ASUS_MECHANICAL','ASUS','Dual RTX 3050 construction overview',
 'https://www.asus.com/us/motherboards-components/graphics-cards/dual/dual-rtx3050-8g/',
 'Describes shroud, heatsink, heatpipes, axial fans and protective backplate. Used as component terminology evidence only, not an RTX 5080 exact BOM.')
source('R4_ANODIZING','Aluminum Anodizers Council','Anodizing and colouring FAQ',
 'https://members.anodizing.org/page/anodized-aluminum-faq',
 'Oxide formation and dye colouring are different steps; bath additives, dye and substrate are not one interchangeable commodity.')
source('R4_INTEL_POWER','Intel','12V-2x6 auxiliary power connector pin assignments',
 'https://edc.intel.com/content/www/cn/zh/design/products-and-solutions/processors-and-chipsets/alder-lake-s/atx12vo-12v-only-desktop-power-supply-design-guide/2.11/2.11/dc-connectors/_Ref138773916/_Ref120543312/',
 'Reference connector/pinout for a modern auxiliary-power option. Project selects board-side connector assembly; connector generation/count require a selected card design.')

define('0','Discrete graphics card','finished_assembly',
 'A circuit-board assembly containing a graphics processor, memory, power conversion and external interfaces, with a cooling and mechanical system.',
 'R2_MSI_CARD;R4_ASUS_MECHANICAL','Keep a generic discrete graphics-card case; quantities in the submitted BOM remain unverified design assumptions.')
define('1','Populated graphics-card PCB assembly','assembly',
 'The main printed circuit board after electronic components have been mounted and interconnected.',
 'R4_SIERRA_EDGE;R2_MSI_CARD','Distinguish this populated assembly from bare board 1.1; final assembly manufacturer is a separate role.')
define('1.2 LD:finished_logic_die','Packaged and tested GPU device','packaged_device',
 'A fabricated GPU die integrated with package interconnections and substrate, then tested as a packaged device.',
 'R4_AMKOR_FLIP;SRC_SIA_PROCESS','Treat these two submitted labels as one output in the reviewed graph; packaging occurs once.')
define('1.2.1 LD:logic_die_fabricated','Fabricated bare GPU die','bare_die',
 'The semiconductor die containing fabricated GPU circuitry before package assembly.',
 'SRC_SIA_FRONTEND;R4_AMKOR_FLIP','Alias the two labels in the reviewed graph; wafer fabrication and die preparation precede packaging.')
define('LD:assembly_packaging_testing','GPU package assembly and test','process',
 'Operations that attach and electrically connect the fabricated die, complete its package and test the packaged device.',
 'R4_AMKOR_FLIP;SRC_SIA_PROCESS','Use as a transformation node. Flip-chip and wire-bond recipes are design alternatives, not universally simultaneous inputs.')
define('LD:fabrication','Semiconductor wafer fabrication','process',
 'Repeated deposition, patterning, doping, etching and related operations that create integrated circuits on a semiconductor wafer.',
 'SRC_SIA_FRONTEND','Manufacturing site/operator belongs to this process; a bare die additionally requires wafer test and separation.')
define('1.4','VRM phase','functional_subassembly',
 'One switching-converter channel in a multiphase voltage regulator, including its power stage and associated magnetic energy-storage path.',
 'R4_COILCRAFT_VRM','A board circuit function. Phase count and shared versus per-phase capacitors require schematic evidence.')
define('1.5','Graphics-card I/O mounting bracket','mechanical_part',
 'The rear mounting part that secures the card at chassis expansion slots and provides openings for display connectors.',
 'R4_ASUS_MECHANICAL;R2_MSI_CARD','Project functional definition; material, dimensions and stamping supplier are design-specific.')
define('3','Graphics-card backplate','mechanical_part',
 'A rear cover or stiffening plate over the back of the graphics-card board; heat-spreading function depends on thermal contact and design.',
 'R4_ASUS_MECHANICAL','Mechanical function is defined; aluminium alloy, insulation and thermal pads are not universally required.')
define('7','Cooler shroud','mechanical_part',
 'The housing surrounding portions of the cooling assembly, supporting or covering fans and influencing airflow.',
 'R4_ASUS_MECHANICAL','A custom housing; polymer and metal versions are alternatives. Do not prescribe PC/ABS universally.')
define('4','PCB edge contact fingers','integrated_board_feature',
 'Patterned and finished conductive contacts at the card PCB edge that mate with the host PCI Express connector.',
 'R4_SIERRA_EDGE','Allocate manufacture to PCB/contact finishing; do not count a motherboard socket as the card part.')
define('5','Board-side auxiliary power connector assembly','connector_assembly',
 'The card-mounted connector housing and contacts accepting supplemental electrical power from an external cable.',
 'R4_INTEL_POWER','Choose board-side scope; cable and PSU are outside this node. 12V-2x6 is an option, not a verified part assignment.')
define('6','Display output interface group','functional_group',
 'A grouping of board-mounted video receptacles and associated protection circuitry.',
 'R2_MOLEX_DP;R2_MSI_CARD','Retain HDMI/DisplayPort/protection children; no separate supplier is required for a grouping label.')
define('8','Optional RGB lighting subsystem','optional_assembly',
 'LED emitters plus drive/control circuitry providing decorative multicolour lighting.',
 'R4_TI_RGB;R_CREE_RGB','Optional in a generic GPU card. Absence does not prevent the card from processing graphics.')
define('8.2','RGB lighting control circuit','functional_subassembly',
 'Circuitry controlling LED-channel current or duty cycle to set colour and brightness.',
 'R4_TI_RGB','The submitted MCU and board define one implementation; a dedicated driver IC or main-board integration is also possible.')
define('RAW-AIR','Ambient air resource','local_resource',
 'The local atmospheric gas feed from which industrial air-separation operations recover gases such as nitrogen, oxygen and argon.',
 'R_LINDE_ULTRAPURE','Use local resource intake; purified gases are separately manufactured products with grade and delivery constraints.')
define('RAW-WATER','Freshwater resource','local_resource',
 'Raw water supplied to a site before application-specific purification or treatment.',
 'R4_KURITA_WATER','Utility/source connection is site-dependent; do not interpret it as globally interchangeable shipped UPW.')
define('RAW-ARSENOPYRITE','Arsenopyrite-bearing arsenic feedstock','raw_material_route',
 'Arsenic-bearing mineral feed that can be processed to recover arsenic; smelter byproducts provide alternative recovery routes.',
 'R4_USGS_AS','Keep the original ore node as one route and flag mandatory-ore assumptions; do not invent a specific arsenopyrite mine.')
define('LD:packaging_materials','Semiconductor packaging material family','category',
 'The set of substrate, interconnection, attachment and protective materials used by a selected package process.',
 'R4_AMKOR_FLIP;SRC_SIA_PROCESS','Category membership is not an AND requirement for every listed material.')
define('LD:process_specific_fab_materials','Process-specific fabrication materials','category',
 'Materials selected for particular wafer-fabrication operations and technology nodes.',
 'SRC_SIA_FRONTEND','Expand by actual process recipe; this label has no single product specification.')
define('LD:interconnect_materials','Package-substrate conductive and finishing materials','category',
 'Conductive layers, via metallization and surface finishes used to route electrical connections through a package substrate.',
 'R4_SHINKO_PBGA','The submitted children restrict scope to substrate interconnection; copper foil and ENIG chemistry need separate procurement branches.')
define('LD:plastic_substrate','Organic package-substrate dielectric structure','internal_material_structure',
 'The polymer-based insulating structure of an organic IC substrate, potentially including reinforcement and particulate filler.',
 'R4_SHINKO_PBGA','Interpret from the resin, glass and filler children. It is not the complete routed substrate and is not a generic thermoplastic sheet.')
define('LD:basic_acidic_chemical_inputs','Process acid/base reagents','category',
 'Acidic or alkaline chemicals used for the selected polishing, cleaning or related process conditions.',
 'R_FUJIMI_SLURRY;SRC_SIA_FRONTEND','List alternatives by recipe; the category alone does not prove every named acid belongs in one CMP mixture.')
define('LD:dopants','Semiconductor dopant sources','category',
 'Sources of intentionally introduced dopant species used to adjust semiconductor electrical behaviour.',
 'R_LINDE_GASES;SRC_SIA_FRONTEND','Select p-type or n-type species and introduction method. A gas precursor listing alone does not prove use in crystal growth.')
define('LD:polysilicon_starter_rods','Silicon slim seed rods for polysilicon deposition','process_intermediate',
 'Slender silicon supports on which additional silicon is deposited during a Siemens-type polysilicon-production process.',
 'R4_WACKER_SEED','Route to polysilicon production upstream of wafer growth; merchant sale and exact purity remain open.')
define('LD:sic_lapping_slurry','Silicon-carbide abrasive lapping slurry','process_consumable',
 'A suspension containing silicon-carbide abrasive particles in a liquid carrier, used for mechanical lapping.',
 'R4_LAPMASTER_SIC','The submitted SiC-grit child resolves composition. Wafer grade and carrier are still process specifications, not arbitrary guesses.')
define('LD:deionized_water_coolant','Purified process water for coolant/slurry use','utility_or_consumable',
 'Water with ionic impurities reduced by treatment and supplied to the selected cooling or slurry operation.',
 'R4_KURITA_WATER','DI water and semiconductor UPW are different specifications; set required purity from the downstream process.')
define('SC-DI-WATER','Water working fluid in a sealed cooler','internal_working_fluid',
 'A water charge that evaporates and condenses to transport heat inside a compatible heat pipe or vapor chamber.',
 'R4_ACT_WATER','Copper/water is the chosen representative option; purity and degassing limits require the cooler specification.')
define('LD:aluminum','High-purity aluminium metal feedstock','material',
 'Aluminium metal refined to the impurity limits required by an electronic-material or deposition application.',
 'R4_HYDRO_AL','Distinguish high-purity feedstock from structural alloy plate and finished sputtering targets.')
define('LD:polyurethane_matrix','Polyurethane polishing-pad matrix','internal_material_structure',
 'The polyurethane-based polymer phase forming the functional body of a selected polishing pad.',
 'R2_LAPMASTER_PAD;R_QNITY_PADS','Porosity and formulation depend on pad grade; no separately sold matrix supplier is inferred.')
define('LD:polyester_felt_backing','Polyester-felt polishing-pad layer','internal_material_structure',
 'A nonwoven polyester-fibre layer used in certain pad constructions, sometimes impregnated with polyurethane.',
 'R2_LAPMASTER_PAD','The source supports a felt-based design, not a universal backing required in every CMP pad.')
define('PM-ACRYLIC-PU','Acrylic/urethane coating-resin family','material_family',
 'Resin systems using acrylic and/or polyurethane chemistry, including hybrid formulations selected for coating performance.',
 'R4_NORDSON_COAT;R_SHERWIN_COATING','Separate coating resin, photoresist binder, pressure-sensitive adhesive and interlaminar varnish. Their formulations are not interchangeable.')
define('PM-REFINED-AU','Refined gold metal and gold-plating salt branches','combined_products',
 'Two distinct products: purified elemental gold and a gold-containing salt used in selected plating solutions.',
 'R4_TECHNIC_GOLD','The original combined label must not equate metal purity with gold mass fraction in a salt. Salt identity needs its own datasheet.')
define('DC-ANODIZE-CHEM','Anodizing electrolyte and colourant branches','process_consumable_family',
 'Chemicals used to form an oxide layer on aluminium and, where selected, colour that layer in a subsequent or combined process.',
 'R4_ANODIZING','Electrolyte and black dye are distinct purchases; bath reuse/replenishment means disposable is not a fixed one-use count.')
define('DC-SINTER-BOAT','Ceramic setter or support for firing','process_tool',
 'A refractory support that holds parts during a firing or sintering operation.',
 'R4_IPS_SETTER','Project adopts the support function only; bulk YSZ composition and universal use for resistor firing are not verified. Treat YSZ as a proposed material option.')
define('SC-MYLAR-INSULATOR','Converted polyester-film insulating liner','converted_part',
 'An electrically insulating polyester film cut or formed to the geometry needed between components.',
 'R4_MYLAR_INSULATION','Film manufacture and final die cutting are separate capabilities. Mylar is a brand, not the name of every PET film.')
define('SC-PBT-GF30','Glass-reinforced PBT moulded fan part','moulded_part',
 'A fan impeller or frame formed from polybutylene terephthalate compounded with glass reinforcement.',
 'R4_TORAY_PBT','Material identity comes from the submitted specification; 30% reinforcement and suitability for a selected fan remain unverified design choices.')
define('SC-LCP-GF','Glass-reinforced LCP connector insulator','moulded_part',
 'A connector insulating body moulded from a glass-reinforced liquid-crystal polymer compound.',
 'R4_MOLEX_LCP','Compound and moulded body are different products. Verify the actual connector drawing before prescribing GF30.')
define('SC-PPA-REFLECTOR','PPA-based LED reflector body','moulded_part',
 'A moulded reflector or housing surrounding the LED emitter, using a selected reflective polymer compound.',
 'R4_SHINETSU_REFLECTOR','PPA, glass reinforcement and TiO2 loading are submitted design choices; they are not universal requirements for RGB LED packages.')
define('SC-AL-PLATE','Rolled structural aluminium alloy plate','material',
 'Flat rolled aluminium-alloy stock used to fabricate a structural component.',
 'R4_AL_ROLLING','5052 and 6061 are alternative alloy specifications from the submitted node; the stock must also specify temper, thickness and tolerances. Thin backplates may use sheet rather than plate; the exact alloy-to-part recipe remains unverified.')
define('SC-FE-POWDER-CORE','Pressed soft-magnetic metal-powder core','internal_component',
 'A magnetic body made from metal-powder particles and an insulating/binding system for an inductor.',
 'R4_MURATA_INDUCTOR','Carbonyl iron and Fe-Si-Cr are alternative material routes; exact composition and core shape require a part datasheet.')
define('SC-MAGNET-WIRE','Polyimide-enamelled copper winding wire','material',
 'Copper conductor coated with electrically insulating polyimide enamel for forming a winding.',
 'R4_TAYA_WIRE;R2_ELANTAS_ENAMEL','Polyimide is one insulation choice; oxygen-free copper and wire diameter remain specific requirements to verify.')
define('SC-SILICON-STEEL','Laminated electrical-steel stator core','internal_component',
 'A stack of shaped electrical-steel sheets forming the stationary magnetic circuit of a motor, with interlaminar insulation limiting eddy currents.',
 'R4_MITSUI_CORE;R4_VAC_LAMINATION','Steel strip production, stamping and stacking are distinct operations; core geometry must fit the fan motor.')
define('SC-CU-TERMINAL','Tin-finished copper lead terminal','component',
 'A shaped copper conductor with a tin-containing surface finish for electrical connection or solder attachment.',
 'R3_TECHNIC_TIN','A discrete lead is different from a deposited end termination; dimensions and base alloy require a component drawing.')
define('SC-FBGA-SUB','Fine-pitch BGA package substrate','component',
 'An interconnection substrate carrying a die and routing its electrical connections to a fine-pitch ball-grid-array interface.',
 'R4_SHINKO_PBGA','BT-based and ABF build-up systems are alternatives; select substrate technology from the actual memory package design.')
define('SC-FERRITE-BODY','Multilayer ferrite inductor body','internal_component',
 'A fired magnetic ceramic body with embedded conductive patterns forming the winding of a multilayer inductor.',
 'R4_MURATA_INDUCTOR','Specific NiZn and silver choices need product evidence; this is not the construction of every power inductor.')
define('SC-RES-BODY','Ceramic thick-film resistor body','internal_component',
 'A ceramic substrate carrying a patterned resistive film and protective layers before or as part of termination processing.',
 'R4_ROHM_BODY','Use the thick-film case only; thin-film and metal-element resistors have different material structures.')
define('SC-SMD-TERM','Device-specific surface-mount termination stack','internal_component',
 'Conductive end layers connecting an internal passive element to a solderable external surface, often including barrier and finish layers.',
 'R4_ROHM_TERMINATIONS','Replace universal Cu/Ni/Sn assumption with device-specific base metal; the documented resistor example uses Ag-based/Ni/Sn.')
define('1.4.3 1.6 8.2.3','Surface-mount passive component group','component_group',
 'A collection of resistor, capacitor and inductor parts mounted on a circuit board.',
 'R4_ROHM_TERMINATIONS;R4_MURATA_INDUCTOR','R, C and L are separate required part families in a selected design, not interchangeable suppliers or materials of one combined device.')
define('SC-DRAM-DIE','Fabricated graphics-memory die','bare_die',
 'A semiconductor die implementing a selected generation of graphics double-data-rate memory.',
 'R2_MICRON_GDDR6;SRC_MICRON_GDDR7','Keep generation generic for this case study; GDDR6/GDDR6X/GDDR7 are not drop-in alternatives. The exact design must select one.')

for record in SOURCES:
    if record.get('source_id') == 'R4_ANODIZING':
        record['reliability']='Industry association indexed reference; full page blocked with HTTP 403 in this pass; source verification incomplete'
