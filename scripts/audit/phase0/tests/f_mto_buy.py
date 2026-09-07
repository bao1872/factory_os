# Test F — TRUE MTO + Buy (runtime reproduction)
env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True))


def counts():
    return (
        env['stock.picking'].search_count([]),
        env['stock.move'].search_count([]),
        env['mrp.production'].search_count([]),
        env['purchase.order'].search_count([]),
        env['sale.order'].search_count([]),
    )


env.ref('stock.route_warehouse0_mto').active = True
wh = env.ref('stock.warehouse0')
print('F_WH buy_pull_id exists=', bool(wh.buy_pull_id), '| mto_pull_id=', bool(wh.mto_pull_id))

# bought product: storable goods + vendor + MTO + Buy routes
vendor = env['res.partner'].create({'name': 'VENDOR-F', 'is_company': True})
prod = env['product.product'].create({
    'name': 'PROD-F-MTO-BUY', 'type': 'consu', 'is_storable': True,
    'seller_ids': [(0, 0, {'partner_id': vendor.id, 'min_qty': 0.0, 'price': 10.0, 'delay': 0})],
})
buy_route = wh.buy_pull_id.route_id
mto_route = wh.mto_pull_id.route_id
prod.write({'route_ids': [(6, 0, [buy_route.id, mto_route.id])]})
print('F_ROUTES product routes=', [r.name for r in prod.route_ids])

cust = env['res.partner'].create({'name': 'CUST-F-MTO'})
so = env['sale.order'].create({
    'partner_id': cust.id,
    'order_line': [(0, 0, {'product_id': prod.id, 'product_uom_qty': 5.0})],
})
line = so.order_line[0]
print('F_SO_PRE line routes=', [r.name for r in line.route_ids],
      ('| is_mto=' + str(line.is_mto)) if 'is_mto' in line._fields else '| is_mto n/a')

b0 = counts()
so.action_confirm()
b1 = counts()
print('F_CONFIRM SO=', so.name, 'state=', so.state)
print('F_DELTA picks %d->%d | moves %d->%d | mo %d->%d | po/rfq %d->%d' % (
    b0[0], b1[0], b0[1], b1[1], b0[2], b1[2], b0[3], b1[3]))

pos = env['purchase.order'].search([('origin', 'like', so.name)])
print('F_RFQ_CREATED', [(p.name, p.state, 'origin=' + (p.origin or ''), p.amount_total) for p in pos])
if pos:
    print('F_RFQ_LINES', [(pl.product_id.name, pl.product_qty, pl.price_unit) for p in pos for pl in p.order_line])
# relation: RFQ partner / line links back to SO
pol = env['purchase.order.line'].search([('sale_order_id', '=', so.id)])
print('F_REL pol.sale_order_id links=', len(pol), '| sale_line link field exists=',
      'sale_line_id' in env['purchase.order.line']._fields)

picks = env['stock.picking'].search([('origin', '=', so.name)])
print('F_PICKS origin=SO', [(p.name, p.state) for p in picks])
print('F_END')
