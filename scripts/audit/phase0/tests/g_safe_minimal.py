# Test G — REAL Safe Minimal installation profile (engine-minimal: NO stock/purchase/mrp)
env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True))


def model_exists(m):
    try:
        env[m]
        return True
    except Exception:
        return False


def inst(name):
    return env['ir.module.module'].search_count([('name', '=', name), ('state', '=', 'installed')])


# 1) exact installed addon graph (engine & bridge check)
forbidden = ['stock', 'sale_stock', 'purchase', 'purchase_stock', 'purchase_mrp',
             'mrp', 'sale_mrp', 'stock_account', 'mrp_account', 'delivery']
print('G_MODULES total_installed=', env['ir.module.module'].search_count([('state', '=', 'installed')]))
print('G_FORBIDDEN_PRESENT', [(m, inst(m)) for m in forbidden if inst(m)] or 'NONE — no stock/purchase/mrp engine')
for m in ['sale', 'sale_management', 'sales_team', 'product', 'account', 'account_payment', 'mail']:
    print('G_MOD', m, 'installed=', inst(m))

# 2) model existence
print('G_MODELS stock.picking=', model_exists('stock.picking'),
      '| stock.move=', model_exists('stock.move'),
      '| stock.quant=', model_exists('stock.quant'),
      '| mrp.production=', model_exists('mrp.production'),
      '| purchase.order=', model_exists('purchase.order'),
      '| sale.order=', model_exists('sale.order'),
      '| product.product=', model_exists('product.product'))

# 3) physical Goods customer order (Customer/Product/Quotation/SO/mail only)
cust = env['res.partner'].create({'name': 'CUST-G-MIN'})
prod = env['product.product'].create({'name': 'FG-G-GOODS', 'type': 'consu'})
print('G_PRODUCT type=', prod.type, '| is_storable field=', 'is_storable' in prod._fields)
so = env['sale.order'].create({
    'partner_id': cust.id,
    'order_line': [(0, 0, {'product_id': prod.id, 'product_uom_qty': 2.0})],
})
print('G_SO_PRE line fields: route_ids=', 'route_ids' in so.order_line._fields)
so.action_confirm()
print('G_CONFIRM SO=', so.name, 'state=', so.state, '| order_line qty=', so.order_line.product_uom_qty)
# logistics model check: stock not installed so nothing should exist
print('G_LOGISTICS stock.picking count=', env['stock.picking'].search_count([]) if model_exists('stock.picking') else 'MODEL-ABSENT')
print('G_END')
