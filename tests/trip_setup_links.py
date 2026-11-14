"""Setup links with a realistic 26-student roster: length, QR, import on a fresh phone, truncated-link error."""
import http.server, threading, functools, sys, os, random
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS=sys.argv[sys.argv.index("--shots")+1] if "--shots" in sys.argv else None
fails=[]
def check(c,m):
    print(("PASS " if c else "FAIL ")+m)
    if not c: fails.append(m)
h=functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); h.log_message=lambda *a: None
srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),h); threading.Thread(target=srv.serve_forever,daemon=True).start()
base="http://127.0.0.1:%d/trip/index.html"%srv.server_port
random.seed(4)
first=["Jordan","Ava","Marcus","Maya","Chris","Elijah","Sophia","Isaiah","Camila","Jayden","Aaliyah","Gabriel","Brianna","Nathaniel"]
last=["Washington","Rodriguez","Thompson","Jefferson","Williams","Henderson","Montgomery","Alexander"]
groups=[("Mrs. Graham's Group",10),("Mr. Graham's Group",7),("Ms. Kaitlyn's Group",9)]
meds=["","","","Peanut allergy, carries EpiPen","Asthma, has inhaler","","Type 1 diabetes, insulin pump; snacks in bag","",""]
lines=[]; used=set()
for g,n in groups:
    for i in range(n):
        while True:
            fn,ln=random.choice(first),random.choice(last)
            if (fn,ln) not in used: used.add((fn,ln)); break
        lines.append(f"{fn} {ln} |  | {g} | {random.choice(first)} {ln} | 912-555-{random.randint(1000,9999)} | {random.choice(meds)}")
