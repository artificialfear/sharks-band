"""Smoke test for the Sharks Band board.
Run from repo root:  python3 tests/smoke.py  [--shots DIR]
Serves the folder locally, drives it with Playwright, and screenshots key screens.
"""
import http.server, threading, functools, sys, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
FIXED = "new Date(2026, 10, 12, 9, 41, 0)"  # Thu Nov 12 2026, 9:41 AM

DATE_PATCH = """
(() => { const real = Date; const base = %s.getTime(); const start = real.now();
  class D extends real { constructor(...a){ if(a.length) super(...a); else super(base + (real.now()-start)); }
    static now(){ return base + (real.now()-start); } }
  window.Date = D; })();
""" % FIXED

fails = []
def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond: fails.append(msg)

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = "http://127.0.0.1:%d/index.html" % srv.server_port

def shot(page, name):
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True)
        page.screenshot(path=os.path.join(SHOTS, name + ".png"))

with sync_playwright() as p:
    b = p.chromium.launch(channel="chromium")
    ctx = b.new_context(viewport={"width": 1920, "height": 1080})
    ctx.add_init_script(DATE_PATCH)
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(url); page.wait_for_load_state("networkidle")

    check(page.inner_text("#clock").startswith("9:41"), "clock shows fixed time")
    check("Thursday, November 12" in page.inner_text("#date"), "date line")
    check(page.locator(".classbtn").count() == 4, "4 default class buttons")
    shot(page, "01-home-empty")

    # settings: event + note + rename/add class
    page.click("#setBtn")
    page.fill("#sClasses", "Concert Band\nSymphonic Band\nJazz Band\nMusic Appreciation\nAP Music Theory")
    page.fill("#sEvName", "Winter Concert")
    page.fill("#sEvDate", "2026-12-10")
    page.fill("#sNote", "Grab your folder and get set up!")
    page.click("#sSave")
    check(page.locator(".classbtn").count() == 5, "5 class buttons after settings")
    check("28 days" in page.inner_text("#cards"), "event countdown 28 days")

    # agenda edit
    page.locator(".classbtn").nth(0).click()
    page.click("#editBtn")
    page.fill("#eGoal", "Clean m. 41-58 of the Holst so it's concert-ready")
    page.fill("#ePlan", "Warm-up: Remington + B-flat chorale\nSight-reading: line 12\nHolst Mvt. 1, m. 41-58\nSleigh Ride run-through\nPack up + chairs")
    page.fill("#eRem", "Concert attire check Friday\nPlaying test: concert F scale due Tue")
    page.click("#eSave")
    check(page.locator("#agPlan li").count() == 5, "5 plan items")
    page.locator("#agPlan li").nth(0).click()
    check("done" in page.locator("#agPlan li").nth(0).get_attribute("class"), "tap crosses off item")
    shot(page, "02-agenda")

    # persistence
    page.reload(); page.wait_for_load_state("networkidle")
    check("Today's agenda ready" in page.inner_text("#classbar"), "agenda persists after reload")
    shot(page, "03-home-filled")

    # timer
    page.locator(".classbtn").nth(0).click()
    page.click("#timerBtn"); page.click("text=5 min")
    check(page.inner_text("#tBig") == "5:00", "timer preset 5:00")
    shot(page, "04-timer")
    page.click("#tClose")

    # settings modal screenshot
    page.click("#homeBtn"); page.click("#setBtn"); shot(page, "05-settings"); page.click("#sCancel")

    # tablet / portrait-ish width
    page.set_viewport_size({"width": 1180, "height": 820}); shot(page, "06-tablet-home")
    page.locator(".classbtn").nth(0).click(); shot(page, "07-tablet-agenda")

    check(not errs, "no page errors " + "; ".join(errs))
    b.close()

srv.shutdown()
print("\n%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
