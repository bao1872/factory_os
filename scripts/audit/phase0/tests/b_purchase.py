env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True, no_document=True))
def counts():
    return dict(picking=env['stock.picking'].search_count([]), move=env['stock.move'].search_count([]),
                po=env['purchase.order'].search_count([]), mo=env['mrp.production'].search_count([]),
                orderpoint=env['stock.warehouse.orderpoint'].search_count([]))
def mk(name, **kw):
    base = {'name': name}; base.update(kw)
    return env['product.product'].create(base)

p_stor  = mk('PHA0-B-Storable', type='consu', is_storable=True)
p_plain = mk('PHA0-B-Plain', type='consu', is_storable=False)
p_serv  = mk('PHA0-B-Service', type='service')
supplier = env['res.partner'].create({'name': 'PHA0-B-Supplier', 'is_company': True})
print("B_BEFORE", counts())
for p in (p_stor, p_plain, p_serv):
    # supplierinfo so the product can be purchased
    p.write({'seller_ids': [(0,0,{'partner_id': supplier.id, 'price': 10.0, 'delay': 2})]})
    po = env['purchase.order'].create({'partner_id': supplier.id, 'order_line': [(0,0,{'product_id': p.id, 'product_qty': 8, 'price_unit': 10.0})]})
    print("B_PO", po.name, "state=", po.state, "| line.qty=", po.order_line.product_qty)
    b = counts(); po.button_confirm(); a = counts()
    picks = env['stock.picking'].search([('origin','=',po.name)])
    moves = env['stock.move'].search([('purchase_line_id','=',po.order_line.id)])
    print("B_CONFIRMED", po.name, "state=", po.state, "| prod:", p.name, p.type, "is_storable=", p.is_storable,
          "| picks", b['picking'], "->", a['picking'], "| moves", b['move'], "->", a['move'], "| MO", b['mo'], "->", a['mo'])
    print("B_PICKINGS", po.name, [(pk.name, pk.picking_type_code, pk.state, pk.location_id.complete_name, '->', pk.location_dest_id.complete_name) for pk in picks])
    for m in moves:
        print("B_MOVE", po.name, m.id, "state=", m.state, m.location_id.complete_name, '->', m.location_dest_id.complete_name, m.product_uom_qty, m.procure_method)
print("B_FINAL", counts())
