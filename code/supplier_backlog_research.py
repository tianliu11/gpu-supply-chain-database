"""Primary-source evidence for the remaining supplier and site leads."""
from additional_public_research import source, vendor, site
from claude_followup_research import edge, LEAD_TIME_DISCLOSURES, REFERENCE_SUPPLY_QUALIFICATION

s = source('R12_PCP_ASSEMBLY', 'PC Partner Group', 'Listing document: VGA production facilities and process',
    'https://www.pcpartner.com/attachment/ac/1731423968JkIWv.pdf',
    'Documents surface-mount graphics-card production at Dongguan and its reported 2024 line capacity.')
t = source('R12_PCP_PRODUCTS', 'PC Partner Group', 'Listing document: graphics-card products',
    'https://www.pcpartner.com/attachment/ac/1731423968nYn0G.pdf',
    'Describes assembling graphics chips, memory and other parts onto graphics-card PCBs.')
a = source('R12_PCP_2025', 'PC Partner Group', '2025 Annual Report',
    'https://www.pcpartner.com/attachment/pdf/1775010921kL9l9.pdf',
    'Names operating manufacturing businesses in Dongguan and Indonesia; records Batam production.')
vendor('PC Partner', t, '1', 'Populated graphics-card PCB assembly by an ODM; bare PCB and specific customer allocation are separate')
site('PC Partner Dongguan graphics assembly', 'PC Partner', 'China', 'Dongguan', 'Dongguan production factory', s+';'+a, '1')
site('PC Partner Batam manufacturing', 'PC Partner', 'Indonesia', 'Batam', 'Batamindo Industrial Park', a, '')
edge('E0001 E0002 E0003 E0006',t,'supported_component_family',
     'Manufacturer uses bare PCBs, graphics chips and memory in card assembly. Exact package type and board model remain design-specific.')
LEAD_TIME_DISCLOSURES.append(dict(company='PC Partner Group', reporting_period='2024 listing',
    measure='configured high-end graphics-card throughput', comparison='approximately', value=10000,
    unit='cards per eight-hour shift', scope='reported Dongguan line capacity',
    node_id='1', facility_name='PC Partner Dongguan graphics assembly',
    facility_id=None, use_as_node_duration=False, source_ids=s))
REFERENCE_SUPPLY_QUALIFICATION.append(dict(node_id='1', reference_product='PC Partner graphics-card portfolio',
    supplier='PC Partner', role='same_group_manufacturing_footprint',
    facility_names=['PC Partner Dongguan graphics assembly', 'PC Partner Batam manufacturing'],
    qualified_alternate_supplier_ids=[], alternate_status='two_same_owner_sites_per_model_transfer_unverified',
    missing_evidence=['site-approved model', 'transfer time', 'spare capacity'], source_ids=a))

s = source('R12_BIRLA_PRODUCT', 'Birla Carbon', 'Carbon black for engineering plastics',
    'https://www.birlacarbon.com/plastics/engineering-plastics/',
    'Documents specialty carbon black grades for engineering polymers; electronic encapsulation qualification is separate.')
vendor('Birla Carbon', s, 'LD:carbon_black', 'Specialty carbon black for polymer pigmentation; semiconductor package grade unverified')
t = source('R12_BIRLA_LOCATIONS', 'Birla Carbon', 'Manufacturing and commercial locations',
    'https://www.birlacarbon.com/locations/',
    'Separates named manufacturing units from offices and technology centers.')
