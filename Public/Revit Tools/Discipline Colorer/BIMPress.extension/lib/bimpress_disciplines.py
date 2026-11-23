# -*- coding: utf-8 -*-
"""
BIM PRESS - DISCIPLINE COLORS
Shared settings and helper functions.

=============================================================================
WHAT THIS FILE IS
=============================================================================
This file is a "library" - it does not do anything on its own. It holds the
settings (discipline names, RGB colors, category list) and the reusable
functions that the three toolbar buttons call.

Because everything lives here, there is exactly ONE place to change a color
or add a discipline. The buttons never repeat these values.

pyRevit automatically puts the extension's "lib" folder on the Python search
path, which is why the button scripts can simply say:

    import bimpress_disciplines as bp

=============================================================================
IF YOU ONLY EDIT ONE THING, EDIT "DISCIPLINE_LIST" BELOW.
=============================================================================
"""

import os

# "DB" is pyRevit's shortcut for Autodesk.Revit.DB, the main Revit API
# namespace. Everything Revit-related (Material, Transaction, Color, ...)
# comes from there.
from pyrevit import DB

# .NET generic List - needed because some Revit API methods want a real
# .NET list rather than a Python list.
from System.Collections.Generic import List


# =============================================================================
# 1. SETTINGS - THE SINGLE SOURCE OF TRUTH
# =============================================================================

# The name of the project parameter you will type values into, inside Revit's
# Properties panel. Change it here and every script follows.
PARAM_NAME = "BIM Press Discipline"

# Every material this tool creates is named PREFIX + discipline name,
# e.g. "BIM Press - Electrical". The prefix makes them easy to find in
# Revit's Material Browser and easy to spot in Navisworks.
MATERIAL_PREFIX = "BIM Press - "

# ---------------------------------------------------------------------------
# THE DISCIPLINES AND THEIR COLORS.  <-- EDIT HERE, NOWHERE ELSE.
# ---------------------------------------------------------------------------
# Format: ("Discipline name", (Red, Green, Blue))
# RGB values are 0-255, the same numbers you see in Revit's color picker.
# This is a LIST (not a plain dictionary) so the on-screen summary always
# prints in this same order.
DISCIPLINE_LIST = [
    ("Architectural",   (180, 180, 180)),   # gray
    ("Structural",      ( 90, 110, 140)),   # steel blue
    ("Mechanical",      (230, 180,  40)),   # gold / yellow
    ("Plumbing",        (  0, 150, 130)),   # green / teal
    ("Electrical",      (255, 140,   0)),   # orange
    ("Fire Protection", (200,  30,  30)),   # red
]

# A convenience dictionary built from the list above, so code can do
# DISCIPLINES["Electrical"] and get (255, 140, 0).
DISCIPLINES = dict(DISCIPLINE_LIST)

# ---------------------------------------------------------------------------
# OPTIONAL: short-hand spellings you are allowed to type in Revit.
# ---------------------------------------------------------------------------
# These are purely typing shortcuts. They do NOT define new colors - each one
# just points at a discipline name from the list above. Delete this whole
# block if you want to force people to type the exact discipline names.
ALIASES = {
    "arch":   "Architectural",
    "a":      "Architectural",
    "struct": "Structural",
    "s":      "Structural",
    "mech":   "Mechanical",
    "m":      "Mechanical",
    "hvac":   "Mechanical",
    "plumb":  "Plumbing",
    "p":      "Plumbing",
    "elec":   "Electrical",
    "e":      "Electrical",
    "fire":   "Fire Protection",
    "fp":     "Fire Protection",
    "f":      "Fire Protection",
}

