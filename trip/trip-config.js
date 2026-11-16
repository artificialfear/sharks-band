// ============================================================
//  TRIP DETAILS: edit this file to change what students see.
//  No student names or phone numbers go here (this repo is public).
//  Times are 24-hour "HH:MM" on the trip date.
//
//  NEW TRIP CHECKLIST
//   1. Give the trip a new `id` (any text, e.g. "2027-04-10-sixflags").
//      A new id wipes the last trip's check-ins, roster and bus counts from
//      every phone, turns off old student/setup links, and gives every
//      group a fresh auto check-off channel, even if you reuse BAND chats.
//   2. Change date, place names, check-ins, schedule, rules and bring list.
//   3. In index.html bump ?v= on trip-config.js; in sw.js bump the same ?v=
//      and the CACHE name. Then push.
//   4. Trip leader opens #chap, pastes the new roster, sends new setup links.
//
//  Last trip: Universal Orlando, Sat Nov 14, 2026 (Kelly Tours #31740).
// ============================================================
window.TRIP = {
  id: "2026-11-14-universal",       // change for every trip (see checklist)
  title: "Universal Orlando Trip",
  band: "Islands Band",             // header shows the last word in teal
  date: "2026-11-14",               // Saturday

  // Short names used on bus-count labels ("Leaving Islands", "Off at Universal").
  home: "Islands",
  venue: "Universal",
  // Shown to students under "Can't reach any chaperone?" and in the chaperone lost-student steps.
  venueHelp: "Find any Universal team member or go to Guest Services and say you're with a school group.",

  // Check-ins. Each app check-in is credited to the nearest time on this list.
  checkins: [
    { time: "08:00", label: "Check-in 1" },
    { time: "12:00", label: "Check-in 2" },
    { time: "14:00", label: "Check-in 3" },
    { time: "16:00", label: "Check-in 4" },
    { time: "18:00", label: "Check-in 5 + head to the Lighthouse for the 6:30 meet-up" }
  ],

  // Day schedule shown to students and chaperones.
  // remind: true = also added to students' calendar reminders.
  schedule: [
    { time: "04:45", what: "Arrive at Islands High School for check-in and boarding" },
    { time: "05:00", what: "Bus leaves for Orlando (one rest stop on the way, snack and juice included)" },
    { time: "10:00", what: "Arrive at Universal Orlando. Park-to-Park: Universal Studios and Islands of Adventure" },
    { time: "18:30", what: "Meet up at the Islands of Adventure Lighthouse. The bus leaves for home right after (one rest stop on the way)" },
    { time: "23:30", what: "Arrive back at Islands High School" }
  ],

  // "Where are you right now?" choices (students also get "On the bus").
  // short = the label chaperones see next to app check-ins. One park is fine: [{ name: "Six Flags", short: "Six Flags" }]
  parks: [
    { name: "Universal Studios",    short: "Universal" },
    { name: "Islands of Adventure", short: "Islands" }
  ],
  parkOpen: "10:00", parkClose: "18:30",   // outside these times the check-in defaults to "On the bus"

  regroup: "Contact your chaperone for a meetup spot.",

  // Shown to chaperones only (Team tab). Set to null to hide.
  tourCompany: { name: "Kelly Tours", trip: "31740", phones: ["(912) 964-2010", "800-442-6152"] },

  rules: [
    "Stay with your buddy group at all times. Never go anywhere alone.",
    "Check in at every check-in time, even if nothing has changed.",
    "Answer your chaperone's BAND messages and calls right away.",
    "Keep your phone charged and BAND notifications on. Bring a battery pack if you have one.",
    "Both parks are OK (Park-to-Park). You may not spend time in CityWalk.",
    "Lunch and dinner are on your own inside the park.",
    "Meet up at 6:30 PM at the Islands of Adventure Lighthouse. The bus leaves right after.",
    "At rest stops, stay with your buddies and get back on the bus as soon as you're called."
  ],

  bring: [
    "Money for 2 meals: about $20-$25 each (lunch and dinner)",
    "Good walking shoes, closed toe (required for some rides)",
    "Comfortable clothes for the weather (check the forecast), within dress code",
    "Small backpack if needed",
    "Charged phone + battery pack",
    "BAND app installed and logged in"
  ]
};
