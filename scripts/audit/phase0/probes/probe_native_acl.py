# Phase 0 native probe — fresh DB factory_phase0_r2 (2026-09-07)
env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True, no_document=True))

def safe(fn):
    try:
        return fn()
    except Exception as e:
        return "ERR " + repr(e)[:160]

print("ODOO_VERSION", safe(lambda: __import__('odoo.release', fromlist=['version']).version))

mods = env['ir.module.module'].search([('state', '=', 'installed')])
print("INSTALLED_MODS_COUNT", len(mods))
print("INSTALLED_MODS", ','.join(sorted(m.name for m in mods)))

# warehouse / company instance info
for wh in env['stock.warehouse'].search([]):
    f = wh._fields
    print("WH", wh.name, "| lot_stock=", wh.lot_stock_id.complete_name,
          "| mfg_to_resupply=", getattr(wh, 'manufacture_to_resupply', None),
          "| buy_to_resupply=", getattr(wh, 'buy_to_resupply', None),
          "| code=", wh.code, "| company=", wh.company_id.name)
    # force parity with first-round environment (original DB had these True)
    if 'manufacture_to_resupply' in f and not wh.manufacture_to_resupply:
        wh.manufacture_to_resupply = True
    if 'buy_to_resupply' in f and not wh.buy_to_resupply:
        wh.buy_to_resupply = True
print("COMPANIES", [(c.id, c.name) for c in env['res.company'].search([])])
print("USERS", env['res.users'].search_count([]))

# selection values for state fields
for model, fld in [('sale.order', 'state'), ('purchase.order', 'state'), ('stock.picking', 'state'),
                   ('stock.move', 'state'), ('mrp.production', 'state'), ('mrp.workorder', 'state'),
                   ('product.template', 'type'), ('product.template', 'tracking'),
                   ('sale.order.line', 'qty_delivered_method')]:
    print("SEL", model, fld, safe(lambda m=model, fl=fld: [(v, str(l)[:24]) for v, l in env[m].fields_get([fl])[fl].get('selection', [])]))

# model existence in registry
for m in ['product.template', 'product.product', 'res.partner', 'sale.order', 'sale.order.line',
          'purchase.order', 'purchase.order.line', 'stock.move', 'stock.move.line', 'stock.picking',
          'stock.quant', 'stock.lot', 'stock.warehouse.orderpoint', 'stock.scrap', 'stock.inventory',
          'stock.count', 'stock.rule', 'stock.route', 'mrp.bom', 'mrp.bom.line', 'mrp.production',
          'mrp.workorder', 'mrp.workcenter', 'mrp.workcenter.productivity', 'stock.traceability.report',
          'quality.check', 'quality.point', 'quality.alert', 'procurement.group', 'sale.stock.rule']:
    print("EXIST", m, m in env)

# key field presence on critical models (report MISSING ones only)
probes = {
    'stock.move': ['name', 'production_id', 'raw_material_production_id', 'sale_line_id', 'purchase_line_id',
                   'procure_method', 'product_uom_qty', 'picking_id', 'location_id', 'location_dest_id', 'quantity_done'],
    'stock.move.line': ['quantity', 'qty_done', 'product_uom_qty', 'lot_id', 'move_id', 'picking_id', 'consume_line_ids', 'produce_line_ids'],
    'mrp.production': ['move_raw_ids', 'move_finished_ids', 'workorder_ids', 'qty_producing', 'bom_id', 'origin', 'product_qty', 'procurement_group_id'],
    'product.product': ['is_storable', 'type', 'tracking', 'route_ids', 'seller_ids'],
    'product.template': ['is_storable', 'type', 'tracking', 'route_ids'],
    'sale.order.line': ['route_ids', 'is_mto', 'qty_delivered', 'qty_to_deliver', 'is_storable'],
    'purchase.order.line': ['route_ids', 'qty_received', 'is_storable'],
    'res.partner': ['company_type', 'is_company'],
    'stock.picking': ['picking_type_code', 'origin', 'move_ids', 'move_line_ids'],
    'stock.quant': ['quantity', 'reserved_quantity', 'available_quantity', 'lot_id', 'location_id'],
    'stock.warehouse.orderpoint': ['product_min_qty', 'product_max_qty', 'qty_forecast'],
    'stock.traceability.report': ['move_line_id', 'parent_id'],
}
for model, flist in probes.items():
    if model not in env:
        print("FIELDS_MODEL_MISSING", model)
        continue
    missing = [fl for fl in flist if fl not in env[model]._fields]
    print("FIELDS", model, "missing=", missing or "NONE")

# route structure on default warehouse
wh0 = env['stock.warehouse'].search([], limit=1)
print("WH0_PULLS", "mfg_pull=", wh0.manufacture_pull_id.route_id.name if wh0.manufacture_pull_id else None,
      "| buy_pull=", wh0.buy_pull_id.route_id.name if wh0.buy_pull_id else None)
print("ALL_ROUTES", [(r.id, r.name) for r in env['stock.route'].search([])])

# security: ir.model.access per core model (group + perms)
core = ['sale.order', 'sale.order.line', 'purchase.order', 'purchase.order.line', 'stock.move',
        'stock.move.line', 'stock.quant', 'stock.picking', 'stock.picking.type', 'stock.lot',
        'stock.warehouse.orderpoint', 'mrp.production', 'mrp.bom', 'mrp.workorder', 'product.template',
        'product.product', 'res.partner']
print("--- ACL ---")
for m in core:
    rules = env['ir.model.access'].search([('model_id.model', '=', m)])
    line = "; ".join("%s[grp=%s r%dw%dc%du%d]" % (
        r.name, r.group_id.full_name if r.group_id else 'base(implied)', r.perm_read, r.perm_write, r.perm_create, r.perm_unlink)
        for r in rules)
    print("ACL", m, "|", line)
print("--- RECORD RULES ---")
for m in core:
    rules = env['ir.rule'].search([('model_id.model', '=', m)])
    line = "; ".join("%s[grp=%s global=%s]" % (r.name, ','.join(g.full_name for g in r.group_id) or '-', r.global_) for r in rules)
    print("RULE", m, "| n=", len(rules), "|", line)

# key groups exist?
for xid in ['base.group_user', 'base.group_system', 'base.group_no_one', 'sales_team.group_sale_salesman',
            'sales_team.group_sale_salesman_all_leads', 'purchase.group_purchase_user', 'purchase.group_purchase_manager',
            'stock.group_stock_user', 'stock.group_stock_manager', 'mrp.group_mrp_user', 'mrp.group_mrp_manager',
            'stock.group_tracking_lot', 'base.group_partner_manager', 'product.group_stock_packaging']:
    try:
        g = env.ref(xid)
        print("GROUP", xid, "->", g.display_name)
    except Exception:
        print("GROUP_MISSING", xid)

env.cr.commit()
