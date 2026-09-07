env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True, no_document=True))
wh = env['stock.warehouse'].search([], limit=1)
manuf_route = wh.manufacture_pull_id.route_id
buy_route = wh.buy_pull_id.route_id
cust = env['res.partner'].create({'name': 'PHA0-D-Customer'})
# Day-1 style: plain goods, NO inventory/mrp capability concepts
p = env['product.product'].create({'name': 'PHA0-D-Product', 'type': 'consu', 'is_storable': False})
so_old = env['sale.order'].create({'partner_id': cust.id, 'order_line': [(0,0,{'product_id': p.id, 'product_uom_qty': 10})]})
so_old.action_confirm()
n1 = dict(mo=env['mrp.production'].search_count([]), pick=env['stock.picking'].search_count([]), move=env['stock.move'].search_count([]), po=env['purchase.order'].search_count([]))
print("D_DAY1_SO", so_old.name, "confirmed | counts=", n1, "| prod routes=", [(r.name) for r in p.route_ids])
# Later: capability ON (product becomes storable with buy+manufacture routes; warehouse resupply ON)
p.is_storable = True
p.route_ids = [(6, 0, (manuf_route | buy_route).ids)]
print("D_LATER_CAPABILITY_ON routes=", [(r.name) for r in p.route_ids])
n2 = dict(mo=env['mrp.production'].search_count([]), pick=env['stock.picking'].search_count([]), move=env['stock.move'].search_count([]), po=env['purchase.order'].search_count([]))
print("D_AFTER_FLIP_NO_ACTION counts=", n2, "| delta_mo=", n2['mo']-n1['mo'], "| delta_pick=", n2['pick']-n1['pick'])
old_moves = env['stock.move'].search([('sale_line_id','=',so_old.order_line.id)])
print("D_OLD_SO_STILL", so_old.name, "state=", so_old.state, "| move count still=", len(old_moves))
# now a NEW sale on same product (post capability) -> observe what native creates
so_new = env['sale.order'].create({'partner_id': cust.id, 'order_line': [(0,0,{'product_id': p.id, 'product_uom_qty': 4})]})
so_new.action_confirm()
n3 = dict(mo=env['mrp.production'].search_count([]), pick=env['stock.picking'].search_count([]), move=env['stock.move'].search_count([]), po=env['purchase.order'].search_count([]))
print("D_NEW_SO", so_new.name, "| counts=", n3, "| delta_mo=", n3['mo']-n2['mo'], "| delta_pick=", n3['pick']-n2['pick'])
mos = env['mrp.production'].search([])
print("D_MOs_now=", [(m.name, m.product_id.name) for m in mos])
# replenishment trigger on new demand path -> MO appears only via explicit procure action?
