/* =========================================================================
 * BIM PRESS - DISCIPLINE COLORS
 * Revit Macro version (no pyRevit install needed)
 * =========================================================================
 *
 * WHAT THIS IS
 * ------------
 * The same tool as the pyRevit buttons, rewritten as a Revit Macro so it
 * runs with nothing installed beyond Revit itself.
 *
 * It is written in C# rather than Python because C# is the one language
 * Revit's Macro Manager is guaranteed to offer in every version. You do not
 * need to understand C# to use this - just paste and press Run.
 *
 * HOW TO INSTALL IT  (about two minutes)
 * --------------------------------------
 *  1. Open your Revit project.
 *  2. Ribbon: Manage tab > Macros panel > Macro Manager.
 *  3. Pick the tab named after your project (NOT the "Application" tab).
 *  4. Click "Module".
 *        Name:     BIMPressDisciplineColors
 *        Language: C#
 *     Click OK. Revit opens its built-in code editor (SharpDevelop).
 *  5. In the editor you will see a class called "ThisDocument" containing
 *     Module_Startup and Module_Shutdown. Leave those alone.
 *  6. Copy EVERYTHING in this file from the line marked
 *        "----- PASTE FROM HERE -----"
 *     down to
 *        "----- PASTE TO HERE -----"
 *     and paste it INSIDE the ThisDocument class, just below
 *     Module_Shutdown.
 *  7. Scroll to the very top of the editor file and make sure these lines
 *     are in the "using" list. Add any that are missing:
 *
 *        using System;
 *        using System.Collections.Generic;
 *        using System.IO;
 *        using System.Linq;
 *        using System.Text;
 *        using Autodesk.Revit.DB;
 *        using Autodesk.Revit.DB.Visual;
 *        using Autodesk.Revit.UI;
 *
 *  8. Press the Build button (or F8). It should say "Build succeeded".
 *  9. Close the editor and go back to Revit.
 *
 * HOW TO RUN IT
 * -------------
 * Manage tab > Macro Manager > your project tab > expand
 * BIMPressDisciplineColors. You will see three macros:
 *
 *     BIMPress_Setup          run this FIRST, once per project
 *     BIMPress_ApplyColors    run this after tagging elements
 *     BIMPress_RemovePaint    run this to undo the painting
 *
 * Select one and click Run.
 *
 * TAGGING ELEMENTS (between Setup and ApplyColors)
 * ------------------------------------------------
 * Select elements in Revit, open the Properties panel, scroll to the Data
 * group, find "BIM Press Discipline", and type one of:
 *
 *     Architectural, Structural, Mechanical, Plumbing,
 *     Electrical, Fire Protection
 *
 * Capitals do not matter. Short forms like "elec" or "mech" also work.
 *
 * A NOTE ON KEEPING THE TWO VERSIONS IN STEP
 * ------------------------------------------
 * This macro is standalone - it cannot read the pyRevit library file. The
 * colours and category list below are the single source of truth FOR THIS
 * FILE. If you change a colour here, change it in
 *     BIMPress.extension/lib/bimpress_disciplines.py
 * as well, so the two tools do not drift apart. Pick one tool and stick
 * with it if you would rather not think about that.
 *
 * REVIT VERSION NOTES
 * -------------------
 * Written against the Revit 2027 API. Two lines need changing on older
 * Revit versions; both are flagged with "OLDER REVIT:" in the comments.
 * ========================================================================= */


