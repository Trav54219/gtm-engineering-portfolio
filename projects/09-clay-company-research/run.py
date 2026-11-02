"""Run one Clay function routine on items through the Clay CLI, poll to done, record credits.
usage: run.py <function_id> <items.json> <out.json>"""
import json,subprocess,sys,time
def clay(*a):
    p=subprocess.run(["clay",*a],capture_output=True,text=True); 
    try: return json.loads(p.stdout)
    except Exception: return {"raw":p.stdout,"err":p.stderr}
fid,items_path,out=sys.argv[1:4]
items=json.load(open(items_path))
b0=clay("credits","balance").get("balance")
r=clay("routines","runs","start","function:"+fid,"--input",json.dumps({"items":items}))
rid=r.get("routineRunId"); 
if not rid: print(r); sys.exit(1)
for _ in range(120):
    g=clay("routines","runs","get",rid)
    if g.get("status")!="in_progress": break
    time.sleep(5)
b1=clay("credits","balance").get("balance")
g["credits_before"]=b0; g["credits_after"]=b1; g["function"]=fid
json.dump(g,open(out,"w"),indent=1)
print(fid,"status",g.get("status"),"rows",g.get("total"),"credits",b0,"->",b1)
for d in g.get("data",[]): print(" ",d.get("id"),d.get("status"),json.dumps(d.get("result"))[:300])
