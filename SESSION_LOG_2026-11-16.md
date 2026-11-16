# Session log: 2026-11-16 (bim-press)

## What was done

**Added the Revit Keys app (public, no password).**

- New folder `WEBSITE/apps/revit-keys/` with the app exactly as supplied in
  `REVIT-KEYS CONCEPT/BIM-Press_Revit_Shortcut_Manager_v1.zip`:
  `index.html`, `Revit_2023.xml` to `Revit_2026.xml`, `README.md`, `VERSION_CHECK.md`.
  `index.html` is byte-identical to the zip (SHA-256 checked). No logic was edited.
- New icon `WEBSITE/assets/apps/revit-keys-icon.png` (the 256 px app icon from the asset pack).
- `WEBSITE/index.html` (12 lines added):
  - a "Revit Keys — Shortcut Manager" card in the main Apps grid, before P-DXF
  - a small style rule (`.app-icon.pic`) so a picture icon sits on a dark tile
  - a "Revit Keys" entry in the hamburger menu's Apps list
  - a "Revit Keys" entry in the site search list

Share link once pushed: https://bim-press.com/apps/revit-keys/

## Things found along the way

- **There is no password gate on this site.** No edge function, no gate config, no
  Netlify site password. All other app cards link out to separate Netlify sites.
  So nothing needed unlocking and nothing else was locked to begin with.
- The app is fully self-contained (no outside scripts or files), so moving it
  broke no paths.
- Default Move is MM for Revit 2025 and MV for 2023, 2024 and 2026. This comes
  from the supplied XML files and is intentional. Left alone.
- `netlify.toml` (the HTML minifier from the September audit) is still
  uncommitted and was left that way. If it is ever committed, exclude
  `WEBSITE/apps/revit-keys/` first, or the minifier will rewrite the app's
  1.5 MB `index.html`.

## Testing

Local server on the `WEBSITE` folder:

- `/apps/revit-keys/` loads with no password prompt, 2,112 commands, version
  picker shows 2023 to 2026, no console errors, no failed requests.
- Home page: the card shows in the top row of Apps (fourth card); P-DXF moves
  to a second row. Icon loads, link goes to `apps/revit-keys/`.
- Not done: a visual screenshot check (the browser screenshot tool timed out),
  and phone-width layout was not looked at.

## Still to do

- Fire-Press footer link: skipped for now at Robbie's request. fire-press.com
  DNS is correct but its HTTPS certificate had not been issued yet.

## Deployed

Pushed to GitHub on 2026-11-16 at Robbie's request (two commits, plus a
`.gitattributes` rule that keeps the app files byte-exact). Checked live:
https://bim-press.com/apps/revit-keys/ returns 200 with no password, the file
matches the local copy exactly, and the card shows on the home page.

Note: GitHub reports the repo has moved to `robbiefromramona-press/BIM-Press`.
The old address still works through a redirect.
