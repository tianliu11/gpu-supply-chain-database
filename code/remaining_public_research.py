"""Further source-specific closure work; preserves unknown grades and customers."""
from additional_public_research import source, vendor, site, edge as register_edge

CLAIMS=[]
def edge(ids,sid,status,note):
    register_edge(ids,sid,status,note)
    CLAIMS.extend(dict(edge_id=eid,source_ids=sid,validation_status=status,claim_scope=note) for eid in ids.split())

s=source('R6_SHIN_PLANTS','Shin-Etsu Chemical','Plants and site-level product lists',
 'https://www.shinetsu.co.jp/en/company/network/plant/',
 'Six Japanese manufacturing locations; named product classes only. Isesaki lithography class is not an allocation of each resist ingredient.')
for name,city,address,nodes in [
 ('Naoetsu','Joetsu','28-1 Nishifukushima, Kubiki-ku','LD:synthetic_fused_quartz PM-PDMS-SILICONE LD:photoresists LD:sodium_hydroxide'),
 ('Takefu','Echizen','1-5 Kitago 2-chome','PM-PDMS-SILICONE'),
 ('Isobe','Annaka','13-1 Isobe 2-chome','PM-PDMS-SILICONE LD:encapsulation_resins'),
 ('Matsuida','Annaka','1-10 Hitomi, Matsuida-machi','PM-PDMS-SILICONE'),
 ('Kashima','Kamisu','1 Towada','LD:synthetic_fused_quartz'),
 ('Isesaki','Isesaki','88-1 Kokuryo-cho','')]:
    site('Shin-Etsu '+name+' manufacturing site','Shin-Etsu Chemical','Japan',city,address,s,nodes)
vendor('Shin-Etsu Chemical',s,'LD:photoresists LD:sodium_hydroxide LD:encapsulation_resins',
 'Photoresist, caustic-soda and epoxy-mould-compound product classes; exact grade/customer unspecified')

s=source('R6_SILTRONIC_SITES','Siltronic','Production locations and wafer capabilities',
 'https://www.siltronic.com/en/our-company/sites.html',
 'Four manufacturing complexes; Munich and sales offices excluded. Portland is 200 mm, not a 300 mm GPU-logic substitute. Singapore adjacent fabs grouped.')
for name,country,city,address in [
 ('Burghausen','Germany','Burghausen','Johannes-Hess-Strasse 24'),
 ('Freiberg','Germany','Freiberg','Berthelsdorfer Strasse 113'),
 ('Portland 200 mm','United States','Portland, Oregon','7200 NW Front Avenue'),
 ('Singapore wafer complex','Singapore','Singapore','10, 12 and 77 Tampines Industrial Avenue 5')]:
    site('Siltronic '+name,'Siltronic',country,city,address,s,'LD:wafer',
         operating_status='public_production_site;diameter_and_grade_specific;not_automatically_interchangeable')

s=source('R6_GW_SITES','GlobalWafers','Subsidiary manufacturing locations',
 'https://www.gw-semi.com/overview-locations/',
 'Eight existing plants with product descriptions. Merano ingots and St Peters SOI are not prime-wafer substitutes. Sherman new-fab commissioning requires newer evidence.')
for name,country,city,address,nodes in [
 ('GlobiTech','United States','Sherman, Texas','200 FM 1417 West','LD:wafer'),
 ('MEMC St Peters SOI','United States','St. Peters, Missouri','501 Pearl Drive',''),
 ('MEMC Korea','South Korea','Cheonan','854 Manghyang-ro, Seonggeo-eup','LD:wafer'),
 ('Taisil','Taiwan','Hsinchu','2 Creation Road 1','LD:wafer'),
 ('MEMC Malaysia','Malaysia','Petaling Jaya','Jalan SS 8/2, Sungai Way Free Industrial Zone','LD:wafer'),
 ('MEMC Merano ingots','Italy','Merano','Via Nazionale 59',''),
 ('MEMC Novara','Italy','Novara','Viale Gherzi 31','LD:wafer'),
 ('MEMC Japan','Japan','Utsunomiya','11-2 Kiyohara Industrial Park','LD:wafer PM-SI-WAFER')]:
    site('GlobalWafers '+name,'GlobalWafers',country,city,address,s,nodes,
         operating_status='listed_manufacturing_site;product_and_diameter_specific')

