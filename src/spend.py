"""Print cumulative spend by exp x model."""
import budget
rows = budget.summary()
print(f"{'exp':6} {'provider':8} {'model':28} {'n':>2} {'ok':>2} {'est$':>7} {'actual$':>8}")
te = ta = 0
for (exp, prov, model), r in sorted(rows.items()):
    print(f"{exp:6} {prov:8} {model:28} {r['n']:>2} {r['ok']:>2} {r['est']:>7.3f} {r['actual']:>8.3f}")
    te += r["est"]; ta += r["actual"]
print(f"{'TOTAL':6} {'':8} {'':28} {'':>2} {'':>2} {te:>7.3f} {ta:>8.3f}")
for prov in ("omni", "xai"):
    print(f"new spend {prov}: {budget.spent(prov):.3f} / cap {budget.CFG['budget']['caps_usd'][prov]:.2f}")

print(f"opening (O*) spend: {budget.spent_opening():.3f} / cap {budget.CFG['budget']['caps_usd']['opening']:.2f}")
