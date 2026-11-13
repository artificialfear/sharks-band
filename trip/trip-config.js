// ============================================================
//  TRIP DETAILS: edit this file to change what students see.
//  No student names or phone numbers go here (this repo is public).
//  Times are 24-hour "HH:MM" on the trip date.
//  Source: Kelly Tours itinerary, Trip #31740 (Nov 14, 2026).
// ============================================================
window.TRIP = {
  title: "Universal Orlando Trip",
  band: "Islands Band",
  date: "2026-11-14",               // Saturday

  // Check-ins (Mat, Nov 13): 8 AM, 12, 2, 4, 6 PM.
  // inPerson: true = meet your chaperone face to face instead of messaging.
  checkins: [
    { time: "08:00", label: "Check-in 1" },
    { time: "12:00", label: "Check-in 2" },
    { time: "14:00", label: "Check-in 3" },
    { time: "16:00", label: "Check-in 4" },
    { time: "18:00", label: "Check-in 5 + meet up at TBD location" }
  ],

  // Day schedule shown to students and chaperones.
  // remind: true = also added to students' calendar reminders.
  schedule: [
    { time: "04:45", what: "Arrive at Islands High School for check-in and boarding" },
    { time: "05:00", what: "Bus leaves for Orlando (one rest stop on the way, snack and juice included)" },
    { time: "10:00", what: "Arrive at Universal Orlando. Park-to-Park: Universal Studios and Islands of Adventure" },
    { time: "18:00", what: "Meet up at TBD location" },   // the 6:00 check-in reminder covers this
    { time: "18:30", what: "Bus leaves for home (one rest stop on the way)" },
    { time: "23:30", what: "Arrive back at Islands High School" }
  ],

  parks: ["Universal Studios Florida", "Islands of Adventure"],

  bus: { pickup: "Kelly Tours motor coach. TBD: where it parks at Universal",
         note: "Take a photo of where the bus is parked. Trip #31740." },
  regroup: "TBD: where to go",

  // Shown to chaperones only (Chaperones tab).
  tourCompany: { name: "Kelly Tours", trip: "31740", phones: ["(912) 964-2010", "800-442-6152"] },

  rules: [
    "Stay with your buddy group at all times. Never go anywhere alone.",
    "Check in at every check-in time, even if nothing has changed.",
    "Answer your chaperone's BAND messages and calls right away.",
    "Keep your phone charged and BAND notifications on. Bring a battery pack if you have one.",
    "Both parks are OK (Park-to-Park). You may not spend time in CityWalk.",
    "Lunch and dinner are on your own inside the park.",
    "Meet up at 6:00 PM (location TBD). The bus leaves at 6:30.",
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