s=source('R6_LINDE_PHOENIX','Linde','Existing Phoenix gas complex and announced expansion, July 2026',
 'https://www.linde.com/news-and-media/2026/linde-to-invest-1-billion-to-support-major-us-semiconductor-facility-expansion',
 'Existing three ASUs distinguished from two planned additions. Nitrogen/oxygen/argon scope; customer unnamed; planned units not counted as operating backups.')
site('Linde Phoenix existing on-site gas complex','Linde','United States','Phoenix, Arizona',
 'Customer complex city documented; gate undisclosed',s,'LD:nitrogen LD:oxygen_gas LD:argon LD:ultra_pure_argon LD:electronic_gases',
 operating_status='existing_three_ASUs;planned_expansion_excluded')
s=source('R6_LINDE_ELECTRONICS','Linde Engineering','Electronics gas production and supply modes',
 'https://www.linde-engineering.com/industries/electronics',
 'On-site ASU/electrolysis and bulk tanker modes; Villach hydrogen plant example. Local utility supply cannot be assumed to pass through a cargo airport.')
site('Linde Villach on-site hydrogen plant','Linde','Austria','Villach',
 'At Infineon production site; street not specified',s,'LD:hydrogen',
 operating_status='official_operating_example;purification_and_ownership_boundary_require_check')
edge('E0223',s,'supported_process_stage','Purification can upgrade hydrogen; purity is process-specific. No universal transport step or exact qualification established.')

s=source('R6_BASF_PBT','BASF','Ultradur B4300 G6 manufacturer product specification',
 'https://download.basf.com/p1/8a8082587fd4b608017fd63d9cd26b1f/en/ULTRADUR%3Csup%3E%C2%AE%3Csup%3E_B4300_G6_HR',
 'PBT injection-moulding compound with 30 percent glass fibres. Supplies compound, not proof BASF manufactures the submitted fan impeller.')
vendor('BASF',s,'SC-PBT-GF30','PBT-GF30 compound branch only; finished fan part supplier not established')
edge('E0531 E0532',s,'supported_material_class_composition',
 'PBT and glass fibres make the documented compound. Chopped-fibre branch selected, not woven cloth; fan geometry and qualification unverified.')

s=source('R6_OKMETIC','Okmetic','Vantaa manufacturing scope and volume-production announcement',
 'https://www.okmetic.com/about-us/news-articles/okmetic-vantaa-fab-expansion-enters-volume-production/',
 'February 2026 confirmation of 150-200 mm wafer production; expanded buildings grouped as one campus. Not an owned 300 mm plant.')
site('Okmetic Vantaa wafer campus','Okmetic','Finland','Vantaa','Koivuhaka manufacturing campus',s,'LD:wafer PM-SI-WAFER',
 operating_status='volume_production_2026;150_200mm;not_300mm_logic_backup')
s=source('R6_SK_SITES','SK Siltron','Domestic plants and product diameters',
 'https://www.sksiltron.com/m/en/company/office01.do',
 'Gumi 1 crystal growth, 2 wafering, 3 growth/wafering/epitaxy. Seoul office excluded; product diameter differs by site.')
for name,address,nodes in [
 ('1 crystal growth','435 Suchul-daero',''),
 ('2 200mm wafering','53 Imsu-ro','LD:wafer'),
 ('3 300mm wafering','132-11 3gongdan 3-ro','LD:wafer')]:
    site('SK Siltron Gumi '+name,'SK Siltron','South Korea','Gumi',address,s,nodes)
s=source('R6_IQE_SITES','IQE','Manufacturing-platform capability matrix and addresses',
 'https://www.iqep.com/about-us/sites/',
 'Seven manufacturing locations; platform evidence only. Epitaxial material is not a finished LED die. No automatic GaAs/sapphire allocation to every site.')