for name, country, city, address in [
    ('Ulysses', 'United States', 'Ulysses, Kansas', '3500 South Road S'),
    ('Centerville', 'United States', 'Centerville, Louisiana', '370 Columbian Chemicals Lane'),
    ('Hamilton', 'Canada', 'Hamilton, Ontario', '755 Parkdale Avenue North'),
    ('Camacari', 'Brazil', 'Camaçari, Bahia', 'Via Fontal, petrochemical complex'),
    ('Cubatao', 'Brazil', 'Cubatão, São Paulo', 'Estrada Rene Fonseca'),
    ('Gajano', 'Spain', 'Gajano, Cantabria', 'Carretera Gajano-Pontejos'),
    ('Trecate', 'Italy', 'Trecate', 'Via San Cassiano 140'),
    ('Tiszaujvaros', 'Hungary', 'Tiszaújváros', 'Tiszaújváros manufacturing unit'),
    ('Amreya', 'Egypt', 'Alexandria', 'El Nahda Road, Amreya'),
    ('Gummidipoondi', 'India', 'Gummidipoondi, Tamil Nadu', 'SIPCOT Industrial Complex'),
    ('Patalganga', 'India', 'Khalapur, Maharashtra', 'Lohop, Patalganga'),
    ('Renukoot', 'India', 'Renukoot, Uttar Pradesh', 'Murdhawa Industrial Area'),
    ('Naidupeta', 'India', 'Naidupeta, Andhra Pradesh', 'APIIC Industrial Area'),
    ('Ang Thong', 'Thailand', 'Ang Thong', 'Posa, Ayutthaya-Ang Thong Highway'),
    ('Rayong', 'Thailand', 'Rayong', 'Samnak Thong'),
    ('Jining', 'China', 'Jining, Shandong', 'Jibei High Tech Development Zone'),
    ('Weifang', 'China', 'Weifang, Shandong', 'Binhai Economic Development Zone'),
    ('Yeosu', 'South Korea', 'Yeosu', '46-101 Yeosusandan 2-ro'),
]:
    site('Birla Carbon '+name, 'Birla Carbon', country, city, address, t, 'LD:carbon_black')

s = source('R12_ORION_PRODUCT', 'Orion S.A.', 'Specialty carbon black in polymers',
    'https://orioncarbons.com/solutions/polymers/',
    'Describes carbon black products for polymer coloring and other applications.')
vendor('Orion S.A.', s, 'LD:carbon_black', 'Specialty carbon black for polymers; encapsulation grade unallocated')
s = source('R12_PCBL_PRODUCT', 'PCBL Chemical', 'Specialty black catalogue',
    'https://www.pcblltd.com/product/specialty-black',
    'Lists specialty carbon black products; GPU package grade unverified.')
vendor('PCBL Chemical', s, 'LD:carbon_black', 'Specialty carbon black candidate; semiconductor end use requires qualification')
t = source('R12_PCBL_SITES', 'PCBL Chemical', 'FY2027 Q2 investor presentation: plant network',
    'https://api.pcblltd.com/uploads/Intimationof_Investor_Update_Q2_FY_27_1_bdebefa3eb.pdf',
    'Identifies five carbon-black locations and a wider group footprint; other business locations excluded.')
for name, city in [
    ('Mundra','Mundra, Gujarat'), ('Durgapur','Durgapur, West Bengal'),
    ('Chennai','Chennai, Tamil Nadu'), ('Palej','Palej, Gujarat'), ('Kochi','Kochi, Kerala'),
]:
    site('PCBL '+name, 'PCBL Chemical', 'India', city, 'Manufacturing area named in investor disclosure', t, 'LD:carbon_black')

s = source('R12_NMC_WIRE', 'Nippon Micrometal', 'Bonding wire product catalogue',
    'https://www.nmc-net.co.jp/en/products/',
    'Offers bonding wire products. Specific metal, alloy and package application require a part selection.')
vendor('Nippon Micrometal', s, 'SC-BOND-WIRE', 'Semiconductor bonding wire; exact wire metal and package application remain open')
t = source('R12_NMC_SITES', 'Nippon Micrometal', 'Production network',
    'https://www.nmc-net.co.jp/en/company/network/',
    'Identifies Iruma Factory and Yorii Manufacturing Plant. Unspecified overseas offices excluded.')
for name, city, address in [
    ('Iruma', 'Iruma, Saitama', '158-1 Sayamagahara'), ('Yorii', 'Yorii, Saitama', '5320 Yodo'),
]:
    site('Nippon Micrometal '+name, 'Nippon Micrometal', 'Japan', city, address, t, '')
s = source('R12_TANAKA_WIRE', 'TANAKA Precious Metal Technologies', 'Bonding wire product catalogue',
    'https://tanaka-preciousmetals.com/en/products/bonding_wires/',
    'Product family includes semiconductor wire-bond materials.')
vendor('TANAKA Precious Metal Technologies', s, 'SC-BOND-WIRE', 'Bonding wire family; selected metal/diameter and device qualification unverified')

