"""Curated observations from public sources reviewed on 2026-11-24.

Node IDs are explicit. No supplier is inferred from a parent category. A mapping
to a combined node documents only the named product in `product_scope`.
"""

REVIEW_DATE = '2026-11-24'
SOURCES = []
VENDORS = []
SITES = []
EDGE_EVIDENCE = []


def source(sid, organization, title, url, observation):
    SOURCES.append(dict(source_id=sid, organization=organization, title=title,
        url=url, use=observation, reliability='Official company product or operations evidence; no independent market rank implied',
        reviewed_on=REVIEW_DATE))
    return sid


def vendor(name, sid, nodes, product_scope, qualification='grade_and_customer_qualification_unverified'):
    for node in nodes.split():
        VENDORS.append(dict(provider_name=name, source_ids=sid, node_id=node,
            product_scope=product_scope, qualification=qualification))


def site(name, company, country, city, address, sid, node_ids, operating_status='publicly_listed_production_site'):
    SITES.append(dict(facility_name=name, company=company, country=country,
        city=city, address=address, source_ids=sid, node_ids=node_ids,
        operating_status=operating_status))


def edge(ids, sid, status, note):
    for eid in ids.split():
        EDGE_EVIDENCE.append(dict(edge_id=eid, source_ids=sid, validation_status=status,
            evidence_scope='manually_scoped_public_evidence', audit_note=note))

source('R_OSM_GEOCODE','OpenStreetMap contributors / Nominatim','Public geocoding service',
 'https://nominatim.org/release-docs/latest/api/Search/',
 'City/district coordinates used as approximate factory-location proxies; public company sources establish the site, not OSM.')
SOURCES[-1]['reliability'] = 'Community-maintained geospatial data; approximate location screening only'

source('R_WPI_MIRROR','ArcGIS hosted World Port Index mirror','Port-coordinate download endpoint',
 'https://services-eu1.arcgis.com/BuS9rtTsYEV5C0xh/ArcGIS/rest/services/World_Port_Index/FeatureServer/0',
 'Actual endpoint used for the cached port records. Mirror revision and completeness have not been independently reconciled with the current NGA release.')
SOURCES[-1]['reliability'] = 'Third-party mirror of government-origin data; version and cargo suitability unverified'


sid = source('R_LINDE_GASES', 'Linde', 'Electronics specialty gases',
 'https://www.linde-gas.com/products-and-services/gases/specialty-gases-for-electronics',
 'Lists specific deposition, etching and doping gases and supply-container modes; availability varies by location.')
vendor('Linde', sid, 'LD:nitrogen LD:helium LD:carbon_dioxide LD:tungsten_hexafluoride LD:ammonia LD:chlorine LD:neon LD:hydrogen LD:argon LD:nitrogen_trifluoride LD:hydrogen_chloride LD:silane LD:nitrous_oxide LD:krypton LD:oxygen_gas LD:fluorine_gas LD:trichlorosilane LD:boron_dopant_precursors LD:phosphine_gas LD:arsine_gas LD:anhydrous_hcl',
 'Specific gas named in manufacturer electronics catalog; BCl3 and diborane are alternatives within boron-precursor node.')
edge('E0064 E0065 E0066 E0067 E0068 E0069 E0070 E0071 E0072 E0073 E0074 E0075 E0076 E0077 E0225 E0226 E0227',sid,
 'supported_category_membership','Catalog names the gas and semiconductor use. This establishes category membership, not a compulsory ingredient in every GPU process.')

sid = source('R_KANTO_CHEM', 'Kanto Chemical', 'Ultra pure chemicals catalog',
 'https://www.kanto.co.jp/english/products/denshi/ultra_pure_chemicals.html',
 'Lists named solvents, acids and alkalis with individual SDS links.')
vendor('Kanto Chemical',sid,'LD:sulfuric_acid LD:ammonium_hydroxide LD:nitric_acid LD:acetic_acid LD:isopropyl_alcohol LD:phosphoric_acid LD:hydrofluoric_acid LD:sodium_hydroxide LD:potassium_hydroxide LD:hydrogen_peroxide LD:methanol LD:pgmea_casting_solvent',
 'Named ultra-pure chemical; PGMEA evidence supports PGMEA branch only, not ethyl lactate.')
edge('E0094 E0095 E0096 E0097 E0098 E0099 E0100 E0169 E0170 E0171 E0172',sid,
 'supported_category_membership','Official electronic-chemical catalog supports the named acid/alkali or solvent category.')

sid = source('R_SOLVAY_WET', 'Solvay', 'Electronic wet chemicals',
 'https://www.solvay.com/en/chemical-categories/fluorine-chemicals/electronic-wet-chemicals',
 'High-purity HF and hydrogen peroxide; manufacturing countries are identified but not every plant.')
vendor('Solvay',sid,'LD:hydrofluoric_acid LD:hydrogen_peroxide','Electronic-grade hydrofluoric acid and hydrogen peroxide')

sid = source('R_TOKUYAMA_IPA','Tokuyama','High purity IPA SE',
 'https://www.tokuyama.co.jp/eng/products/electronic_materials/ipa_se.html',
 'Names electronic-grade IPA and describes manufacture from propylene and water.')
vendor('Tokuyama',sid,'LD:isopropyl_alcohol','Electronic-grade isopropyl alcohol')

sid = source('R_TOKUYAMA_BUSINESS','Tokuyama','Business products',
 'https://www.tokuyama.co.jp/eng/company/business.html',
 'Names high-purity polycrystalline silicon and high-purity trichlorosilane for semiconductor wafers.')
vendor('Tokuyama',sid,'LD:trichlorosilane','High-purity trichlorosilane; polysilicon listing does not establish sale of slim starter rods')

sid = source('R_EVO_PEROXIDE_SITES','Evonik','Active Oxygens global production sites',
 'https://active-oxygens.evonik.com/en/about-active-oxygens/global-presence',
 'Separately labels production plants, business offices and distribution locations for hydrogen peroxide and peracetic acid.')
vendor('Evonik',sid,'LD:hydrogen_peroxide','Hydrogen peroxide producer; electronic-grade availability must be checked per site')
for name,country,city,address in [
 ('Bayport','United States','Pasadena, Texas','12000 Bay Area Blvd, Pasadena, TX 77507'),
 ('Saratoga Springs','United States','Saratoga Springs, New York','24 Freedom Way, Saratoga Springs, NY 12866'),
 ('Mobile','United States','Mobile, Alabama','4201 Degussa Road, Mobile, AL 36582'),
 ('Gibbons','Canada','Gibbons, Alberta','Highway 643 East, Gibbons, AB T0A 1N0'),
 ('Maitland','Canada','Maitland, Ontario','1380 County Road 2, Maitland, ON K0E 1P0'),
 ('Aracruz','Brazil','Aracruz','Av. Luiz Cariacica dos Santos 910, Barra do Riacho, Aracruz'),
 ('Rheinfelden','Germany','Rheinfelden','Untere Kanalstrasse 3, 79602 Rheinfelden'),
 ('Weissenstein','Austria','Weissenstein','Industriestrasse 1, 9721 Weissenstein'),
 ('Delfzijl','Netherlands','Delfzijl','Oosterhorn 14, 9930 AD Delfzijl'),
 ('Antwerp','Belgium','Antwerp','Tijsmanstunnel West, 2040 Antwerp'),
 ('La Zaida','Spain','La Zaida','C/Afueras s/n, 50784 La Zaida, Zaragoza'),
 ('Umbogintwini','South Africa','Umbogintwini','Ukhozi Road, Umbogintwini Industrial Complex, 4120'),
 ('Jilin','China','Jilin City','117 Hangjiang Road, Longtan District, Jilin City 132021'),
 ('Ulsan JV','South Korea','Ulsan','482-3 Ssangge-dong, Nam-gu, Ulsan'),
 ('Cikarang','Indonesia','Cikarang','Jl. Jababeka V No. 5, Cikarang Utara, Bekasi'),
 ('Morrinsville','New Zealand','Morrinsville','276 Walton Road, Morrinsville'),
 ('Saraburi JV','Thailand','Kaeng Khoi, Saraburi','82 Moo 5, Sudbandat Road, Tarndiew, Kaengkhoi, Saraburi')]:
    site('Evonik '+name+' peroxide plant','Evonik',country,city,address,sid,'LD:hydrogen_peroxide')

