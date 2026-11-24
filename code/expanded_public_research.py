"""Second public-evidence pass. Empty site scopes deliberately mean unallocated.

Imported by the builder after additional_public_research; mutates its curated
registers through their helpers. No proposed JSON hierarchy is changed.
"""
from additional_public_research import source, vendor, site, edge, SOURCES

sid=source('R2_FUJIMI_PLANTS','Fujimi','Global network: explicitly named plants',
 'https://www.fujimiinc.co.jp/english/company/network.html',
 'Five directly named Japanese plants; R&D, logistics, offices and ambiguously typed overseas subsidiaries excluded. Specific abrasive-to-plant allocation not given.')
for name,city,address in [
 ('Biwajima','Kiyosu','1-1 Chiryo-2, Nishibiwajima-cho'),
 ('Inazawa','Inazawa','1-1 Ichisuke kawado, Nishijima-cho'),
 ('Kakamigahara','Kakamigahara','1-8 Jyogo-cho-7'),
 ('Kakamihigashimachi','Kakamigahara','62-1 Kakamihigashimachi-5'),
 ('Kakamiyama','Kakamigahara','1-6 Kakamiyama')]:
 site(name+' Plant','Fujimi','Japan',city,address,sid,'')

sid=source('R2_SHINKO_PLANTS','Shinko Electric Industries','Domestic network: plant addresses',
 'https://www.shinko.co.jp/english/corporate/branch/',
 'Six sites explicitly called plants; R&D center, general center and branch offices excluded. Directory does not allocate every package or leadframe to a plant.')
for name,city,address in [
 ('Kohoku','Nagano','80 Oshimada-machi'),
 ('Wakaho','Nagano','1457-1 Wakaho kawada'),
 ('Chikuma','Chikuma','2789-1 Amenomiya'),
 ('Takaoka','Nakano','1216-9 Kusama'),
 ('Arai','Myoko','921-3 Himegawara'),
 ('Kyogase','Agano','1062-5 Kyogase Kogyodanchi')]:
 site(name+' Plant','Shinko Electric Industries','Japan',city,address,sid,'')

sid=source('R2_HERAEUS_PLANTS','Heraeus Electronics','Manufacturing locations',
 'https://www.heraeus-electronics.com/en/about-heraeus-electronics/about-us/locations/',
 'Explicit manufacturing list covers seven cities; Changshu has two named entities. Office and R&D-only cities excluded; material-to-site allocation remains open.')
for name,country,city,address in [
 ('Hanau','Germany','Hanau','Heraeusstrasse 12-14'),
 ('Conshohocken','United States','Conshohocken','Production city documented; street address not confirmed'),
 ('Timisoara','Romania','Timisoara','Production city documented; street address not confirmed'),
 ('Changshu HZCM','China','Changshu','180 Huangpujiang Road'),
 ('Changshu Electronics','China','Changshu','68-2 Lushan Road'),
 ('Zhaoyuan','China','Zhaoyuan','9 Ankang South Road'),
 ('Singapore','Singapore','Singapore','Production city documented; street address not confirmed'),
 ('Johor Bahru','Malaysia','Johor Bahru','Production city documented; street address not confirmed')]:
 site(name+' manufacturing site','Heraeus Electronics',country,city,address,sid,'')

sid=source('R2_OLIN_PLANTS','Olin','Chlor-alkali plant capability directory',
 'https://olinchloralkali.com/about-us/locations/',
 'Site-level product lists identify six relevant chlor-alkali plants. Contradictory table/text entries for other locations are not used for material allocation. Industrial grades, not established semiconductor purity.')
vendor('Olin',sid,'LD:hydrogen LD:hydrogen_chloride LD:sulfuric_acid PM-IND-CHEM',
 'Industrial hydrogen, hydrochloric acid, sulfuric acid and caustic soda branches only; not all salts or electronic grades')
for city,country,nodes in [
 ('McIntosh, Alabama','United States','LD:sodium_hydroxide LD:chlorine LD:hydrogen_chloride LD:hydrogen PM-IND-CHEM'),
 ('Plaquemine, Louisiana','United States','LD:sodium_hydroxide LD:chlorine LD:hydrogen PM-IND-CHEM'),
 ('St. Gabriel, Louisiana','United States','LD:sodium_hydroxide LD:chlorine LD:hydrogen LD:sulfuric_acid PM-IND-CHEM'),
 ('Niagara Falls, New York','United States','LD:sodium_hydroxide LD:chlorine LD:hydrogen_chloride LD:hydrogen LD:sulfuric_acid PM-IND-CHEM'),
 ('Charleston, Tennessee','United States','LD:sodium_hydroxide LD:chlorine LD:hydrogen_chloride LD:hydrogen LD:potassium_hydroxide PM-IND-CHEM'),
 ('Freeport, Texas','United States','LD:sodium_hydroxide LD:chlorine LD:hydrogen_chloride LD:hydrogen LD:sulfuric_acid PM-IND-CHEM'),
 ('Becancour, Quebec','Canada','LD:sodium_hydroxide LD:chlorine LD:hydrogen_chloride LD:hydrogen PM-IND-CHEM')]:
 site(city+' chlor-alkali plant','Olin',country,city,'Plant city documented; gate address not confirmed',sid,nodes)

