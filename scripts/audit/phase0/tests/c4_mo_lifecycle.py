env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True, no_document=True))
wh = env['stock.warehouse'].search([], limit=1)
manuf_route = wh.manufacture_pull_id.route_id
buy_route = wh.buy_pull_id.route_id
supplier = env['res.partner'].create({'name': 'PHA0-C4R-Supplier'})
comp = env['product.product'].create({'name': 'PHA0-C4R-Comp', 'type': 'consu', 'is_storable': True,
                                       'route_ids': [(4, buy_route.id)], 'seller_ids': [(0,0,{'partner_id': supplier.id, 'price': 3.0})]})
fg = env['product.product'].create({'name': 'PHA0-C4R-FG', 'type': 'consu', 'is_storable': True,
                                     'route_ids': [(4, manuf_route.id)], 'tracking': 'lot'})
bom = env['mrp.bom'].create({'product_tmpl_id': fg.product_tmpl_id.id, 'product_qty': 1,
                              'bom_line_ids': [(0,0,{'product_id': comp.id, 'product_qty': 2})]})
print("C4R_FG tracking=", fg.tracking, "| comp storable=", comp.is_storable)

# 1) receive 20 comps via PO
po = env['purchase.order'].create({'partner_id': supplier.id, 'order_line': [(0,0,{'product_id': comp.id, 'product_qty': 20, 'price_unit': 3.0})]})
po.button_confirm()
rp = po.picking_ids
rp.move_ids.picked = True; rp.button_validate()
q = env['stock.quant'].search([('product_id','=',comp.id),('location_id','=',wh.lot_stock_id.id)])
print("C4R_RECEIVED comp qty=", q.quantity, "| quant rows=", len(q))

# 2) create MO manually
mo = env['mrp.production'].create({'product_id': fg.id, 'product_qty': 5, 'bom_id': bom.id})
mo.action_confirm()
print("C4R_MO", mo.name, "state=", mo.state,
      "| raw moves=", [(m.product_id.name, m.product_uom_qty, m.state, m.location_id.complete_name,'->',m.location_dest_id.complete_name) for m in mo.move_raw_ids],
      "| fin moves=", [(m.product_id.name, m.product_uom_qty, m.state) for m in mo.move_finished_ids],
      "| workorders=", [(w.id, w.state) for w in mo.workorder_ids])

# 3) register finished lot + mark done (19 native completion API)
lot = env['stock.lot'].create({'name': 'LOT-C4R-0001', 'product_id': fg.id, 'company_id': wh.company_id.id})
print("C4R_LOT_CREATED", lot.name)
mo.qty_producing = 5.0
mo.lot_producing_ids = [(6, 0, [lot.id])]
for m in mo.move_raw_ids:
    m.quantity = m.product_uom_qty
mo.move_raw_ids.picked = True
mo.button_mark_done()
print("C4R_MO_DONE", mo.name, "state=", mo.state, "| qty_produced=", mo.qty_produced)
fin_q = env['stock.quant'].search([('product_id','=',fg.id)])
print("C4R_FG_QUANTS", [(x.quantity, x.lot_id.name, x.location_id.complete_name) for x in fin_q])
comp_q = env['stock.quant'].search([('product_id','=',comp.id)])
print("C4R_COMP_QUANTS", [(x.quantity, x.location_id.complete_name) for x in comp_q])
# traceability linkage evidence
print("C4R_FIN_LINE_LINKS", [(ml.lot_id.name, ml.quantity, ml.move_id.production_id.name if ml.move_id.production_id else None,
                              ml.move_id.mrp_production_id.name if 'mrp_production_id' in ml.move_id._fields and ml.move_id.mrp_production_id else None) for ml in mo.move_finished_ids.move_line_ids])
for ml in mo.move_raw_ids.move_line_ids:
    print("C4R_RAW_LINE", ml.product_id.name, ml.quantity, ml.lot_id.name if ml.lot_id else None,
          "| consumed_by_fin_line=", ml.consume_line_ids.mapped(lambda x: (x.lot_id.name, x.move_id.production_id.name)) if 'consume_line_ids' in ml._fields else "no_field",
          "| raw_mo=", ml.move_id.raw_material_production_id.name if 'raw_material_production_id' in ml.move_id._fields and ml.move_id.raw_material_production_id else None)