sid = source('R_OLIN_CHEM','Olin','Chlor Alkali Products and Vinyls ISO scope',
 'https://www.olin.com/wp-content/uploads/Olin-North-America-CAPV-Certificate.pdf',
 'Manufacturing certification scope names chlorine, caustic soda, potassium hydroxide, hydrochloric acid and sulfuric acid.')
vendor('Olin',sid,'LD:chlorine LD:sodium_hydroxide LD:potassium_hydroxide','Industrial chemical manufacture; electronic purity is unconfirmed')

sid = source('R_INOVYN','INEOS Inovyn','Organic chlorine derivatives',
 'https://www.inovyn.com/products/organic-chlorine-derivatives/',
 'Manufacturer lists epichlorohydrin and describes its use in epoxy resins.')
vendor('INEOS Inovyn',sid,'LD:epichlorohydrin','Epichlorohydrin')
edge('E0142',sid,'supported_process_input','Manufacturer identifies epichlorohydrin as an epoxy-resin building block. Other reactants and purification remain outside this edge.')

sid = source('R_LYB_CHANNELVIEW','LyondellBasell','Channelview North production',
 'https://www.lyondellbasell.com/en/locations/north-america/united-states/channelview-complex/channelview-north/',
 'Plant manufactures ethylene, propylene, butadiene and benzene.')
vendor('LyondellBasell',sid,'LD:ethylene LD:propylene LD:benzene_aromatics','Named petrochemical products; benzene branch of combined BTX node')
site('LyondellBasell Channelview North','LyondellBasell','United States','Channelview, Texas','8280 Sheldon Road, Channelview, TX 77530',sid,'LD:ethylene LD:propylene LD:benzene_aromatics')

sid = source('R_METHANEX','Methanex','October 2026 investor presentation',
 'https://www.methanex.com/wp-content/uploads/MEOH-Investor-Presentation-October-2026.pdf',
 'Lists methanol production locations separately from offices and terminals; operating status requires plant-level review.')
vendor('Methanex',sid,'LD:methanol','Methanol; high-purity semiconductor grade is unconfirmed')
for name,country,city in [('Geismar','United States','Geismar, Louisiana'),('Beaumont','United States','Beaumont, Texas'),('Punta Arenas','Chile','Punta Arenas'),('Damietta','Egypt','Damietta'),('New Plymouth','New Zealand','New Plymouth')]:
    site('Methanex '+name,'Methanex',country,city,city,sid,'LD:methanol','production_location_listed_operating_units_need_review')

sid = source('R_CELANESE_POLYMERS','Celanese','AI data-center materials',
 'https://www.celanese.com/applications/ai-data-centers',
 'Product portfolio includes LCP, PBT and high-temperature nylons for electronics.')
vendor('Celanese',sid,'PM-LCP-POLYMER PM-PBT-POLYMER PM-PPA-POLYMER','LCP, PBT and PPA resin; exact glass fill and flame rating need a grade datasheet')

sid = source('R_COVESTRO_BAYBLEND','Covestro','Bayblend PC/ABS grades',
 'https://www.covestro.com/en/brands/bayblend',
 'Lists flame-retardant PC/ABS blends with product-level properties.')
vendor('Covestro',sid,'PM-PC-ABS-POLYMER SC-PC-ABS','Flame-retardant PC/ABS blend; molding supplier remains separate')
edge('E0679',sid,'candidate_design_option','PC/ABS exists as an electronics housing material; this does not establish the shroud material of the reference card.')

sid = source('R_SHINETSU_TIM','Shin-Etsu Chemical','Silicone thermal interface materials',
 'https://www.shinetsusilicone-global.com/products/function/heat/index.shtml',
 'Thermal-interface sheets and silicone compounds use thermally conductive fillers, including alumina.')
vendor('Shin-Etsu Chemical',sid,'2.5 PM-PDMS-SILICONE SC-SILICONE-MATRIX','Silicone thermal-interface products; silicone branch, no exact formulation claim')
edge('E0674 E0708',sid,'candidate_design_option','Supports silicone matrix and conductive filler in thermal-interface products; the precise pad recipe is product dependent.')

sid = source('R_DENKA_MATERIALS','Denka','Electronics and innovative products',
 'https://www.denka.co.jp/eng/electronics/',
 'Names fused silica, spherical alumina and boron nitride powder products.')
vendor('Denka',sid,'PM-HBN PM-ALUMINA PM-FUSED-SILICA LD:fused_silica_filler LD:alumina SC-CERAMIC-FILLER',
 'Fused silica, alumina and boron nitride powders; thermal filler branch only')

sid = source('R_SAKAI_BT','Sakai Chemical Industry','Electronic materials',
 'https://www.sakai-chem.co.jp/en/products_services_electronic_materials.php',
 'Names barium titanate dielectric powder for multilayer ceramic capacitors.')
vendor('Sakai Chemical Industry',sid,'PM-BATIO3','Barium titanate dielectric powder')
edge('E0594',sid,'supported_process_input','Barium titanate is a documented MLCC dielectric; this does not require every MLCC to use the same formulation.')

sid = source('R_HERAEUS_WIRE','Heraeus Electronics','Fine bonding wires',
 'https://www.heraeus-electronics.com/en/products-and-solutions/bonding-wires/fine-bonding-wires/',
 'Lists gold, silver, copper and aluminum bonding-wire types.')
vendor('Heraeus Electronics',sid,'SC-BOND-WIRE LD:fine_metal_wire LD:bond_wires','Fine bonding wires; alternatives are separate wire products')
edge('E0120 E0122 E0124',sid,'supported_product_class','Bonding wires may be made from copper or aluminum; alternatives must use OR logic.')

sid = source('R_TANAKA_WIRE','TANAKA','Bonding wires',
 'https://tanaka-preciousmetals.com/en/products/bonding_wires/',
 'Lists gold, silver, copper and palladium-coated copper fine wires plus aluminum power bonding wire.')
vendor('TANAKA',sid,'SC-BOND-WIRE LD:fine_metal_wire LD:bond_wires','Gold, silver, copper, palladium-coated copper and aluminum bonding-wire alternatives')

sid = source('R_HERAEUS_RESISTOR','Heraeus Electronics','Thick-film resistor pastes',
 'https://www.heraeus-electronics.com/en/products-and-solutions/thick-film-materials/resistor-pastes/',
 'Official manufacturer product family for thick-film resistor pastes; exact RuO2 formulation requires product evidence.')
vendor('Heraeus Electronics',sid,'PM-RUO2-PASTE','Thick-film resistor paste; RuO2 composition is a candidate pending exact grade evidence')

sid = source('R_JX_TARGETS','JX Advanced Metals','Semiconductor sputtering targets',
 'https://www.jx-nmm.com/english/products/sputtering/semiconductor_st/',
 'Describes high-purity semiconductor sputtering targets and integrated target manufacture.')
vendor('JX Advanced Metals',sid,'LD:sputtering_targets','Semiconductor sputtering targets; exact element and purity depend on product')
edge('E0102',sid,'supported_category_membership','Official product evidence establishes sputtering targets as semiconductor deposition materials.')

sid = source('R_JX_TARGET_METALS','JX Advanced Metals','Sputtering target recycling capacity',
 'https://www.jx-nmm.com/english/newsrelease/fy2026/20261028_02.html',
 'Names copper and tantalum semiconductor sputtering targets.')
vendor('JX Advanced Metals',sid,'LD:copper LD:tantalum','High-purity target material branch, not generic commodity-grade metal')
edge('E0103 E0106',sid,'supported_process_input','Copper and tantalum are named semiconductor target materials; usage depends on device process.')

sid = source('R_ENTEGRIS_GASES','Entegris','Specialty gases catalog',
 'https://www.entegris.com/shop/en/USD/Products/Specialty-Gases/Gases/c/Gases',
 'Catalog names arsine and phosphine gases for semiconductor implantation.')
vendor('Entegris',sid,'LD:arsine_gas LD:phosphine_gas','Arsine and phosphine; site of synthesis is not established by the catalog')

sid = source('R_QNITY_PADS','Qnity Electronics','IC1000 CMP polishing pads',
 'https://www.qnityelectronics.com/products/ic-1000-cmp-pad.html/1000',
 'Current supplier page for IC1000 polishing pads with copper, tungsten and oxide applications.')
