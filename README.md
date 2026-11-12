# Flux Polymath shortcut files

Keyboard-shortcut sets for the [Flux Keyboard](https://fluxkeyboard.com), in the `.flux` format used by its Polymath software. Each file labels the keys with one application's shortcuts, so the keyboard can show them when that application is in front.

| File | Application | Shortcuts | Platforms | Source of the bindings |
|---|---|---|---|---|
| `freecad.flux` | FreeCAD | 104 | Windows, Mac | Default accelerators in the FreeCAD 1.1.4 source |
| `terminal.flux` | Apple Terminal, plus Claude Code | 109 | Mac | Apple's Terminal shortcut list and the Claude Code interactive-mode docs |
| `claude.flux` | Claude desktop app | 59 | Mac (Windows inferred) | The app's own Cmd+/ shortcut panel, November 2026 |

This is an unofficial project. It is not affiliated with or endorsed by Flux Keyboard, FreeCAD, Apple or Anthropic.

## What's in this repository

| Path | What it is |
|---|---|
| `freecad.flux`, `terminal.flux`, `claude.flux` | The shortcut files. Download these if you only want to use them |
| `tools/fluxlib.py` | Small Python library that reads and writes `.flux` files |
| `tools/build_freecad.py` | Generates `freecad.flux` |
| `tools/build_terminal.py` | Generates `terminal.flux` |
| `tools/build_claude.py` | Generates `claude.flux`; the simplest one to copy for a new application |
| `tools/inspect_flux.py` | Prints the contents of any `.flux` file |

The scripts need Python 3.8 or later and nothing outside the standard library.

## Status

The files follow the structure of a shortcut file exported from Polymath and pass a schema comparison against it. Import has not yet been confirmed on a keyboard for every file. If one fails to import or a key shows the wrong label, please open an issue.

## What is in each file

**`freecad.flux`**

| Group | Count | Examples |
|---|---|---|
| Popular shortcuts | 17 | Toggle Visibility, Recompute, Undo, Redo, Box Selection |
| Navigate views | 17 | Isometric, Front, Top (0–6), Zoom, Rotate View |
| Use function keys | 11 | Help, Rename, macro debugging |
| Sketcher tools | 15 | Dimension, Coincident, Horizontal, Tangent |
| Assembly tools | 21 | Fixed, Revolute and Slider joints, Solve Assembly |
| default | 23 | File and clipboard, overlay panels, TechDraw, Draft, Spreadsheet |

- Only single-chord shortcuts are included. FreeCAD's multi-key sequences, such as `G, L` for Line or `V, F` for Fit All, cannot be expressed in this format.
- Where Windows and Mac use different physical keys (Redo, Delete, Help, Close Window), there is one entry per platform with the same label.

**`terminal.flux`**

| Group | Count | Examples |
|---|---|---|
| Popular shortcuts | 13 | New Tab, Close Tab, Split Pane, Clear to Start, Find |
| Windows and tabs | 22 | Tab Overview, Inspector, Close Other Tabs, Scroll to Top |
| Command line | 11 | Line Start, Delete Word Back, History Search, Break |
| Claude Code | 25 | Interrupt, Permission Mode, Switch Model, Transcript Viewer |
| Select and find | 12 | Copy Plain Text, Paste Escaped, Find Next |
| Marks and bookmarks | 14 | Mark, Insert Bookmark, Clear to Mark |
| default | 12 | Export Text, Soft Reset, Option as Meta, Man Page |

- Claude Code runs inside Terminal, so it cannot have a profile of its own. It is a group in this file instead.
- Line-editing keys that Claude Code shares with the shell (Ctrl+A, Ctrl+E, Ctrl+K, Ctrl+U, Ctrl+W, Ctrl+R) are listed once, under Command line.
- Some Option shortcuts, such as Delete Word Forward and Switch Model, need **Use Option as Meta Key** turned on in Terminal's Settings → Profiles → Keyboard.

**`claude.flux`**

| Group | Count | Examples |
|---|---|---|
| General | 21 | Quick Chat or Search, Incognito, Toggle Sidebar, New Session |
| In sessions | 16 | Send, Queue for Later, Toggle Thinking, Model Menu, Find |
| Dictation | 3 | Toggle, Finish, Cancel |
| Browser | 10 | Toggle Browser, Browser Tab 1–9 |
| default | 9 | Jump to 1–9 |

- The bindings match one version of the Mac app. Press Cmd+/ in your own copy to check for differences.
- The Windows bindings are derived by mapping Cmd to Ctrl and Option to Alt. They were not read from the Windows app.

## Using a file

The menu names below are from Polymath 1.4.5.7 and may differ in other versions.

1. Download the `.flux` file you want.
2. In Polymath, go to **SHORTCUTS → Create New → Import** and choose the file.
3. Create a profile for the application, or open the one the import created. Set its associated application (FreeCAD, Terminal or Claude) and select the imported shortcut set as that profile's shortcuts.
4. Click **Save to Keyboard**. The keyboard does the switching itself, so the profile has to be stored on it.
5. Leave Polymath running. Automatic switching by active window needs it.
6. Open the application. Shortcuts that use a modifier appear while you hold that modifier.

These files contain a shortcut set only, with no profile, theme or keymap. If your version of Polymath will only import a complete profile, see [Full profiles](#full-profiles).

## The `.flux` file format

This description was worked out from files exported by Polymath. It is not official and may change with new Polymath versions.

### Container

All integers are unsigned 32-bit, little-endian.

| Part | Contents |
|---|---|
| Length | Byte length of the JSON that follows |
| JSON | UTF-8, compact, non-ASCII characters not escaped |
| Attachment count | Number of attached files, such as a theme's background image |
| Per attachment | Name length, name, data length, data |
| Terminator | `0` |

A file with no attachments therefore ends in eight zero bytes.

### Top-level JSON

```json
{
  "profile": [], "appearance": [], "actuation": [], "icons": [],
  "keymaps": [], "media": [],
  "shortcuts": [ { ...one shortcut set per application... } ]
}
```

A shortcut-only file leaves everything except `shortcuts` empty.

### Shortcut set

| Field | Meaning |
|---|---|
| `applicationName` | Name of the set, as shown in Polymath |
| `sourceTemplate` | Template the set came from; the same as `applicationName` in these files |
| `shortcuts` | List of shortcut entries |
| `deltas` | Empty object in every file seen so far |
| `applicationContexts` | Group names, starting with `"all"`; every entry's `applicationContext` must appear here |

### Shortcut entry

```json
{
  "id": "FreeCAD_Save_6",
  "iconFilename": "Smock_SaveFloppy_18_N.png",
  "applicationContext": "Popular shortcuts",
  "collectionName": "FreeCAD",
  "isSvg": false,
  "builtInIcon": true,
  "shortcutKey": {
    "win_us_key1_constant": "VK_S",
    "HidKeyCode": {
      "lctrl": false, "lshift": false, "lalt": false, "lmeta": false,
      "rctrl": false, "rshift": false, "ralt": false, "rmeta": false,
      "keycode": 22, "type": 0
    },
    "win_us_key1": "S",
    "mac_us_key1_constant": "S",
    "mac_us_key1": "S",
    "keyCode": "KC_S"
  },
  "shortcutLabel": "Save",
  "keyCombo": {
    "WIN_CTRL": true, "WIN_SHIFT": false, "WIN_ALT": false, "WIN_WINKEY": false,
    "WIN_US_KEY1_CONSTANT": true,
    "MAC_CMD": true, "MAC_CTRL": false, "MAC_SHIFT": false, "MAC_OPT": false, "MAC_FN": false,
    "MAC_US_KEY1_CONSTANT": true
  }
}
```

| Field | Meaning |
|---|---|
| `id` | Unique within the file; the pattern is `<app>_<label>_<number>` |
| `iconFilename` | Optional. Name of an icon built into Polymath. The file holds no image data |
| `applicationContext` | The group this shortcut belongs to |
| `shortcutLabel` | Text shown on the key. The longest label in Polymath's own Photoshop set is 20 characters |
| `win_us_key1_constant` | Windows virtual-key name, such as `VK_S`, `VK_F5`, `VK_OEM_COMMA` |
| `win_us_key1`, `mac_us_key1` | Key name as displayed on each platform |
| `HidKeyCode.keycode` | USB HID usage ID of the key (A is 4, 1 is 30, F1 is 58) |
| `HidKeyCode` modifier flags | `false` in every file seen so far; modifiers are carried by `keyCombo` |
| `keyCode` | QMK-style key name, such as `KC_S`, `KC_F5`, `KC_COMMA` |
| `keyCombo` | Modifier flags per platform, plus one flag per platform saying whether a key is defined |

Things to know:

- **One key plus modifiers.** There is no way to express a sequence such as `G, L`, or a double-tap.
- **Platform-specific shortcuts.** To define a shortcut for one platform only, leave the other platform's key strings empty and set its `*_US_KEY1_CONSTANT` flag to `false`.
- **Keys are physical US positions.** The HID code identifies the key, whatever layout the computer uses.
- **Icons.** Only icons that ship with Polymath can be referenced by name. Entries without `iconFilename` show the label alone.
- **Repeated chords are fine.** Two entries can use the same chord, which is useful when a key means different things in different groups.

### Full profiles

A complete profile export also fills the `profile`, `appearance`, `actuation` and `keymaps` sections, and may carry attachments. The profile object is what ties a shortcut set to a program:

```json
{
  "id": "47eaee8e-7dcc-573c-99b0-5744111ccf3a",
  "name": "Brave",
  "association": 1,
  "associatedProcess": "brave.exe",
  "selectedShortcutApplication": "Brave",
  "themeId": "default",
  "actuationModeId": "default-typing-general",
  "defaultKeymapLayer": 0
}
```

`associatedProcess` is the program's file name on Windows. The form it takes on a Mac has not been confirmed. `selectedShortcutApplication` must match the `applicationName` of a shortcut set in the same file.

To build a full profile, export one of your own profiles from Polymath, keep its theme, actuation and keymap sections, and replace the profile fields and the shortcut set. The [D6D/flux_app_profiles](https://github.com/D6D/flux_app_profiles) project has a script that does this.

## Make your own

The scripts in `tools/` generated the three files in this repository, and each builder reproduces its file byte for byte. To make a file for another application, describe its shortcuts as rows and let `fluxlib` write the file.

### A minimal builder

Save this as `tools/build_myapp.py`:

```python
from fluxlib import ICON_SAVE, Row, build_file

GROUPS = ["File", "default"]          # shown in this order; "all" is added automatically

ROWS = [
    #   group      label      key  modifiers per platform
    Row("File",    "Save",    "S", mac="cmd",       win="ctrl",       icon=ICON_SAVE),
    Row("File",    "Save As", "S", mac="cmd+shift", win="ctrl+shift"),
    Row("default", "Quit",    "Q", mac="cmd",       win=None),        # Mac only
    Row("default", "Help",    "F1", mac=None,       win=""),          # Windows only, no modifiers
]

build_file("myapp.flux", "MyApp", GROUPS, ROWS)
```

Then run it and check the result:

```
python tools/build_myapp.py
python tools/inspect_flux.py myapp.flux --keys
```

How a row works:

- **`key`** is a name from the `KEYS` table in `fluxlib.py`: letters, digits, `F1`–`F12`, `Enter`, `Esc`, `Tab`, `Space`, the arrow keys and common punctuation. Add a key there if you need one that is missing.
- **`mac`** takes any of `cmd`, `ctrl`, `shift`, `opt`, joined with `+`. **`win`** takes any of `ctrl`, `shift`, `alt`.
- An empty string means the key on its own. `None` means the shortcut does not exist on that platform.
- **`icon`** is optional. The `ICON_` constants in `fluxlib.py` are the built-in icon names known to work.

`build_file` prints a count per group and warns about labels longer than 20 characters and about a chord used twice in one group.

### The scripts

| Script | Use |
|---|---|
| `python tools/build_freecad.py [output.flux]` | Rebuild `freecad.flux`. Each row names the FreeCAD command it came from, so bindings can be checked against the FreeCAD source |
| `python tools/build_terminal.py [output.flux]` | Rebuild `terminal.flux` |
| `python tools/build_claude.py [output.flux]` | Rebuild `claude.flux` |
| `python tools/inspect_flux.py file.flux [--keys]` | Summarise any `.flux` file, including full profile exports; `--keys` lists every shortcut |

To change a shortcut set, edit the rows in its builder and run it again. The docstring at the top of each builder says where its bindings came from and how to update them.

`fluxlib` also exposes `read_flux()` and `write_flux()`, which handle attachments, for working with full profile exports.

### Tips

- Export a shortcut set or profile from Polymath first and run `inspect_flux.py` on it. Copy its spellings for key names and icon filenames instead of guessing.
- Take bindings from a primary source: the application's source code, its official shortcut page, or its own in-app shortcut list. Third-party cheat sheets often disagree with each other.
- Keep labels short.
- Check per-platform differences. The same action is often a different key on Mac and Windows, and needs one row for each.

## Credits

- [D6D/flux_app_profiles](https://github.com/D6D/flux_app_profiles) (MIT) documented the attachment section of the container, the profile fields and the import steps.
- FreeCAD bindings come from the [FreeCAD source](https://github.com/FreeCAD/FreeCAD) at tag 1.1.4.
- Terminal bindings come from Apple's [Keyboard shortcuts in Terminal on Mac](https://support.apple.com/guide/terminal/trmlshtcts).
- Claude Code bindings come from the [interactive mode reference](https://code.claude.com/docs/en/interactive-mode).

## License

MIT. See [LICENSE](LICENSE).