# ---------------------------------------------------------------------------
# WHICH REVIT CATEGORIES GET THE PARAMETER
# ---------------------------------------------------------------------------
# These are Revit's internal category names ("OST_" = Object STyle).
# They are listed as plain text on purpose: if a category does not exist in
# your Revit version, the script quietly skips it instead of crashing.
# Add or remove lines freely.
CATEGORY_NAMES = [
    # ---- Architectural --------------------------------------------------
    "OST_Walls",
    "OST_Floors",
    "OST_Roofs",
    "OST_Ceilings",
    "OST_Doors",
    "OST_Windows",
    "OST_Stairs",
    "OST_StairsRailing",
    "OST_Ramps",
    "OST_Columns",                 # architectural columns
    "OST_CurtainWallPanels",
    "OST_CurtainWallMullions",
    "OST_Casework",
    "OST_Furniture",
    "OST_FurnitureSystems",
    "OST_SpecialityEquipment",
    "OST_GenericModel",
    "OST_Parts",

    # ---- Structural -----------------------------------------------------
    "OST_StructuralFraming",
    "OST_StructuralColumns",
    "OST_StructuralFoundation",
    "OST_StructuralStiffener",
    "OST_StructuralTruss",
    "OST_StructConnections",
    "OST_Rebar",

    # ---- Mechanical -----------------------------------------------------
    "OST_DuctCurves",
    "OST_FlexDuctCurves",
    "OST_DuctFitting",
    "OST_DuctAccessory",
    "OST_DuctTerminal",
    "OST_DuctInsulations",
    "OST_MechanicalEquipment",

    # ---- Plumbing -------------------------------------------------------
    "OST_PipeCurves",
    "OST_FlexPipeCurves",
    "OST_PipeFitting",
    "OST_PipeAccessory",
    "OST_PipeInsulations",
    "OST_PlumbingFixtures",

    # ---- Electrical -----------------------------------------------------
    "OST_Conduit",
    "OST_ConduitFitting",
    "OST_CableTray",
    "OST_CableTrayFitting",
    "OST_ElectricalEquipment",
    "OST_ElectricalFixtures",
    "OST_LightingFixtures",
    "OST_LightingDevices",
    "OST_DataDevices",
    "OST_CommunicationDevices",
    "OST_SecurityDevices",
    "OST_TelephoneDevices",
    "OST_NurseCallDevices",

    # ---- Fire protection -------------------------------------------------
    "OST_Sprinklers",
    "OST_FireAlarmDevices",
    "OST_FireProtection",          # only exists in Revit 2022 and newer
]

# ---------------------------------------------------------------------------
# WHERE THE SHARED PARAMETER FILE LIVES
# ---------------------------------------------------------------------------
# Revit can only create a real project parameter from a "shared parameter",
# and shared parameters live in a plain text file. The script creates this
# file for you if it is missing.
#
# Keep this file! It stores the parameter's permanent ID (a GUID). If you
# delete it and re-run the script, Revit makes a NEW parameter with a new ID,
# and older models will not recognise it as the same parameter.
SHARED_PARAM_FILE = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "BIM Press",
    "BIM Press Shared Parameters.txt"
)

# The group heading the parameter sits under inside the shared parameter file.
SHARED_PARAM_GROUP = "BIM Press"

# Set to False if you only care about Revit's flat shaded color and want to
# skip editing the render appearance (see set_render_appearance_color below).
SET_RENDER_APPEARANCE = True


# =============================================================================
# 2. SMALL HELPERS - PLAIN PYTHON, NO REVIT INVOLVED
# =============================================================================

def material_name_for(discipline):
    """'Electrical' -> 'BIM Press - Electrical'."""
    return MATERIAL_PREFIX + discipline


def match_discipline(raw_value):
    """
    Take whatever text someone typed into the parameter and figure out which
    discipline it means. Returns the proper discipline name, or None.

    Matching ignores upper/lower case and surrounding spaces, so "ELECTRICAL",
    "electrical" and "  Electrical " all work. Aliases like "elec" work too.
    """
    if raw_value is None:
        return None

    cleaned = str(raw_value).strip().lower()
    if cleaned == "":
        return None

    # Exact (case-insensitive) match against the real discipline names.
    for name, _rgb in DISCIPLINE_LIST:
        if name.strip().lower() == cleaned:
            return name

    # Otherwise try the optional shorthand list.
    return ALIASES.get(cleaned)


def revit_color(rgb):
    """Turn a Python tuple (255, 140, 0) into a Revit DB.Color object."""
    return DB.Color(rgb[0], rgb[1], rgb[2])


# =============================================================================
# 3. CATEGORY HELPERS
# =============================================================================

