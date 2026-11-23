# BIM Press — Discipline Colorer

Colors Revit elements by discipline using **real materials painted onto the
geometry**, so the colors survive export to NWC and open correctly in
Navisworks Manage instead of arriving white.

Built for **Revit 2027.2** and **Navisworks Manage 2027** on Windows 11.

---

## Why paint instead of view filters

This is the whole point of the tool, so it's worth being clear about.

| Approach | Lives where | Survives NWC / DWG export? |
|---|---|---|
| View filter | In one view | **No** |
| View template override | In one view template | **No** |
| Override Graphics in View | In one view | **No** |
| **Paint (this tool)** | **In the element's geometry** | **Yes** |

Revit's `Document.Paint()` assigns a material to the actual *faces* of an
element. That assignment is stored in the model, not in a view, so the
exporter writes it into the NWC file and Navisworks reads it back.

View filters and graphic overrides only change how a view draws. The moment
you export, they're gone.

---

## What's in this folder

```
Discipline Colorer/
├── README.md                        ← you are here
│
├── BIMPress.extension/              ← the pyRevit version (main tool)
│   ├── lib/
│   │   └── bimpress_disciplines.py  ← ALL settings + shared code live here
│   └── BIMPress.tab/
│       └── Discipline Colors.panel/
│           ├── _layout              ← button order
│           ├── Setup.pushbutton/
│           ├── Apply Colors.pushbutton/
│           └── Remove Paint.pushbutton/
│
└── Macro Fallback/
    └── BIMPressDisciplineColors.cs  ← same tool as a Revit Macro, no install
```

**Colors, discipline names and the category list are defined in exactly one
place:** `BIMPress.extension/lib/bimpress_disciplines.py`. The three buttons
import it. Change a color there and all three buttons follow.

(The macro fallback is standalone and can't read that file, so it carries its
own copy. If you edit colors and use both tools, edit both. Simplest is to
pick one tool and stick with it.)

---

## The six disciplines

| Type this in Revit | Material created | RGB | Color |
|---|---|---|---|
| `Architectural` | BIM Press - Architectural | 180, 180, 180 | gray |
| `Structural` | BIM Press - Structural | 90, 110, 140 | steel blue |
| `Mechanical` | BIM Press - Mechanical | 230, 180, 40 | gold / yellow |
| `Plumbing` | BIM Press - Plumbing | 0, 150, 130 | green / teal |
| `Electrical` | BIM Press - Electrical | 255, 140, 0 | orange |
| `Fire Protection` | BIM Press - Fire Protection | 200, 30, 30 | red |

**Capitals don't matter.** `ELECTRICAL`, `electrical` and `Electrical` all
work, and leading/trailing spaces are ignored.

Short forms also work if you're typing a lot: `arch`, `struct`, `mech`,
`hvac`, `plumb`, `elec`, `fire`, `fp`, or just the single letters
`a` `s` `m` `p` `e` `f`. Delete the `ALIASES` block in the library file if
you'd rather force exact names.

---

# Part 1 — Install pyRevit