vendor('Qnity Electronics',sid,'LD:polishing_pads','IC1000 polishing pads; current supplier naming supersedes older DuPont product pages')

sid = source('R_JSR_RESIST_RECIPE','JSR','Manufacturing processes of major products',
 'https://www.jsr.co.jp/jsr_e/company/assets/pdf/Web%E7%94%A82020%E5%B7%A5%E5%A0%B4%E6%A1%88%E5%86%85_E.pdf',
 'Describes adding polymers, photoacid generators, solvents and additives to semiconductor photoresist.')
edge('E0281 E0282 E0283',sid,'supported_product_class','Manufacturer documents polymer, PAG and solvent inputs to photoresist. Specific polymer and solvent grades vary.')

sid = source('R_PQ_SILICATE','PQ Corporation','Silicates and specialty silica products',
 'https://www.pqcorp.com/products/',
 'Describes furnace sodium-silicate manufacture from silica sand and soda ash, and hydrothermal manufacture from silica and sodium hydroxide.')
vendor('PQ Corporation',sid,'LD:sodium_silicate','Sodium silicate; electronics qualification is unconfirmed')
edge('E0256 E0257',sid,'supported_process_input','Documents silica sand and soda ash in one sodium-silicate production route; a separate hydrothermal route also exists.')

sid = source('R_LANXESS_RESINS','LANXESS','Lewatit storage technical guide',
 'https://lanxess.com/-/media/project/lanxess/corporate-internet/products-and-solutions/brands/lewatit/service-center-product-literature/brochure_technical_guideline_storage-of-lewatit-resins_en_2024.pdf',
 'Specifies styrenic resins made using divinylbenzene crosslinking.')
vendor('LANXESS',sid,'LD:ion_exchange_resins','Styrene-divinylbenzene ion-exchange resins; ultrapure-water qualification varies by grade')

sid = source('R_BASF_CIP','BASF','Carbonyl iron powder',
 'https://electronics-electric.basf.com/global/en/electronics/products/carbonyl_iron_powder',
 'BASF identifies itself as inventor and leading producer of carbonyl iron powder.')
vendor('BASF',sid,'PM-FE-POWDER','Carbonyl-iron powder branch; does not establish Fe-Si-Cr alloy powder supply')

sid = source('R_SUMIBE_SITES','Sumitomo Bakelite','Suzhou and Singapore encapsulation materials',
 'https://www.sumibe.co.jp/english/topics/2026/it-materials/1007_01/index.html',
 'Existing sites make epoxy molding compounds and die bonding paste; announced added lines begin in later years.')
vendor('Sumitomo Bakelite',sid,'SC-EMC LD:encapsulation_resins LD:die_attach_materials','Semiconductor epoxy molding compounds and die-bonding paste')
site('Sumitomo Bakelite Suzhou plant','Sumitomo Bakelite','China','Suzhou, Jiangsu','Suzhou, Jiangsu, China',sid,'SC-EMC LD:encapsulation_resins LD:die_attach_materials')
site('Sumitomo Bakelite Singapore plant','Sumitomo Bakelite','Singapore','Singapore','Senoko South Road, Singapore',sid,'SC-EMC LD:encapsulation_resins LD:die_attach_materials')

sid = source('R_HENKEL_DIE_ATTACH','Henkel','LOCTITE ABLESTIK CDF 500',
 'https://next.henkel-adhesives.com/us/en/products/industrial-adhesives/central-pdp.html/loctite-ablestik-cdf-500/105233IB.html',
 'Manufacturer specifies silver-filled conductive die-attach paste for integrated circuits.')
vendor('Henkel',sid,'SC-DIE-ATTACH LD:die_attach_materials','Silver-filled conductive die-attach adhesive; epoxy chemistry needs grade-specific evidence')

sid = source('R_INDIUM_SAC','Indium Corporation','SAC305 jetting solder paste',
 'https://www.indium.com/press-releases/indium-corporation-announces-new-jetting-solder-paste/',
 'Official manufacturer names SAC305 solder paste for electronics.')
vendor('Indium Corporation',sid,'SC-SOLDER-PASTE','SAC305 solder paste; flux chemistry varies by grade')
sid2 = source('R_INDIUM_SAC_COMPOSITION','Indium Corporation','SAC305 alloy composition',
 'https://www.indium.com/blog/questions-for-tim-jensen/',
 'States SAC305 composition as 96.5% tin, 3% silver and 0.5% copper.')
edge('E0608 E0609 E0610 E0611 E0612 E0613',sid2,'supported_alloy_composition','SAC305 contains Sn, Ag and Cu. Refinery and plating-salt choices require separate evidence.')

sid = source('R_MACDERMID_FINISH','MacDermid Alpha','IC substrate final finishes',
 'https://www.macdermidalpha.com/products/circuitry-solutions/ic-substrates/final-finishes',
 'Lists ENIG, ENEPIG and other substrate finishes as alternative processes.')
vendor('MacDermid Alpha',sid,'DC-ENIG-CHEM LD:copper_foil_enig','ENIG chemistry branch only; no copper-foil producer claim')
edge('E0630 E0656 E0662',sid,'candidate_process_option','ENIG is a documented surface-finish option; other PCB finishes also exist.')

sid = source('R_CREE_RGB','Cree LED','UHD1110-FKA RGB LED datasheet',
 'https://downloads.cree-led.com/files/ds/h/HB-UHD1110-FKA.pdf',
 'Documents a three-color RGB SMD LED and its separate red, green and blue channels.')
vendor('Cree LED',sid,'8.1','RGB SMD LED; actual graphics-card supplier is unconfirmed')
edge('E0754',sid,'optional_or_design_dependent','The reference RGB product has separate color channels. YAG phosphor must not be imposed as a universal requirement for all RGB LEDs.')

sid = source('R_HOYA_BLANKS','HOYA','2025 information technology operations',
 'https://www.hoya.com/ir/2025/en/review/it.html',
 'Describes semiconductor mask blanks and distinct DUV/EUV product markets.')
edge('E0101',sid,'technology_specific_review_required','Soda-lime glass cannot be assumed for the leading-edge GPU mask process. Specify DUV quartz or EUV low-expansion multilayer blank using a process-matched reference.')

sid = source('R_LUCAS_BRAZE','Lucas-Milhaupt','SIL-FOS 18 brazing alloy',
 'https://www.lucasmilhaupt.com/EN/Products/SIL-FOS-18.htm',
 'Names a silver-copper-phosphorus braze with an explicit composition.')
vendor('Lucas-Milhaupt',sid,'SC-AG-BRAZE','Silver-copper-phosphorus braze branch; BAg and BCuP are distinct alloy families')

# Raw materials: candidate producers are established by an operating source.
sid = source('R_RIO_BORON','Rio Tinto','California borates operations',
 'https://www.riotinto.com/en/operations/us/california-operations',
 'Describes mining and refining borates at Boron, California.')
vendor('Rio Tinto',sid,'RAW-BORATE','Borate mining and refining')
site('Rio Tinto Boron mine and refinery','Rio Tinto','United States','Boron, California','Boron, California, USA',sid,'RAW-BORATE')

sid = source('R_BHP_COPPER','BHP','Copper products and assets',
 'https://www.bhp.com/what-we-do/products/copper',
 'Names Escondida, Olympic Dam, Carrapateena and Prominent Hill copper assets.')
vendor('BHP',sid,'RAW-COPPER-ORE','Copper-bearing ore production')
site('BHP Escondida mine','BHP','Chile','Escondida, Antofagasta','Escondida mine, Antofagasta, Chile',sid,'RAW-COPPER-ORE')
sid2 = source('R_BHP_OLYMPIC','BHP','Olympic Dam integrated mine and refinery',
 'https://www.bhp.com/what-we-do/global-locations/australia/south-australia/south-australia-olympic-dam',
 'Integrated copper mine, processing, smelter and refinery with gold and silver coproducts.')
vendor('BHP',sid2,'PM-REFINED-CU LD:refined_copper RAW-GOLD-ORE RAW-SILVER-ORE','Copper cathode and gold/silver-bearing ore; plating salts are not covered')
site('BHP Olympic Dam mine and refinery','BHP','Australia','Olympic Dam, South Australia','Olympic Dam, South Australia',sid2,'RAW-COPPER-ORE PM-REFINED-CU LD:refined_copper RAW-GOLD-ORE RAW-SILVER-ORE')

