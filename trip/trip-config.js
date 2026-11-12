// ============================================================
//  TRIP DETAILS: edit this file to change what students see.
//  No student names or phone numbers go here (this repo is public).
//  Times are 24-hour "HH:MM" on the trip date.
// ============================================================
window.TRIP = {
  title: "Universal Orlando Trip",
  band: "Islands Band",
  date: "2026-11-14",               // Saturday

  // Text check-ins (students tap "Check in" at these times).
  // inPerson: true = meet your chaperone face to face instead of texting.
  checkins: [
    { time: "11:00", label: "Check-in 1" },
    { time: "13:00", label: "Lunch meetup", inPerson: true, place: "TBD: meeting spot" },
    { time: "15:00", label: "Check-in 3" },
    { time: "17:00", label: "Check-in 4" },
    { time: "19:00", label: "Check-in 5" }
  ],

  // Day schedule shown to students (time can be "" for no time).
  schedule: [
    { time: "TBD", what: "Arrive at Islands High School" },
    { time: "TBD", what: "Buses leave for Orlando" },
    { time: "TBD", what: "Arrive at Universal, meet your chaperone at the bus" },
    { time: "13:00", what: "Lunch meetup with your chaperone (in person)" },
    { time: "TBD", what: "Meet at the buses to leave. Be EARLY.", remind: true },   // remind: true = added to the calendar reminders
    { time: "TBD", what: "Arrive back at Islands High School" }
  ],

  parks: ["Universal Studios Florida", "Islands of Adventure", "CityWalk"],

  bus: { pickup: "TBD: bus parking area / lot", note: "Take a photo of where the bus is parked." },
  regroup: "TBD: where to go if you are separated from your group",

  rules: [
    "Stay with your buddy group at all times. Never go anywhere alone.",
    "Check in at every check-in time, even if nothing has changed.",
    "Answer your chaperone's BAND messages and calls right away.",
    "Keep your phone charged and BAND notifications on. Bring a battery pack if you have one.",
    "Both parks are OK. Ask your chaperone before going to CityWalk.",
    "Be at the buses 15 minutes before departure."
  ],

  bring: ["Charged phone + battery pack", "Water bottle", "Sunscreen", "Poncho or light jacket", "Money / card for food", "School ID"]
};
