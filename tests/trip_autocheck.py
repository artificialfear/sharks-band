"""Auto check-off test: student tap -> (fake) ntfy relay -> chaperone page ticks the name.
python3 tests/trip_autocheck.py [--shots DIR]"""
import http.server, threading, functools, sys, os, json, time, urllib.parse
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = sys.argv[sys.argv.index("--shots")+1] if "--shots" in sys.argv else None
DATE_PATCH = """(() => { const real=Date; const base=new real(2026,10,14,11,58,0).getTime(); const start=real.now();
 class D extends real { constructor(...a){ if(a.length) super(...a); else super(base+(real.now()-start)); } static now(){ return base+(real.now()-start); } }
 window.Date=D; })();"""
fails=[]
def check(c,m):
    print(("PASS " if c else "FAIL ")+m)
    if not c: fails.append(m)
h=functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); h.log_message=lambda *a: None
srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),h); threading.Thread(target=srv.serve_forever,daemon=True).start()
base="http://127.0.0.1:%d/trip/index.html"%srv.server_port

RELAY={}   # topic -> [msg]
CORS={"Access-Control-Allow-Origin":"*"}
def relay(route, request):
    u=urllib.parse.urlparse(request.url); parts=u.path.strip("/").split("/")
    topic=parts[0]
    if request.method=="POST":
        m={"id":"m%d"%(sum(len(v) for v in RELAY.values())+1),"time":int(time.time()),"event":"message","topic":topic,"message":request.post_data}
        RELAY.setdefault(topic,[]).append(m)
        return route.fulfill(status=200, headers=CORS, body=json.dumps(m))
    q=urllib.parse.parse_qs(u.query); since=q.get("since",["12h"])[0]
    msgs=RELAY.get(topic,[])
    if since.isdigit(): msgs=[m for m in msgs if m["time"]>=int(since)]
    return route.fulfill(status=200, headers=CORS, body="".join(json.dumps(m)+"\n" for m in msgs))