sid = source('R_ALCOA_WA','Alcoa','Australian integrated bauxite and alumina operations',
 'https://aacomaua.apps.alcoa.com/australia/en/',
 'Describes two operating WA bauxite mines, two alumina refineries and Portland aluminum smelting; closed sites are separate.')
vendor('Alcoa',sid,'RAW-BAUXITE PM-REFINED-AL','Bauxite and primary aluminum; electronic-grade alumina is not established')
sid2 = source('R_ALCOA_CHAIN','Alcoa','Environmental assessments: mine-to-refinery chain',
 'https://aacomaua.apps.alcoa.com/australia/en/sustainability/environmental-assessments',
 'Huntly and Willowdale supply bauxite to Pinjarra and Wagerup alumina refineries.')
for name,city,node in [('Huntly bauxite mine','Dwellingup, Western Australia','RAW-BAUXITE'),('Willowdale bauxite mine','Waroona, Western Australia','RAW-BAUXITE'),('Pinjarra alumina refinery','Pinjarra, Western Australia','RAW-BAUXITE'),('Wagerup alumina refinery','Wagerup, Western Australia','RAW-BAUXITE')]:
    site('Alcoa '+name,'Alcoa','Australia',city,city,sid2,node if 'mine' in name else '')

sid = source('R_SIBELCO_QUARTZ','Sibelco','Spruce Pine production sites',
 'https://www.sibelco.com/en/locations/spruce-pine',
 'Lists high-purity quartz production and mining/separation locations in Spruce Pine.')
vendor('Sibelco',sid,'RAW-PEGMATITE-QUARTZ RAW-QUARTZ','High-purity quartz; raw node categories overlap and should not be double-counted')
site('Sibelco Crystal quartz plant','Sibelco','United States','Spruce Pine, North Carolina','136 Crystal Drive, Spruce Pine, NC 28777',sid,'RAW-PEGMATITE-QUARTZ RAW-QUARTZ')
site('Sibelco Quartz mining and separation','Sibelco','United States','Spruce Pine, North Carolina','7638 South Highway 226, Spruce Pine, NC 28777',sid,'RAW-PEGMATITE-QUARTZ RAW-QUARTZ')

sid = source('R_SYRAH_BALAMA','Syrah Resources','Balama graphite operation',
 'https://www.syrahresources.com.au/our-business/balama-graphite-operation',
 'Identifies the Balama natural graphite operation in Mozambique; current operating interruptions require status checks.')
vendor('Syrah Resources',sid,'RAW-NATURAL-GRAPHITE','Natural graphite; site existence does not imply uninterrupted production')
site('Syrah Balama graphite operation','Syrah Resources','Mozambique','Balama, Cabo Delgado','Balama graphite operation, Mozambique',sid,'RAW-NATURAL-GRAPHITE','production_asset_current_availability_requires_review')

sid = source('R_MP_MOUNTAIN','MP Materials','Mountain Pass operations',
 'https://mpmaterials.com/mountain-pass/',
 'Describes rare-earth mining and processing at Mountain Pass, California.')
vendor('MP Materials',sid,'RAW-RARE-EARTH-ORE','Rare-earth ore and concentrate; does not establish every element in the aggregated node')
site('MP Materials Mountain Pass mine and processing','MP Materials','United States','Mountain Pass, California','Mountain Pass, California',sid,'RAW-RARE-EARTH-ORE')

sid = source('R_ILUKA_WA','Iluka Resources','Western Australia production operations',
 'https://www.iluka.com/operations-resource-development/operations/western-australia',
 'Cataby mineral-sands mine and Narngulu separation plant produce zircon and titanium mineral products.')
vendor('Iluka Resources',sid,'RAW-ZIRCON RAW-ILMENITE','Zircon and titanium mineral feedstocks')
site('Iluka Cataby mine','Iluka Resources','Australia','Cataby, Western Australia','Cataby, Western Australia',sid,'RAW-ZIRCON RAW-ILMENITE')
site('Iluka Narngulu mineral separation plant','Iluka Resources','Australia','Narngulu, Western Australia','Narngulu, Western Australia',sid,'RAW-ZIRCON RAW-ILMENITE')

sid = source('R_GLEN_COBALT','Glencore','Cobalt production operations',
 'https://www.glencore.com/what-we-do/metals-and-minerals/cobalt',
 'Documents cobalt extraction and processing as a copper or nickel coproduct.')
vendor('Glencore',sid,'RAW-COBALT-ORE','Cobalt-bearing ores; exact cobaltite/heterogenite composition depends on mine')
sid = source('R_GLEN_NICKEL','Glencore','Nickel operations',
 'https://www.glencore.com/what-we-do/metals-and-minerals/nickel',
 'Documents nickel production regions and copper/cobalt/PGM coproducts.')
vendor('Glencore',sid,'RAW-NICKEL-ORE PM-REFINED-NI','Nickel ore/refining capability; nickel sulfate branch unconfirmed')

sid = source('R_VALE_CANADA','Vale','Canadian base metals production',
 'https://vale.com/in/canada/-/categories',
 'Documents nickel and copper production and refining in Canadian operations.')
vendor('Vale',sid,'RAW-NICKEL-ORE PM-REFINED-NI','Nickel mining and refining; electronic powder purity unconfirmed')
site('Vale Port Colborne refinery','Vale','Canada','Port Colborne, Ontario','Port Colborne, Ontario',sid,'PM-REFINED-NI')

sid = source('R_MOSAIC','Mosaic','North America mining and production',
 'https://mosaicco.com/North-America-Business',
 'Documents phosphate mining in Florida and potash mining in Saskatchewan and New Mexico.')
vendor('Mosaic',sid,'RAW-PHOSPHATE-ROCK RAW-POTASH-SYLVITE','Phosphate and potash mineral producer; not semiconductor-grade downstream chemicals')

sid = source('R_ALMONTY_SANGDONG','Almonty Industries','Sangdong commercial operating certification',
 'https://almonty.com/almontys-sangdong-processing-plant-receives-final-operational-certification/',
 'Names Sangdong mine and processing facilities in Yeongwol, South Korea, authorized for commercial operation.')
vendor('Almonty Industries',sid,'RAW-TUNGSTEN-ORE','Tungsten ore and concentrate; high-purity metal powder needs a downstream supplier')
site('Almonty Sangdong mine and processing plant','Almonty Industries','South Korea','Sangdong, Yeongwol','Sangdong, Yeongwol, Gangwon, South Korea',sid,'RAW-TUNGSTEN-ORE')

sid = source('R_SISECAM_SODA','Sisecam','US natural soda ash operation',
 'https://www.sisecam.com/en/press-releases/sisecams-us-move-to-bring-global-leadership',
 'Identifies the Wyoming natural soda ash facility.')
vendor('Sisecam',sid,'RAW-TRONA-SODA-ASH LD:soda_ash','Trona-derived soda ash; exact mine location requires separate site evidence')

sid = source('R_ICL_BROMINE','ICL','Bromine production at the Dead Sea',
 'https://www.icl-group.com/blog/what-is-bromine-where-it-is-produced-and-used/',
 'Describes Dead Sea brine extraction and bromine production after salt precipitation.')
vendor('ICL',sid,'RAW-HALITE-BRINE','Brine resource branch only; node also contains NaCl and KCl alternatives')
sid = source('R_ICL_SITES','ICL','2024 water-management production-site register',
 'https://www.icl-group.com/wp-content/uploads/2025/06/1750668672_Water_Management_2024N.pdf',
 'Lists Sodom bromine and magnesium manufacturing plants, separately from offices.')
vendor('ICL',sid,'LD:magnesium_metal RAW-DOLOMITE-MAGNESITE','Dead Sea magnesium branch; other raw feedstocks are alternatives')
site('ICL Dead Sea Bromine plant','ICL','Israel','Sodom','Sodom, Israel',sid,'RAW-HALITE-BRINE')
site('ICL Dead Sea Magnesium plant','ICL','Israel','Sodom','Sodom, Israel',sid,'LD:magnesium_metal')

sid = source('R_CARMEUSE','Carmeuse','Production operations and products',
 'https://www.carmeuse.com/na-en/products-map',
 'Lists limestone/dolomitic products and named plant addresses.')
