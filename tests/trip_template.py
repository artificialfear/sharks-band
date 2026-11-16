"""Template test: per-trip data reset, old-link rejection, "trip is over" card, a different trip's config.
python3 tests/trip_template.py"""
import http.server, threading, functools, sys, os, json, re
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = open(os.path.join(ROOT, "trip", "trip-config.js")).read()
TID = re.search(r'id:\s*"([^"]+)"', CFG).group(1)
def date_patch(y, mo, d, h, mi):
    return """(() => { const real=Date; const base=new real(%d,%d,%d,%d,%d,0).getTime(); const start=real.now();
 class D extends real { constructor(...a){ if(a.length) super(...a); else super(base+(real.now()-start)); } static now(){ return base+(real.now()-start); } }
 window.Date=D; })();""" % (y, mo-1, d, h, mi)
TRIP_DAY = date_patch(2026, 11, 14, 12, 30)
AFTER = date_patch(2026, 11, 16, 18, 0)
fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); h.log_message = lambda *a: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
base = "http://127.0.0.1:%d/trip/index.html" % srv.server_port
ENC = """(o)=>btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,'')"""
BAND = "https://band.us/band/12345678/chat/CAbcDEF"

# a different trip: new id, one park as a plain string, different home/venue, no tour company
ALT = (CFG.replace('id: "%s"' % TID, 'id: "2027-04-10-sixflags"')
          .replace('home: "Islands"', 'home: "Islands HS"').replace('venue: "Universal"', 'venue: "Six Flags"')
          .replace('date: "2026-11-14"', 'date: "2027-04-10"'))