def resolve_builtin_categories():
    """
    Turn the CATEGORY_NAMES text list into real Revit BuiltInCategory values.

    Any name that does not exist in this Revit version is silently skipped,
    so the script keeps working across Revit releases.

    Returns: (list_of_builtincategories, list_of_names_that_were_skipped)
    """
    found = []
    skipped = []
    for name in CATEGORY_NAMES:
        bic = getattr(DB.BuiltInCategory, name, None)
        if bic is None:
            skipped.append(name)
        else:
            found.append(bic)
    return found, skipped


def build_category_set(doc, builtin_categories):
    """
    Build the CategorySet that Revit needs in order to bind a parameter.

    Some categories cannot hold project parameters at all (Revit says so via
    AllowsBoundParameters); those are dropped here.
    """
    app = doc.Application
    cat_set = app.Create.NewCategorySet()
    used = []

    for bic in builtin_categories:
        try:
            cat = doc.Settings.Categories.get_Item(bic)
        except Exception:
            cat = None

        if cat is None:
            continue
        try:
            if not cat.AllowsBoundParameters:
                continue
        except Exception:
            continue

        cat_set.Insert(cat)
        used.append(cat.Name)

    return cat_set, used


def collect_candidate_elements(doc, builtin_categories):
    """
    Gather every placed (non-type) element that could carry the parameter.

    Fast path: ask Revit for only the categories we care about.
    Safety net: if that filter is rejected for any reason, fall back to
    walking every model element instead. Slower, but it always works.
    """
    try:
        net_list = List[DB.BuiltInCategory]()
        for bic in builtin_categories:
            net_list.Add(bic)

        cat_filter = DB.ElementMulticategoryFilter(net_list)
        collector = (DB.FilteredElementCollector(doc)
                     .WherePasses(cat_filter)
                     .WhereElementIsNotElementType())
        return list(collector)
    except Exception:
        collector = (DB.FilteredElementCollector(doc)
                     .WhereElementIsNotElementType()
                     .WhereElementIsViewIndependent())
        return list(collector)


# =============================================================================
# 4. PROJECT PARAMETER (STEP 1)
# =============================================================================

# The minimum valid contents of a Revit shared parameter file. The columns are
# separated by TAB characters ("\t") - Revit will refuse the file otherwise.
SHARED_PARAM_HEADER = (
    "# This is a Revit shared parameter file.\n"
    "# Do not edit manually.\n"
    "*META\tVERSION\tMINVERSION\n"
    "META\t2\t1\n"
    "*GROUP\tID\tNAME\n"
    "*PARAM\tGUID\tNAME\tDATATYPE\tDATACATEGORY\tGROUP\tVISIBLE\t"
    "DESCRIPTION\tUSERMODIFIABLE\n"
)


def _ensure_shared_param_file_exists():
    """Create the shared parameter text file (with its header) if missing."""
    folder = os.path.dirname(SHARED_PARAM_FILE)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    if (not os.path.isfile(SHARED_PARAM_FILE)
            or os.path.getsize(SHARED_PARAM_FILE) == 0):
        handle = open(SHARED_PARAM_FILE, "w")
        try:
            handle.write(SHARED_PARAM_HEADER)
        finally:
            handle.close()