// ----- PASTE FROM HERE -----

    // =====================================================================
    // 1. SETTINGS - THE SINGLE SOURCE OF TRUTH FOR THIS FILE
    // =====================================================================

    // The project parameter you will type discipline names into.
    const string BP_PARAM_NAME = "BIM Press Discipline";

    // Every material is named PREFIX + discipline, e.g.
    // "BIM Press - Electrical".
    const string BP_MATERIAL_PREFIX = "BIM Press - ";

    // ---------------------------------------------------------------------
    // THE DISCIPLINES AND THEIR COLOURS.  <-- EDIT HERE, NOWHERE ELSE.
    // ---------------------------------------------------------------------
    // Kept as an ordered list so the on-screen summary always prints in
    // this order. The numbers are Red, Green, Blue from 0 to 255 - the same
    // numbers Revit's colour picker shows.
    static readonly List<KeyValuePair<string, byte[]>> BP_DISCIPLINES =
        new List<KeyValuePair<string, byte[]>>()
    {
        new KeyValuePair<string, byte[]>("Architectural",   new byte[] { 180, 180, 180 }),  // gray
        new KeyValuePair<string, byte[]>("Structural",      new byte[] {  90, 110, 140 }),  // steel blue
        new KeyValuePair<string, byte[]>("Mechanical",      new byte[] { 230, 180,  40 }),  // gold / yellow
        new KeyValuePair<string, byte[]>("Plumbing",        new byte[] {   0, 150, 130 }),  // green / teal
        new KeyValuePair<string, byte[]>("Electrical",      new byte[] { 255, 140,   0 }),  // orange
        new KeyValuePair<string, byte[]>("Fire Protection", new byte[] { 200,  30,  30 }),  // red
    };

    // Optional typing shortcuts. These define no colours of their own - each
    // one just points at a discipline name from the list above. Delete this
    // block if you want to force people to type the exact names.
    // StringComparer.OrdinalIgnoreCase is what makes the lookup ignore
    // upper/lower case.
    static readonly Dictionary<string, string> BP_ALIASES =
        new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
    {
        { "arch",   "Architectural" },
        { "a",      "Architectural" },
        { "struct", "Structural"    },
        { "s",      "Structural"    },
        { "mech",   "Mechanical"    },
        { "m",      "Mechanical"    },
        { "hvac",   "Mechanical"    },
        { "plumb",  "Plumbing"      },
        { "p",      "Plumbing"      },
        { "elec",   "Electrical"    },
        { "e",      "Electrical"    },
        { "fire",   "Fire Protection" },
        { "fp",     "Fire Protection" },
        { "f",      "Fire Protection" },
    };

    // ---------------------------------------------------------------------
    // WHICH REVIT CATEGORIES GET THE PARAMETER
    // ---------------------------------------------------------------------
    // Revit's internal category names ("OST_" = Object STyle). Listed as
    // plain text on purpose: any name that does not exist in your Revit
    // version is skipped quietly instead of breaking the macro.
    static readonly string[] BP_CATEGORY_NAMES = new string[]
    {
        // ---- Architectural ----
        "OST_Walls", "OST_Floors", "OST_Roofs", "OST_Ceilings",
        "OST_Doors", "OST_Windows", "OST_Stairs", "OST_StairsRailing",
        "OST_Ramps", "OST_Columns", "OST_CurtainWallPanels",
        "OST_CurtainWallMullions", "OST_Casework", "OST_Furniture",
        "OST_FurnitureSystems", "OST_SpecialityEquipment",
        "OST_GenericModel", "OST_Parts",

        // ---- Structural ----
        "OST_StructuralFraming", "OST_StructuralColumns",
        "OST_StructuralFoundation", "OST_StructuralStiffener",
        "OST_StructuralTruss", "OST_StructConnections", "OST_Rebar",

        // ---- Mechanical ----
        "OST_DuctCurves", "OST_FlexDuctCurves", "OST_DuctFitting",
        "OST_DuctAccessory", "OST_DuctTerminal", "OST_DuctInsulations",
        "OST_MechanicalEquipment",

        // ---- Plumbing ----
        "OST_PipeCurves", "OST_FlexPipeCurves", "OST_PipeFitting",
        "OST_PipeAccessory", "OST_PipeInsulations", "OST_PlumbingFixtures",

        // ---- Electrical ----
        "OST_Conduit", "OST_ConduitFitting", "OST_CableTray",
        "OST_CableTrayFitting", "OST_ElectricalEquipment",
        "OST_ElectricalFixtures", "OST_LightingFixtures",
        "OST_LightingDevices", "OST_DataDevices",
        "OST_CommunicationDevices", "OST_SecurityDevices",
        "OST_TelephoneDevices", "OST_NurseCallDevices",

        // ---- Fire protection ----
        "OST_Sprinklers", "OST_FireAlarmDevices",
        "OST_FireProtection",   // only exists in Revit 2022 and newer
    };

    // Where the shared parameter file lives. Revit can only build a real
    // project parameter out of a "shared parameter", and shared parameters
    // live in a plain text file. The macro creates it if it is missing.
    //
    // KEEP THIS FILE. It stores the parameter's permanent ID. Delete it and
    // re-run, and Revit makes a brand new parameter that older models will
    // not recognise as the same one.
    static string BP_SharedParamFile()
    {
        return Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "BIM Press",
            "BIM Press Shared Parameters.txt");
    }

    const string BP_SHARED_PARAM_GROUP = "BIM Press";

    // Set to false to skip the render-appearance colour and only set the
    // flat shaded colour (which is the one the NWC export reads anyway).
    const bool BP_SET_RENDER_APPEARANCE = true;


    // =====================================================================
    // 2. MACRO 1 OF 3 - SETUP
    // =====================================================================
    //
    // Creates the project parameter and the six materials.
    // Safe to run as many times as you like: it checks for each one first
    // and updates rather than duplicating.
    //
    public void BIMPress_Setup()
    {
        Document doc = this.Document;

        if (doc.IsFamilyDocument)
        {
            TaskDialog.Show("BIM Press - Setup",
                "This macro runs on a Revit PROJECT (.rvt). "
                + "You currently have a family open.");
            return;
        }

        var report = new StringBuilder();
        string paramAction = "unchanged";
        int boundCategories = 0;
        var skippedCategories = new List<string>();
        var createdMaterials = new List<string>();
        var updatedMaterials = new List<string>();

        // Render-appearance work that must wait until after the transaction
        // below is committed - see the comment further down.
        var appearanceJobs = new List<KeyValuePair<ElementId, byte[]>>();

        // -----------------------------------------------------------------
        // A Transaction is Revit's undo bundle. Every change to the model
        // has to happen inside one, and the name is what shows up in the
        // undo list.
        // -----------------------------------------------------------------
        using (var trans = new Autodesk.Revit.DB.Transaction(
            doc, "BIM Press - Setup Discipline Parameter and Materials"))
        {
            trans.Start();
            try
            {
                // ---- STEP 1: the project parameter ----------------------
                paramAction = BP_EnsureProjectParameter(
                    doc, out boundCategories, skippedCategories);

                // ---- STEP 2: the six materials --------------------------
                foreach (var entry in BP_DISCIPLINES)
                {
                    string matName = BP_MATERIAL_PREFIX + entry.Key;
                    byte[] rgb = entry.Value;

                    Material material = BP_FindMaterial(doc, matName);
                    bool created = false;

                    if (material == null)
                    {
                        ElementId newId = Material.Create(doc, matName);
                        material = doc.GetElement(newId) as Material;
                        created = true;
                    }

                    var color = new Color(rgb[0], rgb[1], rgb[2]);

                    // The flat shaded colour. THIS is the one the Navisworks
                    // NWC exporter reads, so it matters most.
                    material.Color = color;

                    // Use that flat colour directly rather than deriving the
                    // shading from the render appearance - keeps it exact.
                    try { material.UseRenderAppearanceForShading = false; }
                    catch { }

                    // Fully opaque so nothing shows through in Navisworks.
                    try { material.Transparency = 0; } catch { }

                    // Keep plans and sections reading the same as 3D views.
                    try { material.SurfaceForegroundPatternColor = color; }
                    catch { }
                    try { material.CutForegroundPatternColor = color; }
                    catch { }

                    if (created) createdMaterials.Add(matName);
                    else updatedMaterials.Add(matName);

                    if (BP_SET_RENDER_APPEARANCE)
                    {
                        ElementId assetId =
                            BP_AttachAppearanceAsset(doc, material, entry.Key);
                        if (assetId != ElementId.InvalidElementId)
                        {
                            appearanceJobs.Add(
                                new KeyValuePair<ElementId, byte[]>(assetId, rgb));
                        }
                    }
                }

                trans.Commit();
            }
            catch (Exception ex)
            {
                // Undo everything, so the model is never left half-finished.
                trans.RollBack();
                TaskDialog.Show("BIM Press - Setup",
                    "Setup failed and nothing was changed in the model.\n\n"
                    + ex.Message);
                return;
            }
        }

        // -----------------------------------------------------------------
        // Render appearance colours.
        //
        // This has to run AFTER the transaction above is committed. Revit's
        // appearance-asset editor starts its own transaction internally and
        // refuses to run while another one is open.
        //
        // This is optional polish for Realistic / rendered views. If it
        // fails, the shaded colour set above is still what drives the NWC
        // export, so the tool still does its job.
        // -----------------------------------------------------------------
        int appearanceOk = 0;
        foreach (var job in appearanceJobs)
        {
            if (BP_SetRenderAppearanceColor(doc, job.Key, job.Value))
                appearanceOk++;
        }

        // ---- Summary -----------------------------------------------------
        report.AppendLine("STEP 1 - PROJECT PARAMETER");
        report.AppendLine("  '" + BP_PARAM_NAME + "' was " + paramAction + ".");
        report.AppendLine("  Attached to " + boundCategories + " categories.");
        if (skippedCategories.Count > 0)
        {
            report.AppendLine("  Skipped " + skippedCategories.Count
                + " category name(s) not present in this Revit version:");
            report.AppendLine("    " + string.Join(", ", skippedCategories.ToArray()));
        }
        report.AppendLine("  Shared parameter file:");
        report.AppendLine("    " + BP_SharedParamFile());
        report.AppendLine();

        report.AppendLine("STEP 2 - MATERIALS");
        foreach (var entry in BP_DISCIPLINES)
        {
            string matName = BP_MATERIAL_PREFIX + entry.Key;
            byte[] rgb = entry.Value;
            string state = createdMaterials.Contains(matName)
                ? "created"
                : "already existed (colour reset)";
            report.AppendLine("  " + matName + "  RGB ("
                + rgb[0] + ", " + rgb[1] + ", " + rgb[2] + ")  - " + state);
        }
        report.AppendLine("  " + createdMaterials.Count + " created, "
            + updatedMaterials.Count + " updated.");
        if (BP_SET_RENDER_APPEARANCE)
        {
            report.AppendLine("  Render appearance colour set on "
                + appearanceOk + " of " + BP_DISCIPLINES.Count + " materials.");
        }
        report.AppendLine();

        report.AppendLine("NEXT STEP");
        report.AppendLine("  Select elements, open the Properties panel, find");
        report.AppendLine("  '" + BP_PARAM_NAME + "' under Data, and type one of:");
        report.AppendLine("    " + BP_DisciplineNamesJoined());
        report.AppendLine("  Then run the BIMPress_ApplyColors macro.");

        BP_ShowReport("BIM Press - Setup complete", report.ToString());
    }


    // =====================================================================
    // 3. MACRO 2 OF 3 - APPLY COLORS
    // =====================================================================
    //
    // Reads every element's "BIM Press Discipline" value and paints its
    // faces with the matching material.
    //
    // Painting is the whole point: a view filter or graphic override only
    // changes one view and is discarded on export, whereas Document.Paint
    // writes the material onto the geometry so it travels into NWC and DWG.
    //
    public void BIMPress_ApplyColors()
    {
        Document doc = this.Document;

        if (doc.IsFamilyDocument)
        {
            TaskDialog.Show("BIM Press - Apply Colors",
                "This macro runs on a Revit PROJECT (.rvt). "
                + "You currently have a family open.");
            return;
        }

        // ---- Find the six materials first --------------------------------
        var materialIds = new Dictionary<string, ElementId>();
        var missing = new List<string>();

        foreach (var entry in BP_DISCIPLINES)
        {
            string matName = BP_MATERIAL_PREFIX + entry.Key;
            Material material = BP_FindMaterial(doc, matName);
            if (material == null) missing.Add(matName);
            else materialIds[entry.Key] = material.Id;
        }

        if (missing.Count > 0)
        {
            TaskDialog.Show("BIM Press - Apply Colors",
                "These materials do not exist yet:\n\n"
                + string.Join("\n", missing.ToArray())
                + "\n\nRun the BIMPress_Setup macro first.");
            return;
        }

        // ---- Gather the elements to check --------------------------------
        List<Element> elements = BP_CollectCandidateElements(doc);

        // ---- Counters for the summary ------------------------------------
        var paintedElements = new Dictionary<string, int>();
        var paintedFaces = new Dictionary<string, int>();
        foreach (var entry in BP_DISCIPLINES)
        {
            paintedElements[entry.Key] = 0;
            paintedFaces[entry.Key] = 0;
        }

        int skippedNoValue = 0;
        var unrecognised = new Dictionary<string, int>();
        var couldNotPaint = new List<string>();
        const int MaxExamples = 15;

        Options geomOptions = BP_GeometryOptions();

        using (var trans = new Autodesk.Revit.DB.Transaction(
            doc, "BIM Press - Apply Discipline Colors"))
        {
            trans.Start();
            try
            {
                foreach (Element element in elements)
                {
                    // ---- Read the parameter ---------------------------
                    string raw = BP_ReadDisciplineValue(element);
                    if (raw == null)
                    {
                        skippedNoValue++;
                        continue;
                    }

                    // ---- Match it (ignoring capitals) -----------------
                    string discipline = BP_MatchDiscipline(raw);
                    if (discipline == null)
                    {
                        string key = raw.Trim();
                        if (unrecognised.ContainsKey(key)) unrecognised[key]++;
                        else unrecognised[key] = 1;
                        continue;
                    }

                    // ---- Paint it --------------------------------------
                    int faceCount = BP_PaintElement(
                        doc, element, materialIds[discipline], geomOptions);

                    if (faceCount > 0)
                    {
                        paintedElements[discipline]++;
                        paintedFaces[discipline] += faceCount;
                    }
                    else if (couldNotPaint.Count < MaxExamples)
                    {
                        // Revit refused every face on this element. Record it
                        // rather than silently doing nothing.
                        couldNotPaint.Add("id " + BP_IdNumber(element.Id)
                            + " - " + BP_CategoryName(element)
                            + " - tagged " + discipline);
                    }
                }

                trans.Commit();
            }
            catch (Exception ex)
            {
                trans.RollBack();
                TaskDialog.Show("BIM Press - Apply Colors",
                    "Something went wrong and NO changes were saved.\n\n"
                    + ex.Message);
                return;
            }
        }

        // ---- Summary -----------------------------------------------------
        int totalPainted = 0, totalFaces = 0, totalUnrecognised = 0;
        foreach (var kv in paintedElements) totalPainted += kv.Value;
        foreach (var kv in paintedFaces) totalFaces += kv.Value;
        foreach (var kv in unrecognised) totalUnrecognised += kv.Value;

        var report = new StringBuilder();
        report.AppendLine("Checked " + elements.Count + " elements.");
        report.AppendLine();
        report.AppendLine("PAINTED");

        if (totalPainted == 0)
        {
            report.AppendLine("  Nothing was painted - no element had a");
            report.AppendLine("  recognised value in '" + BP_PARAM_NAME + "'.");
        }
        else
        {
            foreach (var entry in BP_DISCIPLINES)
            {
                int count = paintedElements[entry.Key];
                if (count == 0) continue;
                byte[] rgb = entry.Value;
                report.AppendLine("  " + entry.Key + ": " + count
                    + " element(s), " + paintedFaces[entry.Key] + " face(s)"
                    + "  RGB (" + rgb[0] + ", " + rgb[1] + ", " + rgb[2] + ")");
            }
            report.AppendLine("  TOTAL: " + totalPainted + " elements, "
                + totalFaces + " faces.");
        }

        report.AppendLine();
        report.AppendLine("SKIPPED");
        report.AppendLine("  " + skippedNoValue
            + " element(s) had no value - left untouched.");

        if (unrecognised.Count > 0)
        {
            report.AppendLine("  " + totalUnrecognised
                + " element(s) had a value that matches no discipline:");
            var badValues = new List<string>(unrecognised.Keys);
            badValues.Sort();
            foreach (string text in badValues)
            {
                report.AppendLine("    \"" + text + "\" - on "
                    + unrecognised[text] + " element(s)");
            }
            report.AppendLine("  Valid values: " + BP_DisciplineNamesJoined());
        }
        else
        {
            report.AppendLine("  No unrecognised values.");
        }

        if (couldNotPaint.Count > 0)
        {
            report.AppendLine();
            report.AppendLine("REVIT WOULD NOT PAINT THESE (up to "
                + MaxExamples + " shown)");
            foreach (string line in couldNotPaint)
                report.AppendLine("  " + line);
            report.AppendLine("  Some element types have no paintable faces.");
        }

        report.AppendLine();
        report.AppendLine("NEXT STEP");
        report.AppendLine("  File > Export > NWC, then open it in Navisworks.");
        report.AppendLine("  The painted elements carry their colour with them.");

        BP_ShowReport("BIM Press - Apply Colors: "
            + totalPainted + " element(s) painted", report.ToString());
    }


    // =====================================================================
    // 4. MACRO 3 OF 3 - REMOVE PAINT
    // =====================================================================
    //
    // Strips the paint back off, so you can re-shoot the demo from a clean
    // model. Only touches paint that uses a "BIM Press - ..." material, so
    // paint applied by hand for other reasons is left alone.
    //
    // The parameter, the materials and your typed values all survive, so you
    // can run BIMPress_ApplyColors again straight afterwards.
    //
    public void BIMPress_RemovePaint()
    {
        Document doc = this.Document;

        if (doc.IsFamilyDocument)
        {
            TaskDialog.Show("BIM Press - Remove Paint",
                "This macro runs on a Revit PROJECT (.rvt).");
            return;
        }

        // Work out which materials count as "ours".
        var ourMaterialIds = new HashSet<long>();
        var ourMaterialNames = new List<string>();

        foreach (var entry in BP_DISCIPLINES)
        {
            string matName = BP_MATERIAL_PREFIX + entry.Key;
            Material material = BP_FindMaterial(doc, matName);
            if (material != null)
            {
                ourMaterialIds.Add(BP_IdNumber(material.Id));
                ourMaterialNames.Add(matName);
            }
        }

        if (ourMaterialIds.Count == 0)
        {
            TaskDialog.Show("BIM Press - Remove Paint",
                "No 'BIM Press - ...' materials exist in this project, "
                + "so there is nothing to remove.");
            return;
        }

        // Ask first - stripping paint across a whole model is worth a check.
        var confirm = new TaskDialog("BIM Press - Remove Paint");
        confirm.MainInstruction = "Remove all paint using the BIM Press materials?";
        confirm.MainContent = string.Join("\n", ourMaterialNames.ToArray())
            + "\n\nYour discipline parameter values are kept, so you can run "
            + "BIMPress_ApplyColors again afterwards.";
        confirm.CommonButtons = TaskDialogCommonButtons.Yes | TaskDialogCommonButtons.No;
        confirm.DefaultButton = TaskDialogResult.No;

        if (confirm.Show() != TaskDialogResult.Yes) return;

        List<Element> elements = BP_CollectCandidateElements(doc);
        Options geomOptions = BP_GeometryOptions();

        int elementsCleaned = 0;
        int facesCleaned = 0;

        using (var trans = new Autodesk.Revit.DB.Transaction(
            doc, "BIM Press - Remove Discipline Paint"))
        {
            trans.Start();
            try
            {
                foreach (Element element in elements)
                {
                    int removed = 0;
                    foreach (Face face in BP_GetPaintableFaces(element, geomOptions))
                    {
                        try
                        {
                            if (!doc.IsPainted(element.Id, face)) continue;

                            ElementId paintedWith =
                                doc.GetPaintedMaterial(element.Id, face);
                            if (!ourMaterialIds.Contains(BP_IdNumber(paintedWith)))
                                continue;

                            doc.RemovePaint(element.Id, face);
                            removed++;
                        }
                        catch { }
                    }

                    if (removed > 0)
                    {
                        elementsCleaned++;
                        facesCleaned += removed;
                    }
                }

                trans.Commit();
            }
            catch (Exception ex)
            {
                trans.RollBack();
                TaskDialog.Show("BIM Press - Remove Paint",
                    "Something went wrong and NO changes were saved.\n\n"
                    + ex.Message);
                return;
            }
        }

        TaskDialog.Show("BIM Press - Remove Paint",
            "Done.\n\nChecked " + elements.Count + " elements.\n"
            + "Paint removed from " + elementsCleaned + " element(s) / "
            + facesCleaned + " face(s).");
    }


    // =====================================================================
    // 5. HELPERS - the shared plumbing the three macros above call.
    //    You should not need to change anything below this line.
    // =====================================================================

    // ---- Discipline matching --------------------------------------------

    // Turn whatever somebody typed into a proper discipline name, or null.
    // Ignores capitals and surrounding spaces.
    static string BP_MatchDiscipline(string raw)
    {
        if (string.IsNullOrEmpty(raw)) return null;
        string cleaned = raw.Trim();
        if (cleaned.Length == 0) return null;

        foreach (var entry in BP_DISCIPLINES)
        {
            if (string.Equals(entry.Key, cleaned,
                    StringComparison.OrdinalIgnoreCase))
                return entry.Key;
        }

        string alias;
        if (BP_ALIASES.TryGetValue(cleaned, out alias)) return alias;

        return null;
    }

    static string BP_DisciplineNamesJoined()
    {
        var names = new List<string>();
        foreach (var entry in BP_DISCIPLINES) names.Add(entry.Key);
        return string.Join(", ", names.ToArray());
    }

    // ---- Categories -------------------------------------------------------

    // Turn the BP_CATEGORY_NAMES text list into real BuiltInCategory values,
    // skipping any name this Revit version does not know about.
    static List<BuiltInCategory> BP_ResolveCategories(List<string> skippedOut)
    {
        var found = new List<BuiltInCategory>();

        foreach (string name in BP_CATEGORY_NAMES)
        {
            BuiltInCategory bic;
            if (Enum.TryParse<BuiltInCategory>(name, out bic)
                && Enum.IsDefined(typeof(BuiltInCategory), bic))
            {
                found.Add(bic);
            }
            else if (skippedOut != null)
            {
                skippedOut.Add(name);
            }
        }

        return found;
    }

    // Every placed (non-type) element that could carry the parameter.
    // Fast path asks Revit for only our categories; if that filter is ever
    // rejected we fall back to walking the whole model.
    static List<Element> BP_CollectCandidateElements(Document doc)
    {
        List<BuiltInCategory> cats = BP_ResolveCategories(null);

        try
        {
            var filter = new ElementMulticategoryFilter(cats);
            return new FilteredElementCollector(doc)
                .WherePasses(filter)
                .WhereElementIsNotElementType()
                .ToList();
        }
        catch
        {
            return new FilteredElementCollector(doc)
                .WhereElementIsNotElementType()
                .WhereElementIsViewIndependent()
                .ToList();
        }
    }

    // ---- The project parameter -------------------------------------------

    // The minimum valid contents of a Revit shared parameter file. The
    // columns are separated by TAB characters ("\t") - Revit rejects the
    // file otherwise.
    const string BP_SHARED_PARAM_HEADER =
        "# This is a Revit shared parameter file.\r\n"
        + "# Do not edit manually.\r\n"
        + "*META\tVERSION\tMINVERSION\r\n"
        + "META\t2\t1\r\n"
        + "*GROUP\tID\tNAME\r\n"
        + "*PARAM\tGUID\tNAME\tDATATYPE\tDATACATEGORY\tGROUP\tVISIBLE\t"
        + "DESCRIPTION\tUSERMODIFIABLE\r\n";

    static void BP_EnsureSharedParamFileExists()
    {
        string path = BP_SharedParamFile();
        string folder = Path.GetDirectoryName(path);

        if (!Directory.Exists(folder)) Directory.CreateDirectory(folder);

        if (!File.Exists(path) || new FileInfo(path).Length == 0)
            File.WriteAllText(path, BP_SHARED_PARAM_HEADER);
    }

    // Find or create the "BIM Press Discipline" shared parameter definition.
    // Temporarily points Revit at our shared parameter file, then puts the
    // user's own file back.
    static Definition BP_GetOrCreateSharedDefinition(Document doc)
    {
        var app = doc.Application;
        string previousFile = app.SharedParametersFilename;

        BP_EnsureSharedParamFileExists();
        app.SharedParametersFilename = BP_SharedParamFile();

        try
        {
            DefinitionFile defFile = app.OpenSharedParameterFile();
            if (defFile == null)
            {
                throw new Exception(
                    "Revit could not open the shared parameter file at:\n"
                    + BP_SharedParamFile());
            }

            DefinitionGroup group = null;
            foreach (DefinitionGroup grp in defFile.Groups)
            {
                if (grp.Name == BP_SHARED_PARAM_GROUP) { group = grp; break; }
            }
            if (group == null)
                group = defFile.Groups.Create(BP_SHARED_PARAM_GROUP);

            foreach (Definition dfn in group.Definitions)
            {
                if (dfn.Name == BP_PARAM_NAME) return dfn;
            }

            // OLDER REVIT: on Revit 2021 and earlier replace
            // "SpecTypeId.String.Text" with "ParameterType.Text".
            var options = new ExternalDefinitionCreationOptions(
                BP_PARAM_NAME, SpecTypeId.String.Text);
            options.Visible = true;
            options.UserModifiable = true;
            options.Description =
                "BIM Press demo: type a discipline name here - "
                + BP_DisciplineNamesJoined() + ".";

            return group.Definitions.Create(options);
        }
        finally
        {
            // Always restore whatever shared parameter file was set before.
            if (!string.IsNullOrEmpty(previousFile))
            {
                try { app.SharedParametersFilename = previousFile; }
                catch { }
            }
        }
    }

    // Create the parameter, or re-attach an existing one to the full
    // category list. Either way this is safe to run repeatedly.
    // Must be called inside an open Transaction.
    static string BP_EnsureProjectParameter(
        Document doc, out int boundCategoryCount, List<string> skippedOut)
    {
        List<BuiltInCategory> cats = BP_ResolveCategories(skippedOut);

        CategorySet catSet = doc.Application.Create.NewCategorySet();
        boundCategoryCount = 0;

        foreach (BuiltInCategory bic in cats)
        {
            Category cat = null;
            try { cat = doc.Settings.Categories.get_Item(bic); }
            catch { }

            if (cat == null) continue;
            try { if (!cat.AllowsBoundParameters) continue; }
            catch { continue; }

            catSet.Insert(cat);
            boundCategoryCount++;
        }

        // Is the parameter already bound in this project?
        Definition existing = null;
        DefinitionBindingMapIterator it = doc.ParameterBindings.ForwardIterator();
        it.Reset();
        while (it.MoveNext())
        {
            if (it.Key.Name == BP_PARAM_NAME) { existing = it.Key; break; }
        }

        // "Instance" binding = each placed element gets its own value, as
        // opposed to a type parameter shared by every instance of a type.
        InstanceBinding binding =
            doc.Application.Create.NewInstanceBinding(catSet);

        // OLDER REVIT: on Revit 2021 and earlier replace "GroupTypeId.Data"
        // with "BuiltInParameterGroup.PG_DATA".
        if (existing != null)
        {
            doc.ParameterBindings.ReInsert(existing, binding, GroupTypeId.Data);
            return "updated";
        }

        Definition definition = BP_GetOrCreateSharedDefinition(doc);
        doc.ParameterBindings.Insert(definition, binding, GroupTypeId.Data);
        return "created";
    }

    // ---- Materials --------------------------------------------------------

    static Material BP_FindMaterial(Document doc, string name)
    {
        string wanted = name.Trim();
        foreach (Material mat in new FilteredElementCollector(doc)
                     .OfClass(typeof(Material))
                     .Cast<Material>())
        {
            if (string.Equals(mat.Name.Trim(), wanted,
                    StringComparison.OrdinalIgnoreCase))
                return mat;
        }
        return null;
    }

    // Give the material its own private appearance asset, so changing one
    // discipline's render colour does not change the others.
    // Must be called inside an open Transaction. Never throws.
    static ElementId BP_AttachAppearanceAsset(
        Document doc, Material material, string uniqueSuffix)
    {
        try
        {
            string newName = "BIM Press Appearance - " + uniqueSuffix;

            // Reuse the one we made on a previous run, if it is there.
            foreach (AppearanceAssetElement existing
                in new FilteredElementCollector(doc)
                    .OfClass(typeof(AppearanceAssetElement))
                    .Cast<AppearanceAssetElement>())
            {
                if (existing.Name == newName)
                {
                    material.AppearanceAssetId = existing.Id;
                    return existing.Id;
                }
            }

            // Find any "generic" appearance asset in the project - one that
            // exposes a plain diffuse colour we are able to overwrite.
            AppearanceAssetElement source = null;
            foreach (AppearanceAssetElement candidate
                in new FilteredElementCollector(doc)
                    .OfClass(typeof(AppearanceAssetElement))
                    .Cast<AppearanceAssetElement>())
            {
                try
                {
                    Asset asset = candidate.GetRenderingAsset();
                    if (asset != null
                        && asset.FindByName("generic_diffuse") != null)
                    {
                        source = candidate;
                        break;
                    }
                }
                catch { }
            }

            if (source == null) return ElementId.InvalidElementId;

            AppearanceAssetElement duplicate = source.Duplicate(newName);
            material.AppearanceAssetId = duplicate.Id;
            return duplicate.Id;
        }
        catch
        {
            return ElementId.InvalidElementId;
        }
    }

    // Set the RENDER colour to match the shaded colour.
    // MUST run with NO transaction open - AppearanceAssetEditScope starts its
    // own transaction and throws if one is already running.
    static bool BP_SetRenderAppearanceColor(
        Document doc, ElementId assetElementId, byte[] rgb)
    {
        try
        {
            var scope = new AppearanceAssetEditScope(doc);
            Asset editable = scope.Start(assetElementId);

            var prop = editable.FindByName("generic_diffuse")
                as AssetPropertyDoubleArray4d;

            bool changed = false;
            if (prop != null)
            {
                prop.SetValueAsColor(new Color(rgb[0], rgb[1], rgb[2]));
                changed = true;
            }

            // Commit either way - an edit scope must always be closed, and
            // committing an asset we did not change is harmless.
            scope.Commit(true);
            return changed;
        }
        catch
        {
            return false;
        }
    }

    // ---- Geometry and painting -------------------------------------------

    static Options BP_GeometryOptions()
    {
        var opts = new Options();
        // Paint needs faces Revit can trace back to the element. Computing
        // references is what makes that possible.
        opts.ComputeReferences = true;
        opts.IncludeNonVisibleObjects = false;
        opts.DetailLevel = ViewDetailLevel.Fine;
        return opts;
    }

    // Walk an element's geometry and collect every face.
    //
    // Family instances (doors, sprinklers, light fixtures...) wrap their
    // geometry in a GeometryInstance, so we look inside those too:
    //   GetSymbolGeometry()   - geometry in the family's own coordinates.
    //                           Its faces keep their references, which is
    //                           what Paint needs, so it is tried first.
    //   GetInstanceGeometry() - geometry moved into place in the project,
    //                           kept as a backup.
    static void BP_GatherFaces(GeometryElement geometry, List<Face> collected)
    {
        if (geometry == null) return;

        foreach (GeometryObject geomObj in geometry)
        {
            var solid = geomObj as Solid;
            if (solid != null)
            {
                try
                {
                    if (solid.Faces.Size > 0)
                    {
                        foreach (Face face in solid.Faces) collected.Add(face);
                    }
                }
                catch { }
                continue;
            }

            var instance = geomObj as GeometryInstance;
            if (instance != null)
            {
                try { BP_GatherFaces(instance.GetSymbolGeometry(), collected); }
                catch { }
                try { BP_GatherFaces(instance.GetInstanceGeometry(), collected); }
                catch { }
            }
        }
    }

    static List<Face> BP_GetPaintableFaces(Element element, Options opts)
    {
        var faces = new List<Face>();
        try
        {
            GeometryElement geometry = element.get_Geometry(opts);
            BP_GatherFaces(geometry, faces);
        }
        catch { }
        return faces;
    }

    // Paint every face of one element. Returns how many faces took the paint;
    // zero means Revit would not paint this element at all.
    // Must be called inside an open Transaction.
    static int BP_PaintElement(
        Document doc, Element element, ElementId materialId, Options opts)
    {
        int painted = 0;
        foreach (Face face in BP_GetPaintableFaces(element, opts))
        {
            try
            {
                doc.Paint(element.Id, face, materialId);
                painted++;
            }
            catch
            {
                // Faces Revit will not paint - and duplicates picked up from
                // both symbol and instance geometry - land here. Normal.
            }
        }
        return painted;
    }

    // ---- Small odds and ends ---------------------------------------------

    // Read the element's "BIM Press Discipline" text, or null if blank.
    static string BP_ReadDisciplineValue(Element element)
    {
        try
        {
            Parameter param = element.LookupParameter(BP_PARAM_NAME);
            if (param == null || !param.HasValue) return null;

            string value = param.AsString();
            if (string.IsNullOrEmpty(value) || value.Trim().Length == 0)
                return null;

            return value;
        }
        catch
        {
            return null;
        }
    }

    // OLDER REVIT: on Revit 2023 and earlier this was "elementId.IntegerValue".
    static long BP_IdNumber(ElementId elementId)
    {
        return elementId.Value;
    }

    static string BP_CategoryName(Element element)
    {
        try
        {
            if (element.Category != null) return element.Category.Name;
        }
        catch { }
        return "(no category)";
    }

    // TaskDialog truncates very long text, so the full report goes in the
    // expandable section and a short headline stays visible.
    static void BP_ShowReport(string title, string body)
    {
        var dialog = new TaskDialog("BIM Press");
        dialog.MainInstruction = title;
        dialog.MainContent = body.Length > 1500
            ? body.Substring(0, 1500) + "\n..."
            : body;
        if (body.Length > 1500) dialog.ExpandedContent = body;
        dialog.CommonButtons = TaskDialogCommonButtons.Close;
        dialog.Show();
    }

// ----- PASTE TO HERE -----