for sid, company, node, title, url, scope in [
    ('R12_MCC_EPOXY', 'Mitsubishi Chemical', 'PM-EPOXY-RESIN', 'jER epoxy resin catalogue',
     'https://us.mitsubishi-chemical.com/product/jer/', 'Epoxy resin family for electronics and industrial uses; exact hardener and package formulation open'),
    ('R12_WESTLAKE', 'Westlake Epoxy', 'PM-EPOXY-RESIN', 'Westlake Epoxy portfolio',
     'https://investors.westlake.com/news-releases/news-release-details/westlake-epoxy-expands-distribution-relationship-brenntag-india',
     'Vendor identifies its epoxy resin and curing agent portfolio; electronic grade must be selected'),
    ('R12_KUKDO_EPOXY', 'Kukdo Chemical', 'PM-EPOXY-RESIN', 'Epoxy and hardener production scope',
     'https://www.kukdo.com/upload/inquiry/Sustainability-FactBook2023_en.pdf',
     'Plant-level epoxy and hardener manufacturing scope; no individual package-grade assignment'),
    ('R12_CHIMEI_PCABS', 'Chi Mei', 'PM-PC-ABS-POLYMER', 'WONDERLOY PC alloys',
     'https://www.chimeicorp.com/en-US/?feature=T10701&material=T10700&page=products&series=T10000',
     'PC/ABS alloy product family; shroud flame rating, geometry and customer allocation open'),
    ('R12_DOMO_PA66', 'Domo Chemicals', 'PM-PA66-POLYMER', 'TECHNYL engineered materials',
     'https://www.domochemicals.com/en/about-domo-chemicals/business-areas/engineered-materials',
     'PA66 engineering-polyamide grades; finished part and specific grade require qualification'),
]:
    source(sid, company, title, url, scope)
    vendor(company, sid, node, scope)

for name, city in [('Iksan','Iksan'), ('Siwha','Siheung'), ('Busan No. 1','Busan'), ('Busan No. 2','Busan')]:
    site('Kukdo '+name, 'Kukdo Chemical', 'South Korea', city, 'Epoxy and hardener production unit',
         'R12_KUKDO_EPOXY', 'PM-EPOXY-RESIN')

s = source('R12_PET_FELT', 'Superior Felt & Filtration', 'Industrial synthetic polyester felt',
    'https://www.superiorfelt.com/products/synthetic-felt/polyester/',
    'Sells nonwoven polyester felt. CMP-specific backing requirements need a separate specification.')
vendor('Superior Felt & Filtration', s, 'LD:polyester_felt_backing',
       'Industrial PET felt stock; polishing-pad backing grade and OEM approval unverified')

s = source('R12_SAN_PEDRO_DWELL', 'Pacific Merchant Shipping Association',
    'San Pedro Bay Ports Container Dwell Times for October 2025',
    'https://www.pmsaship.com/maritime-insights-blog/san-pedro-bay-ports-dwell-time-october-2025',
    'Publishes measured import-container marine-terminal dwell by onward mode across Los Angeles and Long Beach.')
for mode, mean in [('truck', 2.74), ('rail', 3.31)]:
    LEAD_TIME_DISCLOSURES.append(dict(company='Pacific Merchant Shipping Association',
        reporting_period='October 2025', measure='observed mean import container terminal dwell',
        comparison='mean', value=mean, unit='days', scope='Los Angeles and Long Beach aggregate',
        onward_mode=mode, node_id=None, facility_id=None, use_as_node_duration=False, source_ids=s))

