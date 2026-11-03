from ..inputs import legacy_values, measurement_path
V = legacy_values('equilibrium')

"""Team-size equilibrium for Qwen3.8-27B: from how many heavy developers does an own all-server
cluster cost less per developer-month than the cloud API, and where does the hybrid stand.

Reuses hybrid_calc4 (same prices, sessions, fleets, store, residuals). Adds:
  * a sweep over team size N for local shares s = 20/50/100% and 1/2/3 regions;
  * regions: one fleet serves the working days of R regions in turn, so it is sized for N/R
    developers at peak and its cost is shared by all N;
  * the crossovers: the smallest N on the grid from which a variant stays at or below another.
Run: python3 hybrid_calc5_equilibrium.py > hybrid_calc5_equilibrium.out
"""
from . import sessions as c3
from . import fleet as c4

GRID = [V['GRID_L14_8'], V['GRID_L14_11'], V['GRID_L14_15'], V['GRID_L14_19'], V['GRID_L14_23'], V['GRID_L14_27'], V['GRID_L14_31'], V['GRID_L14_36'], V['GRID_L14_41'], V['GRID_L14_46'], V['GRID_L14_51'], V['GRID_L14_56'], V['GRID_L14_61'], V['GRID_L14_66'], 1000, V['GRID_L14_77'], V['GRID_L14_83'],
        V['GRID_L15_8'], V['GRID_L15_14'], V['GRID_L15_20'], V['GRID_L15_26'], V['GRID_L15_33']]


OFFICE_ANY_N = False


def units(N, own):
    """Rule A (hybrid_calc4.units_for): office units up to 50 people, datacenter units from 50.
    Rule B (OFFICE_ANY_N): office units at any team size as well (prefill boxes in the offices)."""
    if OFFICE_ANY_N:
        return (("rtx1", "rtx4") if own else c4.OFFICE_UNITS) + c4.DC_UNITS
    return c4.units_for(N, own)


def per_month(N, s, regions, S80, r, premium, api_ps):
    """$ per developer-month: API median, own all-server, hybrid office, hybrid remote."""
    api_m = V['api_m_L31_12'] * s * api_ps["27B API median"]
    peak_devs = N / regions
    ko, no, go, co, ro = c4.best_fleet(0, peak_devs * c4.SESS_PER_H * s, V['_ko__no__go__co__ro__L33_73'], units(N, True),
                                       own_model="dense", sessions=S80)
    own_m = (co - ro) / (N * V['own_m_L35_29'])
    kh, nh, gh, ch, rh = c4.best_fleet(r["srv_gpu"], peak_devs * c4.SESS_PER_H * s, V['_kh__nh__gh__ch__rh__L36_84'], units(N, False))
    store = c4.kv_store_cost(N, "dense")
    mac_net = N * premium * (1 - c4.MAC_RESID[4])
    hyb_m = (ch - rh + store + mac_net) / (N * V['hyb_m_L39_47'])
    egress_m = r["bytes"] / 1e12 * V['egress_m_L40_35'] * s * c4.EGRESS_TB
    return api_m, own_m, hyb_m, hyb_m + egress_m, (no, ko), (nh, kh)


def first_stays(rows, idx_a, idx_b):
    """Smallest N from which column a stays <= column b for the rest of the grid; None if never."""
    hit = None
    for N, vals in rows:
        if vals[idx_a] <= vals[idx_b]:
            if hit is None:
                hit = N
        else:
            hit = None
    return hit


def main():
    global OFFICE_ANY_N
    for rule in (False, True):
        OFFICE_ANY_N = rule
        print(f"\n######## Rule {'B: office units at any team size' if rule else 'A: office units up to 50 people, datacenter from 50'}")
        sweep()


def sweep():
    S = c3.make_sessions()
    S80 = S[:80]
    api_ps = {n: c3.api_cost(n, S) for n in c3.API}
    cap = {}
    for key in ("m5pro", "m5max64", "m5max", "ultra96"):
        K = c4.device_k("dense", key)
        if K:
            cap[key] = (K, c3.run("dense", c4.DEV[key], 1000, K, S80)["per8h"])
    print("== Team-size equilibrium, Qwen3.8-27B, 4 years, $ per heavy developer-month net of residual")
    print("   heavy developer = 40 sessions/day of 20k->200k (63 agent turns each), 21 days/month; s = share of that")
    print("   work on the open model; API = 27B median list price; own = all-server (prefill + decode on the server);")
    print("   hybrid = server prefill + Mac decode, office (LAN) / remote (egress $5/TB); regions share one fleet")
    summary = []
    for s in (V['sweep_L78_14'], V['sweep_L78_19'], 1.0):
        key = c4.pick_device("dense", s, cap)
        dev = c4.DEV[key]
        r = c3.run("dense", dev, 1000, cap[key][0], S80)
        premium = dev.price[1] - c4.BASELINE_LAPTOP
        for regions in (1, 2, V['sweep_L83_30']):
            rows = []
            print(f"\n  s={int(s*V['sweep_L85_33'])}%, {regions} region{'s' if regions > 1 else ''}, client {dev.label} (premium ${premium:,}):")
            print("      N |   API |   own (fleet)        | hybrid office/remote (fleet)")
            for N in GRID:
                api_m, own_m, hyb_o, hyb_r, fo, fh = per_month(N, s, regions, S80, r, premium, api_ps)
                rows.append((N, (api_m, own_m, hyb_o, hyb_r)))
                print(f"  {N:>5} | {api_m:5.0f} | {own_m:5.0f} ({fo[0]:>3}x {fo[1]:<5}) | {hyb_o:5.0f}/{hyb_r:<5.0f} ({fh[0]:>3}x {fh[1]})")
            own_api = first_stays(rows, 1, 0)
            hyb_api = first_stays(rows, 2, 0)
            hybr_api = first_stays(rows, V['hybr_api_L93_41'], 0)
            own_hyb = first_stays(rows, 1, 2)
            summary.append((s, regions, own_api, hyb_api, hybr_api, own_hyb, rows[-1][1]))
            print(f"    own <= API from N = {own_api}; hybrid office <= API from N = {hyb_api};"
                  f" hybrid remote <= API from N = {hybr_api}; own <= hybrid office from N = {own_hyb}")
    print("\n== Summary: smallest team (on the grid) from which the first stays at or below the second")
    print("   s     regions | own <= API | hybrid office <= API | hybrid remote <= API | own <= hybrid office | at N=20000: API/own/hybrid")
    for s, regions, a, b, c, d, last in summary:
        print(f"   {int(s*V['sweep_L101_26']):>3}%  {regions}       | {str(a):>10} | {str(b):>20} | {str(c):>20} | {str(d):>20} |"
              f" {last[0]:.0f}/{last[1]:.0f}/{last[2]:.0f}")


if __name__ == "__main__":
    main()