BAND="https://band.us/band/12345678/chat/CAbcDEF"
with sync_playwright() as pw:
    b=pw.chromium.launch(channel="chromium")
    errs=[]
    def mk():
        c=b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        c.add_init_script(DATE_PATCH); c.route("https://ntfy.sh/**", relay)
        c.route("https://band.us/**", lambda r,q: r.fulfill(status=200, body="<html>BAND</html>", content_type="text/html"))
        return c
    # chaperone: manual setup with a BAND link that differs only in form (no https, trailing slash) from the students' link
    cc=mk(); p=cc.new_page(); p.on("pageerror",lambda e: errs.append(str(e)))
    p.goto(base+"#chap"); p.wait_for_timeout(300)
    p.fill("#cName","Mrs. Graham"); p.fill("#cPhone","912-555-0123"); p.fill("#cGroup","Group A"); p.fill("#cBand","band.us/band/12345678/chat/CAbcDEF/")
    p.fill("#cRoster","Jordan Smith\nAva Jones\nMarcus Lee\nMaya Brown\nMaya Banks")
    p.click("#cSave"); p.wait_for_timeout(300)
    p.click("[data-t=checkins]"); p.wait_for_timeout(300)
    check("Auto check-off is on" in p.inner_text("#autoLine"), "chaperone shows auto check-off on: "+p.inner_text("#autoLine"))
    # name matching
    mn=lambda t: p.evaluate("window.__matchName(%s, [{n:'Jordan Smith'},{n:'Ava Jones'},{n:'Marcus Lee'},{n:'Maya Brown'},{n:'Maya Banks'}])"%json.dumps(t))
    check(mn("ava jones ")=="Ava Jones" and mn("Ava")=="Ava Jones" and mn("ava j")=="Ava Jones" and mn("Jones")==None, "match: full, first-only, first+initial")
    check(mn("Maya")==None and mn("maya brown")=="Maya Brown" and mn("Maya Br")=="Maya Brown" and mn("M. Lee")=="Marcus Lee" and mn("John Lee")==None and mn("Kim Jones")==None, "match: ambiguous first name refused, last name works")
    # student
    sc=mk(); s=sc.new_page(); s.on("pageerror",lambda e: errs.append(str(e)))
    link=base+"#s="+s.evaluate("""(o)=>btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,'')""",
        {"c":"Mrs. Graham","k":BAND,"g":"Group A","b":[{"n":"Mr. Graham"}]})
    s.goto(link); s.wait_for_timeout(300)
    s.fill("#sNameIn","ava"); s.fill("#sBudIn","Marcus and Kim from Group B"); s.click("#sNameSave")
    s.click("#checkBtn"); s.wait_for_timeout(1200)
    check(s.url.startswith(base), "check-in tap stays on the trip page (no BAND)")
    check("Check-in: ava" in (s.evaluate("localStorage.getItem('trip.student.lastMsg')") or ""), "message still copied/saved")
    topics=list(RELAY.keys()); allmsgs=[m for v in RELAY.values() for m in v]
    check(len(allmsgs)==1 and topics[0].startswith("ihsband-"), "student tap sent one note to the relay")
    check(allmsgs and allmsgs[0]["message"].startswith("v1.") and "ava" not in allmsgs[0]["message"].lower() and "Marcus" not in allmsgs[0]["message"], "relay only sees encrypted text")
    # student came back from BAND
    s.goto(base); s.wait_for_timeout(600)
    check("reached Mrs. Graham's tracker" in s.inner_text("#autoNote"), "student sees 'reached tracker': "+s.inner_text("#autoNote"))
    check(s.evaluate("JSON.parse(localStorage.getItem('trip.student.outbox')||'[]').length")==0, "outbox emptied")
    # unknown typed name from another phone, same group
    s2=mk().new_page(); s2.goto(link); s2.wait_for_timeout(300); s2.fill("#sNameIn","Bubba"); s2.click("#sNameSave")
    s2.evaluate("document.getElementById('checkBtn').click()"); s2.wait_for_timeout(1000)
    # wrong group link: different topic, must not reach Mrs. Graham
    s3=mk().new_page()
    l3=base+"#s="+s3.evaluate("""(o)=>btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,'')""",
        {"c":"Ms. Kaitlyn","k":"https://band.us/band/12345678/chat/ZZZother","g":"Group C","b":[]})
    s3.goto(l3); s3.wait_for_timeout(300); s3.fill("#sNameIn","Jordan Smith"); s3.click("#sNameSave")
    s3.evaluate("document.getElementById('checkBtn').click()"); s3.wait_for_timeout(1000)
    check(len(RELAY)==2, "other group's note went to a different topic")
    # chaperone polls
    p.evaluate("window.__poll()"); p.wait_for_timeout(800)
    p.click("#roundChips .chip[data-r='1']"); p.wait_for_timeout(100)
    ci=p.inner_text("#ciList")
    check(p.inner_text("#ciTally")=="1/5", "12:00 round auto-checked 1/5 (tapper only): "+p.inner_text("#ciTally"))
    check("Ava Jones" in ci and "app" in ci, "Ava checked by the app")
    rows={r.split("\n")[0].strip() if not r.startswith("✓") else r: r for r in p.locator("#ciList .name-row").all_inner_texts()}
    ok=[r for r in p.locator("#ciList .name-row.ok").all_inner_texts()]
    check(not any("Marcus Lee" in r for r in ok) and not any("Jordan" in r for r in ok), "buddy Marcus NOT checked, other-group Jordan not: "+str(ok))
    check('"Bubba"' in p.inner_text("#ciUnmatched"), "unmatched name shown: "+p.inner_text("#ciUnmatched"))
    if SHOTS: os.makedirs(SHOTS,exist_ok=True); p.locator("#ciUnmatched").screenshot(path=os.path.join(SHOTS,"auto-um.png"))
    p.locator("#ciUnmatched .umx").first.click(); p.wait_for_timeout(100)
    check(p.inner_text("#ciUnmatched")=="", "x clears the unmatched name")
    p.evaluate("window.__poll()"); p.wait_for_timeout(800)
    check(p.inner_text("#ciUnmatched")=="", "cleared name stays gone after the next poll")
    # undo by hand sticks after another poll
    p.locator("#ciList .name-row[data-n='Ava Jones']").click(); p.wait_for_timeout(100)
    p.evaluate("window.__poll()"); p.wait_for_timeout(800)
    check(p.inner_text("#ciTally")=="0/5", "hand undo is not overwritten by the next poll")
    if SHOTS:
        os.makedirs(SHOTS,exist_ok=True); p.evaluate("window.scrollTo(0,0)"); p.screenshot(path=os.path.join(SHOTS,"auto-chap.png"))
        s.screenshot(path=os.path.join(SHOTS,"auto-student.png"))
    # relay down: chaperone says so, student keeps the note queued
    RELAYDOWN=lambda r,q: r.fulfill(status=503, headers=CORS, body="down")
    cc.unroute("https://ntfy.sh/**"); cc.route("https://ntfy.sh/**", RELAYDOWN)
    p.evaluate("window.__poll()"); p.wait_for_timeout(600)
    check("can't connect" in p.inner_text("#autoLine"), "relay down shown to chaperone")
    sc.unroute("https://ntfy.sh/**"); sc.route("https://ntfy.sh/**", RELAYDOWN)
    s.evaluate("document.getElementById('checkBtn').click()"); s.wait_for_timeout(800)
    s.goto(base); s.wait_for_timeout(500)
    check(s.evaluate("JSON.parse(localStorage.getItem('trip.student.outbox')||'[]').length")==1, "note stays queued while relay is down")
    check("Sending your" in s.inner_text("#autoNote") and "paste your copied message in BAND" in s.inner_text("#autoNote"), "student sees pending warning")
    if SHOTS: s.locator("#checkBtn").evaluate("e=>e.closest('.card').scrollIntoView()"); s.locator("#checkBtn").evaluate("e=>0"); s.screenshot(path=os.path.join(SHOTS,"auto-pending.png"))
    sc.unroute("https://ntfy.sh/**"); sc.route("https://ntfy.sh/**", relay)
    s.evaluate("window.__flush()"); s.wait_for_timeout(800)
    check(s.evaluate("JSON.parse(localStorage.getItem('trip.student.outbox')||'[]').length")==0, "queued note sent once relay is back")
    check("reached" in s.inner_text("#autoNote"), "note turns green once sent")
    check(not errs,"no page errors "+"; ".join(errs))
    b.close()
srv.shutdown(); print("\n%d failure(s)"%len(fails)); sys.exit(1 if fails else 0)