sid=source('R2_OLIN_10K','Olin','2025 Form 10-K: epoxy products and locations',
 'https://www.sec.gov/Archives/edgar/data/74303/000007430326000027/oln-20251231.htm',
 'Lists epoxy resin manufacture at Freeport and Stade; Guaruja closure decision means it is not added as an available resin source. Product-class evidence does not prove electronic-grade qualification.')
SOURCES[-1]['reliability']='Company annual filing hosted by SEC; dated site and product-class evidence, not customer qualification'
vendor('Olin',sid,'LD:epoxy_resin PM-EPOXY-RESIN','Liquid/solid epoxy resin branch; electronic-grade and specific cresol-novolac/hardener branches unconfirmed')
site('Freeport epoxy resin plant','Olin','United States','Freeport, Texas','Freeport manufacturing complex',sid,'LD:epoxy_resin PM-EPOXY-RESIN')
site('Stade epoxy resin plant','Olin','Germany','Stade','Stade manufacturing complex',sid,'LD:epoxy_resin PM-EPOXY-RESIN')

sid=source('R2_NIPPON_CHEM_PLANTS','Nippon Chemical Industrial','Factories and major products',
 'https://www.nippon-chem.co.jp/en/company/organization/',
 'Separately names four factories and their major products. Head office and Tokyo logistics center excluded. Only directly named gases/chemicals mapped.')
vendor('Nippon Chemical Industrial',sid,'LD:phosphine_gas LD:phosphoric_acid','High-purity phosphine gas and phosphoric acid; phosphoric acid grade at Aichi needs confirmation')
site('Fukushima No.1 Factory','Nippon Chemical Industrial','Japan','Koriyama','2-25 Matsuki-cho',sid,'')
site('Fukushima No.2 Factory','Nippon Chemical Industrial','Japan','Miharu, Fukushima','3 Tennomae',sid,'LD:phosphine_gas')
site('Aichi Factory','Nippon Chemical Industrial','Japan','Taketoyo','1-17-1 Taketoyo-cho',sid,'LD:phosphoric_acid')
site('Tokuyama Factory','Nippon Chemical Industrial','Japan','Shunan','1-2 Harumi-cho',sid,'')

sid=source('R2_PHILLIPS_COKE','Phillips 66','Specialty petroleum coke production',
 'https://www.phillips66.com/specialties/',
 'Explicitly identifies premium needle coke production at Humber and Lake Charles refineries.')
vendor('Phillips 66',sid,'LD:petroleum_needle_coke','Premium petroleum needle coke; suitability for the proposed graphite product still requires qualification')
site('Humber refinery','Phillips 66','United Kingdom','South Killingholme','Humber refinery, North Lincolnshire',sid,'LD:petroleum_needle_coke')
site('Lake Charles refinery','Phillips 66','United States','Westlake, Louisiana','Lake Charles refinery',sid,'LD:petroleum_needle_coke')

sid=source('R2_RAIN_PITCH','Rain Carbon','Carbon products and coal-tar pitch',
 'https://raincarbon.com/products-and-services/carbon-products',
 'Documents coal-tar pitch production and binder function; no implication every pitch grade fits the proposed graphite component.')
vendor('Rain Carbon',sid,'LD:coal_tar_pitch','Coal-tar pitch binder product class')
sid=source('R2_RAIN_HAMILTON','Rain Carbon','Hamilton plant environmental monitoring report',
 'https://www.raincarbon.com/Upload/PDF/Rain-Carbon-Canada-Inc.-August-2025-Ambient-Air-Monitoring-Report.pdf',
 'Environmental report identifies the Hamilton processing plant and its coal-tar pitch production line; site status should be refreshed for operational analysis.')
site('Hamilton coal-tar processing plant','Rain Carbon','Canada','Hamilton, Ontario','725 Strathearne Avenue North',sid,'LD:coal_tar_pitch')

sid=source('R2_JNM_TUNGSTEN','Mitsubishi Materials / Japan New Metals','Tungsten recycling and Akita production',
 'https://news.mmc.co.jp/corporate/en/newsroom/press/news20260909.html',
 'Names Akita plant and integrated tungsten concentrate-to-APT/oxide/powder/carbide capability. Planned capacity increases are not counted as current capacity.')
