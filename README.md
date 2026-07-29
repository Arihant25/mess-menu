# IIIT-H Mess Menus

A static page for deciding where to eat at IIIT Hyderabad.

Pick a day and a meal, and every mess open for it appears side by side with its
categories lined up across columns, so you can compare the dal, or the rice, or
the sweet, across all of them in one glance. Tap a mess to pick it; your picks
are kept per day in local storage.

## What it knows

- **Six messes**: Kadamba NonVeg/Veg, Bakul NonVeg/Veg, Yuktāhār, Palāsh
- **Which are actually open.** Messes don't all serve every meal. The two
  non-veg kitchens alternate: Kadamba NV does lunch Sun/Wed and dinner
  Mon/Thu/Fri; Bakul NV does lunch Tue/Fri and dinner Sun/Wed/Sat. Closed
  messes are listed under the sheet rather than shown as empty columns.
- **Estimated nutrition per plate.** Calories and macros for one typical
  plate at each mess, so you can compare them on a given day. See the caveat
  below; these are modelled, not measured.
- **Palāsh mirrors Bakul Veg.** Their menus are identical, so where they match
  the two collapse into one column. Palāsh matters on Tue/Fri, when Bakul Veg
  shuts its lunch line because Bakul NonVeg is running lunch.

## Nutrition is estimated

The mess API publishes no nutrition data. Every menu item carries just a name
and a category, and there is no nutrition endpoint. So the figures are modelled:
each dish takes a per-serving baseline for its food category, adjusted by
ingredient keywords in its name (chicken, paneer, fried, ghee, jaggery, millet).

Items whose category badly misleads carry their own values instead. A boiled egg
sits in the Non-Veg category, so inheriting that baseline made it a 250 kcal,
29 g protein serving; it is now 78 kcal and 6 g.

The total describes **one plate**, not the whole counter: one starch, one
lentil, one vegetable, one dairy and two rotis. Real portion size varies more
than the model does. Compare messes against each other on a given day; don't
count calories with it.