for name,country,city,address in [
 ('Cardiff','United Kingdom','Cardiff','Pascal Close, St Mellons'),
 ('Newport','United Kingdom','Newport','Celtic Way, Marshfield'),
 ('Wafer Technology','United Kingdom','Milton Keynes','34 Maryland Road, Tongwell'),
 ('Massachusetts','United States','Taunton, Massachusetts','200 John Hancock Road'),
 ('North Carolina','United States','Greensboro, North Carolina','494 Gallimore Dairy Road'),
 ('Galaxy substrates','United States','Spokane, Washington','9922 East Montgomery Avenue 7'),
 ('Taiwan','Taiwan','Hsinchu','2-1 Li-Hsin Road')]:
    site('IQE '+name,'IQE',country,city,address,s,'')
s=source('R6_PHOTRONICS','Photronics','Investor FAQ: IC versus display-mask manufacturing',
 'https://photronicsinc.gcs-web.com/investor-faqs',
 'Nine IC-mask manufacturing cities; Hefei display-only. Hsinchu facilities grouped because separate gate addresses not established here; EUV qualification not implied.')
for city,country in [('Brookfield, Connecticut','United States'),('Allen, Texas','United States'),
 ('Boise, Idaho','United States'),('Bridgend','United Kingdom'),('Dresden','Germany'),
 ('Cheonan','South Korea'),('Hsinchu','Taiwan'),('Taichung','Taiwan'),('Xiamen','China'),('Hefei','China')]:
    site('Photronics '+city+' manufacturing','Photronics',country,city,
         'Manufacturing city documented; gate not established',s,'LD:photomasks' if city!='Hefei' else '',
         operating_status='listed_manufacturing_location;city_group_not_independent_plant_count')

s=source('R6_IND_SITES','Indium Corporation','Manufacturing directory with addresses',
 'https://www.indium.com/corporate/facilities/',
 'Thirteen production addresses. Headquarters, offices and the Penang warehouse excluded even though the directory labels that warehouse manufacturing. Product allocation remains separate.')
for name,country,city,address in [
 ('Jalisco','Mexico','Santa Cruz del Valle','Carretera a El Zapote 100-C07-C08'),
 ('Clinton','United States','Clinton, New York','34 Robinson Road'),
 ('Utica Lincoln','United States','Utica, New York','1676 Lincoln Avenue'),
 ('Utica Business Park','United States','Utica, New York','111 Business Park Drive'),
 ('Rome','United States','Rome, New York','5836 Success Drive'),
 ('Chicago','United States','Elk Grove Village, Illinois','80 Scott Street'),
 ('Korea','South Korea','Cheongju','24 Jikjidae-ro 436beon-gil'),
 ('Chennai','India','Chennai','Shed A, NP7 Guindy Industrial Estate'),
 ('UK','United Kingdom','Milton Keynes','7 Newmarket Court, Kingston'),
 ('Penang','Malaysia','Batu Kawan','PMT 795 Jalan Cassia Selatan 3/11'),
 ('Singapore','Singapore','Singapore','29 Kian Teck Avenue'),
 ('Suzhou','China','Suzhou','Building E, 77 Xiapu Road'),
 ('Landshut','Germany','Landshut','Fragnerstrasse 4')]:
    site('Indium Corporation '+name,'Indium Corporation',country,city,address,s,'')
s=source('R6_HENKEL_SONGDO','Henkel','Songdo electronics-adhesive plant inauguration',
 'https://www.henkel.com/press-and-media/press-releases-and-kits/2022-08-23-henkel-korea-inaugurates-songdo-plant-delivering-world-class-production-capacity-for-electronics-solutions-1738854',
 'Production began in 2022; semiconductor-packaging adhesives. Specific silver-filled formulation allocation not disclosed.')
site('Henkel Songdo electronics-adhesive plant','Henkel','South Korea','Incheon','Songdo industrial district; gate unverified',s,'LD:die_attach_materials')

s=source('R6_TI_PACKAGING','Texas Instruments / National Semiconductor','Semiconductor Packaging Assembly Technology, SNOA286',
 'https://www.ti.com/lit/an/snoa286/snoa286.pdf',
 'Historical technical description of leadframe, wire-bond PBGA and hermetic options. Not proof of a specific modern GPU, memory or power-device recipe.')
