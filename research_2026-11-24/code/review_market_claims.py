"""Compare supplied rows with two independently read TrendForce rankings."""

TABLES = {
    'V01_S002': {
        'market': 'global foundry revenue',
        'period': '2025 Q3',
        'in_scope_node': 'LD:fabrication',
        'entries': [
            ('TSMC', '71% share'), ('Samsung Foundry', '6.8% share'), ('SMIC', ''),
            ('UMC', '4.2% share'), ('GlobalFoundries', '3.6% share'),
            ('Hua Hong Group', '2.6% share'), ('Vanguard International Semiconductor', ''),
            ('Nexchip', ''), ('Tower Semiconductor', ''), ('PSMC', ''),
        ],
    },
    'V01_S003': {
        'market': 'outsourced assembly and test revenue',
        'period': '2024',
        'in_scope_node': 'LD:assembly_packaging_testing',
        'entries': [
            ('ASE Technology Holding (incl. SPIL)', 'US$18.54B revenue'),
            ('Amkor Technology', 'US$6.32B revenue'), ('JCET Group', 'US$5.0B revenue'),
            ('Tongfu Microelectronics', 'US$3.32B revenue'),
            ('Powertech Technology', 'US$2.28B revenue'), ('HT-Tech (Tianshui Huatian)', 'US$2.01B revenue'),
            ('WiseRoad', 'US$1.56B revenue'), ('Hana Micron', 'US$0.92B revenue'),
            ('KYEC (King Yuan Electronics)', 'US$0.91B revenue'), ('ChipMOS', 'US$0.71B revenue'),
        ],
    },
}


def review_claim(row):
    for sid in row['source_ids'].split(';'):
        table = TABLES.get(sid)
        if table is None:
            continue
        match = next(((rank, value) for rank, (name, value) in enumerate(table['entries'], 1)
                      if name == row['vendor_name']), None)
        rank, value = match or ('', '')
        discrepancy = (
            'supplier_role_or_name_outside_cited_table' if match is None else
            'market_rank_has_broader_scope_than_node' if row['node_id'] != table['in_scope_node'] else
            'submitted_rank_or_metric_differs' if str(rank) != row['vendor_rank'] or
                (row['metric_value'] and row['metric_value'] != value) else
            'market_rank_matches_source'
        )
        return dict(record_id=row['record_id'], node_id=row['node_id'], vendor_name=row['vendor_name'],
                    source_id=sid, period=table['period'], market=table['market'],
                    submitted_rank=row['vendor_rank'], submitted_metric=row['metric_value'],
                    source_rank=rank, source_metric=value, result=discrepancy,
                    exact_gpu_product_or_factory_qualification=False)
    return None
