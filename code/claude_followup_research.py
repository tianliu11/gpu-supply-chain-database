"""Independently inspected evidence extending the supplied Claude batches."""
from additional_public_research import source, vendor, site, edge as register_edge

SITE_UPDATES = {}
DISCLOSED_FREIGHT = []
LEAD_TIME_DISCLOSURES = []
REFERENCE_SUPPLY_QUALIFICATION = []

CLAIMS=[]
def edge(ids,sid,status,note):
    register_edge(ids,sid,status,note)
    CLAIMS.extend(dict(edge_id=eid,source_ids=sid,validation_status=status,claim_scope=note) for eid in ids.split())

s=source('R7_HANA_VIETNAM','Hana Micron','Vietnam production facilities',
 'https://hanamicron.com/contents/cont.do?mId=65&mPid=10&sCode=eng',
 'Two explicitly designated package/test/module production sites. No specific GPU qualification or capacity interchangeability established.')
vendor('Hana Micron',s,'LD:assembly_packaging_testing','Assembly/test operator; exact GPU package qualification unverified')
site('Hana Micron Vietnam Yen Phong','Hana Micron','Vietnam','Yen Phong, Bac Ninh',
 'Yen Phong Industrial Zone, Long Chau',s,'LD:assembly_packaging_testing')
site('Hana Micron VINA Van Trung','Hana Micron','Vietnam','Nenh, Bac Ninh',
 'Part of CNSG-02, Van Trung Industrial Zone',s,'LD:assembly_packaging_testing')
s=source('R7_TONGFU_PRODUCTION','Tongfu Microelectronics','Production footprint and service scope',
 'https://en.tfme.com/About.html',
 'Seven production bases across Nantong, Hefei, Xiamen, Suzhou and Penang. Aggregate footprint does not establish which GPU product uses each plant.')
vendor('Tongfu Microelectronics',s,'LD:assembly_packaging_testing','IC packaging/test service; exact GPU package and qualified plant selection not established')
t=source('R7_TONGFU_ADDRESSES','Tongfu Microelectronics','Named production subsidiaries and addresses',
 'https://en.tfme.com/contact.html',
 'Addresses cross-checked against production cities. Taiwan sales contact excluded. Headquarters and Tongke not admitted without further site-specific production confirmation.')
for name,country,city,address in [
 ('Hefei','China','Hefei','Crossing of Yungu Road and Hezhang Road'),
 ('Nantong','China','Nantong','99 Jiangda Road, Sutong Technology Industrial Park'),
 ('TF-AMD Suzhou','China','Suzhou','88 Sutong Road, Suzhou Industrial Park'),
 ('TF-AMD Penang','Malaysia','Bayan Lepas','Phase 3, Free Industrial Zone'),
 ('Xiamen','China','Xiamen','89 Nanhai Second Road, Haicang District')]:
    site('Tongfu '+name,'Tongfu Microelectronics',country,city,address,s+';'+t,'LD:assembly_packaging_testing')

s=source('R7_SUMITOMO_LCP','Sumitomo Chemical','SUMIKASUPER LCP grades and fillers',
 'https://www.sumitomo-chem.co.jp/sep/english/products/lcp/lcp_fg_grade.html',
 'E5006L lists 30% glass-fibre filling. Compound evidence only, not manufacture of a specific connector insulator.')
vendor('Sumitomo Chemical',s,'PM-LCP-POLYMER SC-LCP-GF',
 'LCP and glass-fibre-reinforced moulding compound; moulded insulator geometry and GPU allocation unverified')
s=source('R7_TORAY_LCP','Toray','SIVERAS liquid-crystal-polyester resin',
 'https://www.plastics.toray/products/siveras/',
 'Liquid-crystal-polyester resin for precision electronic mouldings; not proof of a finished GF30 connector body.')
vendor('Toray Industries',s,'PM-LCP-POLYMER','SIVERAS LCP resin; finished moulded insulator not established')
s=source('R7_KENMARE_ZIRCON','Kenmare Resources','Moma mineral sands mine and separation process',
 'https://www.kenmareresources.com/our-business/the-moma-mine/',
 'Mineral separation produces zircon alongside ilmenite and rutile. No semiconductor-grade zirconia or customer allocation inferred.')
