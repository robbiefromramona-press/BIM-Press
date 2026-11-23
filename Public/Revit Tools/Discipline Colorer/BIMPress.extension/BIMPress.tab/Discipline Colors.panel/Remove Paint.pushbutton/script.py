# -*- coding: utf-8 -*-
"""
BIM PRESS - DISCIPLINE COLORS :: BUTTON 3 OF 3 - REMOVE PAINT

WHAT THIS BUTTON DOES
---------------------
Undoes the painting. Useful when you want to re-shoot the demo from a clean
model, or when you have changed a colour and want to start over.

IMPORTANT: it only removes paint that uses a "BIM Press - ..." material.
Paint that somebody applied by hand with a different material is left alone.

It does NOT delete the parameter, the materials, or the values you typed -
so you can press "Apply Colors" again straight afterwards.
"""

__title__ = "Remove\nPaint"
__author__ = "BIM Press"

from pyrevit import revit, DB, forms, script

import bimpress_disciplines as bp


doc = revit.doc
output = script.get_output()


if doc.IsFamilyDocument:
    forms.alert(
        "This tool runs on a Revit PROJECT (.rvt).\n\n"
        "You currently have a family (.rfa) open.",
        title="BIM Press - Remove Paint",
        exitscript=True)


# -----------------------------------------------------------------------------
# Work out which materials count as "ours".
# -----------------------------------------------------------------------------
our_material_ids = set()
our_material_names = []

for discipline, _rgb in bp.DISCIPLINE_LIST:
    name = bp.material_name_for(discipline)
    material = bp.find_material(doc, name)
    if material is not None:
        our_material_ids.add(bp.element_id_value(material.Id))
        our_material_names.append(name)

if not our_material_ids:
    forms.alert(
        "No 'BIM Press - ...' materials exist in this project, so there is "
        "nothing for this button to remove.",
        title="BIM Press - Remove Paint",
        exitscript=True)


# -----------------------------------------------------------------------------
# Ask first. Stripping paint across a whole model is worth confirming.
# -----------------------------------------------------------------------------
proceed = forms.alert(
    "Remove all paint that uses these materials?\n\n{0}\n\n"
    "Your discipline parameter values are kept, so you can press "
    "'Apply Colors' again afterwards.".format(
        "\n".join(our_material_names)),
    title="BIM Press - Remove Paint",
    yes=True, no=True)

if not proceed:
    script.exit()


# -----------------------------------------------------------------------------
# Strip the paint, inside one named Transaction.
# -----------------------------------------------------------------------------
builtin_cats, _skipped = bp.resolve_builtin_categories()
elements = bp.collect_candidate_elements(doc, builtin_cats)

geom_opts = bp.geometry_options()
elements_cleaned = 0
faces_cleaned = 0
run_error = None

transaction = DB.Transaction(doc, "BIM Press - Remove Discipline Paint")
transaction.Start()
try:
    for element in elements:
        removed = bp.strip_paint(
            doc, element, geom_opts, only_material_ids=our_material_ids)
        if removed > 0:
            elements_cleaned += 1
            faces_cleaned += removed

    transaction.Commit()

except Exception as err:
    transaction.RollBack()
    run_error = err

if run_error is not None:
    forms.alert(
        "Something went wrong and NO changes were saved to the model.\n\n"
        "{0}".format(run_error),
        title="BIM Press - Remove Paint",
        exitscript=True)


# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
output.print_md("# BIM Press - Discipline Colors :: Remove Paint")
output.print_md("Project: **{0}**".format(doc.Title))
output.print_md(
    "Checked {0} elements. Removed paint from **{1}** element(s), "
    "**{2}** face(s).".format(len(elements), elements_cleaned, faces_cleaned))

forms.alert(
    "Done.\n\n"
    "Paint removed from {0} element(s) / {1} face(s).".format(
        elements_cleaned, faces_cleaned),
    title="BIM Press - Remove Paint")
