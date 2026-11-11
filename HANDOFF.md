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