vendor('Kenmare Resources',s,'RAW-ZIRCON','Moma mineral-sands zircon product, not downstream purified zirconia')

s=source('R9_AL_SMELTING','Australian Aluminium Council','Aluminium smelting',
 'https://aluminium.org.au/about-aluminium/how-aluminium-is-made/aluminium-smelting/',
 'Documents the alumina-to-primary-aluminium process and carbon anodes made with petroleum coke and pitch.')
edge('E0318',s,'supported_process_input','Alumina is a feedstock in primary aluminium smelting; metal grade is a separate allocation.')
edge('E0320',s,'needle_coke_grade_unverified','Petroleum coke is an upstream anode material. The cited process does not specify needle coke as required.')
s=source('R9_SILICA_SOL','United States patent US3647709A','Production of silica gels',
 'https://patents.google.com/patent/US3647709A/en','Documents a sodium-silicate and ion-exchange route to silica sol.')
edge('E0254',s,'supported_process_option_not_universal','Sodium silicate is an input to the documented silica-sol route.')
edge('E0255',s,'ion_exchange_resin_grade_unverified','The route uses ion exchange. The submitted resin chemistry requires separate confirmation.')

s=source('R9_SHINKO_MEMORY','Shinko Electric Industries','Organic BGA substrate lineup',
 'https://www.shinko.co.jp/english/product/docs/substrate_EN.pdf',
 'Lists organic prepreg BGA substrates for memory and logic. The material grade and selected memory part remain open.')
vendor('Shinko Electric Industries',s,'SC-FBGA-SUB','Memory BGA substrate class; specified BT/ABF material and GPU application remain open')
t=source('R9_SHINKO_ARAI','Shinko Electric Industries','Memory substrate investment at Arai',
 'https://www.shinko.co.jp/english/news/docs/20220729_02_e.pdf',
 'The company identifies Arai as the site of a plastic BGA substrate capacity expansion for memory.')
SITE_UPDATES['PUBLIC_SITE:81f6b00aa0fa'] = dict(component_categories='SC-FBGA-SUB',
    source_ids='R9_SHINKO_MEMORY;R9_SHINKO_ARAI;R_OSM_GEOCODE',
    product_assignment='Company identifies Arai for memory PBGA expansion. Exact substrate grade and completed expansion volume are open.')
s=source('R9_KAISER_6061','Kaiser Aluminum','6061 sheet, coil and plate specification',
 'https://online.kaiseraluminum.com/depot/PublicProductInformation/Document/1015/Kaiser_Aluminum_6061_Sheet_Coil_and_Plate.pdf',
 'Documents a 6061 rolled stock product.')
vendor('Kaiser Aluminum',s,'SC-AL-PLATE','6061 rolled plate branch; 5052 and GPU backplate drawing are separate.')
t=source('R9_KAISER_TRENTWOOD','Kaiser Aluminum','Trentwood sheet and plate portfolio',
 'https://www.kaiseraluminum.com/end-markets/aerospace-and-high-strength/',
 'The Trentwood catalogue lists 6061 in its plate range.')
site('Kaiser Trentwood Works','Kaiser Aluminum','United States','Spokane Valley, Washington',
     'Trentwood rolled-products plant',s+';'+t,'SC-AL-PLATE')

s=source('R9_MAADEN','Ma’aden','2024 annual report: phosphate mining and processing',
 'https://axvpvthrjz64.compat.objectstorage.me-jeddah-1.oraclecloud.com/maaden-website-assets/reports/bod-reports/2024-bod-report-en.pdf',
 'Identifies Al Jalamid and Al Khabra phosphate operations and rail movement to Ras Al Khair.')
vendor("Ma'aden",s,'RAW-PHOSPHATE-ROCK','Commercial phosphate rock mining and beneficiation')
site('Maaden Al Jalamid phosphate operation',"Ma'aden",'Saudi Arabia','Hazm Al Jalamid',
     'Al Jalamid mine and beneficiation complex',s,'RAW-PHOSPHATE-ROCK')
site('Maaden Al Khabra phosphate mine',"Ma'aden",'Saudi Arabia','Turaif',
     'Al Khabra mine in the Umm Wual area; Turaif vicinity',s,'RAW-PHOSPHATE-ROCK')
site('Maaden Ras Al Khair phosphate fertilizer complex',"Ma'aden",'Saudi Arabia','Ras Al Khair',
     'Ras Al Khair industrial city',s,'')