roster="Copy into trip tool\n"+"\n".join(lines)
with sync_playwright() as pw:
    b=pw.chromium.launch(channel="chromium"); errs=[]
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=3,is_mobile=True,has_touch=True); p=c.new_page(); p.on("pageerror",lambda e: errs.append(str(e)))
    p.goto(base+"#chap"); p.wait_for_timeout(300)
    p.evaluate("document.getElementById('masterDetails').open = true")
    p.fill("#masterIn",roster); p.click("#masterLoad"); p.wait_for_timeout(200)
    check("26 students loaded" in p.inner_text("#masterStatus"),"26 loaded")
    p.evaluate("document.getElementById('teamCard').open = true")
    for i,(g,n) in enumerate(groups):
        card=p.locator('#teamRows [data-g="%s"]'%g)
        card.locator("input[data-f=p]").fill("912-555-03%02d"%i); card.locator("input[data-f=k]").fill("https://band.us/band/98765432/chat/CHAT%d"%i)
    full_len=p.evaluate("""(()=>{var x=window.__buildFor("Mrs. Graham's Group"); var m=JSON.parse(localStorage.getItem('trip.master.v1'));
       return (location.href.split('#')[0]+'#chap&setup='+btoa(unescape(encodeURIComponent(JSON.stringify({s:x.s,m:m}))))).length;})()""")
    p.evaluate("window.__warmZip()"); p.wait_for_timeout(500)
    urls={g:p.evaluate('window.__setupUrl("%s")'%g) for g,_ in groups}
    check(all("#chap&setup=z" in u for u in urls.values()), "setup links are compressed")
    for g,u in urls.items(): print("  setup link", g, len(u), "chars   (old full-roster link was", full_len, ")")
    check(all(len(u) < full_len*0.35 for u in urls.values()), "setup links are a third of the old length or less")
    # plain (uncompressed) compact format still imports, for phones without CompressionStream
    plain=p.evaluate("""(()=>{ var x=window.__buildFor("Mr. Graham's Group"); return location.href.split('#')[0]+'#chap&setup='+(function(o){return btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,'')})(window.__packSetup(x.s, JSON.parse(localStorage.getItem('trip.master.v1')).filter(function(m){return m.g==="Mr. Graham's Group"}))); })()""")
    card=p.locator('#teamRows [data-g="Mrs. Graham\'s Group"]'); card.locator("button[data-a=qr]").click(); p.wait_for_timeout(300)
    check(p.is_visible("#setupQR") and p.locator("#setupQR svg").count()==1, "setup QR shows")
    p.locator("#setupQR").screenshot(path="/tmp/trip/setup-qr.png")
    import cv2
    img=cv2.imread("/tmp/trip/setup-qr.png"); val,_,_=cv2.QRCodeDetector().detectAndDecode(img)
    check(val==urls["Mrs. Graham's Group"], "QR decodes to the exact setup link (%d chars)"%len(val))
    # fresh phone opens Emily's link
    c2=b.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True); e=c2.new_page(); e.on("pageerror",lambda x: errs.append(str(x)))
    e.goto(urls["Mrs. Graham's Group"].replace(urls["Mrs. Graham's Group"].split("#")[0], base)); e.wait_for_timeout(500)
    sd=e.inner_text("#setupDone") if e.is_visible("#setupDone") else ""
    check("Mrs. Graham" in sd and "10 students" in sd, "Emily's phone set up from group link: "+sd.replace(chr(10)," | "))
    e.click("[data-t=bus]"); e.wait_for_timeout(150)
    scope=e.locator("#busScope .chip").all_inner_texts()
    check(scope==["Whole bus (26)","My group (10)"], "bus scope chips on Emily's phone: "+str(scope))
    check(e.inner_text("#busTally")=="0/26" and e.locator("#busList .name-row").count()==26 and e.locator("#busList h2").count()==3, "whole-bus count lists all 26 in 3 groups")
    heads=e.locator("#busList h2").all_inner_texts()
    check(heads[0].upper().startswith("MRS. GRAHAM'S GROUP"), "her own group is listed first: "+str(heads))
    e.locator("#busList .name-row").first.click(); e.wait_for_timeout(100)
    check(e.inner_text("#busTally")=="1/26" and "25 not checked yet (Mrs. Graham 9, Mr. Graham 7, Ms. Kaitlyn 9)" in e.inner_text("#busBanner"), "many missing: per-group counts: "+e.inner_text("#busBanner"))
    rows=e.locator("#busList .name-row")
    e.evaluate("for (let i=1;i<18;i++) document.querySelectorAll('#busList .name-row')[i].click()")
    e.wait_for_timeout(100)
    check("Missing:" in e.inner_text("#busBanner") and "(Ms. Kaitlyn)" in e.inner_text("#busBanner") and e.inner_text("#busTally")=="18/26", "8 or fewer left: names tagged by group: "+e.inner_text("#busBanner"))
    e.evaluate("for (let i=1;i<18;i++) document.querySelectorAll('#busList .name-row')[i].click()")
    e.wait_for_timeout(100)
    rpt=e.inner_text("#busReport"); check("Whole bus (Mrs. Graham)" in rpt and "1/26" in rpt, "whole-bus report text")
    if SHOTS: e.screenshot(path=os.path.join(SHOTS,"bus-whole.png"), full_page=True)
    e.click("#busScope .chip[data-s=mine]"); e.wait_for_timeout(100)
    check(e.inner_text("#busTally")=="1/10" and e.locator("#busList .name-row").count()==10, "My group shows her 10")
    e.click("#busScope .chip[data-s=all]")
    # leader counts at the first rest stop, shares checkmarks; Emily taps the link
    p.click("[data-t=bus]"); p.click("#busChips .chip[data-k=stop1]"); p.wait_for_timeout(100)
    check(p.inner_text("#busTally")=="0/26", "leader with no group of their own still sees the whole bus")
    p.evaluate("for (let i=0;i<20;i++) document.querySelectorAll('#busList .name-row')[i].click()")
    p.wait_for_timeout(100)
    check(p.inner_text("#busTally")=="20/26" and p.locator("#busShareCopy").count()==1, "leader: 20/26 + share checkmarks button")
    surl=p.evaluate("window.__busShareUrl()"); print("  checkmarks link", len(surl), "chars")
    e.goto(surl.replace(surl.split("#")[0], base)); e.wait_for_timeout(500)
    check(e.evaluate("location.hash")=="#chap" and e.is_visible("#busList"), "Emily's phone opens straight to Bus count")
    check(e.inner_text("#busTally")=="20/26" and "Rest stop (going)" in e.inner_text("#busChips .chip.on"), "Emily sees the leader's 20 checkmarks on the same count")
    e.locator("#busList .name-row:not(.ok)").first.click(); e.wait_for_timeout(100)
    check(e.inner_text("#busTally")=="21/26", "Emily can keep counting from there")
    sd=e.evaluate("JSON.parse(localStorage.getItem('trip.chap.v1')).name")
    check(sd=="Mrs. Graham", "her setup is untouched")
    # other groups' parent/medical info is NOT on her phone
    m=e.evaluate("JSON.parse(localStorage.getItem('trip.master.v1'))")
    check(len(m)==10 and all(x["g"]=="Mrs. Graham's Group" for x in m), "only her own group's contact/medical info is stored")
    e.click("[data-t=lost]"); opts=e.locator("#lostWho option").count()
    check(opts==11, "lost tab lists her 10 students (+placeholder): %d"%opts)
    e.goto(plain.replace(plain.split("#")[0], base)); e.wait_for_timeout(500)
    check("Mr. Graham" in e.inner_text("#setupDone") and "7 students" in e.inner_text("#setupDone"), "plain compact setup link also works")
    c2.close()
    # truncated link -> visible error card
    c3=b.new_context(viewport={"width":390,"height":844},is_mobile=True); t=c3.new_page()
    u=urls["Ms. Kaitlyn's Group"]; t.goto(base+"#"+u.split("#",1)[1][:400]); t.wait_for_timeout(400)
    check(t.is_visible("#setupErr"), "cut-off link shows a clear error card")
    if SHOTS: t.screenshot(path=os.path.join(SHOTS,"setup-err.png"))
    c3.close()
    check(not errs,"no page errors "+"; ".join(errs))
    b.close()
srv.shutdown(); print("\n%d failure(s)"%len(fails)); sys.exit(1 if fails else 0)