Skip to [Part 5](#part-5--fallback-the-revit-macro-version) if you'd rather
not install anything.

1. Go to **<https://github.com/pyrevitlabs/pyRevit/releases>**
2. Download the latest `pyRevit_<version>_signed.exe` installer.
   (The `_admin_signed` variant installs for all users — you don't need it.)
3. **Close Revit completely** before running the installer.
4. Run the installer, accept the defaults, finish.
5. Start Revit. You should see a new **pyRevit** tab on the ribbon.

> **Revit 2027 note:** pyRevit support for a brand-new Revit release
> sometimes lags a few months behind Autodesk's April launch. If the pyRevit
> tab doesn't appear, or it appears but reports that Revit 2027 is
> unsupported, check the releases page for a newer build — and in the
> meantime use the Macro version in Part 5, which needs no install and has
> no version dependency.

---

# Part 2 — Load this tool as a pyRevit button

pyRevit loads any folder ending in `.extension` that you point it at.

1. In Revit, go to the **pyRevit** tab → **pyRevit** dropdown → **Settings**.
2. Scroll to **Custom Extension Directories**.
3. Click **Add Folder** and select this folder:

   ```
   C:\Users\robbi\Documents\bim-press\Public\Revit Tools\Discipline Colorer
   ```

   Point it at the folder that *contains* `BIMPress.extension`, **not** at
   `BIMPress.extension` itself. This is the single most common mistake.
4. Click **Save Settings and Reload**.
5. A new **BIM Press** tab appears on the ribbon, with a **Discipline
   Colors** panel holding three buttons:

   **Setup** · **Apply Colors** · **Remove Paint**

**When you edit the code:** press **pyRevit → Reload** and your changes take
effect immediately. No Revit restart needed.

---

# Part 3 — Using it

### Step 1 — Press **Setup** (once per project)

This does two things:

* Creates the project parameter **"BIM Press Discipline"** (Text, Instance)
  and attaches it to ~54 model categories — walls, floors, roofs, ceilings,
  doors, windows, stairs, structural framing, structural columns,
  foundations, ducts, duct fittings, air terminals, pipes, pipe fittings,
  plumbing fixtures, conduit, cable tray, electrical equipment, electrical
  fixtures, lighting, data/comms/security devices, sprinklers, fire alarm
  devices, generic models, and more.
* Creates the six materials with their fixed colors.

**Safe to run again any time.** It checks whether the parameter and each
material already exist and updates them rather than making duplicates. Run it
again after adding a category to the list and the parameter picks it up.

It also creates a shared parameter file at:

```
C:\Users\robbi\AppData\Roaming\BIM Press\BIM Press Shared Parameters.txt
```

**Keep that file.** It holds the parameter's permanent ID. Delete it and
re-run, and Revit creates a brand-new parameter that older models won't
recognise as the same one.

---

### Step 2 — Tag your elements (you do this by hand)

This has to happen **before** Apply Colors — the script only reads what's
already there, it doesn't guess.

1. **Select elements in Revit.** You can select many at once. Fast ways:
   - Rubber-band select, then use the **Filter** button (bottom-right of the
     Revit window) to keep only the categories you want.
   - Right-click an element → **Select All Instances → In Entire Project**.
   - Click one element, then **Tab** to cycle through connected MEP runs.
2. Open the **Properties** panel (if it's hidden: **View → User Interface →
   Properties**, or type `PP`).
3. Scroll down to the **Data** group. You'll see:

   ```
   Data
     BIM Press Discipline      [                    ]
   ```
4. **Click the empty box and type a discipline name**, e.g. `Electrical`.
5. Press **Enter**, or click into the drawing area, to commit the value.

With multiple elements selected, whatever you type applies to all of them at
once. That's the quick way to tag a whole demo model.

> **Don't see "BIM Press Discipline" in Properties?** Three usual reasons:
> you haven't run **Setup** yet; you have a *type* selected rather than a
> placed instance; or that element's category isn't in the list. To add a
> category, open `lib/bimpress_disciplines.py`, add its `OST_` name to
> `CATEGORY_NAMES`, then press **Setup** again.

---

### Step 3 — Press **Apply Colors**

The script walks the model, reads each element's parameter, and paints the
faces of every element whose value matches a discipline.

Everything happens inside one named transaction — **"BIM Press - Apply
Discipline Colors"** — so a single **Ctrl+Z** undoes the whole run. If
anything goes wrong mid-way the transaction is rolled back and *nothing* is
changed.

---

## What to expect when it runs

A dialog gives you the headline numbers, and the pyRevit output window shows
the full breakdown. It looks roughly like this:

```
BIM Press - Discipline Colors :: Apply
Project: BIM Press Demo Building
Checking 1,847 elements...

Painted
  Architectural   - 412 element(s), 3,140 face(s) - RGB (180, 180, 180)
  Structural      - 168 element(s), 1,344 face(s) - RGB (90, 110, 140)
  Mechanical      -  96 element(s),   720 face(s) - RGB (230, 180, 40)
  Plumbing        -  74 element(s),   512 face(s) - RGB (0, 150, 130)
  Electrical      -  58 element(s),   406 face(s) - RGB (255, 140, 0)
  Fire Protection -  31 element(s),   186 face(s) - RGB (200, 30, 30)
  Total: 839 elements, 6,308 faces.

Skipped
  - 1,004 element(s) had no value in BIM Press Discipline - left untouched.
  - 4 element(s) had a value that does not match any discipline:
      `Electricle` - used on 3 element(s)
      `Civil`      - used on 1 element(s)
    Valid values: Architectural, Structural, Mechanical, Plumbing,
                  Electrical, Fire Protection
```

Reading that output:

* **Painted** — one line per discipline, with element count, face count and
  the RGB actually used.
* **had no value** — normal. Every element you didn't tag lands here and is
  left completely untouched.
* **does not match any discipline** — typos. The exact text is echoed back
  with a count, so `Electricle` is easy to find and fix. These elements are
  skipped, not painted, and **nothing crashes**.
* **Revit would not paint these** — appears only if some element type has no
  paintable faces. It lists element IDs so you can look them up.

Then re-run Apply Colors after fixing typos. It's safe to run repeatedly.

---

### Optional — **Remove Paint**

Strips the paint back off so you can re-shoot the demo from a clean model.

It only removes paint that uses a `BIM Press - ...` material, so paint you
applied by hand for other reasons is left alone. It doesn't delete the
parameter, the materials, or the values you typed — press **Apply Colors**
again straight afterwards and you're back.

---

# Part 4 — Export to Navisworks

1. In Revit, open a **3D view** containing the elements you want.
2. **File → Export → NWC** (Navisworks). If that entry is missing, the
   Navisworks Exporter add-in for Revit 2027 isn't installed — it ships with
   Navisworks Manage; re-run the Navisworks installer and tick the Revit
   exporter.
3. Click **Navisworks Settings** and confirm:
   - **Convert element properties** — on (so you can still search by the
     "BIM Press Discipline" property in Navisworks)
   - **Export** — `Entire project` or `Current view`, your choice
4. Save the `.nwc` and open it in **Navisworks Manage 2027**.

Your painted elements arrive in their discipline colors.

**If everything still looks white or gray in Navisworks:**

* Check you're in **Shaded** or **Full Render** mode, not Wireframe —
  Navisworks' **Viewpoint → Render Style**.
* Check no **Appearance Profiler** profile is running, and that
  **Item Tools → Reset Appearance** hasn't been overridden.
* Back in Revit, click a painted element and look at **Modify → Paint** —
  Revit shows which material a face carries.
* Re-run **Apply Colors** and read the summary. If the "Painted" total is 0,
  no element had a recognised value, which usually means Step 2 was skipped.

---

# Part 5 — Fallback: the Revit Macro version

If installing pyRevit isn't an option, `Macro Fallback/BIMPressDisciplineColors.cs`
does the same three jobs using Revit's built-in **Macro Manager** — nothing
to install.

It's written in C# rather than Python because C# is the one macro language
every Revit version reliably offers. You don't need to read C# to use it;
full paste-and-go instructions are in the comment block at the top of the
file.

The short version:

1. **Manage → Macros → Macro Manager**
2. Pick the tab named after your **project** (not "Application")
3. **Module** → name `BIMPressDisciplineColors`, language **C#** → OK
4. Paste the marked block into the `ThisDocument` class, add the `using`
   lines listed at the top of the file
5. **Build** (F8), close the editor
6. Back in Macro Manager you get three macros to run:
   `BIMPress_Setup`, `BIMPress_ApplyColors`, `BIMPress_RemovePaint`

Behaviour, colors, parameter name and summary output are the same as the
pyRevit version.

> Macros are stored inside the `.rvt` file, so they travel with the project
> but need re-pasting into each new project. That's the trade-off versus
> pyRevit, where the buttons are always on the ribbon.

---

# Troubleshooting

**"These materials do not exist yet"** — you pressed Apply Colors before
Setup. Press Setup.

**"BIM Press Discipline" missing from Properties** — see the note in Step 2.

**Nothing painted, everything counted as "no value"** — the values didn't
commit. In Revit you must press Enter or click away after typing into the
Properties box.

**Some elements report "Revit would not paint"** — a few element types have
no paintable faces (some hosted/analytical/line-based items). Options: paint
the host element instead, or give the family a material parameter and set it
to the matching `BIM Press - ...` material.

**A whole MEP system stays one color no matter what** — check you tagged the
individual duct/pipe elements, not just the equipment. Rubber-band select
plus the **Filter** button is the fast way.

**Changing a color later** — edit the RGB in `DISCIPLINE_LIST` in
`lib/bimpress_disciplines.py`, press **pyRevit → Reload**, then press
**Setup** (updates the existing materials in place — already-painted elements
change color immediately, no repaint needed).

**Worksharing** — on a workshared model you need the elements borrowed or
editable before the script can paint them. Elements owned by someone else are
reported as failures rather than crashing the run.

---

# Revit version notes

Written against the **Revit 2027** API. Both scripts already fall back
gracefully where they can, but if you ever run them on an older Revit:

| API used | Introduced | Older equivalent |
|---|---|---|
| `SpecTypeId.String.Text` | 2022 | `ParameterType.Text` |
| `GroupTypeId.Data` | 2022 | `BuiltInParameterGroup.PG_DATA` |
| `ElementId.Value` | 2024 | `ElementId.IntegerValue` |

The Python library tries the new form first and falls back automatically, so
it should just work. The C# macro can't do that at compile time — the three
lines to change are flagged with `OLDER REVIT:` comments.

`OST_FireProtection` only exists in Revit 2022+. Any category name the
running Revit doesn't recognise is skipped and reported, never fatal.
