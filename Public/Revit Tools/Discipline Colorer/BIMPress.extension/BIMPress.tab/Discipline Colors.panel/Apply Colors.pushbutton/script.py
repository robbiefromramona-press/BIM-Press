# -*- coding: utf-8 -*-
"""
BIM PRESS - DISCIPLINE COLORS :: BUTTON 2 OF 3 - APPLY COLORS

WHAT THIS BUTTON DOES
---------------------
Walks the model, reads each element's "BIM Press Discipline" parameter, and
PAINTS that element's faces with the matching discipline material.

WHY PAINT AND NOT A VIEW FILTER
-------------------------------
A view filter or a graphic override only changes how an element looks in one
view. Revit does not write that into the geometry, so it is gone the moment
you export to NWC or DWG - the elements arrive in Navisworks white.

Document.Paint() is different. It assigns a material to the actual faces of
the element, stored in the model itself, so the colour travels with the
geometry into Navisworks Manage.

BEFORE YOU RUN THIS
-------------------
1. Run the "Setup" button once (creates the parameter and the materials).
2. Select elements in Revit, and in the Properties panel type a discipline
   name into "BIM Press Discipline".

Matching ignores capitals, so "ELECTRICAL", "electrical" and "Electrical"
all work.

WHAT YOU GET AT THE END
-----------------------
A summary in the pyRevit output window:
  * how many elements were painted, per discipline
  * how many were skipped because they had no value
  * any values typed that did not match a discipline (with a count of each,
    so typos are easy to find)
  * any elements Revit refused to paint

Nothing here crashes on a bad value - it is counted and reported instead.

Colours, names and categories are NOT defined here. They live in one place:
    BIMPress.extension/lib/bimpress_disciplines.py
"""

__title__ = "Apply\nColors"
__author__ = "BIM Press"

from pyrevit import revit, DB, forms, script

import bimpress_disciplines as bp


doc = revit.doc
output = script.get_output()


# -----------------------------------------------------------------------------
# Guard clauses - fail early with a clear message rather than halfway through.
# -----------------------------------------------------------------------------
if doc.IsFamilyDocument:
    forms.alert(
        "This tool runs on a Revit PROJECT (.rvt).\n\n"
        "You currently have a family (.rfa) open.",
        title="BIM Press - Apply Colors",
        exitscript=True)


# Look up the six materials before touching anything. If they are missing the
# user has not run Setup yet.
material_ids = {}          # discipline name -> ElementId of its material
missing_materials = []

for discipline, _rgb in bp.DISCIPLINE_LIST:
    name = bp.material_name_for(discipline)
    material = bp.find_material(doc, name)
    if material is None:
        missing_materials.append(name)
    else:
        material_ids[discipline] = material.Id

if missing_materials:
    forms.alert(
        "These materials do not exist yet:\n\n{0}\n\n"
        "Press the 'Setup' button first.".format(
            "\n".join(missing_materials)),
        title="BIM Press - Apply Colors",
        exitscript=True)


# -----------------------------------------------------------------------------
# Gather the elements we are going to look at.
# -----------------------------------------------------------------------------
builtin_cats, _skipped = bp.resolve_builtin_categories()
elements = bp.collect_candidate_elements(doc, builtin_cats)

output.print_md("# BIM Press - Discipline Colors :: Apply")
output.print_md("Project: **{0}**".format(doc.Title))
output.print_md("Checking **{0}** elements...".format(len(elements)))


# -----------------------------------------------------------------------------
# Counters for the end-of-run summary.
# -----------------------------------------------------------------------------
painted_elements = {}      # discipline -> how many elements got painted
painted_faces = {}         # discipline -> how many faces got painted
for discipline, _rgb in bp.DISCIPLINE_LIST:
    painted_elements[discipline] = 0
    painted_faces[discipline] = 0

skipped_no_value = 0       # parameter blank or not present on this element
unrecognised = {}          # the text that was typed -> how many times
could_not_paint = []       # (element id, category, discipline) tuples

# A few examples of each problem, so the summary stays readable on big models.
MAX_EXAMPLES = 15