vendor('Carmeuse',sid,'RAW-LIMESTONE RAW-DOLOMITE-MAGNESITE','Limestone/dolomite branch; no magnesium-metal claim')
site('Carmeuse Annville operation','Carmeuse','United States','Annville, Pennsylvania','3 Clear Spring Road, Annville, PA 17003',sid,'RAW-LIMESTONE')

sid = source('R_MINSUR_CHAIN','Minsur','Responsible minerals due-diligence report',
 'https://www.minsur.com/wp-content/uploads/2022/09/MINSUR_RMAP-DUE-DILIGENCE-2022_compressed-1.pdf',
 'Names San Rafael tin mine and Pisco smelting/refining, and their reported concentrate flow.')
vendor('Minsur',sid,'RAW-TIN-ORE PM-REFINED-SN','Tin concentrate and refined tin; stannous sulfate is not established')
site('Minsur San Rafael mine','Minsur','Peru','Antauta, Puno','San Rafael mine, Antauta, Puno',sid,'RAW-TIN-ORE')
site('Minsur Pisco smelter and refinery','Minsur','Peru','Pisco','Pisco, Peru',sid,'PM-REFINED-SN')

sid = source('R_AMG_TANTALUM','AMG','Mibra tantalum supply partnership',
 'https://amg-nv.com/investors/press-release/amg-advanced-metallurgical-group-n-v-announces-tantalum-strategic-partnership-with-nippon-mining-metals-corporation/',
 'Identifies tantalum concentrate from Mibra mine in Minas Gerais and a disclosed supply partnership.')
vendor('AMG',sid,'RAW-TANTALITE-COLTAN','Tantalum-bearing concentrate from Mibra')
site('AMG Mibra mine','AMG','Brazil','Nazareno, Minas Gerais','Mibra mine, Minas Gerais, Brazil',sid,'RAW-TANTALITE-COLTAN')

sid = source('R_BHP_IRON','BHP','Western Australia iron-ore production',
 'https://www.bhp.com/what-we-do/global-locations/australia/western-australia',
 'Names integrated iron-ore mining, rail and port infrastructure; nickel operations are suspended.')
vendor('BHP',sid,'RAW-IRON-ORE','Iron-ore mining; no current nickel supplier claim from this source')
sid = source('R_BHP_AUSTRALIA','BHP','Australian operations',
 'https://www.bhp.com/what-we-do/global-locations/australia',
 'Names Queensland coal assets and other Australian mining operations.')
vendor('BHP',sid,'RAW-COAL-CARBON','Metallurgical coal branch; petroleum coke and other carbon sources remain separate')

sid = source('R_ARAMCO_FADHILI','Saudi Aramco','Fadhili gas processing plant',
 'https://www.aramco.com/en/what-we-do/mega-projects/fadhili-gas-plant',
 'Describes natural-gas processing and high sulfur-recovery operation.')
vendor('Saudi Aramco',sid,'RAW-NATURAL-GAS RAW-SULFUR','Natural-gas production/processing and recovered sulfur; pyrite is an alternative route')
site('Aramco Fadhili gas plant','Saudi Aramco','Saudi Arabia','Fadhili','Fadhili gas plant, Saudi Arabia',sid,'RAW-NATURAL-GAS RAW-SULFUR')

sid = source('R_SIBANYE_PGM','Sibanye-Stillwater','US PGM operations',
 'https://www.sibanyestillwater.com/business/pgm-operations-americas/',
 'Names Stillwater and East Boulder mines and the Columbus metallurgical complex; palladium/platinum products.')
vendor('Sibanye-Stillwater',sid,'RAW-PGM-ORE','PGM ore, principally palladium/platinum; not proof of ruthenium supply')
for name,city in [('Stillwater mine','Nye, Montana'),('East Boulder mine','McLeod, Montana'),('Columbus metallurgical complex','Columbus, Montana')]:
    site('Sibanye-Stillwater '+name,'Sibanye-Stillwater','United States',city,city,sid,'RAW-PGM-ORE')

sid = source('R_NEWMONT_LIHIR','Newmont','Lihir gold operation',
 'https://operations.newmont.com/papua-new-guinea/lihir/',
 'Names the open-pit gold mine and ore processing on Aniolam Island, Papua New Guinea.')
vendor('Newmont',sid,'RAW-GOLD-ORE','Gold-bearing ore production; not refined gold or plating chemistry')
site('Newmont Lihir mine and processing plant','Newmont','Papua New Guinea','Lihir Island','Lihir, New Ireland, Papua New Guinea',sid,'RAW-GOLD-ORE')

sid = source('R_PANAMERICAN','Pan American Silver','Mining operations',
 'https://panamericansilver.com/operations/',
 'Lists silver-producing mines across the Americas and coproducts; projects and inactive sites also appear in the register.')
vendor('Pan American Silver',sid,'RAW-SILVER-ORE','Silver-bearing ore producer; individual-site status needs review')

sid = source('R_ORBIA_FLUORSPAR','Orbia','Fluorspar resource and fluorine supply chain',
 'https://www.orbia.com/this-is-orbia/news-and-stories/custom-electrolyte-batteries/',
 'Company states it operates a major fluorspar mine and supplies a substantial global share.')
vendor('Orbia Fluor & Energy Materials',sid,'RAW-FLUORSPAR','Fluorspar mining; exact mine and operating status need a site-level reference')

sid = source('R_CABOT_MAUA','Cabot Corporation','Maua carbon-black production',
 'https://www.cabotcorp.com/company/worldwide-locations/south-america/brazil-maua',
 'Names three carbon-black manufacturing units at Maua, Brazil.')
vendor('Cabot Corporation',sid,'LD:carbon_black','Carbon black; semiconductor encapsulant qualification is unconfirmed')
site('Cabot Maua carbon-black plant','Cabot Corporation','Brazil','Maua, Sao Paulo','Maua, Sao Paulo, Brazil',sid,'LD:carbon_black')

sid = source('R_IQE_GAAS','IQE','GaAs epitaxial wafers',
 'https://www.iqep.com/products/gaas/',
 'Lists GaAs epitaxy products including red LED applications.')
vendor('IQE',sid,'PM-SAPPHIRE-WAFER SC-LED-DIE','GaAs epiwafer branch only; does not supply all combined sapphire/InGaN/AlInGaP options')
sid = source('R_RUBICON_SAPPHIRE','Rubicon Technology','Sapphire product range',
 'https://www.rubicontechnology.com/sapphire-products-overview',
 'Lists synthetic sapphire bulk products and thin wafers.')
vendor('Rubicon Technology',sid,'PM-SAPPHIRE-WAFER','Synthetic sapphire branch only; GaAs epiwafer is a separate material')

sid = source('R_MOMENTIVE_CRUCIBLES','Momentive Technologies','Quartz glass crucibles',
 'https://www.momentivetech.com/products/crucibles/quartz-glass-crucibles',
 'Documents fused-quartz crucibles for melting polysilicon and growing single-crystal silicon.')
vendor('Momentive Technologies',sid,'LD:fused_quartz_crucible','Fused-quartz crucibles; natural versus synthetic quartz construction is grade dependent')
edge('E0083',sid,'supported_consumable_use','Quartz crucible supports silicon crystal growth as a consumable; it is not a constituent remaining in the wafer.')

sid = source('R_SHINETSU_PROCESS_PRODUCTS','Shin-Etsu Chemical','2025 electronics materials business',
 'https://www.shinetsu.co.jp/wp-content/uploads/2025/07/Business-Activity.pdf',
 'Maps silicon metal, quartz crucibles, SiC powder, silicon wafers, synthetic quartz substrates, photomask blanks, pellicles and encapsulants to semiconductor processes.')
vendor('Shin-Etsu Chemical',sid,'LD:metallurgical_grade_silicon LD:fused_quartz_crucible LD:silicon_carbide_grit LD:pellicle_membrane_frame PM-SI-WAFER LD:synthetic_fused_quartz',
 'Named semiconductor material; pellicle and quartz-product branches only, not every combined specification')

sid = source('R_FUJIMI_SLURRY','Fujimi','COMPOL polishing slurry',
 'https://www.fujimiinc.co.jp/service/catalog/file/compol_fz_clealite.pdf',
 'Describes high-purity colloidal-silica slurry for polishing electronic substrates and ceramics.')