vendor('Japan New Metals',sid,'LD:tungsten_metal_powder','Tungsten powder; exact high-purity specification requires a grade datasheet')
site('Akita tungsten plant','Japan New Metals','Japan','Akita','Akita plant; precise gate address unconfirmed',sid,'LD:tungsten_metal_powder')

sid=source('R2_E6_DIAMOND','Element Six','Semiconductor diamond grit and micron products',
 'https://www.e6.com/en/products/semiconductors',
 'Names industrial diamond grit, micron and fine-micron products for dicing, lapping and polishing.')
vendor('Element Six',sid,'LD:synthetic_diamond_grit LD:diamond_sic_slurry_glycol','Synthetic diamond abrasive branch only; does not establish glycol-carrier slurry formulation')
sid=source('R2_E6_SHANNON','Element Six','Corporate production history',
 'https://www.e6.com/about/corporate-information',
 'Identifies the Shannon production plant. Specific grade-to-site allocation remains unconfirmed.')
site('Shannon plant','Element Six','Ireland','Shannon, Clare','Shannon plant; precise gate address unconfirmed',sid,'')

sid=source('R2_SE_MICRO_SILANES','Shin-Etsu Chemical','High-purity silane compounds',
 'https://www.shinetsu-encap-mat.jp/e/product/ka.html',
 'Product table explicitly names silicon tetrachloride KA-04 and electronics uses.')
vendor('Shin-Etsu Chemical',sid,'LD:silicon_tetrachloride','High-purity silicon tetrachloride; grade and customer process qualification remain open')
sid=source('R2_EVONIK_STC','Evonik','Siridion STC 1000E',
 'https://www.evonik.com/en/products/se/pr_52012331.html',
 'Ultrapure silicon tetrachloride precursor product for semiconductor epitaxy.')
vendor('Evonik',sid,'LD:silicon_tetrachloride','Ultrapure silicon tetrachloride')

sid=source('R2_DIC_EPOXY','DIC','Semiconductor and printed-wiring-board epoxy applications',
 'https://www.dic-global.com/en/products/epoxy/type/semiconductor.html',
 'Official indexed product page identifies semiconductor/PWB epoxy resin families; full-page fetch was blocked, so grade-level detail requires direct document review.')
vendor('DIC',sid,'LD:epoxy_resin PM-EPOXY-RESIN','Semiconductor/PWB epoxy resin family; specific resin/hardener combination requires selection')
sid=source('R2_DIC_PHENOLITE','DIC','Novolac phenol resin curing agents',
 'https://www.dic-global.com/ap/products/epoxy/phenolite/',
 'Official product page identifies novolac phenol curing-agent family; no specific plant assignment.')
vendor('DIC',sid,'LD:phenolic_hardener PM-EPOXY-RESIN','Novolac phenolic epoxy curing-agent branch')

sid=source('R2_TOHO_TITANIUM','Toho Titanium','High-purity titanium ingots',
 'https://www.toho-titanium.co.jp/en/products/hpti/',
 'Dedicated electron-beam melting of high-purity titanium sponge produces 4N5-5N titanium ingots.')
vendor('Toho Titanium',sid,'LD:titanium LD:ultra_high_purity_metals','Titanium ingot branch only; published range 4N5-5N does not establish 6N or every metal in combined node')

sid=source('R2_TREIBACHER_CERIA','Treibacher Industrie','Auerpol cerium-oxide polishing agents',
 'https://treibacher.com/en/products/auerpol-polishing-agents/',
 'Cerium-oxide-based polishing products for glass/precision optics; semiconductor CMP-grade qualification is not established.')
vendor('Treibacher Industrie',sid,'LD:ceria_abrasive','Cerium-oxide polishing abrasive; composition and semiconductor grade require confirmation')

sid=source('R2_MPIL_TANTALATE','Metallurgical Products India','Potassium fluorotantalate',
 'https://www.mpil.co.in/pottassium-fluorotantalate.html',
 'Manufacturer product specification identifies K2TaF7 as a tantalum-powder feedstock.')
vendor('Metallurgical Products India',sid,'LD:potassium_heptafluorotantalate','Potassium fluorotantalate; electronic-grade qualification and leadership rank not independently established')

sid=source('R2_AURAS_COOLER','Auras Technology','Company overview: graphics-card cooling modules',
 'https://www.auras.com.tw/Overview/9',
 'Explicitly documents graphics-card cooling-module manufacture; does not identify a specific NVIDIA card purchase order.')