DISCLOSED_FREIGHT.append(dict(origin='Maaden Al Jalamid phosphate operation',
    destination='Maaden Ras Al Khair phosphate fertilizer complex',mode='rail',
    commodity='Phosphate concentrate for fertilizer production',source_ids=s,
    evidence='Company-reported freight corridor', transit_time_days=None,
    gpu_procurement_established=False))
s=source('R9_PHOSAGRO','PhosAgro','2025 integrated report: apatite mining and phosphate-rock production',
 'https://ar2025.phosagro.com/en/strategic-report/strategy/',
 'Lists operating ore-base projects and 2025 phosphate rock output for Apatit.')
vendor('PhosAgro',s,'RAW-PHOSPHATE-ROCK','Phosphate rock produced by mining and beneficiation at Apatit')
for mine in ('Kirovsky','Rasvumchorrsky','Vostochny'):
    site('Apatit '+mine+' mine','PhosAgro','Russia','Kirovsk, Murmansk Oblast',
         mine+' mine, Khibiny district',s,'RAW-PHOSPHATE-ROCK',
         operating_status='reported_mining_operation;regional_coordinate_proxy')
s=source('R9_ESHIDIYA_BOUNDS','Atmospheric Environment','Study of chemical composition in wet atmospheric precipitation in Eshidiya area, Jordan',
 'https://www.sciencedirect.com/science/article/abs/pii/S1352231005005819',
 'The published abstract reports a latitude and longitude bounding box for the phosphate mine area.')
SITE_UPDATES['PUBLIC_SITE:d55392fb8565'] = dict(
    latitude=29.892778, longitude=36.21875,
    coordinate_precision='published_mining_area_bounds_midpoint_not_gate',
    geocode_display_name='Eshidiya mine area, southern Jordan',
    source_ids='R8_JPMC;'+s)

s=source('R9_ZOTAC_CARD','Zotac','RTX 5080 AMP Extreme Infinity product specification',
 'https://www.zotac.com/us/us-store/product/graphics_card/zotac-gaming-geforce-rtx-5080-amp-extreme-infinity',
 'Provides board-level display outputs, auxiliary power, lighting, PCIe interface, cooler and backplate for this configuration.')
edge('E0020 E0021 E0022 E0025 E0026 E0027',s,'supported_component_family',
 'One commercial card documents a metal backplate, PCIe interface, 12V-2x6 power input and both display-port families. The original generic graph does not establish exact part suppliers.')
edge('E0030',s,'supported_optional_design_feature',
 'The named card includes RGB lighting. Keep this as a model-dependent feature and do not infer a separate controller PCB.')
edge('E0006',s,'supported_component_family',
 'The reference 5080 card uses GDDR7. GDDR6/GDDR6X descendants in the submitted graph represent a different configuration and cannot be inherited as its recipe.')

s=source('R8_ADMAFUSE','Admatechs','ADMAFUSE spherical silica',
 'https://www.admatechs.co.jp/en/product-admafuse.html',
 'Melt-spheroidized amorphous silica filler. Product grades and customer qualification are separate.')
vendor('Admatechs',s,'LD:fused_silica_filler PM-FUSED-SILICA','Spherical fused silica filler')
s=source('R8_ADMATECHS_SITES','Admatechs','Business establishments',
 'https://www.admatechs.co.jp/en/about-estb.html','Three named factories. The directory does not assign individual filler grades.')
for name,city,address in [
    ('Toyota','Miyoshi, Aichi','1 Nishiyama, Myochi-cho'),
    ('Toki','Toki, Gifu','1431-22 Kitayama, Kujiri, Izumi-cho'),
    ('Toki Minami','Toki, Gifu','304-879 Aza-nishiyama, Oroshi-cho'),
]:
    site('Admatechs '+name,'Admatechs','Japan',city,address,s,'')

s=source('R8_JPMC','Jordan Phosphate Mines Company','2025 phosphate production by mine',
 'https://www.jpmc.com.jo/en/phosphate-production','Reports phosphate production from Al Hassa, Al Abiad and Eshidiya.')
