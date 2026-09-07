env = env(context=dict(env.context, mail_create_nolog=True, mail_notrack=True, tracking_disable=True))
core = ['sale.order','sale.order.line','purchase.order','purchase.order.line','stock.move','stock.move.line','stock.quant','stock.picking','stock.picking.type','stock.lot','stock.warehouse.orderpoint','mrp.production','mrp.bom','mrp.workorder','product.template','product.product','res.partner']
print("--- RECORD RULES ---")
for m in core:
    rules = env['ir.rule'].search([('model_id.model','=',m)])
    line = "; ".join("%s[%s]" % (r.name, ','.join(g.full_name for g in r.groups) or '-') for r in rules)
    print("RULE", m, "| n=", len(rules), "|", line)
print("--- KEY GROUPS ---")
for xid in ['base.group_user','base.group_system','sales_team.group_sale_salesman','purchase.group_purchase_user','purchase.group_purchase_manager','stock.group_stock_user','stock.group_stock_manager','mrp.group_mrp_user','mrp.group_mrp_manager','stock.group_tracking_lot','base.group_partner_manager','base.group_portal','base.group_public','sales_team.group_sale_salesman_all_leads']:
    try:
        g = env.ref(xid); print("GROUP", xid, "->", g.display_name)
    except Exception:
        print("GROUP_MISSING", xid)