edge('E0042 E0043 E0046',s,'supported_category_membership',
 'Packaging catalogue contains leadframes, wires and die-attach options; not universally mandatory.')
edge('E0152 E0153 E0574 E0575',s,'supported_material_class_composition',
 'Selected silver-filled epoxy die attach: epoxy and silver-metal branches, not silver salt or every solder alloy.')
edge('E0138 E0140 E0516 E0580',s,'supported_material_class_composition',
 'Epoxy and silica in mould compound; exact grade and formulation unspecified.')
edge('E0565 E0566',s,'supported_material_class_composition',
 'Gold or copper bonding wire; salts and palladium coating are not established here.')
edge('E0687 E0689 E0690 E0740',s,'supported_packaging_option_not_part_specific',
 'Wire-bond PBGA can use substrate, encapsulant and solder balls; GDDR generation and SAC305 not confirmed.')
edge('E0692 E0693 E0694 E0695 E0718 E0719 E0720 E0721 E0732 E0733 E0734 E0735 E0738 E0739',s,'supported_packaging_option_not_part_specific',
 'Leadframe/wire/attach/mould route is an option, not proof of the named IC package, alloy or adhesive.')
s=source('R6_DOE_SMR','US Department of Energy','Natural-gas hydrogen production',
 'https://www.energy.gov/cmei/fuels/hydrogen-production-natural-gas-reforming',
 'Methane reforming, water-gas shift and purification; process route only. No market percentage or actual site-to-site shipping inferred.')
edge('E0187 E0188 E0191',s,'supported_upstream_process_not_direct_input',
 'Selected methane-reforming/shift route produces syngas and separates hydrogen and CO2; steam, processing and purification are additional dependencies.')
edge('E0271','R_TOKUYAMA_IPA','supported_process_input',
 'Tokuyama documents propylene hydration for IPA; not a claim every supplier uses this route.')
edge('E0272','R_TOKUYAMA_IPA','water_role_requires_definition_review',
 'Hydration requires process water, not necessarily the submitted coolant node.')

s=source('R6_ENT_CMP','Entegris','Increasing yield through complete control of CMP',
 'https://www.entegris.com/content/dam/web/resources/pictograms/pictogram-increasing-yield-through-complete-control-of-cmp-11501.pdf',
 'CMP slurry uses aqueous silica, alumina or ceria particles; peroxide blending is an example. These are formulation alternatives, not three universally required abrasives.')
edge('E0061',s,'supported_category_use','CMP uses chemical slurry; exact process formulation unspecified.')
edge('E0157 E0158 E0159 E0160',s,'supported_formulation_option',
 'Abrasive alternatives and peroxide additive are documented at class level; not an all-required recipe or exact electronic grade.')
s=source('R6_TOHO_PROCESS','Toho Titanium','Titanium production and electronic-material applications',
 'https://www.toho-titanium.co.jp/about/',
 'Manufacturer explains ore chlorination, magnesium reduction, sponge melting and high-purity target applications. Not an exact GPU material qualification.')
edge('E0312 E0313 E0315',s,'supported_upstream_process_not_direct_input',
 'Selected Kroll process: chlorination and magnesium reduction require intervening processing; relation is not a shipment or complete reaction inventory.')
edge('E0305 E0104',s,'supported_material_class_use',
 'Purified titanium is used in semiconductor sputtering targets and thin-film deposition; ordinary titanium is not automatically target grade.')
s=source('R6_TOHO_SITES','Toho Titanium','Production-site directory',
 'https://www.toho-titanium.co.jp/en/company/profile/',
 'Five named plants. Yokohama headquarters excluded; individual product allocation not supplied by this directory.')
for name,city,address in [
 ('Chigasaki','Chigasaki','3-3-5 Chigasaki'),
 ('Wakamatsu','Kitakyushu','1-62-1 Hibiki-machi, Wakamatsu-ku'),
 ('Yahata','Kitakyushu','2-3 Nishikukioka, Maeda, Yahatahigashi-ku'),
 ('Kurobe','Kurobe','8 Tenjinshin'),
 ('Hitachi','Hitachi','3453 Miyata-cho')]:
    site('Toho Titanium '+name,'Toho Titanium','Japan',city,address,s,'')
