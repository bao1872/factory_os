# Test H1 — Safe Minimal DB: create & confirm SO-OLD before any engine addon
env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True))
cust = env['res.partner'].create({'name': 'CUST-H-OLD'})
prod = env['product.product'].create({'name': 'FG-H1-GOODS', 'type': 'consu'})
so = env['sale.order'].create({
    'partner_id': cust.id,
    'order_line': [(0, 0, {'product_id': prod.id, 'product_uom_qty': 4.0})],
})
so.action_confirm()
print('H1_CONFIRM SO=', so.name, '| partner=', cust.name, '| product=', prod.name, '| state=', so.state)
print('H1_END')