ALT = re.sub(r'parks: \[[^\]]*\]', 'parks: ["Six Flags Over Georgia"]', ALT)
ALT = re.sub(r'tourCompany: \{[^}]*\}', 'tourCompany: null', ALT)
ALT = re.sub(r'venueHelp: "[^"]*"', 'venueHelp: "Find any Six Flags employee."', ALT)

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chromium")
    errs = []
    def mk(clock=TRIP_DAY, cfg=None):
        c = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        c.add_init_script(clock)
        c.route("https://ntfy.sh/**", lambda r, q: r.fulfill(status=200, headers={"Access-Control-Allow-Origin": "*"}, body=""))
        if cfg: c.route("**/trip-config.js*", lambda r, q: r.fulfill(status=200, content_type="application/javascript", body=cfg))
        return c

    # 1. data from before the template (no trip.id) is wiped on load; the student's name survives
    c = mk(); p = c.new_page(); p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(base); p.evaluate("""localStorage.clear();
      localStorage.setItem('trip.chap.v1', JSON.stringify({name:'Old',group:'Old group',ci:{r0:{'Ava':'8:01 AM'}},bus:{},lost:{who:'',where:'',wear:'',done:[]}}));
      localStorage.setItem('trip.master.v1', JSON.stringify([{n:'Ava'}]));
      localStorage.setItem('trip.student.name', JSON.stringify('Ava Jones'));
      localStorage.setItem('trip.student.outbox', JSON.stringify([{id:'x'}]));""")
    p.reload(); p.wait_for_timeout(300)
    keys = p.evaluate("Object.keys(localStorage).sort()")
    check(keys == ["trip.id", "trip.student.name"], "old trip data wiped, name kept: " + str(keys))
    check(p.evaluate("JSON.parse(localStorage.getItem('trip.id'))") == TID, "trip id stored")
    p.reload(); p.wait_for_timeout(200)
    p.evaluate("localStorage.setItem('trip.chap.v1', JSON.stringify({name:'Keep',group:'G',ci:{},bus:{},lost:{who:'',where:'',wear:'',done:[]}}))")
    p.reload(); p.wait_for_timeout(200)
    check(p.evaluate("JSON.parse(localStorage.getItem('trip.chap.v1')).name") == "Keep", "same trip id: data is left alone")

    # 2. student links: no trip id or a different one -> "earlier trip"; this trip's id -> works
    for label, info in [("no id", {"c": "Mrs. Graham", "k": BAND, "g": "A", "b": []}),
                        ("other id", {"t": "2025-old", "c": "Mrs. Graham", "k": BAND, "g": "A", "b": []})]:
        p.goto(base + "#s=" + p.evaluate(ENC, info)); p.wait_for_timeout(300)
        check(p.is_visible("#old") and not p.is_visible("#student"), "student link with %s shows 'earlier trip'" % label)
    p.goto(base + "#s=" + p.evaluate(ENC, {"t": TID, "c": "Mrs. Graham", "k": BAND, "g": "A", "b": []})); p.wait_for_timeout(300)
    check(p.is_visible("#student"), "this trip's student link opens")
    check(not p.is_visible(".overCard"), "no 'trip is over' card on trip day")
    p.goto(base + "#s=garbage"); p.wait_for_timeout(200)
    check(p.is_visible("#bad"), "garbage link still shows 'didn't open'")

    # 3. setup link from an earlier trip changes nothing
    p.goto(base + "#chap"); p.wait_for_timeout(200)
    before = p.evaluate("localStorage.getItem('trip.chap.v1')")
    old = p.evaluate(ENC, {"v": 2, "s": ["Intruder", "", "Old Group", BAND, ""], "m": [["Zed"]]})
    p.goto(base + "#chap&setup=" + old); p.wait_for_timeout(400)
    check(p.is_visible("#oldSetup"), "old setup link shows 'earlier trip' card")
    check(p.evaluate("localStorage.getItem('trip.chap.v1')") == before, "old setup link didn't touch this phone")
    check("setup=" not in p.url, "setup data removed from the address bar")
    good = p.evaluate(ENC, {"v": 2, "t": TID, "s": ["Mrs. Graham", "", "Group A", BAND, ""], "m": [["Ava Jones"], ["Maya Brown"]]})
    p.goto(base + "#chap&setup=" + good); p.wait_for_timeout(400)
    check(p.evaluate("JSON.parse(localStorage.getItem('trip.chap.v1')).name") == "Mrs. Graham", "this trip's setup link works")

    # 4. "Clear all trip data on this phone" needs two taps
    p.goto(base + "#chap"); p.wait_for_timeout(300)
    p.click("#wipeAll"); p.wait_for_timeout(150)
    check(p.evaluate("localStorage.getItem('trip.chap.v1')") is not None, "one tap does nothing")
    p.click("#wipeAll"); p.wait_for_timeout(800)
    keys = p.evaluate("Object.keys(localStorage).sort()")
    check(keys == ["trip.id", "trip.mode"], "two taps wipe everything incl. student name: " + str(keys))
    c.close()

    # 5. after the trip: banner on both pages
    c = mk(AFTER); p = c.new_page(); p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(base + "#s=" + p.evaluate(ENC, {"t": TID, "c": "Mrs. Graham", "k": BAND, "g": "A", "b": []})); p.wait_for_timeout(300)
    check(p.locator("#student .overCard").is_visible() and "Universal Orlando Trip" in p.inner_text("#student .overCard"), "student sees 'trip is over'")
    p.goto(base + "#chap"); p.wait_for_timeout(300)
    check(p.locator("#chap .overCard").is_visible(), "chaperone sees 'trip is over'")
    c.close()

    # 6. a different trip's config
    c = mk(date_patch(2027, 4, 10, 12, 0), ALT); p = c.new_page(); p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(base); p.wait_for_timeout(200)
    t_new = p.evaluate("window.__relay.relayFor(%s).then(function(r){return r.topic;})" % json.dumps(BAND))
    p.goto(base + "#s=" + p.evaluate(ENC, {"t": "2027-04-10-sixflags", "c": "Mr. Jones", "k": BAND, "g": "A", "b": []})); p.wait_for_timeout(300)
    chips = [x.strip() for x in p.locator("#parkChips .chip").all_inner_texts()]
    check(chips == ["On the bus", "Six Flags Over Georgia"], "one park as a plain string: " + str(chips))
    check("Find any Six Flags employee." in p.inner_text("#venueHelp"), "venue help text from config")
    check(p.inner_text("#hdrBand").replace("\n", " ") == "Islands Band", "header from config")
    p.goto(base + "#chap"); p.wait_for_timeout(300)
    p.fill("#cName", "Mr. Jones"); p.fill("#cGroup", "A"); p.fill("#cBand", BAND); p.fill("#cRoster", "Ava Jones"); p.click("#cSave"); p.wait_for_timeout(200)
    p.click("[data-t=bus]"); p.wait_for_timeout(200)
    bus = [x.strip() for x in p.locator("#busChips .chip").all_inner_texts()]
    check("Leaving Islands HS" in bus[0] and "Off at Six Flags" in bus[2] and "Off at Islands HS" in bus[5], "bus labels from home/venue: " + str(bus))
    check(not p.is_visible("#tourCard"), "tourCompany: null hides the tour card")
    c.close()
    c = mk(); p = c.new_page(); p.goto(base); p.wait_for_timeout(200)
    t_old = p.evaluate("window.__relay.relayFor(%s).then(function(r){return r.topic;})" % json.dumps(BAND))
    check(t_new != t_old, "same BAND chat, new trip id -> different relay topic")
    c.close()
    check(not errs, "no page errors: " + "; ".join(errs[:3]))
    b.close()
print("\n%d failure(s)" % len(fails)); sys.exit(1 if fails else 0)
