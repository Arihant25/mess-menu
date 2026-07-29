# IIIT-H Mess Menus

A static page for deciding where to eat at IIIT Hyderabad.

Pick a day and a meal, and every mess open for it appears side by side with its
categories lined up across columns — so you can compare the dal, or the rice, or
the sweet, across all of them in one glance. Tap a mess to pick it; your picks
are kept per day in local storage.

## What it knows

- **Six messes** — Kadamba NonVeg/Veg, Bakul NonVeg/Veg, Yuktāhār, Palāsh
- **Which are actually open.** Messes don't all serve every meal. The two
  non-veg kitchens alternate: Kadamba NV does lunch Sun/Wed and dinner
  Mon/Thu/Fri; Bakul NV does lunch Tue/Fri and dinner Sun/Wed/Sat. Closed
  messes are listed under the sheet rather than shown as empty columns.
- **Palāsh mirrors Bakul Veg.** Their menus are identical, so where they match
  the two collapse into one column. Palāsh matters on Tue/Fri, when Bakul Veg
  shuts its lunch line because Bakul NonVeg is running lunch.

## Notes

Opening days are empirical. The API's timings endpoint reports some messes as
open when registration then refuses with `mess-closed`, so the table follows
what registration actually accepts.

Menu data is embedded at build time from the IIIT-H mess API, one entry per
Sunday-anchored week. The page picks the week containing the selected date, so
it stays correct across months without edits — but it only covers the weeks that
were fetched. Re-run the extraction to extend it.