vendor('Jordan Phosphate Mines Company',s,'RAW-PHOSPHATE-ROCK','Phosphate rock mining and beneficiation')
for mine,city in [('Al Hassa','Al Hasa'),('Al Abiad','Al Abyad'),('Eshidiya','Eshidiya')]:
    site('JPMC '+mine+' mine','Jordan Phosphate Mines Company','Jordan',city,mine+' mining area',s,'RAW-PHOSPHATE-ROCK')

s=source('R8_MOSAIC','The Mosaic Company','2025 Form 10-K, Florida phosphate properties',
 'https://s1.q4cdn.com/823038994/files/doc_downloads/2026/04/MOS-2025-12-31-10K-Updated.pdf',
 'Names South Fort Meade, Four Corners and Wingate as production-stage phosphate mining facilities.')
vendor('The Mosaic Company',s,'RAW-PHOSPHATE-ROCK','Phosphate rock mining, including Florida operations')
t=source('R8_MOSAIC_FOUR_CORNERS','The Mosaic Company','Four Corners Facility fact sheet',
 'https://mosaicfloridaphosphate.com/wp-content/uploads/2022/07/Four-Corners-Facility-Fact-Sheet-1.pdf',
 'Locates the mining and processing facility near Bradley, Florida.')
for mine,area in [('South Fort Meade','Hardee County, Florida'),('Four Corners','Bradley, Florida'),('Wingate','Manatee County, Florida')]:
    site('Mosaic '+mine,'The Mosaic Company','United States',area,mine+' phosphate property',
         s+';'+t if mine=='Four Corners' else s,'RAW-PHOSPHATE-ROCK')

s=source('R8_ISOLA_FR4','Isola','370HR laminate and prepreg technical data',
 'https://www.isola-group.com/pcb-laminates-prepreg/370hr-laminate-prepreg/',
 'Documents epoxy, E-glass fabric, and copper foil options for a commercial FR-4 system.')
vendor('Isola',s,'SC-PREPREG','Commercial FR-4 epoxy and E-glass prepreg')
edge('E0511 E0538',s,'supported_material_class_composition',
 'Woven E-glass fabric is documented for this laminate/prepreg system. Chopped strands are a separate branch.')
edge('E0567',s,'supported_material_class_composition',
 'The product uses an epoxy system. The submitted specific resin/hardener formulation remains open.')
edge('E0568',s,'foil_role_requires_feedstock_evidence',
 'Copper foil is the laminate input. A cathode-to-foil conversion and its feedstock grade require separate evidence.')
t=source('R8_ISOLA_PLANTS','Isola','US quick-turn manufacturing and plant capabilities',
 'https://www.isola-group.com/wp-content/uploads/Isola-Quick-Turnaround-Program_31523.pdf',
 'Identifies Chandler and Ridgeway as plants and describes laminate constructions.')
for city,address in [('Chandler, Arizona','6565 W Frye Road'),('Ridgeway, South Carolina','100 Tillessen Boulevard')]:
    site('Isola '+city,'Isola','United States',city,address,t,'')

s=source('R8_ABF','Ajinomoto','Ajinomoto Build-up Film technology',
 'https://www.ajinomoto.com/innovation/our_innovation/buildupfilm',
 'The supplier documents an epoxy, hardener and inorganic filler formulation used as build-up dielectric.')
edge('E0132 E0332 E0333',s,'supported_material_class_composition',
 'The ABF branch uses an epoxy-based insulating film in a substrate. The BT branch and exact resin grade are separate questions.')

s=source('R7_EPA_HCL','US Environmental Protection Agency','AP-42 section 8.6 hydrochloric acid',
 'https://www.epa.gov/sites/default/files/2020-09/documents/8.6_hydrochloric_acid.pdf',
 'Historical technical account documents several HCl production routes, including synthesis from elements; dated market percentages are not used.')
edge('E0198 E0199 E0217 E0218',s,'supported_process_option_not_universal',
 'Hydrogen/chlorine synthesis is a documented HCl route. Other industrial routes exist; anhydrous semiconductor-grade purification and actual supplier process remain unverified.')
s=source('R7_EPA_HF','US Environmental Protection Agency','AP-42 section 8.7 hydrofluoric acid',
 'https://www.epa.gov/sites/default/files/2020-09/documents/8.7_hydrofluoric_acid.pdf',
 'Acid-grade fluorspar and sulfuric acid feed a documented HF process. Ore beneficiation, purification and concentration choices intervene before electronic-grade use.')
