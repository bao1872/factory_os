# Test E — TRUE MTO + Manufacture (official sale_mrp recipe, runtime reproduction)
env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True))


def counts():
    return (
        env['stock.picking'].search_count([]),
        env['stock.move'].search_count([]),
        env['mrp.production'].search_count([]),
        env['purchase.order'].search_count([]),
        env['sale.order'].search_count([]),
    )


def model_exists(m):
    try:
        env[m]
        return True
    except Exception:
        return False


print('E_PRECOND model_exists mrp.production=', model_exists('mrp.production'),
      '| stock.picking=', model_exists('stock.picking'),
      '| sale_stock installed=', env['ir.module.module'].search_count([('name', '=', 'sale_stock'), ('state', '=', 'installed')]))

# 1) official MTO activation
env.ref('stock.route_warehouse0_mto').active = True
wh = env.ref('stock.warehouse0')

# 2) canonical product setup: routes = [Manufacture, MTO]
comp = env['product.product'].create({'name': 'COMP-E-RAW', 'type': 'consu', 'is_storable': True})
fg = env['product.product'].create({'name': 'FG-E-MTO-MFG', 'type': 'consu', 'is_storable': True})
mfg_route = wh.manufacture_pull_id.route_id
mto_route = wh.mto_pull_id.route_id
fg.write({'route_ids': [(6, 0, [mfg_route.id, mto_route.id])]})
print('E_ROUTES product routes=', [r.name for r in fg.route_ids],
      '| mfg=', mfg_route.name, '| mto=', mto_route.name)

# 3) valid BoM (type=normal)
bom = env['mrp.bom'].create({
    'product_tmpl_id': fg.product_tmpl_id.id,
    'product_qty': 1.0,
    'type': 'normal',
    'bom_line_ids': [(0, 0, {'product_id': comp.id, 'product_qty': 1.0})],
})
print('E_BOM id=', bom.id, 'type=', bom.type, '| lines=', bom.bom_line_ids.product_id.mapped('name'))

# 4) SO for manufactured MTO product
cust = env['res.partner'].create({'name': 'CUST-E-MTO'})
so = env['sale.order'].create({
    'partner_id': cust.id,
    'order_line': [(0, 0, {'product_id': fg.id, 'product_uom_qty': 3.0})],
})
line = so.order_line[0]
print('E_SO_PRE line routes=', [r.name for r in line.route_ids],
      '| is_mto field=', 'is_mto' in line._fields,
      ('| is_mto=' + str(line.is_mto)) if 'is_mto' in line._fields else '')

# 5) confirm & record exact deltas
b0 = counts()
so.action_confirm()
b1 = counts()
print('E_CONFIRM SO=', so.name, 'state=', so.state)
print('E_DELTA picks %d->%d | moves %d->%d | mo %d->%d | po/rfq %d->%d' % (
    b0[0], b1[0], b0[1], b1[1], b0[2], b1[2], b0[3], b1[3]))

mos = env['mrp.production'].search([('origin', 'like', so.name)])
print('E_MO_CREATED', [(m.name, m.state, 'origin=' + (m.origin or ''), 'qty=' + str(m.product_qty)) for m in mos])

# 6) native SO<->MO relation (official assertion: action_view_mrp_production res_id == mo.id)
try:
    act = so.action_view_mrp_production()
    print('E_REL action_view_mrp_production res_id=', act.get('res_id'),
          '| first_mo.id=', mos[0].id if mos else None,
          'MATCH=' + str(act.get('res_id') == (mos[0].id if mos else None)))
except Exception as ex:
    print('E_REL_EXC', type(ex).__name__, str(ex)[:200])

# 7) native SO<->stock.move / picking link
picks = env['stock.picking'].search([('origin', '=', so.name)])
print('E_PICKS origin=SO', [(p.name, p.state, p.location_id.name + '->' + p.location_dest_id.name) for p in picks])
moves = env['stock.move'].search([('sale_line_id', '=', line.id)])
print('E_MOVES sale_line linked', [(m.id, m.product_id.name, m.location_id.name + '->' + m.location_dest_id.name,
                                    'proc=' + str(m.procure_method), 'origin=' + (m.origin or ''), 'state=' + m.state) for m in moves])
# moves carrying the produced lot toward customer
produced_moves = env['stock.move'].search([('production_id', 'in', mos.ids)])
print('E_MO_MOVES raw/finished', [(m.id, m.product_id.name, m.location_id.name + '->' + m.location_dest_id.name,
                                   m.state, 'qty=' + str(m.product_uom_qty)) for m in produced_moves])

print('E_END')