vendor('Fujimi',sid,'LD:chemical_slurries LD:colloidal_silica LD:fumed_silica_abrasive','Colloidal-silica polishing slurry branch; no fumed-silica powder claim')

sid = source('R_GRAPHITE_INDIA','Graphite India','Graphite electrode life-cycle assessment',
 'https://graphiteindia.com/esg_backoffice/documents/synthetic%20graphite%20electrode%20lca%20april%202024-2654d1a3172507938864847314011053639.pdf',
 'Identifies graphite-electrode manufacture at Durgapur and Satpur factories.')
vendor('Graphite India',sid,'LD:graphite_electrodes','Graphite electrodes; semiconductor upstream application qualification remains open')
site('Graphite India Durgapur electrode factory','Graphite India','India','Durgapur, West Bengal','Durgapur, West Bengal, India',sid,'LD:graphite_electrodes')
site('Graphite India Satpur electrode factory','Graphite India','India','Satpur, Nashik','Satpur, Nashik, India',sid,'LD:graphite_electrodes')

sid = source('R_TANAKA_PLATING','TANAKA','Precious-metal plating processes',
 'https://tanaka-preciousmetals.com/en/products/plating_processes.html',
 'Lists pure-gold, gold-alloy, silver and platinum-group-metal plating chemistry for electronics.')
vendor('TANAKA',sid,'LD:precious_metal_plating DC-AU-PLATE DC-AG-PLATE','Precious-metal plating solutions; exact hard-gold brightener and silver-anode choices need grade evidence')

sid = source('R_TAIYO_PCB','Taiyo Holdings','PCB materials',
 'https://www.taiyo-hd.co.jp/en/business/electronics/pcb.html',
 'Names solder resist, legend ink, plating resist and etching resist as distinct PCB materials.')
vendor('Taiyo Holdings',sid,'SC-LEGEND SC-SOLDERMASK DC-PHOTORESIST','PCB legend ink and photoimageable resists; dry-film and stripper branches require exact product confirmation')
edge('E0684 E0686 E0730 E0731',sid,'supported_product_class','Official manufacturer identifies legend ink and solder resist as PCB products; epoxy recipe is grade dependent.')

sid = source('R_NIPPON_STEEL','Nippon Steel','Flat-rolled steel product scope',
 'https://www.nipponsteel.com/en/factbook/02-02.html',
 'Lists cold-rolled sheets, heavy plates and cold-rolled electrical steel sheets.')
vendor('Nippon Steel',sid,'PM-CARBON-STEEL PM-SILICON-STEEL SC-SPCC-SHEET','Steel product-class capability; exact BOF route, SPCC grade and silicon content need current grade evidence')

sid = source('R_OUTOKUMPU_TORNIO','Outokumpu','Tornio stainless-steel plant',
 'https://www.outokumpu.com/en/locations/torniostainless-steel',
 'Describes integrated stainless melting, hot and cold rolling and finishing; identifies Roytta harbor.')
vendor('Outokumpu',sid,'PM-STAINLESS-STEEL','Stainless-steel producer; shaft machining is a separate manufacturing stage')
site('Outokumpu Tornio stainless plant','Outokumpu','Finland','Tornio','Terastie, 95490 Tornio, Finland',sid,'PM-STAINLESS-STEEL')

sid = source('R_CONSTELLIUM_FOIL','Constellium','Aluminum foil-stock alloys',
 'https://www.constellium.com/packaging-solutions',
 'Lists 1100 and 3003 series foil-stock alloys and heat-exchanger applications.')
vendor('Constellium',sid,'SC-AL-FIN-STOCK','1100/3003 foil stock; actual GPU fin geometry and temper need confirmation')

sid = source('R_NMB_BEARINGS','MinebeaMitsumi / NMB','Precision bearing and electromechanical products',
 'https://nmbtc.com/our-products/',
 'Names miniature ball bearings, cooling fans and small motors.')
vendor('MinebeaMitsumi',sid,'SC-BEARING 2.4','Miniature ball bearings and fan motors; fluid-dynamic bearing branch not established')

sid = source('R_PANASONIC_FR4','Panasonic Industry','FR-4 laminate and prepreg technical guide',
 'https://api.pim.na.industrial.panasonic.com/file_stream/main/fileversion/180199',
 'Documents R-1755E laminate and R-1650E prepreg as FR-4 products.')
vendor('Panasonic Industry',sid,'SC-CCL SC-PREPREG','FR-4 copper-clad laminate and prepreg product family')

sid = source('R_DISCO_DICING','DISCO','GaAs wafer dicing technologies',
 'https://www.disco.co.jp/eg/solution/technical_review/doc/TR25-02_GaAs%20Wafer%20Dicing%20Technologies_20260123.pdf',
 'Manufacturer describes mechanical abrasive blades and laser dicing as different wafer-singulation processes.')
vendor('DISCO',sid,'DC-DICING-BLADE','Abrasive dicing-blade product branch; CMP slurry is a separate product')

sid = source('R_GLEN_ZINC','Glencore','2025 resources and reserves',
 'https://www.glencore.com/.rest/api/v1/documents/static/a17cc44b-7947-4169-9b6b-b882403fb42b/GLENCORE-Resources-and-Reserves-report-2025.pdf',
 'Describes operating zinc mines including McArthur River and Mount Isa region assets.')
vendor('Glencore',sid,'RAW-SPHALERITE-ZINC','Zinc-bearing ore; exact mineralogy and mine availability need site-specific confirmation')
site('Glencore McArthur River zinc mine','Glencore','Australia','McArthur River, Northern Territory','McArthur River mine, Northern Territory',sid,'RAW-SPHALERITE-ZINC')

sid = source('R_CLIMAX_MOLY','Freeport-McMoRan / Climax Molybdenum','US molybdenum production operations',
 'https://www.climaxmolybdenum.com/operations/usa',
 'Identifies Climax and Henderson molybdenum mining operations and separate processing locations.')
vendor('Freeport-McMoRan',sid,'RAW-MOLYBDENITE','Molybdenum-bearing ore production')
site('Climax Molybdenum Henderson mine','Freeport-McMoRan','United States','Empire, Colorado','Henderson mine near Empire, Colorado',sid,'RAW-MOLYBDENITE')
site('Climax Molybdenum Climax mine','Freeport-McMoRan','United States','Climax, Colorado','Climax mine, Colorado',sid,'RAW-MOLYBDENITE')

sid = source('R_THARISA_CHROME','Tharisa','Tharisa Minerals mine and processing',
 'https://www.tharisa.com/tharisa-minerals.php',
 'Names chromitite mining and separate chrome/PGM concentration stages at the Tharisa mine.')
vendor('Tharisa',sid,'RAW-CHROMITE RAW-PGM-ORE','Chrome and PGM concentrate coproduction')
site('Tharisa mine and concentration plants','Tharisa','South Africa','Marikana','Tharisa mine near Marikana, South Africa',sid,'RAW-CHROMITE RAW-PGM-ORE')

sid = source('R_EXXON_UPSTREAM','ExxonMobil','2025 Form 10-K upstream operations',
 'https://investor.exxonmobil.com/sec-filings/annual-reports/content/0000034088-26-000045/0000034088-26-000045.pdf',
 'Reports crude-oil and natural-gas production by geography.')
vendor('ExxonMobil',sid,'RAW-CRUDE-OIL RAW-NATURAL-GAS','Crude petroleum and natural-gas production; no GPU-specific procurement connection')

sid = source('R_COMPASS_SALT','Compass Minerals','Goderich mine and salt production',
 'https://www.compassminerals.com/who-we-are/locations/goderich-ontario/',
 'Names underground salt mining and evaporative salt production in Goderich.')
vendor('Compass Minerals',sid,'RAW-HALITE-BRINE','Halite/rock-salt branch of combined salt-and-brine node')
site('Compass Minerals Goderich salt mine','Compass Minerals','Canada','Goderich, Ontario','Goderich, Ontario',sid,'RAW-HALITE-BRINE')

sid = source('R_SAKAI_BARITE','Sakai Chemical Industry','Barium and strontium products',
 'https://sakai-chem.co.jp/en/products_services_barium_strontium.php',
 'Lists ground barite and precipitated barium-sulfate product lines.')
vendor('Sakai Chemical Industry',sid,'RAW-BARITE','Ground barite product supplier; this source does not establish a company-owned mine')

