env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True, no_document=True))
def counts():
    return dict(picking=env['stock.picking'].search_count([]), move=env['stock.move'].search_count([]), mo=env['mrp.production'].search_count([]))
p_serv = env['product.product'].create({'name': 'PHA0-A4-Service', 'type': 'service'})
p_stor = env['product.product'].create({'name': 'PHA0-A4-Storable', 'type': 'consu', 'is_storable': True})
cust = env['res.partner'].create({'name': 'PHA0-A4-Customer'})
for p in (p_serv, p_stor):
    so = env['sale.order'].create({'partner_id': cust.id, 'order_line': [(0,0,{'product_id': p.id, 'product_uom_qty': 5})]})
    b = counts(); so.action_confirm(); a = counts()
    picks = env['stock.picking'].search([('origin','=',so.name)])
    print("A4_RESULT", so.name, "| prod:", p.name, "type=", p.type, "is_storable=", p.is_storable,
          "| picks", b['picking'], "->", a['picking'], "| moves", b['move'], "->", a['move'], "| MO", b['mo'], "->", a['mo'],
          "| pickings=", [(pk.name, pk.picking_type_code, pk.state) for pk in picks])
# also check invoice_status/procurement group for service
print("A4_SERVICE_NOMOVE_EXPECTED_CONFIRMED")
