# -*- coding: utf-8 -*-
"""
BIM PRESS - DISCIPLINE COLORS :: BUTTON 1 OF 3 - SETUP

WHAT THIS BUTTON DOES
---------------------
Prepares the current Revit project. Run it once per project, before you do
anything else.

  STEP 1  Creates the project parameter "BIM Press Discipline"
          (Text, Instance) and attaches it to a wide list of model
          categories - walls, floors, framing, ducts, pipes, conduit,
          sprinklers, fire alarm devices and so on.

  STEP 2  Creates the six discipline materials with their fixed colours.

It is SAFE TO RUN AS MANY TIMES AS YOU LIKE. It checks for the parameter and
for each material first, and updates rather than duplicating.

AFTER RUNNING THIS
------------------
Select elements in Revit, open the Properties panel, find
"BIM Press Discipline" under the Data group, and type a discipline name.
Then press the "Apply Colors" button.

Colours and category list are NOT defined here. They live in one place:
    BIMPress.extension/lib/bimpress_disciplines.py
"""

__title__ = "Setup"
__author__ = "BIM Press"

from pyrevit import revit, DB, forms, script

# Our shared settings and helpers. pyRevit finds this because it lives in the
# extension's "lib" folder.
import bimpress_disciplines as bp


# "doc" is the Revit project that is currently open.
doc = revit.doc

# Where our text output goes (the pyRevit output window).
output = script.get_output()


# -----------------------------------------------------------------------------
# Guard clause: this tool only makes sense in a project, not a family editor.
# -----------------------------------------------------------------------------
if doc.IsFamilyDocument:
    forms.alert(
        "This tool runs on a Revit PROJECT (.rvt).\n\n"
        "You currently have a family (.rfa) open.",
        title="BIM Press - Setup",
        exitscript=True)


output.print_md("# BIM Press - Discipline Colors :: Setup")
output.print_md("Project: **{0}**".format(doc.Title))

# -----------------------------------------------------------------------------
# PHASE 1 - everything that changes the model, inside one Transaction.
#
# A Transaction is Revit's "undo bundle". Every model change must happen
# inside one, and it gets a name so the user sees it in the undo list.
# -----------------------------------------------------------------------------
param_result = None
material_results = []
appearance_jobs = []
setup_error = None

transaction = DB.Transaction(doc, "BIM Press - Setup Discipline Parameter "
                                  "and Materials")
transaction.Start()
try:
    # STEP 1 - the project parameter.
    param_result = bp.ensure_project_parameter(doc)

    # STEP 2 - the six materials.
    material_results, appearance_jobs = bp.ensure_materials(doc)

    transaction.Commit()
except Exception as err:
    # If anything at all went wrong, undo the whole lot so the model is not
    # left half-finished.
    transaction.RollBack()
    setup_error = err

if setup_error is not None:
    forms.alert(
        "Setup failed and nothing was changed in the model.\n\n"
        "{0}".format(setup_error),
        title="BIM Press - Setup",
        exitscript=True)


# -----------------------------------------------------------------------------
# PHASE 2 - render appearance colours.
#
# This has to happen AFTER the transaction above is committed. Revit's
# appearance-asset editor runs its own transaction internally and refuses to
# start while another one is open.
#
# This part is optional polish: it makes Realistic / rendered views match the
# shaded colours. If it fails, the shaded colour (already set above) is what
# the NWC export uses anyway, so the tool still does its job.
# -----------------------------------------------------------------------------
appearance_ok = 0
for discipline, asset_id, rgb in appearance_jobs:
    if bp.set_render_appearance_color(doc, asset_id, rgb):
        appearance_ok += 1


# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
output.print_md("## Step 1 - Project parameter")

if param_result["action"] == "created":
    output.print_md(
        "Created the parameter **{0}** (Text, Instance).".format(bp.PARAM_NAME))
else:
    output.print_md(
        "**{0}** already existed - re-attached it to the current category "
        "list.".format(bp.PARAM_NAME))

output.print_md(
    "Attached to **{0}** categories.".format(
        len(param_result["bound_category_names"])))

if param_result["skipped_category_names"]:
    output.print_md(
        "Skipped {0} category name(s) that do not exist in this Revit "
        "version: {1}".format(
            len(param_result["skipped_category_names"]),
            ", ".join(param_result["skipped_category_names"])))

output.print_md(
    "Shared parameter file: `{0}`".format(bp.SHARED_PARAM_FILE))
output.print_md(
    "_Keep that file. It holds the parameter's permanent ID._")


output.print_md("## Step 2 - Materials")

created_count = 0
for item in material_results:
    rgb = item["rgb"]
    state = "created" if item["created"] else "already existed (colour reset)"
    if item["created"]:
        created_count += 1
    output.print_md(
        "- **{0}** - RGB ({1}, {2}, {3}) - {4}".format(
            item["material_name"], rgb[0], rgb[1], rgb[2], state))

output.print_md(
    "{0} created, {1} updated.".format(
        created_count, len(material_results) - created_count))

if bp.SET_RENDER_APPEARANCE:
    output.print_md(
        "Render appearance colour set on {0} of {1} materials.".format(
            appearance_ok, len(material_results)))


output.print_md("## What to do next")
output.print_md(
    "1. Select some elements in Revit.\n"
    "2. In the **Properties** panel, scroll to the **Data** group and find "
    "**{0}**.\n"
    "3. Type one of: {1}.\n"
    "4. Press the **Apply Colors** button on this panel.".format(
        bp.PARAM_NAME,
        ", ".join([name for name, _rgb in bp.DISCIPLINE_LIST])))

forms.alert(
    "Setup finished.\n\n"
    "Parameter '{0}': {1}\n"
    "Materials: {2} created, {3} updated.\n\n"
    "Next: tag elements in the Properties panel, then run 'Apply Colors'.\n"
    "Full details are in the pyRevit output window.".format(
        bp.PARAM_NAME,
        param_result["action"],
        created_count,
        len(material_results) - created_count),
    title="BIM Press - Setup")
