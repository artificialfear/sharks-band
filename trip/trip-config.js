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

  // Check-ins during park time (10:00 AM - 6:30 PM).
  // inPerson: true = meet your chaperone face to face instead of messaging.
  checkins: [
    { time: "11:00", label: "Check-in 1" },
    { time: "13:00", label: "Lunch meetup", inPerson: true, place: "TBD: meeting spot" },
    { time: "15:00", label: "Check-in 3" },
    { time: "17:00", label: "Check-in 4" }
  ],

  // Day schedule shown to students and chaperones.
  // remind: true = also added to students' calendar reminders.
  schedule: [
    { time: "04:45", what: "Arrive at Islands High School for check-in and boarding" },
    { time: "05:00", what: "Bus leaves for Orlando (rest stop on the way, snack and juice included)" },
    { time: "10:00", what: "Arrive at Universal Orlando. Park-to-Park: Universal Studios and Islands of Adventure" },
    { time: "13:00", what: "Lunch meetup with your chaperone (in person)" },
    { time: "18:15", what: "Be at the bus. It leaves at 6:30 sharp.", remind: true },
    { time: "18:30", what: "Bus leaves for home (rest stops as needed)" },
    { time: "23:30", what: "Arrive back at Islands High School" }
  ],

  parks: ["Universal Studios Florida", "Islands of Adventure", "CityWalk"],

  bus: { pickup: "Kelly Tours motor coach. TBD: where it parks at Universal",
         note: "Take a photo of where the bus is parked. Trip #31740." },
  regroup: "TBD: where to go if you are separated from your group",

  // Shown to chaperones only (Chaperones tab).
  tourCompany: { name: "Kelly Tours", trip: "31740", phones: ["(912) 964-2010", "800-442-6152"] },

  rules: [
    "Stay with your buddy group at all times. Never go anywhere alone.",
    "Check in at every check-in time, even if nothing has changed.",
    "Answer your chaperone's BAND messages and calls right away.",
    "Keep your phone charged and BAND notifications on. Bring a battery pack if you have one.",
    "Both parks are OK (Park-to-Park). Ask your chaperone before going to CityWalk.",
    "Lunch and dinner are on your own inside the park.",
    "School dress code applies all day.",
    "Be at the bus by 6:15 PM. It leaves at 6:30."
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
