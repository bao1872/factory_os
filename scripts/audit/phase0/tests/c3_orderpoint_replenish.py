env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True, no_document=True))
wh = env['stock.warehouse'].search([], limit=1)
manuf_route = wh.manufacture_pull_id.route_id
buy_route = wh.buy_pull_id.route_id
supplier = env['res.partner'].create({'name': 'PHA0-C3-Supplier'})
comp = env['product.product'].create({'name': 'PHA0-C3-Component-Buy', 'type': 'consu', 'is_storable': True,
                                       'route_ids': [(4, buy_route.id)], 'seller_ids': [(0,0,{'partner_id': supplier.id, 'price': 2.0})]})
fg = env['product.product'].create({'name': 'PHA0-C3-Finished-Mfg', 'type': 'consu', 'is_storable': True,
                                     'route_ids': [(4, manuf_route.id)]})
bom = env['mrp.bom'].create({'product_tmpl_id': fg.product_tmpl_id.id, 'product_qty': 1,
                              'bom_line_ids': [(0,0,{'product_id': comp.id, 'product_qty': 2})]})
print("C3_BOM", bom.id, bom.display_name, "| product=", bom.product_id.name)
# set up orderpoint on FG and run replenishment like scheduler
op = env['stock.warehouse.orderpoint'].create({'product_id': fg.id, 'warehouse_id': wh.id,
                                                'location_id': wh.lot_stock_id.id, 'product_min_qty': 0, 'product_max_qty': 10})
mo_before = env['mrp.production'].search_count([])
po_before = env['purchase.order'].search_count([])
print("C3_BEFORE mo=", mo_before, "po=", po_before)
# trigger: orderpoint action_replenish (procures fg via manufacture -> needs comp via buy)
try:
    op.action_replenish()
    msg = "action_replenish ok"
except Exception as e:
    msg = "ERR " + repr(e)[:300]
print("C3_TRIGGER", msg)
mo_after = env['mrp.production'].search_count([])
po_after = env['purchase.order'].search_count([])
mos = env['mrp.production'].search([('product_id','=',fg.id)])
pos = env['purchase.order'].search([])
print("C3_AFTER mo=", mo_before, "->", mo_after, "| po=", po_before, "->", po_after)
print("C3_MOs", [(m.name, m.state, m.product_qty) for m in mos])
print("C3_POs", [(p.name, p.state) for p in pos])
