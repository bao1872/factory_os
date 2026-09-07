# Test H3 — after installing mrp(+sale_mrp) on SAME db: old unchanged; MTO+Manufacture+BoM new SO
env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True))


def model_exists(m):
    try:
        env[m]
        return True
    except Exception:
        return False


# 1) old transactions remain unchanged
for pname in ['CUST-H-OLD', 'CUST-H-NEW']:
    so = env['sale.order'].search([('partner_id.name', '=', pname)], limit=1)
    if so:
        picks = env['stock.picking'].search([('origin', '=', so.name)])
        print('H3_OLD_TRX', so.name, 'state=', so.state, '| picks now=', [(p.name, p.state) for p in picks],
              '| retro MO=', env['mrp.production'].search_count([('origin', '=', so.name)]))

# 2) new MTO + Manufacture + BoM product
env.ref('stock.route_warehouse0_mto').active = True
wh = env.ref('stock.warehouse0')
comp = env['product.product'].create({'name': 'COMP-H3', 'type': 'consu', 'is_storable': True})
fg = env['product.product'].create({'name': 'FG-H3-MTO', 'type': 'consu', 'is_storable': True})
fg.write({'route_ids': [(6, 0, [wh.manufacture_pull_id.route_id.id, wh.mto_pull_id.route_id.id])]})
env['mrp.bom'].create({
    'product_tmpl_id': fg.product_tmpl_id.id,
    'product_qty': 1.0,
    'type': 'normal',
    'bom_line_ids': [(0, 0, {'product_id': comp.id, 'product_qty': 1.0})],
})
print('H3_NEW_PRODUCT', fg.name, 'routes=', [r.name for r in fg.route_ids])

# 3) SO-NEW-MRP confirm
cust = env['res.partner'].create({'name': 'CUST-H-MRP'})
so = env['sale.order'].create({
    'partner_id': cust.id,
    'order_line': [(0, 0, {'product_id': fg.id, 'product_uom_qty': 2.0})],
})
p0 = env['stock.picking'].search_count([])
m0 = env['stock.move'].search_count([])
mo0 = env['mrp.production'].search_count([])
so.action_confirm()
print('H3_CONFIRM SO=', so.name, 'state=', so.state)
mos = env['mrp.production'].search([('origin', 'like', so.name)])
print('H3_DELTA picks %d->%d | moves %d->%d | mo %d->%d' % (
    p0, env['stock.picking'].search_count([]), m0, env['stock.move'].search_count([]),
    mo0, env['mrp.production'].search_count([])))
print('H3_MO', [(m.name, m.state, 'origin=' + (m.origin or '')) for m in mos])
picks = env['stock.picking'].search([('origin', '=', so.name)])
print('H3_PICKS', [(p.name, p.state) for p in picks])
line = so.order_line[0]
moves = env['stock.move'].search([('sale_line_id', '=', line.id)])
print('H3_MOVES', [(m.id, m.product_id.name, m.location_id.name + '->' + m.location_dest_id.name, m.state) for m in moves])
if mos:
    act = so.action_view_mrp_production()
    print('H3_REL action_view_mrp_production res_id=', act.get('res_id'), 'mo.id=', mos[0].id,
          'MATCH=' + str(act.get('res_id') == mos[0].id))
print('H3_END')