vendor('Auras Technology',sid,'2','Graphics-card cooling-module product family')
sid=source('R2_AURAS_PLANTS','Auras Technology','Published production footprint presentation',
 'https://www.auras.com.tw/CMSFS/InformationCenters/English/ecfc7b18-d55e-4ca3-a673-b449f83d051c.pdf',
 'Identifies production-site cities; allocation of a particular cooler design to a plant remains unconfirmed.')
for city in ['Kunshan','Guangzhou','Chongqing','Hefei']:
 site(city+' cooling-module plant','Auras Technology','China',city,'Published production city; gate address unconfirmed',sid,'')

sid=source('R2_SENJU_BALL','Senju Metal Industry','Semiconductor solder balls',
 'https://www.senju.com/en/products/soldering_materials/solder_ball/',
 'Documents semiconductor bumping solder balls and selectable compositions; the exact SAC305 option needs its alloy specification.')
vendor('Senju Metal Industry',sid,'SC-SOLDER-BALL','BGA solder-ball product class; SAC305 composition and low-alpha grade require confirmation')
sid=source('R2_SENJU_PLANTS','Senju Metal Industry','Global locations: explicitly named Japanese plants',
 'https://www.senju.com/en/company/global-network.php',
 'Seven Japanese plants are explicitly identified; offices, labs and ambiguously typed foreign facilities excluded. Solder-ball grade-to-plant mapping remains unconfirmed.')
for name,city,address in [
 ('Ichinoseki','Ichinoseki','86-5 Marumori, Nagasaka, Higashiyama-cho'),
 ('Matsuyama','Moka','1 Matsuyama-cho'),
 ('Kinugaoka','Moka','1-1 Kinugaoka'),
 ('Soka','Soka','2-11-7 Yatsuka'),
 ('Nishiwaki','Nishiwaki','257-1 Wada-cho'),
 ('Naka','Taka, Hyogo','101-1 Doibata, Nakakusakamoto'),
 ('Miyazaki','Miyazaki','17880-25 Higashikaminaka, Sadowara-cho')]:
 site(name+' Plant','Senju Metal Industry','Japan',city,address,sid,'')

sid=source('R2_UNION_PCB','Union Tool','PCB drill and router catalog',
 'https://www.uniontool.co.jp/en/catalog/pcb.html',
 'Explicit tungsten-carbide PCB cutting-tool product family; tools are consumables, not constituents left in a board.')
vendor('Union Tool',sid,'DC-PCB-DRILL DC-CUTTING-FLUID','Tungsten-carbide drill/router and end-mill branch only; coolant branch not evidenced')
sid=source('R2_UNION_NAGAOKA','Union Tool','Our business: Nagaoka production lines',
 'https://uniontool.co.jp/en/corporate/about.html',
 'Names PCB-drill manufacture and the main Nagaoka factory production lines.')
site('Nagaoka factory','Union Tool','Japan','Nagaoka','2706-6 Togawa, Settaya-machi',sid,'DC-PCB-DRILL')
sid=source('R2_UNION_PLANTS','Union Tool','Domestic factory addresses',
 'https://uniontool.co.jp/en/corporate/global.html',
 'Directory identifies Nagaoka Nakanoshima and Mitsuke factories; other offices and laboratories excluded. Does not assign every tool to each site.')
site('Nagaoka Nakanoshima factory','Union Tool','Japan','Nagaoka','807-5 Nakanoshima',sid,'')
site('Mitsuke factory','Union Tool','Japan','Mitsuke','3-1 Shinko-cho',sid,'')

sid=source('R2_UYEMURA_NICKEL','C. Uyemura','Electrolytic nickel processes',
 'https://www.uyemura.com/metal-finishes/electrolytic-nickel.html',
 'Official electrolytic nickel-plating chemistry family; nickel anodes and process-specific composition require separate evidence.')
vendor('C. Uyemura',sid,'DC-NI-PLATE','Electrolytic nickel bath chemistry branch only; anode supply not established')
sid=source('R2_UYEMURA_PLANTS','C. Uyemura','Locations: chemical-production sites',
 'https://www.uyemura.co.jp/en/company/location/',
 'Hirakata Chemical Plant is distinguished from the colocated research laboratory; Taiwan and Thailand locations explicitly include chemical production.')
site('Hirakata Chemical Plant','C. Uyemura','Japan','Hirakata','5-1 Deguchi 1-chome',sid,'')
site('Taoyuan chemical-production site','C. Uyemura','Taiwan','Taoyuan','7-1 Minzu Street, Dayuan District',sid,'')
site('Pathum Thani chemical-production site','C. Uyemura','Thailand','Khlong Luang, Pathum Thani','60/63 Navanakorn Industrial Estate Zone 2, Tambol Klong 1',sid,'')

sid=source('R2_CHEMETALL_LUBE','Chemetall','Gardolube metal-forming lubricants',
 'https://www.chemetall.com/global/en/technologies/gardolube',
 'Describes metal-forming lubricants; does not establish a specific stamping bath or degreaser formulation.')
