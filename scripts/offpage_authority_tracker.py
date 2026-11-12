import argparse, csv, json, re, sys, urllib.request
from collections import Counter
from pathlib import Path

DEFAULT_CSV = Path("seo-agent/data/offpage_authority_tracker.csv")
REQUIRED_COLS = ["prospect_domain","prospect_url","site_type","relevance","eligibility","link_terms","action_status","source_page","target_url","anchor_text","link_status","discovered_by_bing","discovered_by_gsc","referral_activity","last_checked","evidence"]
DISALLOWED_SAMEAS = ("saashub.com","futuretools.io","toolpilot.ai","aitooldiscovery.com","altftool.com","hooshware.net","startupnetwork.pk","agentwebmap.com")

def load_rows(path=DEFAULT_CSV):
    with Path(path).open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if r.fieldnames != REQUIRED_COLS: raise ValueError(f"Header mismatch: {r.fieldnames}")
        return list(r)

def validate_tracker(path=DEFAULT_CSV, index_path=Path("index.html")):
    rows = load_rows(path)
    errors = [] if rows else ["Tracker has zero rows"]
    for idx, row in enumerate(rows, start=2):
        if not row["prospect_domain"].strip() or not row["prospect_url"].startswith("https://"):
            errors.append(f"Row {idx}: invalid prospect")
        score = int(row["relevance"])
        if not (0 <= score <= 100): errors.append(f"Row {idx}: bad score")
        if row["link_status"] == "live":
            if row["action_status"] == "rejected": errors.append(f"Row {idx}: rejected cannot be live")
            for k in ("source_page","target_url","anchor_text","evidence"):
                if not row[k].strip(): errors.append(f"Row {idx}: missing {k}")
            if not row["source_page"].startswith("https://"): errors.append(f"Row {idx}: https required")
            if "reciprocal" in row["link_terms"].lower(): errors.append(f"Row {idx}: reciprocal disallowed")
    if Path(index_path).exists():
        html = Path(index_path).read_text(encoding="utf-8")
        for m in re.findall(chr(34)+"sameAs"+chr(34)+r"\s*:\s*\[(.*?)\]", html, re.S):
            for bad in DISALLOWED_SAMEAS:
                if bad in m: errors.append(f"sameAs must not contain {bad}")
    return rows, errors

def summarize_tracker(rows):
    return {"total":len(rows),"by_action":dict(Counter(x["action_status"] for x in rows)),"by_link":dict(Counter(x["link_status"] for x in rows)),"bing":dict(Counter(x["discovered_by_bing"] for x in rows))}

def verify_live(rows):
    res=[]
    for row in rows:
        if row["link_status"]!="live": continue
        req=urllib.request.Request(row["source_page"],headers={"User-Agent":"AIToolGems-Verifier/1.0"})
        try:
            with urllib.request.urlopen(req,timeout=15) as r:
                b=r.read().decode("utf-8",errors="ignore")
                res.append((row["source_page"],r.status,r.status==200 and "aitoolgems.tech" in b))
        except Exception as ex:
            res.append((row["source_page"],str(ex),False))
    return res

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv",default=str(DEFAULT_CSV))
    ap.add_argument("--validate",action="store_true")
    ap.add_argument("--summary",action="store_true")
    ap.add_argument("--verify-live",action="store_true")
    a=ap.parse_args()
    rows,errs=validate_tracker(Path(a.csv))
    if a.validate:
        if errs: print("ERRORS:",errs); sys.exit(1)
        print(f"PASS: {len(rows)} rows valid")
    if a.summary: print(json.dumps(summarize_tracker(rows),indent=2))
    if a.verify_live:
        for sp,st,ok in verify_live(rows): print(f"{sp} -> status={st} has_target={ok}")

if __name__=="__main__": main()