sid = source('R_SHINKO_LEADFRAME','Shinko Electric Industries','Leadframe product datasheet',
 'https://www.shinko.co.jp/english/product/docs/leadframe_EN.pdf',
 'Names stamped or etched leadframes and optional Ag or Pd preplated finishes.')
vendor('Shinko Electric Industries',sid,'SC-CU-LEADFRAME LD:lead_frames','Copper leadframes; C19400 grade and power-clip branch need product-specific confirmation')
edge('E0107 E0109',sid,'supported_product_class','Copper leadframes and plating options are documented. The named alloy constituents and plating alternatives must be selected for an actual package.')

sid = source('R_FURUKAWA_COPPER','Furukawa Electric','OFC and TPC copper strip grades',
 'https://www.furukawaelectric.com/copper/product/strip/ofc_tpc.html',
 'Lists C1020 oxygen-free copper and C1100 tough-pitch copper separately.')
vendor('Furukawa Electric',sid,'SC-OFC-COPPER','Oxygen-free and tough-pitch strip branch; tubes and finished heat pipes are separate products')

sid = source('R_TDK_NDFEB','TDK','Neodymium magnet catalog',
 'https://product.tdk.com/en/search/magnet/magnet/neodymium/catalog',
 'Lists neodymium magnet material families with magnetic properties and separate grades.')
vendor('TDK',sid,'PM-NDFEB-ALLOY SC-NDFEB-MAGNET','Neodymium magnet product class; rotor ring geometry and exact composition need grade evidence')

sid = source('R_NAMICS_ATTACH','NAMICS','Conductive die-attach adhesives',
 'https://www.namics.co.jp/en/products/die-attach-unimec/',
 'Lists conductive heat-cured adhesive products with QFP/QFN die-bonding applications.')
vendor('NAMICS',sid,'LD:die_attach_materials SC-DIE-ATTACH','Conductive die attach; silver-filled epoxy composition requires product SDS confirmation')

sid = source('R_MSSA_SODIUM','Metaux Speciaux / MSSA','Sodium metal product sheet',
 'https://www.metauxspeciaux.fr/wp-content/uploads/2020/08/Sodium-M%C3%A9tal.pdf',
 'Official product document establishes sodium-metal supply. Purity, site and current operating status require separate checks.')
vendor('Metaux Speciaux / MSSA',sid,'LD:sodium_metal','Sodium metal product')

vendor('Nitto Boseki','SRC_NITTOBO_PRODUCT','PM-E-GLASS LD:e_glass_fiberglass',
 'Electronic glass cloth; T-glass and NE-glass are distinct from ordinary E-glass and are not interchangeable without qualification')
vendor('Ajinomoto Fine-Techno','SRC_AJINOMOTO_ABF','LD:bt_abf_resin_matrix',
 'Ajinomoto build-up film branch only; BT resin is a separate chemistry')
vendor('Mitsui Kinzoku','SRC_MITSUI_COPPER','SC-CU-FOIL',
 'Electrodeposited copper foil; exact thickness and roughness need grade evidence')
vendor('Murata','SRC_MURATA_MLCC_MATERIALS','SC-MLCC-BODY',
 'Finished MLCC manufacture; an un-terminated internal MLCC body is not established as an independently sold product')
vendor('Infineon','SRC_INFINEON_POWER','SC-POWER-DIE',
 'Integrated power-stage product manufacturer; separately purchasable bare DrMOS die is unconfirmed')
vendor('Nuvoton','SRC_NUVOTON_MCU','SC-MCU-DIE',
 'Microcontroller product manufacturer; bare-die availability and ARM architecture depend on product')
vendor('Nexperia','SRC_NEXPERIA_ESD','SC-TVS-DIE',
 'ESD-protection semiconductor manufacturer; separate bare-die supply remains unconfirmed')

# Such mappings are useful manufacturer candidates, but must not be mistaken for
# an independently sold internal subcomponent or a qualified alternate source.
for _r in VENDORS:
    if _r['node_id'] in {'SC-MLCC-BODY','SC-POWER-DIE','SC-MCU-DIE','SC-TVS-DIE'}:
        _r['qualification'] = 'finished_device_manufacturer_bare_subcomponent_sale_unverified'

sid = source('R_SAMYANG_BPA','Samyang Innochem','Bisphenol-A manufacture',
 'https://www.samyanginnochem.com/en/product/bpa',
 'Identifies BPA production from phenol and acetone and its use in epoxy and polycarbonate.')
vendor('Samyang Innochem',sid,'LD:bisphenol_a','Bisphenol-A; electronic-grade purification remains unconfirmed')
edge('E0143',sid,'supported_process_input','BPA is documented as an epoxy-resin input; phenol and acetone intermediates are omitted upstream in the submitted graph.')
edge('E0146 E0147',sid,'upstream_lineage_requires_process_evidence','Direct inputs stated by the manufacturer are phenol and acetone, not benzene and propylene. Preserve benzene/propylene only as upstream lineage with intervening chemistry.')

sid = source('R_BASF_GLYCOLS','BASF','Alkylene oxides and glycols',
 'https://chemicals.basf.com/global/en/Petrochemicals/alkylene-oxides-and-glycols/products',
 'Lists monoethylene glycol and glycol applications in polyester and coolants.')
vendor('BASF',sid,'LD:ethylene_glycol','Monoethylene glycol branch; propylene glycol and semiconductor abrasive-carrier grade remain separate')

sid = source('R_SUMIBE_RESIST_POLYMER','Sumitomo Bakelite','Novolac resins for photoresist',
 'https://www.sumibe.co.jp/english/product/hpp/phenolic/exposure/index.html',
 'Official product family for photoresist novolac resin.')
vendor('Sumitomo Bakelite',sid,'LD:photoresist_polymers','Novolac photoresist-resin branch; ArF methacrylate and PHS alternatives not established')

sid = source('R_MICROSI_MASK','Shin-Etsu Chemical / MicroSi','Photomask blanks',
 'https://www.microsi.com/applications-solutions/photomask-pellicles/mask-blanks/',
 'Describes chromium and MoSi absorber options and quartz-based mask-blank products.')
vendor('Shin-Etsu Chemical',sid,'LD:chromium_mosi_absorber','Absorber-coated mask blanks; separate sale of absorber material is not established')

sid = source('R_MITSUBISHI_AUSN','Mitsubishi Materials','Gold-tin alloy solder paste',
 'https://www.mmc.co.jp/adv/en/products/ausn.html',
 'Official AuSn paste products for die bonding and sealing.')
vendor('Mitsubishi Materials',sid,'LD:silver_flakes_solder','AuSn solder-paste branch; silver-flake powder is a separate alternative')

sid = source('R_JSR_PRODUCT_RANGE','JSR','2025 corporate product outline',
 'https://www.jsr.co.jp/jsr_e/company/assets/pdf/251211_JSR_corporate2025_EN.pdf',
 'Lists photoresists and CMP slurries in the semiconductor product range.')
vendor('JSR',sid,'PM-FAB-CHEM LD:chemical_slurries','Photoresist and CMP slurry branches; etch-gas branch is not established')

sid = source('R_MG_ETCH','MG Chemicals','415 ferric chloride technical data',
 'https://mgchemicals.com/downloads/tds/tds-415-l.pdf',
 'Ferric-chloride copper etchant for printed circuit boards; source states it can be reused.')
vendor('MG Chemicals',sid,'DC-CU-ETCHANT','Ferric-chloride branch; cupric chloride is a different product')
edge('E0619 E0624',sid,'candidate_process_option','Ferric chloride is a documented PCB etchant. The commercial reference can be reused, so the node label disposable should not imply single use.')

sid = source('R_MORGAN_YSZ','Morgan Advanced Materials','Yttria-stabilized zirconia datasheet',
 'https://www.morgantechnicalceramics.com/media/lpybwekm/yttria-stabilised-zirconia.pdf',
 'Specifies a yttria-stabilized zirconia material for ceramic injection molding.')
vendor('Morgan Advanced Materials',sid,'PM-ZIRCONIA','YSZ ceramic material class; semiconductor kiln-setter qualification not established')

sid = source('R_LORAD_YAG','Lorad Chemical','Cerium-doped YAG phosphor',
 'https://loradchemical.com/products/cerium-doped-yttrium-aluminum-garnet',
 'Lists YAG:Ce powder for white LED lamps.')