vendor('Chemetall',sid,'DC-STAMP-LUBE','Metal-forming/stamping lubricant branch; alkaline degreaser requires a separate product match')

sid=source('R2_ELANTAS_ENAMEL','ELANTAS','Polyimide wire enamels',
 'https://www.elantas.com/solutions/product-groups/wire-enamels/',
 'Explicitly lists polyimide wire enamel and insulation around copper/aluminum windings. Different enamel chemistries are alternatives, not simultaneous requirements.')
vendor('ELANTAS',sid,'PM-POLYIMIDE','Polyimide magnet-wire enamel; exact monomers/solvent system require selected grade')
edge('E0525',sid,'supported_product_class','Polyimide enamel is an available magnet-wire insulation option; exact wire/core grade and selected fan design remain unconfirmed.')

sid=source('R2_IVL_PET','Indorama Ventures','PET resin products and manufacturing sites',
 'https://www.indoramaventures.com/en/our-products/pet',
 'Names PET resin and Haldia production site in a product/site table. Bottle/sheet grade does not automatically meet electronics-film or felt requirements.')
vendor('Indorama Ventures',sid,'PM-PET-POLYMER','PET resin; film/felt application-grade suitability remains unconfirmed')
site('Haldia PET plant','Indorama Ventures','India','Haldia','IVL Dhunseri Petrochem Industries Haldia site',sid,'PM-PET-POLYMER')

sid=source('R2_TRONOX_PLANTS','Tronox','Production locations: titanium dioxide and titanium chemicals',
 'https://www.tronox.com/about-us/global-locations/',
 'Stallingborough explicitly manufactures titanium dioxide pigment; Thann explicitly produces titanium tetrachloride. Offices excluded; crystal phase and electronics grade require confirmation.')
vendor('Tronox',sid,'PM-TIO2 LD:titanium_tetrachloride','TiO2 pigment and titanium tetrachloride; rutile grade and semiconductor precursor purity must be checked')
site('Stallingborough pigment plant','Tronox','United Kingdom','Stallingborough','Laporte Road, DN40 2PR',sid,'PM-TIO2')
site('Thann titanium-chemicals plant','Tronox','France','Thann','95 Rue du General de Gaulle',sid,'LD:titanium_tetrachloride')

sid=source('R2_AGC_SODA_GLASS','AGC','AS2 soda-lime float glass',
 'https://agc-electronics.com/en/specialty-glass/products/as2',
 'Documents soda-lime float glass as a product; does not establish suitability as a leading-edge semiconductor photomask blank.')
vendor('AGC',sid,'LD:soda_lime_glass','Soda-lime float glass; do not equate this product with DUV/EUV mask blanks')
sid=source('R2_GLASS_RAW','AGC Glass Europe','From sand to glass',
 'https://www.agc-glass.eu/en/products/sand-glass',
 'Float-glass batch identifies sand, soda, limestone and dolomite. Exact chemistry/quantities and high-purity substrate manufacturing differ by glass product.')
edge('E0292 E0293 E0294',sid,'supported_process_input','Sand/silica, soda and limestone/dolomite are documented float-glass feedstocks. This is category-level chemistry, not an observed direct mine shipment.')

sid=source('R2_SANAPRO_PAG','San-Apro','Photoacid generator product families',
 'https://www.san-apro.co.jp/en/products/acid-uv/',
 'Names ionic sulfonium and iodonium photoacid-generator products; exact onium fluorosulfonate and semiconductor purity require grade confirmation.')
vendor('San-Apro',sid,'LD:photoacid_generators','Onium photoacid-generator family; anion chemistry and lithography-grade match need confirmation')

sid=source('R2_MOLEX_DP','Molex','DisplayPort receptacle 0472720001',
 'https://www.molex.com/en-us/products/part-detail/0472720001',
 'Explicit DisplayPort receptacle product with 20 circuits; does not establish use on the submitted GPU card.')
vendor('Molex',sid,'6.2','DisplayPort receptacle product class; selected card pinout/mechanical fit require qualification')
sid=source('R2_TE_HDMI','TE Connectivity','HDMI connector families',
 'https://www.te.com/en/products/connectors/audio-and-video-connectors/hdmi-connectors.html',
 'Official HDMI connector capability; selected Type A high-speed version and board footprint require confirmation.')
vendor('TE Connectivity',sid,'6.1','HDMI receptacle family; exact GPU I/O design not established')

sid=source('R2_NATURAL_EARTH','Natural Earth','Small-scale world country boundaries',
 'https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/',
 'World basemap only; cached boundary data are not factory-location evidence. Mirror download path is recorded in the existing build script.')
