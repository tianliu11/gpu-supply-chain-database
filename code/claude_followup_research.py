"""Independently inspected evidence extending the supplied Claude batches."""
from additional_public_research import source, vendor, site, edge as register_edge

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