def _get_or_create_shared_definition(doc):
    """
    Find (or create) the "BIM Press Discipline" shared parameter definition.

    This temporarily points Revit at our shared parameter file, then puts the
    user's original file back so we do not disturb their setup.
    """
    app = doc.Application
    previous_file = app.SharedParametersFilename

    _ensure_shared_param_file_exists()
    app.SharedParametersFilename = SHARED_PARAM_FILE

    try:
        def_file = app.OpenSharedParameterFile()
        if def_file is None:
            raise Exception(
                "Revit could not open the shared parameter file at:\n"
                + SHARED_PARAM_FILE)

        # Find our group, or make it.
        group = None
        for grp in def_file.Groups:
            if grp.Name == SHARED_PARAM_GROUP:
                group = grp
                break
        if group is None:
            group = def_file.Groups.Create(SHARED_PARAM_GROUP)

        # Find our parameter inside that group, or make it.
        definition = None
        for dfn in group.Definitions:
            if dfn.Name == PARAM_NAME:
                definition = dfn
                break

        if definition is None:
            # Revit 2022+ uses SpecTypeId; older versions use ParameterType.
            try:
                options = DB.ExternalDefinitionCreationOptions(
                    PARAM_NAME, DB.SpecTypeId.String.Text)
            except Exception:
                options = DB.ExternalDefinitionCreationOptions(
                    PARAM_NAME, DB.ParameterType.Text)

            options.Visible = True
            options.UserModifiable = True
            options.Description = (
                "BIM Press demo: type a discipline name here - "
                "Architectural, Structural, Mechanical, Plumbing, "
                "Electrical or Fire Protection.")
            definition = group.Definitions.Create(options)

        return definition

    finally:
        # Always restore whatever shared parameter file was set before.
        if previous_file:
            try:
                app.SharedParametersFilename = previous_file
            except Exception:
                pass


def _insert_or_reinsert(doc, definition, binding, replace_existing):
    """
    Attach the parameter to the categories.

    Revit 2022+ wants a ForgeTypeId (GroupTypeId.Data) to say which Properties
    group the parameter shows up under. Older versions want the
    BuiltInParameterGroup enum. Try the new way, fall back to the old way.
    """
    bindings = doc.ParameterBindings
    try:
        group_id = DB.GroupTypeId.Data
        if replace_existing:
            return bindings.ReInsert(definition, binding, group_id)
        return bindings.Insert(definition, binding, group_id)
    except Exception:
        group_id = DB.BuiltInParameterGroup.PG_DATA
        if replace_existing:
            return bindings.ReInsert(definition, binding, group_id)
        return bindings.Insert(definition, binding, group_id)


def ensure_project_parameter(doc):
    """
    STEP 1: make sure "BIM Press Discipline" exists and is attached to all
    of our categories.

    Safe to run over and over:
      * Not there yet -> creates it.
      * Already there -> re-attaches it to the full category list, which
        quietly picks up any categories you have since added to
        CATEGORY_NAMES.

    MUST be called inside an open Transaction.

    Returns a dictionary describing what happened.
    """
    builtin_cats, skipped_names = resolve_builtin_categories()
    cat_set, bound_names = build_category_set(doc, builtin_cats)

    # Look through the parameters already bound in this project.
    existing_definition = None
    iterator = doc.ParameterBindings.ForwardIterator()
    iterator.Reset()
    while iterator.MoveNext():
        if iterator.Key.Name == PARAM_NAME:
            existing_definition = iterator.Key
            break

    # "Instance" binding = each placed element gets its own value, as opposed
    # to a type parameter shared by every instance of a type.
    binding = doc.Application.Create.NewInstanceBinding(cat_set)

    if existing_definition is not None:
        _insert_or_reinsert(doc, existing_definition, binding, True)
        action = "updated"
    else:
        definition = _get_or_create_shared_definition(doc)
        _insert_or_reinsert(doc, definition, binding, False)
        action = "created"

    return {
        "action": action,
        "bound_category_names": bound_names,
        "skipped_category_names": skipped_names,
    }


# =============================================================================
# 5. MATERIALS (STEP 2)
# =============================================================================

def find_material(doc, name):
    """Return the Material with this name, or None. Ignores upper/lower case."""
    wanted = name.strip().lower()
    for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        if mat.Name.strip().lower() == wanted:
            return mat
    return None