vendor('Lorad Chemical',sid,'PM-YAG-PHOSPHOR SC-PHOSPHOR','YAG:Ce phosphor powder; does not establish use in an RGB-only GPU LED')
edge('E0618',sid,'same_material_duplicate_node','Both nodes describe YAG:Ce powder; no distinct conversion step is established. Merge or identify a real processing distinction.')

sid = source('R_NATIONAL_FERRITE','National Magnetics Group','Ni-Zn ferrite powder SDS',
 'https://www.magneticsgroup.com/wp-content/uploads/2019/08/NiZn-SDS-r.-12-18-18.pdf',
 'Manufacturer SDS identifies calcined/sintered Ni-Zn ferrite powder for soft-ferrite manufacture.')
vendor('National Magnetics Group',sid,'PM-FERRITE','Ni-Zn ferrite powder; exact component frequency grade remains unqualified')

sid = source('R_RSW_SILVER','Rochester Silver Works','Silver nitrate production',
 'https://rochestersilverworks.com/silver-nitrate/',
 'Describes silver-nitrate production from high-purity silver metal and nitric acid.')
vendor('Rochester Silver Works',sid,'PM-REFINED-AG','Silver-nitrate branch; this is not evidence of a primary silver refinery')

sid = source('R_CU_WICK_POWDER','Nippon Atomized Metal Powders','Copper powder product and applications',
 'https://atomize.co.jp/english/products/copper_powder.html',
 'Names atomized copper-powder products and heat-pipe wick applications.')
vendor('Nippon Atomized Metal Powders',sid,'SC-CU-WICK','Copper powder for wick manufacture; finished sintered wick is a downstream product')
edge('E0750 E0751',sid,'candidate_process_option','Copper powder is documented for heat-pipe wick applications; verify the chosen vapor-chamber or heat-pipe wick technology.')

sid = source('R_RBC_SHAFT','RBC Bearings / PIC','Precision-ground stainless shaft stock',
 'https://www.rbcbearings.com/literature/pdfs/PIC_Catalog.pdf',
 'Lists precision-ground 303 stainless-steel shaft stock.')
vendor('RBC Bearings',sid,'SC-SS-SHAFT','Precision-ground stainless stock; GPU fan rotor-shaft dimensions require qualification')

sid = source('R_SEMBLEX_FASTENER','Semblex','EJOT SpringHead cold-headed fastener',
 'https://www.semblex.com/en/technologies/ejot-springhead/',
 'Describes a cold-headed fastener with an integrated spring element.')
vendor('Semblex',sid,'2.6 SC-ALLOY-STEEL-WIRE','Cold-headed screw branch; reference-card screw sizes and retention brackets are unconfirmed')

sid = source('R_KIYOMINE_BRONZE','Kiyomine Metal Industry','Phosphor-bronze alloy lineup',
 'https://www.kiyomine.co.jp/en-products/en-bronze/',
 'Names C5191 and related phosphor-bronze strip alloys with copper, tin and phosphorus composition.')
vendor('Kiyomine Metal Industry',sid,'SC-PHBR-CONTACT','C5191 phosphor-bronze feedstock; stamped finished contacts require another process')
edge('E0599 E0600',sid,'supported_alloy_composition','Phosphor bronze contains copper, tin and phosphorus. The combined refined-metal/salt nodes need branch selection.')

sid = source('R_MPS_FAN_DRIVER','Monolithic Power Systems','Motor-driver product catalog',
 'https://media.monolithicpower.cn/mps_cms_document/m/o/motor_driver_catalog_q4_2022-digital.pdf',
 'Names MP6616A single-phase BLDC fan driver with an integrated Hall sensor.')
vendor('Monolithic Power Systems',sid,'SC-FAN-DRIVER-IC','Hall-sensor BLDC fan-driver IC branch; the small board is a separate assembly')

sid = source('R_SHERWIN_COATING','Sherwin-Williams','Acrolon EG-120 acrylic-polyurethane coating',
 'https://protectiveeu.sherwin-williams.com/product_documentation/product-data-sheets/english-pds/pds-acrolon-eg-120-issue-1.pdf',
 'Official datasheet specifies a two-component acrylic-polyurethane coating.')
vendor('Sherwin-Williams',sid,'SC-PU-COATING','Acrylic-polyurethane coating class; GPU-shroud suitability and finish remain unqualified')

sid = source('R_BASF_PA66','BASF','Ultramid A3EG6 PA66-GF30 processing datasheet',
 'https://download.basf.com/p1/8a8082587fd4b608017fd631677c38e9/en/ULTRAMID%25C2%25AE_A3EG6',
 'Specifies a 30%-glass-filled PA66 injection-molding compound for component housings.')
vendor('BASF',sid,'PM-PA66-POLYMER SC-PA66-GF','PA66 compound branch; required flame rating and completed connector housing need qualification')

sid = source('R_LINDE_ULTRAPURE','Linde','Semiconductor bulk gases',
 'https://www.lindeus.com/industries/electronics/semiconductors',
 'Names ultra-high-purity nitrogen, oxygen, argon, hydrogen, helium and carbon dioxide supply for semiconductors.')
vendor('Linde',sid,'LD:ultra_pure_hydrogen LD:ultra_pure_argon','Ultrahigh-purity gas class; numerical purity and impurity limits require the selected grade specification')

sid = source('R_LINDE_MERGER','Linde','Praxair and Linde combination completed',
 'https://www.linde.com/news-and-media/2018/business-combination-between-praxair-and-linde-ag-successfully-completed',
 'Confirms the 2018 combination of Praxair and Linde. Legacy provider names must not automatically count as independent supplier groups.')

sid = source('R_JSR_INPRIA','JSR','2023 annual report: Inpria acquisition',
 'https://www.jsr.co.jp/jsr_e/ir/library/assets/pdf/annual_report_2023.pdf',
 'Records acquisition of Inpria as a wholly owned subsidiary in 2021; review ownership at the analysis date.')

CORPORATE_GROUPS = {
    'praxair': ('Linde', 'R_LINDE_MERGER', 'legacy_brand_same_group'),
    'linde': ('Linde', 'R_LINDE_MERGER', 'named_group'),
    'inpria': ('JSR', 'R_JSR_INPRIA', 'reported_subsidiary_check_current_ownership'),
    'jsr': ('JSR', 'R_JSR_INPRIA', 'named_group'),
}

sid = source('R_DISCO_KURE','DISCO','High-quality manufacturing: precision diamond products',
 'https://www.disco.com.sg/eg/csr/activity/manufacture/index.html',
 'Explicitly locates blade and wheel manufacture at Kure Plant, Hiroshima; does not establish a specific GPU customer.')
site('Kure Plant','DISCO','Japan','Kure','Kure, Hiroshima Prefecture',sid,'DC-DICING-BLADE')

sid = source('R_INPRIA_CORVALLIS','Inpria','EUV photoresists and Corvallis manufacturing plant',
 'https://www.inpria.com/',
 'Names a manufacturing plant in Corvallis, Oregon and EUV metal-oxide photoresist products; office suite address is not asserted to be the plant gate.')
site('Corvallis EUV photoresist plant','Inpria','United States','Corvallis','Corvallis, Oregon; plant street address unconfirmed',sid,'LD:photoresists')

sid = source('R_SAMYANG_GUNSAN','Samyang Innochem','Facilities: BPA plant',
 'https://www.samyanginnochem.com/en/company/facility',
 'Identifies BPA production in Gunsan Free Trade Zone; electronics-grade qualification is not documented.')
site('Gunsan BPA plant','Samyang Innochem','South Korea','Gunsan','133 Jayumuyeok 1-gil, Gunsan-si',sid,'LD:bisphenol_a')

sid = source('R_MOMENTIVE_SITES','Momentive Technologies','Global production footprint',
 'https://www.momentivetech.com/about-us/corporate-governance/global-footprint',
 'Separates production-product locations from corporate and sales offices; Geesthacht and Oguni explicitly identify crucible products.')
site('Geesthacht quartz crucible plant','Momentive Technologies','Germany','Geesthacht','Geesthacht; exact plant gate unconfirmed',sid,'LD:fused_quartz_crucible')
site('Oguni crucible plant','Momentive Technologies','Japan','Oguni, Yamagata','Oguni, Yamagata; exact plant gate unconfirmed',sid,'LD:fused_quartz_crucible')