# Each observation states the exact supplied product, including examples where
# only one branch or one procurement role is supported.
for sid, company, node, title, url, scope in [
    ('R12_PNY_BRACKET', 'PNY', '1.5', 'RTX A400 package contents',
     'https://www.pny.com/rtx-a400?sku=VCNRTXA400ATX-PB',
     'Supplies attached ATX and separate low-profile I/O brackets with its card; metal stamping contractor undisclosed'),
    ('R12_MATROX_BRACKET', 'Matrox', '1.5', 'M-Series board installation guide',
     'https://video.matrox.com/sites/video/files/2022-09/en_mseries_user_guide.pdf',
     'Supplies interchangeable mounting brackets with named graphics boards; actual bracket manufacturer undisclosed'),
    ('R12_EK_BACKPLATE', 'EK Water Blocks', '3', 'RTX 3080/3090 Vector backplate',
     'https://www.ekwb.com/shop/ek-quantum-vector-rtx-3080-3090-backplate-black',
     'Documented aftermarket aluminum backplate for matching water blocks; site within Slovenia and OEM stock supply unverified'),
    ('R12_APCB_GOLD', 'AdvancedPCB', '4', 'PCB gold finger fabrication',
     'https://www.advancedpcb.com/en-us/resources/blog/gold_fingers/',
     'Documents plated hard-gold PCB edge-contact capability; analyze as a fabricated bare-PCB feature, not a separate socket'),
    ('R12_PALIT_SHROUD', 'Palit Microsystems', '7', 'GamingPro removable front covers',
     'https://www.palit.com/maker/gamingpro.php',
     'Documents a removable front cover on named Palit cards; OEM molding site and interchangeability remain unconfirmed'),
    ('R12_TI_RGB', 'Texas Instruments', '8.2', 'LP5036 RGB LED current driver',
     'https://www.ti.com/product/LP5036',
     'Integrated RGB driver IC for a representative alternative implementation; does not establish the submitted controller-board bill of materials'),
    ('R12_OSRAM_RGB', 'ams OSRAM', '8.1', 'Multi Color LED catalogue',
     'https://ams-osram.com/products/leds/multi-color-leds',
     'Packaged multi-chip RGB LEDs, including gaming applications; no graphics-card SKU allocation'),
    ('R12_SEOUL_RGB', 'Seoul Semiconductor', '8.1', 'STF0A36ZA-B RGB LED',
     'https://www.seoulsemicon.com/en/product/detail/STF0A36ZA-B%283%29',
     'Full-color top-view RGB LED product example; exact GPU footprint and qualification remain open'),
    ('R12_NATIONSTAR_RGB', 'Foshan NationStar Optoelectronics', '8.1', 'Fully colored flat RGB LED catalogue',
     'https://www.nationstar.com/nationstar/channel/flat_screen_full_color',
     'RGB package family demonstrated for displays; GPU application and site allocation remain open'),
    ('R12_HENKEL_DA', 'Henkel', 'SC-DIE-ATTACH', 'ABLESTIK 84-1LMISR4 technical listing',
     'https://next.henkel-adhesives.com/us/en/products/industrial-adhesives/central-pdp.html/loctite-ablestik-84-1lmisr4/SAP_IB-81305.html',
     'Lists silver conductive epoxy for die attach; qualification and bondline properties depend on application'),
    ('R12_MKE_WIRE', 'MK Electron', 'SC-BOND-WIRE', 'Bonding wire catalogue',
     'https://www.mke.co.kr/page/page.php?id=1764147995&mid=22',
     'Gold and copper bonding-wire product families; chosen diameter and grade remain device-specific'),
    ('R12_POLYPLASTICS_LCP', 'Polyplastics', 'SC-LCP-GF', 'LAPEROS E130i grade sheet',
     'https://www.polyplastics.com/Gidb/GradeInfoDownloadAction.do?_LOCALE=ENGLISH&fileNo=1&gradeId=2536&langId=1',
     'Identifies LCP with 30% glass fiber; documents pellet material rather than molded connector housing'),
    ('R12_CELANESE_LCP', 'Celanese', 'SC-LCP-GF', 'Vectra LCP design guide',
     'https://www.celanese.com/-/media/Engineered%20Materials/Files/Product%20Technical%20Guides/LCP-027_VectraLCPDesignGuideTG_AM_0613.pdf',
     'Documents 30% glass-reinforced options in Vectra LCP; molded insulator remains a separate step'),
    ('R12_NOVORAY_SILICA', 'Jiangsu Novoray New Material', 'LD:fused_silica_filler', 'Fused silica for potting',
     'https://novoray.com/en/index.php/application/page/id/34.html',
     'Names fused silica powder as a filler; semiconductor encapsulation specification and lot assignment unverified'),
    ('R12_KAZ_PHOSPHORUS', 'Kazphosphate', 'LD:white_phosphorus', 'Phosphorus products',
     'https://www.kpp.kz/en/products',
     'Lists yellow phosphorus, commercial white elemental phosphorus; semiconductor purity is unverified'),
    ('R12_SHENMA_PA66', 'Shenma Industrial', 'PM-PA66-POLYMER', 'Engineering plastics grade PA66 resin',
     'https://en.shenma.com/product/51.html',
     'Resin grade family for engineering plastics; exact finished part and grade remain open'),
    ('R12_ALPEK_PET', 'Alpek', 'PM-PET-POLYMER', 'PET resin products',
     'https://www.alpekpolyester.com/pet-resins/',
     'PET resin family; suitability for the liner, fiber or other project application is grade-specific'),
    ('R12_FENC_PET', 'Far Eastern New Century', 'PM-PET-POLYMER', '2025 Annual Report PET resin lines',
     'https://www.fenc.com/upload/ir/FENC_AR_2025_EN.pdf',
     'Documents PET resin category; electronics qualification requires a grade selection'),
    ('R12_GRAYMONT_LIMESTONE', 'Graymont', 'RAW-LIMESTONE', 'Dolomitic limestone products',
     'https://www.graymont.com/product/dolomitic-limestone/',
     'Sells screened dolomitic limestone grades; no feedstock link to a specific downstream site'),
    ('R12_USSILICA_KOSSE', 'U.S. Silica', 'RAW-QUARTZ', 'Kosse sand mining and processing',
     'https://www.ussilica.com/locations/kosse-tx',
     'Documents glass-industry silica sand; does not establish high-purity crucible feedstock'),
    ('R12_CARGILL_SALT', 'Cargill', 'RAW-HALITE-BRINE', 'Cayuga rock salt mine',
     'https://www.cargill.com/industrial/winter-road-maintenance/cayuga-salt-mine',
     'Evidence for mined halite branch; potassium and bromine brine branches are separate'),
    ('R12_CHEVRON_OIL', 'Chevron', 'RAW-CRUDE-OIL', 'United States production operations',
     'https://www.chevron.com/worldwide/united-states',
     'Company identifies operating crude oil and gas production; no trace to GPU-specific products'),
    ('R12_SHELL_GAS', 'Shell', 'RAW-NATURAL-GAS', 'Portfolio and major projects',
     'https://www.shell.com/investors/results-and-reporting/portfolio-and-major-projects.html',
     'Natural gas and LNG operations; does not establish delivery to project suppliers'),
    ('R12_NOVATEK_GAS', 'Novatek', 'RAW-NATURAL-GAS', 'Company production business',
     'https://www.novatek.ru/en/about/company/',
     'Natural gas and liquid hydrocarbon production; geographic and commercial eligibility unverified'),
]:
    source(sid, company, title, url, scope)
    vendor(company, sid, node, scope)