SOURCES[-1]['reliability']='Public-domain cartographic reference; coarse boundaries unsuitable for detailed routing'

sid=source('R2_KANTO_PLANTS','Kanto Chemical','Domestic factory addresses',
 'https://www.kanto.co.jp/corp/officejp.html',
 'Six named factories separated from laboratories and logistics centers. Directory does not assign individual ultra-pure chemicals to a factory.')
for name,city,address in [
 ('Kanto Soka','Soka','1-7-1 Inari'),
 ('Kanto Isehara','Isehara','21 Suzukawa'),
 ('Kanto Okayama','Misaki, Okayama','70 Fujiwara'),
 ('Kanto Omuta','Omuta','2 Shinkai-machi'),
 ('Kanto Iwate','Oshu','31-3 Matsunagane, Esashi Iwayado'),
 ('Kanto Mie','Tsu','2-1-1 Anotsudai')]:
 site(name+' Factory','Kanto Chemical','Japan',city,address,sid,'')

sid=source('R2_DENKA_OMUTA','Denka','Omuta plant site report',
 'https://denka_sustainability.disclosure.site/en/themes/763/',
 '2023 report explicitly names spherical fused silica and spherical alumina manufacture at Omuta. Current grades and operating status require refresh before disruption modeling.')
site('Denka Omuta Plant','Denka','Japan','Omuta','1 Shinkai-machi',sid,
 'LD:fused_silica_filler LD:alumina PM-FUSED-SILICA SC-CERAMIC-FILLER',
 'documented_in_2023_site_report_current_status_not_independently_refreshed')

sid=source('R2_TANAKA_HANGZHOU','TANAKA','Hangzhou bonding-wire production',
 'https://www.tanaka.co.jp/english/company/group/tec/',
 'Explicit manufacture of bonding wires at Hangzhou. No customer procurement allocation or plant gate street address disclosed.')
site('TANAKA Hangzhou bonding-wire plant','TANAKA','China','Hangzhou','Manufacturing city documented; gate address unconfirmed',sid,
 'LD:bond_wires LD:fine_metal_wire SC-BOND-WIRE')
sid=source('R2_TANAKA_SINGAPORE','TANAKA','Singapore bonding-wire manufacture',
 'https://www.tanaka.co.jp/english/company/group/tes/',
 'Subsidiary activities explicitly include bonding-wire manufacture in Singapore; precise site address not established by this page.')
site('TANAKA Singapore bonding-wire plant','TANAKA','Singapore','Singapore','Manufacturing city documented; gate address unconfirmed',sid,
 'LD:bond_wires LD:fine_metal_wire SC-BOND-WIRE')
sid=source('R2_TANAKA_SHONAN','TANAKA','Electronics group: Shonan satellite plant',
 'https://www.tanaka.co.jp/english/company/group/td/',
 'Explicitly names Shonan satellite plant in Hiratsuka; head-office location is not automatically asserted to be a plant.')
site('TANAKA Shonan satellite plant','TANAKA','Japan','Hiratsuka','Shonan satellite plant; gate address unconfirmed',sid,'')

sid=source('R2_ENTEGRIS_KAOHSIUNG','Entegris','Kaohsiung Science Park manufacturing facility',
 'https://www.entegris.com/en/home/about-us/manufacturing/kaohsiung-science-park.html',
 'Names a manufacturing facility for filters, drums and advanced deposition materials. Does not identify every individual precursor produced there.')
vendor('Entegris',sid,'LD:deposition_materials','Advanced deposition materials category; no assignment of individual gases to this site')
site('Entegris Kaohsiung Science Park plant','Entegris','Taiwan','Kaohsiung','Kaohsiung Science Park; gate address unconfirmed',sid,'LD:deposition_materials')

sid=source('R2_WIELAND_STRIP','Wieland','Copper-alloy strip portfolio',
 'https://www.wieland.com/en/products/strips-and-foils/bare-strips-and-foils/copper-strips-and-foils',
 'Lists copper-iron C19400/K65 strip and rolled delivery formats. Other Cu-Fe-Ni-Sn-Zn alloy branches are not all established by one grade.')
vendor('Wieland',sid,'LD:copper_alloy_strip','C19400 copper-iron strip branch; not a claim that all named alloying elements are simultaneously necessary')
sid=source('R2_SPECIALMETALS_42','Special Metals','Technical bulletin register: NILO 42',
 'https://www.specialmetals.com/documents/technical-bulletins/',
 'Official technical bulletin register identifies NILO 42 controlled-expansion alloy. Strip dimensions and manufacturing location remain unconfirmed.')
