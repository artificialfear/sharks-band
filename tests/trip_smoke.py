"""Smoke test for trip/ (Universal trip page). python3 tests/trip_smoke.py [--shots DIR]"""
import http.server, threading, functools, sys, os, urllib.parse
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = sys.argv[sys.argv.index("--shots")+1] if "--shots" in sys.argv else None
DATE_PATCH = """(() => { const real=Date; const base=new real(2026,10,14,12,52,0).getTime(); const start=real.now();
 class D extends real { constructor(...a){ if(a.length) super(...a); else super(base+(real.now()-start)); } static now(){ return base+(real.now()-start); } }
 window.Date=D; })();"""
fails=[]
def check(c,m):
    print(("PASS " if c else "FAIL ")+m); 
    if not c: fails.append(m)
h=functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); h.log_message=lambda *a: None
srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),h); threading.Thread(target=srv.serve_forever,daemon=True).start()
base="http://127.0.0.1:%d/trip/index.html"%srv.server_port
def shot(p,n):
    if SHOTS: os.makedirs(SHOTS,exist_ok=True); p.screenshot(path=os.path.join(SHOTS,n+".png"), full_page=True)
with sync_playwright() as pw:
    b=pw.chromium.launch(channel="chromium")
    ctx=b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    ctx.add_init_script(DATE_PATCH)
    errs=[]
    p=ctx.new_page(); p.on("pageerror",lambda e: errs.append(str(e)))
    p.goto(base); check(p.is_visible("text=Open chaperone tools"),"landing shows")
    p.goto(base+"#chap"); p.wait_for_timeout(300)
    p.fill("#cName","Mrs. Graham"); p.fill("#cPhone","912-555-0123"); p.fill("#cGroup","Group A")
    p.fill("#cRoster","Jordan Smith, 912-555-0101\nAva Jones\nMarcus Lee, 912-555-0144")
    p.fill("#cBackups","Mr. Graham, 912-555-0199\nMs. Kaitlynn, 912-555-0177")
    p.click("#cSave"); p.wait_for_timeout(300)
    check(p.locator("#qr svg").count()==1,"QR code rendered")
    link=p.inner_text("#linkTxt"); check("#s=" in link,"student link made")
    shot(p,"c1-setup")
    p.click("[data-t=checkins]"); p.wait_for_timeout(200)
    check(p.locator("#ciList .name-row").count()==3,"3 names in check-ins")
    p.locator("#ciList .name-row").nth(0).click()
    check(p.inner_text("#ciTally")=="1/3","check-in tally 1/3")
    shot(p,"c2-checkins")
    p.click("[data-t=bus]"); p.locator("#busList .name-row").nth(1).click()
    check("Missing: Jordan Smith, Marcus Lee" in p.inner_text("#busBanner"),"bus banner lists missing")
    shot(p,"c3-bus")
    p.click("[data-t=lost]"); p.select_option("#lostWho","Marcus Lee"); p.fill("#lostWhere","Hagrid's line, 2:40")
    check(p.locator("#lostActions a[href^='tel:9125550144']").count()==1,"call missing student button")
    alert=p.locator("#lostActions a.danger").first.get_attribute("href")
    check(alert.startswith("sms:9125550199?&body=") and "Marcus" in urllib.parse.unquote(alert),"alert chaperone sms")
    shot(p,"c4-lost")
    p.reload(); p.wait_for_timeout(300)
    check(p.input_value("#cName")=="Mrs. Graham","chaperone setup persists")
    # full roster: spreadsheet paste (tabs, header, first/last split) + comma lines
    p.click("[data-t=setup]")
    p.evaluate("document.getElementById('masterDetails').open = true")
    p.fill("#masterIn", "First\tLast\tPhone\tGroup\nJordan\tSmith\t912-555-0101\tGroup A\nAva\tJones\t912-555-0102\tGroup B\nMarcus Lee, 912-555-0144, Group A\nZoe Park, B\nEli Ruiz")
    p.click("#masterLoad"); p.wait_for_timeout(200)
    check("5 students loaded" in p.inner_text("#masterStatus"), "master roster parsed 5: "+p.inner_text("#masterStatus"))
    check(p.locator("#pickGroups .chip").count()==4, "group chips All + Group A + Group B + B")
    p.click("#pickGroups .chip[data-g='Group B']"); p.click("#pickGroups .chip[data-all]")
    r=p.input_value("#cRoster")
    check("Ava Jones, 912-555-0102" in r, "select-all Group B fills roster with phone: "+r.replace(chr(10),' | '))
    p.click("#pickGroups .chip[data-g='']"); p.fill("#pickSearch","eli")
    p.locator("#pickList input").first.check()
    check("Eli Ruiz" in p.input_value("#cRoster"), "single pick adds name")
    p.fill("#pickSearch",""); shot(p,"c5-picker")
    p.locator("#pickList input[data-n='Eli Ruiz']").uncheck()
    check("Eli Ruiz" not in p.input_value("#cRoster"), "uncheck removes name")
    share = p.evaluate("location.href.split('#')[0] + '#chap&r=' + (function(){return ''})()")
    # roster link import on a fresh context (another chaperone's phone)
    p.evaluate("navigator.clipboard && (window.__c = null)")
    rl = p.evaluate("(() => { const m = JSON.parse(localStorage.getItem('trip.master.v1')); return btoa(unescape(encodeURIComponent(JSON.stringify(m)))).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,''); })()")
    ctx2=b.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True); q=ctx2.new_page(); q.on("pageerror",lambda e: errs.append(str(e)))
    q.goto(base+"#chap&r="+rl); q.wait_for_timeout(400)
    check("5 students loaded" in q.inner_text("#masterStatus"), "roster link imports on another phone")
    check(q.evaluate("location.hash")=="#chap", "roster removed from address bar")
    ctx2.close()
    # student
    s=ctx.new_page(); s.on("pageerror",lambda e: errs.append(str(e)))
    s.goto(link.replace(link.split("#")[0], base)); s.wait_for_timeout(300)
    check(s.inner_text("#sChap")=="Mrs. Graham","student sees chaperone")
    check(s.is_visible("#nameCard"),"asks student name")
    s.fill("#sNameIn","Ava Jones"); s.click("#sNameSave")
    s.locator("#parkChips .chip").nth(1).click()
    href=s.get_attribute("#checkBtn","href"); body=urllib.parse.unquote(href)
    check(href.startswith("sms:9125550123?&body=") and "Ava Jones" in body and "Islands of Adventure" in body,"check-in sms correct: "+body)
    check(s.get_attribute("#callBtn","href")=="tel:9125550123","call link")
    check(s.locator("#backupBox a").count()==4,"backup chaperone buttons")
    check("Lunch meetup" in s.inner_text("#cdLbl"),"countdown points at lunch: "+s.inner_text("#cdLbl"))
    shot(s,"s1-student")
    s.goto(base+"#s=garbage"); s.wait_for_timeout(200); check(s.is_visible("#bad"),"bad link handled")
    check(not errs,"no page errors "+"; ".join(errs))
    b.close()
srv.shutdown(); print("\n%d failure(s)"%len(fails)); sys.exit(1 if fails else 0)