t = source('R12_APCB_SITES', 'AdvancedPCB', 'U.S. PCB production facilities',
    'https://www.advancedpcb.com/en-us/contact-us/facilities/',
    'Lists six PCB factories; the edge-plating feature was not allocated to every location.')
for name, city, address in [
    ('Aurora', 'Aurora, Colorado', '21101 E. 32nd Parkway'),
    ('Santa Clara', 'Santa Clara, California', '3495 De La Cruz Boulevard'),
    ('Chandler', 'Chandler, Arizona', '6615 W. Boston Street'),
    ('Orange', 'Orange, California', '250 E. Emerson Avenue'),
    ('Maple Grove', 'Maple Grove, Minnesota', '8860 Zachary Lane'),
    ('Placentia', 'Placentia, California', '1900 Petra Lane'),
]:
    site('AdvancedPCB '+name, 'AdvancedPCB', 'United States', city, address, t, '')

t = source('R12_ALPEK_SITES', 'Alpek', 'PET resin manufacturing locations',
    'https://www.alpekpolyester.com/locations/',
    'Identifies each listed facility as a PET resin producer; offices and unrelated production lines are excluded.')
for name, country, city, address in [
    ('Cosoleacaque PET', 'Mexico', 'Cosoleacaque, Veracruz', 'Predio Buenavista de Torres Km. 29'),
    ('Ipojuca PET', 'Brazil', 'Ipojuca, Pernambuco', 'Rodovia PE 60, KM 10'),
    ('Zarate', 'Argentina', 'Zárate, Buenos Aires', 'Camino Santa Ana, Parque Industrial Zarate'),
    ('Pacheco', 'Argentina', 'General Pacheco, Buenos Aires', 'Avda. Gral. Juan Domingo Perón 3659'),
    ('Wilton', 'United Kingdom', 'Redcar', 'Wilton site, Cleveland TS10 4XZ'),
    ('Montreal', 'Canada', 'Montreal, Quebec', '3498 Broadway Avenue'),
    ('Salalah', 'Oman', 'Salalah', 'Salalah Free Zone, Raysut'),
]:
    site('Alpek '+name, 'Alpek', country, city, address, t, 'PM-PET-POLYMER')

site('U.S. Silica Kosse', 'U.S. Silica', 'United States', 'Kosse, Texas',
     'Kosse mining and processing facility', 'R12_USSILICA_KOSSE', 'RAW-QUARTZ')
site('Cargill Cayuga Salt Mine', 'Cargill', 'United States', 'Lansing, New York',
     'Portland Point', 'R12_CARGILL_SALT', 'RAW-HALITE-BRINE')
