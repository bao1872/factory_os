env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True, no_document=True))
def counts():
    return dict(mo=env['mrp.production'].search_count([]), picking=env['stock.picking'].search_count([]),
                move=env['stock.move'].search_count([]), po=env['purchase.order'].search_count([]),
                orderpoint=env['stock.warehouse.orderpoint'].search_count([]))
wh = env['stock.warehouse'].search([], limit=1)
manuf_route = wh.manufacture_pull_id.route_id
buy_route = wh.buy_pull_id.route_id
print("C_WH", wh.name, "| manufacture route:", manuf_route.id, manuf_route.name, "| buy route:", buy_route.id, buy_route.name)
print("C_ROUTES", [(r.id, r.name) for r in env['stock.route'].search([])])
cust = env['res.partner'].create({'name': 'PHA0-C-Customer'})

# C1: product with Manufacture route, SO confirm (MTS delivery via manufacture route on WH resupply)
p1 = env['product.product'].create({'name': 'PHA0-C1-Mfg', 'type': 'consu', 'is_storable': True,
                                     'route_ids': [(4, manuf_route.id)]})
so1 = env['sale.order'].create({'partner_id': cust.id, 'order_line': [(0,0,{'product_id': p1.id, 'product_uom_qty': 10})]})
print("C1_PROD routes=", [(r.name) for r in p1.route_ids])
print("C1_SO_line routes=", [(r.name) for r in so1.order_line.route_ids], "| is_mto=", so1.order_line.is_mto)
b = counts(); so1.action_confirm(); a = counts()
mos = env['mrp.production'].search([('origin','=',so1.name)])
print("C1_CONFIRM", so1.name, "| MO", b['mo'], "->", a['mo'], "| picks", b['picking'], "->", a['picking'],
      "| MOs=", [(m.name, m.state) for m in mos])

# C2: manufacture-route product + make_to_order (MTO): SO confirm -> MO auto?
p2 = env['product.product'].create({'name': 'PHA0-C2-Mfg-MTO', 'type': 'consu', 'is_storable': True,
                                     'route_ids': [(4, manuf_route.id)], 'is_storable': True})
p2.route_ids = [(4, manuf_route.id)]
# put MTO behavior: product delivery via manufacture is pull; set so line route to MTO rule
mto_rule = manuf_route.rule_ids.filtered(lambda rl: rl.action == 'manufacture')
print("C2_MANUF_RULES", [(r.id, r.name, r.action, r.procure_method, r.auto, r.location_src_id.complete_name, '->', r.location_dest_id.complete_name) for r in manuf_route.rule_ids])
so2 = env['sale.order'].create({'partner_id': cust.id, 'order_line': [(0,0,{'product_id': p2.id, 'product_uom_qty': 10, 'route_ids': [(6,0,manuf_route.ids)]})]})
print("C2_SO_line routes=", [(r.name) for r in so2.order_line.route_ids], "| is_mto=", so2.order_line.is_mto)
b = counts(); so2.action_confirm(); a = counts()
mos2 = env['mrp.production'].search([('origin','=',so2.name)])
print("C2_CONFIRM", so2.name, "| MO", b['mo'], "->", a['mo'], "| picks", b['picking'], "->", a['picking'],
      "| MOs=", [(m.name, m.state) for m in mos2])
print("C_FINAL", counts())