edge('E0279 E0280',s,'supported_upstream_process_not_direct_input',
 'Selected fluorspar/sulfuric-acid route supports upstream dependency; crude ore is not a direct qualified electronic-grade feedstock.')
s=source('R7_ALUMINA','The Aluminum Association','Alumina refining and Bayer process',
 'https://www.aluminum.org/alumina-refining-101',
 'Bauxite and caustic solution undergo digestion, separation, precipitation and calcination. No high-purity abrasive grade or vendor assignment inferred.')
edge('E0252 E0253',s,'supported_upstream_process_not_direct_input',
 'Bayer-route alumina uses bauxite and caustic solution with intervening refining stages; specialty high-purity alumina may require a different route.')
s=source('R7_EPA_CHLORALKALI','US Environmental Protection Agency','AP-42 section 8.11 chlor-alkali',
 'https://www.epa.gov/sites/default/files/2020-09/documents/8.11_chlor-alkali.pdf',
 'Brine electrolysis produces chlorine, caustic soda and hydrogen. Historical equipment/market shares are not current operating assumptions.')
edge('E0194 E0195 E0196 E0197',s,'supported_upstream_process_not_direct_input',
 'Sodium-chloride brine and water feed chlor-alkali processing. Only the NaCl branch is supported, not all salts in the combined raw node; water treatment and co-production matter.')

s=source('R10_GB203','NVIDIA','GeForce RTX Blackwell GPU Architecture, Appendix B',
 'https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf',
 'Identifies the GeForce RTX 5080 GB203 die and its custom TSMC 4N fabrication process.')
vendor('TSMC',s,'LD:fabrication','Disclosed foundry and custom 4N process for the RTX 5080 GB203 die',
       qualification='reference_product_foundry_disclosed_site_unverified')
REFERENCE_SUPPLY_QUALIFICATION.append(dict(node_id='LD:fabrication',
    reference_product='GeForce RTX 5080 GB203', supplier='TSMC', role='disclosed_foundry',
    process='NVIDIA custom TSMC 4N', site_id=None, qualified_alternate_supplier_ids=[],
    alternate_status='public_evidence_does_not_identify_a_customer_qualified_alternate',
    missing_evidence=['approved process and site for the specific die', 'customer qualification', 'available capacity'],
    source_ids=s))
s=source('R10_NVIDIA_TIMING','NVIDIA','Fiscal 2026 annual report, supply and manufacturing risks',
 'https://s201.q4cdn.com/141608511/files/doc_financials/2026/ar/2026-annual-report-web-Hyperlinks.pdf',
 'Discloses some extended supply lead times exceeding 12 months at company level; no component, factory, shipment or average is identified.')
LEAD_TIME_DISCLOSURES.append(dict(company='NVIDIA', reporting_period='FY2026',
    measure='extended supply lead time in reported cases', comparison='greater_than', value=12,
    unit='months', scope='company-wide risk disclosure; selected cases',
    node_id=None, facility_id=None, use_as_node_duration=False, source_ids=s))
s=source('R10_AMKOR_GRAPHICS','Amkor Technology','Flip-chip technology for graphics processors',
 'https://ir.amkor.com/news-releases/news-release-details/amkor-announces-new-flip-chip-packaging-technology-semicon',
 'Company documents flip-chip package technology for graphics processors at product-class level.')
vendor('Amkor Technology',s,'1.2 LD:finished_logic_die',
       'Flip-chip graphics package assembly capability; specific GPU award, factory and qualification unverified')
s=source('R10_AMPHENOL_POWER','Amphenol','Minitek PCIe auxiliary power connector system',
 'https://www.amphenol-cs.com/product-series/minitek-pwr-cem-5-pcie.html',
 'Documents a GPU auxiliary power connector and cable assembly in the 12V-2x6 product class.')
vendor('Amphenol',s,'5','12V-2x6 auxiliary power connector family; GPU model allocation unverified')
edge('E0023',s,'supported_component_family','Commercial GPU auxiliary power interface includes the connector. Exact part number is design-specific.')
s=source('R10_COVESTRO_COATING','Covestro','Bayhydrol polyurethane and acrylic coating dispersions',
 'https://solutions.covestro.com/en/brands/bayhydrol',
 'Documents coating-resin classes for flexible and rigid substrates, including metal and plastics.')
