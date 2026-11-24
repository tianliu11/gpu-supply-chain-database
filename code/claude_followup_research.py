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