vendor('Special Metals',sid,'LD:alloy_42_strip','Alloy 42 material family; strip form and grade tolerances need a current quote/specification')
sid=source('R2_LINDE_METHANE','Linde','High-purity methane 4.5',
 'https://www.linde-gas.nl/shop/en/nl-ig/methane-45-detector-p-methaan-45-detector-114',
 'Documents a purified methane cylinder product, not the proposed upstream methane-to-syngas factory connection.')
vendor('Linde',sid,'LD:methane_feedstock','Purified methane gas; production feedstock volume and specification require qualification')
sid=source('R2_MICRON_GDDR6','Micron','GDDR6 and GDDR6X graphics DRAM products',
 'https://www.micron.com/products/memory/graphics-memory',
 'Confirms manufacture/product capability for named graphics-memory families. Does not prove a separately sold bare die or a specific factory allocation.')
vendor('Micron',sid,'SC-DRAM-DIE','Manufacturer of GDDR6/GDDR6X products; the node is a bare internal die rather than a confirmed independently sold part',
 'internal_die_capability_not_independent_bare_die_sales_evidence')

sid=source('R2_LYB_SYNGAS','Texas Commission on Environmental Quality / LyondellBasell','La Porte syngas and methanol permit application, February 2025, section 1',
 'https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/37697-ac.pdf',
 'PDF page 7 identifies LyondellBasell Acetyls as operator, 11603B Strang Road, synthesis-gas manufacture and catalytic methanol production. It documents an internal process, not a confirmed sale to GPU-material suppliers.')
SOURCES[-1]['reliability']='Company permit application hosted by Texas environmental regulator; dated process/operator/site evidence'
vendor('LyondellBasell',sid,'LD:synthesis_gas LD:methanol','Documented syngas/methanol production; independent syngas merchant sale and electronic-grade methanol not established')
site('La Porte syngas and methanol unit','LyondellBasell','United States','La Porte, Texas','11603B Strang Road, La Porte, TX 77571',sid,'LD:synthesis_gas LD:methanol')
edge('E0270',sid,'supported_process_input','The permit explicitly describes catalytic conversion of syngas into methanol. This supports a process relationship, not a shipment to another factory.')
sid=source('R2_LAPMASTER_PAD','Lapmaster Wolters','Lapping and polishing pads',
 'https://www.lapmaster-wolters.com/lapping-polishing-pads-and-accessories.html',
 'Identifies polyurethane pad and polyurethane-impregnated polyester felt pad designs. Does not establish separately sold bare matrix/felt or a universal CMP pad recipe.')
vendor('Lapmaster Wolters',sid,'LD:polishing_pads','Polyurethane and polyurethane-impregnated polyester-felt polishing pad options; semiconductor grade requires qualification')
edge('E0175 E0176',sid,'supported_product_class','Polyurethane/polyester-felt pad construction is documented for particular pad options; not every polishing pad needs both layers.')
sid=source('R2_MSI_CARD','MSI','GeForce RTX 5080 16G EXPERT OC specifications',
 'https://www.msi.com/Graphics-Card/GeForce-RTX-5080-16G-EXPERT-OC/Specification',
 'Explicit branded finished graphics-card product; specifications include GDDR7. This does not expose its complete supplier BOM or assembly factory.')
vendor('MSI',sid,'0','Finished RTX 5080-class graphics card; the submitted generic component list is not asserted to be this model exact BOM')
sid=source('R2_TSMC_LOGIC','TSMC','Logic foundry manufacturing technologies',
 'https://www.tsmc.com/english/dedicatedFoundry/technology/logic',
 'Official portfolio identifies logic processes in volume production. Node-specific capability is not a customer-to-fab allocation or proof a proposed alternative technology is interchangeable.')
vendor('TSMC',sid,'LD:logic_die_fabricated','Logic foundry capability; GPU design, process node and specific fab allocation require separate evidence')
sid=source('R2_NDPP_PHOSPHORUS','Export Credit Agency of Kazakhstan','Novo-Dzhambul Phosphorus Plant profile, February 2025',
 'https://kazakhexport.kz/en/news/novosti-kompanii/1640',
 'Identifies yellow-phosphorus production at NDPP in Taraz; semiconductor purification and ownership affiliation are not established.')
SOURCES[-1]['reliability']='Export-credit agency enterprise profile; named production capability/site, not electronic-grade qualification'
vendor('Novo-Dzhambul Phosphorus Plant',sid,'LD:white_phosphorus','Yellow/white elemental phosphorus product class; impurity grade and semiconductor purification require evidence')
site('Novo-Dzhambul phosphorus plant','Novo-Dzhambul Phosphorus Plant','Kazakhstan','Taraz','Taraz, Zhambyl Region; factory-gate address unconfirmed',sid,'LD:white_phosphorus')