vendor('Covestro',s,'PM-ACRYLIC-PU','Acrylic and polyurethane coating dispersions; ink and GPU formulation unverified')
s=source('R10_MICROMETALS','Micrometals','Core-materials catalogue',
 'https://new.micrometals.com/products/materials/core-materials-lf/',
 'Core material catalogue explicitly lists carbonyl iron formulations.')
vendor('Micrometals',s,'SC-FE-POWDER-CORE','Carbonyl iron powder core branch; Fe-Si-Cr, embedded winding and exact power inductor geometry unverified')
s=source('R10_NICHIA','Nichia','NSSM137A RGB LED product data',
 'https://led-ld.nichia.co.jp/en/product/led_product_data.html?kbn=0&type=NSSM137A',
 'Documents a finished RGB LED package, with no evidence of GPU fit or bare-die sale.')
vendor('Nichia',s,'8.1','Commercial packaged RGB LED; card-level qualification unverified')

for sid, company, title, url in [
    ('R10_NUVOTON_MCU','Nuvoton Technology','NuMicro MCU portfolio',
     'https://www.nuvoton.com/products/microcontrollers/'),
    ('R10_RENESAS_MCU','Renesas Electronics','RA Arm Cortex-M MCU portfolio',
     'https://www.renesas.com/en/products/microcontrollers-microprocessors/ra-cortex-m-mcus'),
    ('R10_ST_MCU','STMicroelectronics','STM32 mainstream MCU portfolio',
     'https://www.st.com/en/microcontrollers-microprocessors/stm32-mainstream-mcus/products.html'),
    ('R10_NXP_MCU','NXP Semiconductors','LPC microcontroller portfolio',
     'https://www.nxp.com/assets/documents/data/en/supporting-information/LPC-MCU-Portfolio-Press-Deck.pdf'),
    ('R10_MICROCHIP_MCU','Microchip Technology','SAM D21 MCU overview',
     'https://developerhelp.microchip.com/xwiki/bin/view/products/mcu-mpu/32bit-mcu/sam/samd21-mcu-overview/'),
]:
    source(sid,company,title,url,'Manufacturer documents a commercial Arm Cortex-M MCU family.')
    vendor(company,sid,'8.2.2','Packaged Cortex-M MCU product class; RGB firmware, pinout, selected part and GPU qualification remain open')

s=source('R11_TYK_SETTER','TYK Corporation','Zirconia setter tiles',
 'https://www.tyk.co.jp/en/02ProductInfoEN/product02-01/details01.html',
 'Lists zirconia setter tiles for electrical ceramic firing.')
vendor('TYK Corporation',s,'DC-SINTER-BOAT',
       'Zirconia ceramic setters; selected stabilizer grade and reuse interval require a specification')
t=source('R11_TYK_TAJIMI','TYK Corporation','Corporate profile and manufacturing locations',
 'https://www.tyk.co.jp/company/company.html','Identifies a production site in Tajimi. Setter product allocation is open.')
site('TYK Tajimi manufacturing site','TYK Corporation','Japan','Tajimi, Gifu','3-1 Obata-cho',t,'')
s=source('R11_TECHCERAMIC_YSZ','Tech Ceramic','Ceramic firing setters',
 'https://www.techceramic.com/products/kiln-furniture/setters/',
 'The supplier lists yttria-stabilized zirconia setters and cites a ceramic varistor application.')
vendor('Tech Ceramic',s,'DC-SINTER-BOAT','YSZ setter product class; exact dimensions, component application and plant unverified')
edge('E0556',s,'supported_material_class_composition',
 'Commercial yttria-stabilized zirconia setters establish this material option. Actual use and lifetime remain process-specific.')
s=source('R11_COLUMBIA_ANODIZE','Columbia Chemical / Alufinish','Anodizing and pretreatment product line',
 'https://www.columbiachemical.com/wp-content/uploads/05-2025-ColChem-Alufinish-Sell-Sheet-linecard-WEB-VERSION.pdf',
 'Lists black anodizing dye and additives for sulfuric-acid baths as separate products.')
vendor('Columbia Chemical',s,'DC-ANODIZE-CHEM',
       'Supplier of black anodizing dye and bath additives; bulk sulfuric acid and exact finishing recipe are separate')
