# Sharks Band board: handoff

**What it is:** A Viewboard welcome and agenda board for Emily's Islands High School band program. Mat built it as a surprise (Nov 2026), and it is phase 1 of a larger plan for her hub.
**Hosting:** GitHub Pages, artificialfear/sharks-band. The Viewboard opens https://artificialfear.github.io/sharks-band/

## Current state (v1.0)
- Single self-contained `index.html` plus `assets/shark.png`: Mat's standalone shark (from shark.jpeg), with the white background flood-removed and the edge rim un-matted to black. The inside of the shark's curl is background in this artwork. The right-hand shark is the same file mirrored with CSS `scaleX(-1)`. A light CSS drop-shadow outline keeps the black fins visible on the dark background. The old IHS logo was removed in v1.1.0. Bump `?v=` when you replace the image.
- Welcome screen (v1.0.3 layout, Mat's pick): a large IHS BAND logo (white-border version) on the left; on the right, ISLANDS BAND, the clock and date centered, "ISLANDS BAND" (Islands in white, Band in teal, one line), a big clock and the date, a "Next up" event countdown card, a "Today" note card, and one button per class.
- Class agenda screen: Goal, Today's Plan (numbered; tap an item to cross it off), Reminders, Home/Edit/Timer, and a warning when the agenda is from a previous day.
- Timer overlay: presets of 1/2/3/5/10/15 min and ±1 min; plays a chime at 0:00.
- Settings (gear icon): school and program name, class list (one per line), next event and date, welcome note, and JSON export/import.
- Full-screen button and a screen wake lock.
- Theme: black + teal (#239692 / #3cc7c0) to match the logo and uniforms.

## Decisions (Mat)
- The board is manual for now; there's no bell-schedule automation because Emily's schedule isn't known yet.
- Program name: "Islands High School Band". Colors: teal/black/white, with black + teal as the theme.
- Emily's district/county: SCCPSS, the same as Mat's. She has a school Google Drive and Microsoft sign-in.
- AP Music Theory meets in a different room, a keyboard lab with no Viewboard. Students there have piano keyboards.

## Notes and limits
- The default event is the Winter Band Concert on 2026-12-09. The `seed` field (currently 1) pushes it once to devices whose saved state has no event. To ship a new default event to everyone, bump the seed number and its check in load().
- All data lives in localStorage (key `sharksBand.v1`) on the device it was typed on. The Viewboard and her laptop don't sync; Export/Import is the workaround.
- No student data is stored.

## Open items / roadmap
1. Get her bell schedule and auto-switch to the current class (same pattern as artificialfear/agenda-board).
2. Optionally source agendas from a Google Sheet or Slides deck so they sync between devices.
3. Pass-off/progress system with a mature look; students see their own progress. The data must live in her school Google Drive, not in Mat's personal account (FERPA).
4. Marching tools Mat wants, all of them: spot/alternate tracking for dropouts, rehearsal attendance, uniform/trip logistics, show-music memorization check-offs, and Drill Writer links.
5. Something for the AP Theory keyboard lab (keyboard-based exercises).

## Testing
`python3 tests/smoke.py --shots /tmp/shots` serves the folder, fixes the clock to Thu Nov 12 2026 at 9:41 AM, and runs settings, agenda edit, cross-off, reload persistence and timer checks. It also takes screenshots at 1920x1080 and 1180x820.

## IHS BAND logo (added 2026-11-11; left side of the welcome screen since v1.4.0)
- `assets/ihs-band-logo.png`: a re-creation of the IHS Sharks badge reading "IHS BAND", with a transparent background.
- `assets/ihs-band-logo-white-border.png`: the same logo with a thin white outer border, for dark backgrounds.
- To rebuild, use `tools/build_logo.py`. Lettering is Anton (IHS) and Archivo Black (BAND), both from the npm packages @fontsource/anton and @fontsource/archivo-black, with the .woff converted to .ttf by fontTools into /tmp/fonts. The letters are sheared 6-7° for italic, with a white fill, a 9px teal stroke and a 26px black stroke (at 1000px). The shark is assets/shark.png at 0.714 scale, offset (140,236), matching its position in the original badge.

## Universal trip page (trip/, added 2026-11-11 for the Sat Nov 14 2026 marching band trip)
- URL: https://artificialfear.github.io/sharks-band/trip/ . Chaperone tools are at `#chap`. Student links are `#s=<base64url JSON {c:chaperone, p:phone, g:group, b:[backups]}>`, made on the chaperone Setup tab, with a QR code from the vendored qrcode-generator (MIT).
- No backend. Students' check-in and help buttons are `sms:NUM?&body=…` links (`?&` works on both iOS and Android) and `tel:` links. The student enters their name once; it's saved in localStorage on their phone.
- Chaperone roster, check-ins, bus counts and the lost-student checklist are stored in localStorage on each chaperone's phone (key `trip.chap.v1`). No student data is in the repo.
- Chaperone names and numbers live only in the link's #fragment, which is never sent to the server, but anyone with the link can read them.
- Trip details (check-in times, schedule, bus spot, regroup spot, rules) are in `trip/trip-config.js`. Several are still TBD and waiting on Mat. Bump `?v=` on the script tag after edits.
- Decisions (Mat): text/call buttons instead of a live board; check-ins at set times plus an in-person lunch meetup; both parks park-to-park, with CityWalk only with chaperone OK; chaperones are Emily, Mat and Kaitlyn (color guard).
- Full roster (added 2026-11-11): Mat pastes the whole roster once on the chaperone Setup tab. Spreadsheet rows (tabs) or "Name, phone, group" lines both work; split first/last columns are joined and a header row is skipped. The roster is stored in localStorage key `trip.master.v1`. "Copy roster link" makes `#chap&r=<base64url roster>` for the other chaperones. On load, the page imports the roster and then rewrites the URL to `#chap` so names don't stay in the address bar or history. Chaperones pick students with checkboxes (filter by group, select a whole group, search), which fills their group roster. Hand-typed names are kept.
- The roster never goes in the repo or to Claude. Mat was told not to send it.
- Added 2026-11-11 (items 1-6):
  - Offline: `trip/sw.js` network-first service worker with a 4 s timeout, then the cached copy (cache `band-trip-v2`). **When trip-config.js changes, bump `?v=` in index.html AND in sw.js ASSETS, and bump CACHE.** The manifest has no start_url, so a home-screen icon keeps the student's #s= link. As a fallback, the page saves the student info and last mode in localStorage and reopens them when opened with no hash. iOS home-screen apps have storage separate from Safari, so a student may have to re-enter their name there. Chaperones should stay in a Safari/Chrome tab.
  - Student: a "Add my location" button (geolocation) puts a maps.google.com link into the check-in and help texts. Buddy names appear in check-ins. "Add check-in reminders" downloads an .ics with VALARMs 5 min before and at each check-in, plus schedule items with `remind: true`; Clock alarm times are shown as a fallback. There's an install/save card.
  - Roster: the Google Sheet "Copy into trip tool" column (Roster!K) outputs `Name | Cell | Group | Parent | Parent phone | Medical`. The parser reads pipe lines by position, and the master roster now holds pn/pp/m. The Lost student tab shows parent call/text and medical notes. The Bus tab has a "Send this count" text to the other chaperones.
  - Google Sheet template (Mat's personal Drive, to be copied to the district Drive): https://docs.google.com/spreadsheets/d/1IH3QS_-xEQy-UJjXur_9D68_-Skm2utzMOwmPVHkUSk/edit
- Student view tabs (added 2026-11-11): bottom nav with Home (chaperone, check-in, next check-in plus reminders, Need help jump, save-page card), Help (location, call, help texts, backup chaperones), Schedule (schedule, bus, meeting spot) and Info (rules, bring, change name/buddies). The panes are `.spane[data-st]` and switch with `goTab()`. askName() jumps to Home.
- BAND (decided 2026-11-11): Emily's program uses the BAND app, with one BAND chat per chaperone group. The chaperone Setup stores `S.band` (the chat link). The student link carries `k` (chat link) and backup chaperone names only, with no phone numbers. Student buttons are real <a href=chat link> taps. On tap they copy the message to the clipboard (navigator.clipboard + execCommand fallback, synchronously inside the tap) and BAND opens; the student pastes and sends. The last message is shown on the page to copy again by hand. Calls use BAND's in-app calling, so there's no tel: for students. Older phone-based links (`p`) still work with sms:/tel:. Chaperone-to-chaperone alerts, parent calls and 911 stay as SMS/phone.
- Setup links (2026-11-13): the trip leader fills each group's chaperone name, cell and BAND chat link in "Trip leader only: set up the other chaperones" (stored in localStorage `trip.team.v1`). **Copy setup link** builds `#chap&setup=<{s: chaperone state, m: master roster}>`. Opening it fills that phone completely: name, group, BAND link, that group's students, and the other chaperones as backups with numbers. The page then rewrites the URL to `#chap`. Once set up, the Setup tab collapses to a "You're all set" summary with the student link; "Change my setup" reopens the fields. **Copy student link** makes a group's student link from the leader's phone.
- Open item: confirm on a real iPhone + Android that tapping the chat link opens the BAND app (universal link) and that paste works.
- Test: `python3 tests/trip_smoke.py --shots /tmp/trip`