# Gap follow-up: only fully inspected product evidence is admitted here.
sid=source('R3_CERATIZIT_WCCO','CERATIZIT','Cemented-carbide production chain',
 'https://ceratizit.com/int/en/cemented-carbide-to-products/production.html',
 'Describes tungsten carbide powder, cobalt binder and sintered hardmetal manufacture. Process-stage times on this page are not total factory lead times; ore-to-product relationships skip intermediate plants.')
vendor('CERATIZIT',sid,'PM-WC-COBALT','Sintered tungsten-carbide/cobalt hardmetal; no specific PCB-drill grade, customer or market-share rank established')
sid=source('R3_CERATIZIT_REUTTE','CERATIZIT','Company history and Reutte production-site description',
 'https://ceratizit.com/int/en/about-us/from-pioneer-to-global-player.html',
 'Explicitly identifies Reutte as a production site. Corporate hardmetal capability does not allocate a particular WC-Co grade to this plant.')
site('CERATIZIT Reutte production site','CERATIZIT','Austria','Reutte','Production city documented; gate address unconfirmed',sid,'')
sid=source('R3_CERATIZIT_CLOSURES','CERATIZIT','Production-network reorganisation, 5 March 2025',
 'https://ceratizit.com/int/fr/news-and-media/news-and-press-releases/2025/CERATIZIT-reorganises-its-production-network.html',
 'Besigheim and Empfingen were announced for closure during 2026. They are excluded from new operating-plant candidates rather than assumed active from a historical directory.')
sid=source('R3_MPET_RELEASE','Mitsubishi Chemical America, Polyester Film Division','Silicone release polyester film products',
 'https://www.m-petfilm.com/products-by-type/silicone-release-polyester-films/',
 'Documents silicone-coated PET release film including electronic and ceramic-capacitor applications. Does not establish a mandatory thermal-pad input, exact silicone chemistry, or single-use disposal.')
vendor('Mitsubishi Chemical America Polyester Film Division',sid,'DC-PET-LINER','Silicone-coated PET release-film product class; required thickness, adhesive compatibility and application grade unqualified')
edge('E0485',sid,'supported_product_class','PET carrier film in silicone-coated release liner is documented; this is not proof of a particular supplier shipment or universal liner use.')
sid=source('R3_MPET_GREER','Mitsubishi Chemical America, Polyester Film Division','Greer production facility and coating capability',
 'https://www.m-petfilm.com/about-us/general-information/',
 'Documents polyester-film manufacture and inline coating/coextrusion in Greer. Exact release-film grade allocation is not expressly stated, so the plant scope is left unallocated.')
site('Mitsubishi polyester-film Greer plant','Mitsubishi Chemical America Polyester Film Division','United States','Greer, South Carolina','2001 Hood Road, Greer, SC',sid,'')
sid=source('R3_TECHNIC_TIN','Technic','Electrolytic tin chemistry',
 'https://www.technic.com/applications/industrial/electrolytic-plating/electrolytic-tin-chemistry',
 'Lists matte-tin plating formulations based on sulfuric acid or methanesulfonic acid. This supports the bath-chemistry branch, not tin anode production or a disposable-bath assumption.')
vendor('Technic',sid,'DC-TIN-PLATE','Matte-tin bath chemistry branch only; tin anodes, final plating specification and replacement frequency require separate evidence')
sid=source('R3_TECHNIC_PLANTS','Technic','Global facilities with manufacturing functions',
 'https://www.technic.com/about/about-technic-global-facilities',
 'Admitted entries explicitly state manufacture; headquarters-only, sales-only, R&D-only and equipment plants excluded. Individual plating-product allocation is unverified. This subset is not the complete global footprint.')
for name,country,city,address in [
 ('Cranston chemical plant','United States','Cranston, Rhode Island','1 Spectacle Street'),
 ('Woonsocket semiconductor plant','United States','Woonsocket, Rhode Island','601 Park East Drive'),
 ('Woonsocket imaging-products plant','United States','Woonsocket, Rhode Island','41 Century Drive'),
 ('Woonsocket engineered-powders plant','United States','Woonsocket, Rhode Island','300 Park East Drive'),
 ('Amiens chemical plant','France','Amiens','121 Rue Andre Durouchez'),
 ('Chalon chemical plant','France','Chalon-sur-Saone','1 Rue Georges Claude'),
 ('Noyarey manufacturing site','France','Noyarey','37 route du Ruisset'),
 ('Anaheim manufacturing site','United States','Anaheim, California','1170 Hawk Circle'),
 ('Markham manufacturing site','Canada','Markham, Ontario','195 Riviera Drive'),
 ('Saint Denis manufacturing site','France','Saint-Denis','15 Rue de la Montjoie')]:
 site('Technic '+name,'Technic',country,city,address,sid,'')