edge('E0478',s,'supported_formulation_option',
 'Supports the sulfuric-acid bath branch. Other chemicals in the combined industrial-input node and exact dyes require separate evidence.')
s=source('R11_SIA_CYCLE','Semiconductor Industry Association','2021 response to Commerce RFI on supply chain risks',
 'https://www.semiconductors.org/wp-content/uploads/2021/11/SIA-Response-to-Commerce-RFI-on-Semiconductor-Supply-Chain-Risks.pdf',
 'Reports an industry-average wafer-fabrication cycle of about 12 weeks and 14–20 weeks for advanced processes.')
LEAD_TIME_DISCLOSURES.extend([
    dict(company='Semiconductor Industry Association', reporting_period='2021',
         measure='typical industry wafer fabrication cycle', comparison='approximately',
         value=12, unit='weeks', scope='cross-industry benchmark',
         node_id='LD:fabrication', facility_id=None, use_as_node_duration=False, source_ids=s),
    dict(company='Semiconductor Industry Association', reporting_period='2021',
         measure='advanced wafer fabrication cycle', comparison='range', value=None,
         lower_bound=14, upper_bound=20, unit='weeks', scope='industry-reported advanced-process benchmark',
         node_id='LD:fabrication', facility_id=None, use_as_node_duration=False, source_ids=s),
])
s=source('R11_ASML_CYCLE','ASML','2022 Form 20-F, lithography process',
 'https://www.sec.gov/Archives/edgar/data/937966/000093796623000014/asml-20221231.htm',
 'Describes a general manufacturing span of 18–26 weeks from start to a tested, packaged chip ready to ship.')
LEAD_TIME_DISCLOSURES.append(dict(company='ASML', reporting_period='2022',
    measure='manufacturing to packaged and tested device', comparison='range', value=None,
    lower_bound=18, upper_bound=26, unit='weeks', scope='industry benchmark including packaging and testing',
    node_id=None, facility_id=None, use_as_node_duration=False, source_ids=s))

for source_id, supplier, title, url, scope in [
    ('R11_MICRON_GDDR7','Micron','GDDR7 product portfolio',
     'https://www.micron.com/products/memory/graphics-memory/gddr7',
     'GDDR7 product family. Current part-number lifecycle and orderability require catalogue checks.'),
    ('R11_SK_GDDR7','SK hynix','Graphics DRAM product portfolio',
     'https://product.skhynix.com/products/dram/gddr.go',
     'GDDR7 product family, including published 16 Gb capability.'),
    ('R11_SAMSUNG_GDDR7','Samsung Electronics','GDDR7 product portfolio',
     'https://semiconductor.samsung.com/dram/gddr/gddr7/',
     'GDDR7 product family, including published 16 Gb capability.'),
]:
    source(source_id,supplier,title,url,scope)
    REFERENCE_SUPPLY_QUALIFICATION.append(dict(node_id='1.3',
        reference_product='GeForce RTX 5080-class board', supplier=supplier, role='catalogue_candidate',
        memory_generation='GDDR7', site_id=None, qualified_alternate_supplier_ids=[],
        alternate_status='part_number_and_customer_approval_not_established',
        missing_evidence=['approved part number and speed bin', 'board qualification', 'available capacity'],
        source_ids=source_id+';R9_ZOTAC_CARD'))

for source_id, supplier, title, url, node_id in [
    ('R11_EVERLIGHT_RGB','Everlight Electronics','19-337 full-colour SMD LED',
     'https://en.everlight.com/visible_led/category-smd_led/surface_mount_chip_led_pcb__top_view_full_color__19_337/', '8.1'),
    ('R11_TI_MCU','Texas Instruments','Arm Cortex-M0+ microcontroller portfolio',
     'https://www.ti.com/en-us/design-development/embedded-development/arm-cortex-m0-mcus', '8.2.2'),
    ('R11_INFINEON_MCU','Infineon Technologies','PSoC 4 Cortex-M microcontrollers',
     'https://www.infineon.com/products/microcontroller/32-bit-psoc-arm-cortex/psoc-4-mcu', '8.2.2'),
]:
    source(source_id,supplier,title,url,'Manufacturer catalogue for a packaged part family.')
    vendor(supplier,source_id,node_id,'Packaged device capability; specific card, part selection and approved substitution are open.')