def _attach_appearance_asset(doc, material, unique_suffix):
    """
    Give the material its own private "appearance asset" (the render material).

    Why: several materials sharing one appearance asset means changing one
    changes them all. Duplicating gives each discipline its own.

    Returns the new asset element's Id, or InvalidElementId if we could not
    make one. Never raises.

    MUST be called inside an open Transaction.
    """
    try:
        new_name = "BIM Press Appearance - " + unique_suffix

        # If we already made this one on a previous run, reuse it.
        for asset_elem in (DB.FilteredElementCollector(doc)
                           .OfClass(DB.AppearanceAssetElement)):
            if asset_elem.Name == new_name:
                material.AppearanceAssetId = asset_elem.Id
                return asset_elem.Id

        # Find any appearance asset in the project that is a "generic" one,
        # i.e. one that exposes a plain diffuse colour we can overwrite.
        source = None
        for asset_elem in (DB.FilteredElementCollector(doc)
                           .OfClass(DB.AppearanceAssetElement)):
            try:
                asset = asset_elem.GetRenderingAsset()
                if asset is not None and \
                        asset.FindByName("generic_diffuse") is not None:
                    source = asset_elem
                    break
            except Exception:
                continue

        if source is None:
            return DB.ElementId.InvalidElementId

        duplicate = source.Duplicate(new_name)
        material.AppearanceAssetId = duplicate.Id
        return duplicate.Id

    except Exception:
        return DB.ElementId.InvalidElementId


def ensure_materials(doc):
    """
    STEP 2: create the six discipline materials, or update them if they exist.

    Sets the SHADING colour - the flat colour Revit draws in Shaded views, and
    the colour the Navisworks NWC exporter reads.

    Safe to run repeatedly - it looks each material up by name first.

    MUST be called inside an open Transaction.

    Returns (results, appearance_jobs) where:
      results          = one dict per discipline, for the summary
      appearance_jobs  = work that has to happen AFTER the transaction closes
                         (see set_render_appearance_color for why)
    """
    results = []
    appearance_jobs = []

    for discipline, rgb in DISCIPLINE_LIST:
        name = material_name_for(discipline)
        color = revit_color(rgb)

        material = find_material(doc, name)
        if material is None:
            material = doc.GetElement(DB.Material.Create(doc, name))
            created = True
        else:
            created = False

        # The flat shaded colour. This is the important one for NWC export.
        material.Color = color

        # Tell Revit to use that flat colour rather than deriving shading from
        # the render appearance - this is what keeps the colour exact.
        try:
            material.UseRenderAppearanceForShading = False
        except Exception:
            pass

        # Fully opaque, so nothing shows through in Navisworks.
        try:
            material.Transparency = 0
        except Exception:
            pass

        # Match the surface/cut pattern colours so plans and sections read the
        # same way as 3D views do.
        for prop in ("SurfaceForegroundPatternColor",
                     "CutForegroundPatternColor"):
            try:
                setattr(material, prop, color)
            except Exception:
                pass

        asset_id = DB.ElementId.InvalidElementId
        if SET_RENDER_APPEARANCE:
            asset_id = _attach_appearance_asset(doc, material, discipline)
            if asset_id != DB.ElementId.InvalidElementId:
                appearance_jobs.append((discipline, asset_id, rgb))

        results.append({
            "discipline": discipline,
            "material_name": name,
            "rgb": rgb,
            "created": created,
        })

    return results, appearance_jobs


def set_render_appearance_color(doc, asset_element_id, rgb):
    """
    Set the RENDER appearance colour to match the shading colour.

    IMPORTANT: this must run with NO transaction open. Revit's
    AppearanceAssetEditScope opens and commits its own transaction, and it
    throws if one is already running. That is why the button scripts do the
    materials inside a transaction, then call this afterwards.

    Returns True on success. Never raises - the render appearance is a
    nice-to-have; the shading colour is what actually drives the NWC export.
    """
    try:
        from Autodesk.Revit.DB.Visual import AppearanceAssetEditScope

        scope = AppearanceAssetEditScope(doc)
        editable_asset = scope.Start(asset_element_id)

        prop = editable_asset.FindByName("generic_diffuse")
        changed = False
        if prop is not None:
            prop.SetValueAsColor(revit_color(rgb))
            changed = True

        # Commit either way - an edit scope must always be closed, and
        # committing an asset we did not change is harmless.
        scope.Commit(True)
        return changed
    except Exception:
        return False


# =============================================================================
# 6. PAINTING (STEP 3)
# =============================================================================

def geometry_options():
    """Standard settings for asking an element for its 3D geometry."""
    opts = DB.Options()
    # Paint needs faces that Revit can trace back to the element. Computing
    # references is what makes that possible.
    opts.ComputeReferences = True
    opts.IncludeNonVisibleObjects = False
    opts.DetailLevel = DB.ViewDetailLevel.Fine
    return opts