s=source('R6_FRALOCK_MYLAR','Fralock','Electrical insulation materials',
 'https://www.fralock.com/solutions-with-engineered-materials/electrical-insulation-dielectric/',
 'Mylar/PET insulation offered; the division directory additionally establishes custom thin-film cutting capability. GPU drawing and qualification remain unverified.')
vendor('Fralock',s,'SC-MYLAR-INSULATOR',
 'Custom Mylar/PET insulation candidate; film selection, die-cut geometry and GPU application require qualification',
 qualification='custom_converter_capability_not_qualified_gpu_part')
s=source('R6_FRALOCK_SITES','Fralock','Manufacturing divisions and facilities',
 'https://www.fralock.com/about-us/fralock-divisions/',
 'Valencia SEM combines headquarters with in-house thin-film manufacturing. Other divisions make flex circuits and ceramics; do not allocate their facilities to Mylar liners.')
site('Fralock Valencia specialty materials manufacturing','Fralock','United States','Valencia, California',
 '28525 W Industry Drive',s,'SC-MYLAR-INSULATOR',
 operating_status='manufacturing_and_headquarters;custom_conversion_capability_not_part_qualification')
for name,city,address in [
 ('AFIP Independence','Chatsworth, California','9134 Independence Avenue'),
 ('AFIP Mason','Chatsworth, California','9334 Mason Avenue'),
 ('AFIP Milpitas','Milpitas, California','311 Turquoise Avenue'),
 ('active ceramics','Poway, California','12131 Community Road'),
 ('structural ceramics','Fremont, California','46211 Research Avenue')]:
    site('Fralock '+name,'Fralock','United States',city,address,s,'')

s=source('R6_PUREON_PAD','Pureon','SUBA X pad construction and properties',
 'https://pureon.com/products/polishing-pads/suba-x/',
 'Polyurethane-impregnated polyester felt is a documented pad construction. Does not establish separately purchased layers or every CMP pad design.')
edge('E0175 E0176',s,'supported_material_class_composition',
 'Polyurethane and polyester felt occur in the documented SUBA pad family; not a universal two-layer recipe or proof of independently sold layers.')
s=source('R6_ARGOR_GOLD','Argor-Heraeus','Precious-metal refining capabilities',
 'https://www.argor-heraeus.com/en/products-and-services/services/refining/',
 'Refined gold at 999.9 and 999.99 parts per thousand; electronics application explicitly named. Not potassium gold cyanide manufacture.')
vendor('Argor-Heraeus',s,'PM-REFINED-AU',
 'Elemental refined-gold branch only, 99.99% and 99.999%; potassium-gold-cyanide branch not covered',
 qualification='partial_combined_node_elemental_gold_only')
s=source('R6_ARGOR_CERT','SQS / Argor-Heraeus','Certified refining and industrial production sites, valid through 18 December 2026',
 'https://www.argor-heraeus.com/dam/jcr:bf5a4192-e900-4601-a3cc-1770d660fd77/102227_en_H38782%20(1).pdf',
 'Two Mendrisio production addresses certified for precious-metal refining and transformation. Purity allocation between the two addresses is not stated.')
for label,address in [('Moree','Via Moree 14'),('Borromini','Via Francesco Borromini 18')]:
    site('Argor-Heraeus Mendrisio '+label,'Argor-Heraeus','Switzerland','Mendrisio',address,s,'',
         operating_status='certified_refining_site;address_specific_gold_grade_unallocated')
s=source('R6_ARGOR_NETWORK','Argor-Heraeus','Refining locations and site roles',
 'https://www.argor-heraeus.com/en/about/locations/',
 'Italy and Germany list refining activities. Hong Kong industrial refining is distinct from its city trading office; no factory gate given. Turkish decorative-coating site is not a gold-refinery match.')
for name,country,city in [('Italy','Italy','Cavenago di Brianza'),('Germany','Germany','Wurmberg'),('Hong Kong industrial refinery','China','Hong Kong')]:
    site('Argor-Heraeus '+name,'Argor-Heraeus',country,city,'Manufacturing city only; gate unverified',s,'',
         operating_status='refining_activity_documented;product_grade_allocation_unverified')
