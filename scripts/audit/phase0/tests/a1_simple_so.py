env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True, no_document=True))
def counts():
    return dict(picking=env['stock.picking'].search_count([]), move=env['stock.move'].search_count([]), mo=env['mrp.production'].search_count([]))
def mk(name, **kw):
    base = {'name': name}; base.update(kw)
    return env['product.product'].create(base)

p_stor  = mk('PHA0-A3R-Goods-Storable', type='consu', is_storable=True)
p_plain = mk('PHA0-A3R-Goods-Plain', type='consu', is_storable=False)
p_serv  = mk('PHA0-A3R-Service', type='service')
cust = env['res.partner'].create({'name': 'PHA0-A3R-Customer'})
print("A3R_BEFORE", counts())
for p in (p_stor, p_plain, p_serv):
    so = env['sale.order'].create({'partner_id': cust.id, 'order_line': [(0,0,{'product_id': p.id, 'product_uom_qty': 10})]})
    b = counts(); so.action_confirm(); a = counts()
    picks = env['stock.picking'].search([('origin','=',so.name)])
    moves = env['stock.move'].search([('origin','=',so.name)])
    print("A3R_RESULT", so.name, "| prod:", p.name, "type=", p.type, "is_storable=", p.is_storable,
          "| picks", b['picking'], "->", a['picking'], "| moves", b['move'], "->", a['move'], "| MO", b['mo'], "->", a['mo'])
    for pk in picks:
        mlrows = [(ml.product_id.name, ml.quantity) for ml in pk.move_line_ids]
        print("A3R_PICKING", so.name, pk.name, pk.picking_type_code, "state=", pk.state,
              "| loc:", pk.location_id.complete_name, "->", pk.location_dest_id.complete_name, "| move_lines:", mlrows)
    for m in moves:
        print("A3R_MOVE", so.name, m.id, "state=", m.state, "| proc=", m.procure_method,
              "| loc:", m.location_id.complete_name, "->", m.location_dest_id.complete_name, "| qty=", m.product_uom_qty,
              "| sale_line=", m.sale_line_id.id)
print("A3R_FINAL", counts())
