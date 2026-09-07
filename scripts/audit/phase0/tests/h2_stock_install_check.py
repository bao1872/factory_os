# Test H2 — after installing stock+sale_stock on the SAME db: old vs new SO behavior
env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True))


def model_exists(m):
    try:
        env[m]
        return True
    except Exception:
        return False


print('H2_MODELS stock.picking=', model_exists('stock.picking'), '| stock.move=', model_exists('stock.move'))
so_old = env['sale.order'].search([('partner_id.name', '=', 'CUST-H-OLD')], limit=1)
line_old = so_old.order_line[0]
print('H2_OLD_SO', so_old.name, 'state=', so_old.state)
picks_old = env['stock.picking'].search([('origin', '=', so_old.name)])
moves_old = env['stock.move'].search([('sale_line_id', '=', line_old.id)])
print('H2_OLD_PICKS_AFTER_INSTALL count=', len(picks_old), '| OLD_MOVES_AFTER_INSTALL count=', len(moves_old),
      '| retro-created=', 'YES-RETRO' if (picks_old or moves_old) else 'NO (unchanged)')

# new SO with the SAME pre-existing product type (plain goods consu)
so_new = env['sale.order'].create({
    'partner_id': env['res.partner'].search([('name', '=', 'CUST-H-OLD')], limit=1).id,
    'order_line': [(0, 0, {'product_id': line_old.product_id.id, 'product_uom_qty': 2.0})],
})
b0 = env['stock.picking'].search_count([])
so_new.action_confirm()
b1 = env['stock.picking'].search_count([])
picks_new = env['stock.picking'].search([('origin', '=', so_new.name)])
print('H2_NEW_SO', so_new.name, 'state=', so_new.state,
      '| picks delta %d->%d' % (b0, b1),
      '| picks=', [(p.name, p.state, p.location_id.name + '->' + p.location_dest_id.name) for p in picks_new])
print('H2_END')
