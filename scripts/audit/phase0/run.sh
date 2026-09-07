#!/usr/bin/env bash
# Phase 0 audit harness runner — runs one audit script via `odoo-bin shell`, commits at end.
# Usage: run.sh <DB> <script.py> [outdir]
# Env:  PYBIN=<venv python>  ODOO_BIN=<odoo-bin path>  ODOO_ADDONS=<addons path comma list>  DBHOST=/tmp  DBUSER=zhenbao
set -euo pipefail
DB="${1:?db required}"
SCRIPT="${2:?script required}"
OUTDIR="${3:-/tmp/phase0_audit}"
PYBIN="${PYBIN:-/Users/zhenbao/.workbuddy/binaries/python/envs/odoo19/bin/python}"
ODOO_BIN="${ODOO_BIN:?set ODOO_BIN}"
ODOO_ADDONS="${ODOO_ADDONS:-addons,odoo/addons}"
DBHOST="${DBHOST:-/tmp}"
DBUSER="${DBUSER:-zhenbao}"
name="$(basename "$SCRIPT" .py)"
mkdir -p "$OUTDIR"
{ cat "$SCRIPT"; echo; echo "env.cr.commit()"; } \
  | "$PYBIN" "$ODOO_BIN" shell -d "$DB" --addons-path="$ODOO_ADDONS" \
      --db_host="$DBHOST" --db_user="$DBUSER" --no-http \
      > "$OUTDIR/${name}.out" 2> "$OUTDIR/${name}.err"
echo "RUN $name EXIT=$?"