def _gather_faces(geometry, collected):
    """
    Walk an element's geometry and collect every face.

    Family instances (doors, sprinklers, light fixtures...) wrap their geometry
    in a GeometryInstance. We look inside those too:

      * GetSymbolGeometry() - geometry in the family's own coordinates. Its
        faces keep their references, which is what Document.Paint needs, so
        this is tried first.
      * GetInstanceGeometry() - geometry moved into place in the project.
        Kept as a backup for cases where symbol geometry comes back empty.
    """
    for geom_obj in geometry:
        if isinstance(geom_obj, DB.Solid):
            try:
                if geom_obj.Faces.Size > 0:
                    for face in geom_obj.Faces:
                        collected.append(face)
            except Exception:
                pass

        elif isinstance(geom_obj, DB.GeometryInstance):
            for getter in ("GetSymbolGeometry", "GetInstanceGeometry"):
                try:
                    inner = getattr(geom_obj, getter)()
                    if inner is not None:
                        _gather_faces(inner, collected)
                except Exception:
                    pass


def get_paintable_faces(element, opts=None):
    """Return a plain Python list of every face on this element."""
    if opts is None:
        opts = geometry_options()

    faces = []
    try:
        geometry = element.get_Geometry(opts)
    except Exception:
        return faces

    if geometry is None:
        return faces

    _gather_faces(geometry, faces)
    return faces


def paint_element(doc, element, material_id, opts=None):
    """
    Paint every face of one element with the given material.

    This is the step that actually bakes the colour into the geometry, which
    is why it survives export to NWC and DWG - unlike a view filter or a
    graphic override, which only affects the view you set it in.

    MUST be called inside an open Transaction.

    Returns the number of faces successfully painted. Zero means this element
    could not be painted - Revit refuses on some element types.
    """
    painted = 0
    for face in get_paintable_faces(element, opts):
        try:
            doc.Paint(element.Id, face, material_id)
            painted += 1
        except Exception:
            # Faces Revit will not paint - and duplicate faces picked up from
            # both symbol and instance geometry - land here. Skipping them is
            # normal and harmless.
            pass
    return painted


def strip_paint(doc, element, opts=None, only_material_ids=None):
    """
    Remove paint from the faces of one element.

    Used by the "Remove Paint" button so you can re-run the demo from a clean
    model. MUST be called inside an open Transaction.

    only_material_ids:
        A set of plain id NUMBERS (use element_id_value on a material's Id to
        get one). Only paint using those materials is removed. That is how the
        Remove Paint button avoids wiping out paint somebody applied by hand
        for a different reason.
        Pass None to remove all paint from the element.

    Returns the number of faces that had paint removed.
    """
    removed = 0
    for face in get_paintable_faces(element, opts):
        try:
            if not doc.IsPainted(element.Id, face):
                continue

            if only_material_ids is not None:
                # Compare the plain numbers rather than the ElementId objects
                # themselves - number comparison behaves the same way in every
                # Python engine pyRevit might be running.
                painted_with = doc.GetPaintedMaterial(element.Id, face)
                if element_id_value(painted_with) not in only_material_ids:
                    continue

            doc.RemovePaint(element.Id, face)
            removed += 1
        except Exception:
            pass
    return removed


def read_discipline_value(element):
    """
    Read the element's "BIM Press Discipline" text.

    Returns the raw text, or None if the parameter is missing or blank.
    """
    try:
        param = element.LookupParameter(PARAM_NAME)
    except Exception:
        return None

    if param is None:
        return None

    try:
        if not param.HasValue:
            return None
        value = param.AsString()
    except Exception:
        return None

    if value is None or value.strip() == "":
        return None
    return value


def element_id_value(element_id):
    """
    Get the plain number out of an ElementId.

    Revit 2024 renamed IntegerValue to Value, so try the new one first.
    """
    try:
        return element_id.Value
    except Exception:
        return element_id.IntegerValue


def category_name(element):
    """Safe way to ask an element for its category name."""
    try:
        if element.Category is not None:
            return element.Category.Name
    except Exception:
        pass
    return "(no category)"