# -----------------------------------------------------------------------------
# THE MAIN LOOP - all model changes wrapped in one named Transaction.
#
# A Transaction is Revit's undo bundle. The name below is what appears in
# Revit's undo list, so it is worth making it recognisable.
# -----------------------------------------------------------------------------
geom_opts = bp.geometry_options()
run_error = None

transaction = DB.Transaction(doc, "BIM Press - Apply Discipline Colors")
transaction.Start()
try:
    for element in elements:

        # --- Read the parameter --------------------------------------------
        raw_value = bp.read_discipline_value(element)
        if raw_value is None:
            skipped_no_value += 1
            continue

        # --- Match it to a discipline (case-insensitive) --------------------
        discipline = bp.match_discipline(raw_value)
        if discipline is None:
            key = raw_value.strip()
            unrecognised[key] = unrecognised.get(key, 0) + 1
            continue

        # --- Paint it -------------------------------------------------------
        face_count = bp.paint_element(
            doc, element, material_ids[discipline], geom_opts)

        if face_count > 0:
            painted_elements[discipline] += 1
            painted_faces[discipline] += face_count
        else:
            # Revit would not paint any face of this element. Record it so the
            # user knows, instead of silently doing nothing.
            if len(could_not_paint) < MAX_EXAMPLES:
                could_not_paint.append((
                    bp.element_id_value(element.Id),
                    bp.category_name(element),
                    discipline))

    transaction.Commit()

except Exception as err:
    # Undo everything so the model is never left half-painted.
    transaction.RollBack()
    run_error = err

if run_error is not None:
    forms.alert(
        "Something went wrong and NO changes were saved to the model.\n\n"
        "{0}".format(run_error),
        title="BIM Press - Apply Colors",
        exitscript=True)


# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
total_painted = sum(painted_elements.values())
total_faces = sum(painted_faces.values())

output.print_md("## Painted")

if total_painted == 0:
    output.print_md(
        "**Nothing was painted.** No element had a recognised value in "
        "**{0}**.".format(bp.PARAM_NAME))
else:
    for discipline, rgb in bp.DISCIPLINE_LIST:
        count = painted_elements[discipline]
        if count == 0:
            continue
        output.print_md(
            "- **{0}** - {1} element(s), {2} face(s) - RGB "
            "({3}, {4}, {5})".format(
                discipline, count, painted_faces[discipline],
                rgb[0], rgb[1], rgb[2]))

    output.print_md(
        "**Total: {0} elements, {1} faces.**".format(
            total_painted, total_faces))


output.print_md("## Skipped")
output.print_md(
    "- **{0}** element(s) had no value in {1} - left untouched.".format(
        skipped_no_value, bp.PARAM_NAME))

if unrecognised:
    output.print_md(
        "- **{0}** element(s) had a value that does not match any "
        "discipline:".format(sum(unrecognised.values())))
    for text in sorted(unrecognised.keys()):
        output.print_md(
            "    - `{0}` - used on {1} element(s)".format(
                text, unrecognised[text]))
    output.print_md(
        "  Valid values: {0}".format(
            ", ".join([name for name, _rgb in bp.DISCIPLINE_LIST])))
else:
    output.print_md("- No unrecognised values. Nice.")

if could_not_paint:
    output.print_md(
        "- Revit would not paint these elements (showing up to {0}):".format(
            MAX_EXAMPLES))
    for elem_id, cat, discipline in could_not_paint:
        output.print_md(
            "    - id {0} - {1} - tagged {2}".format(elem_id, cat, discipline))
    output.print_md(
        "  Some element types have no paintable faces. Painting the host "
        "element, or giving the family a material parameter, is the usual "
        "way around it.")


output.print_md("## Next step")
output.print_md(
    "Export to NWC (**File > Export > NWC**) and open it in Navisworks "
    "Manage. The painted elements carry their discipline colour with them.")


forms.alert(
    "Done.\n\n"
    "Painted:  {0} elements ({1} faces)\n"
    "No value: {2} elements\n"
    "Bad value: {3} elements\n\n"
    "Full breakdown per discipline is in the pyRevit output window.".format(
        total_painted,
        total_faces,
        skipped_no_value,
        sum(unrecognised.values()) if unrecognised else 0),
    title="BIM Press - Apply Colors")
