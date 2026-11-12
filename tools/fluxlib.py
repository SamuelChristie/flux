"""fluxlib: read and write shortcut files (.flux) for the Flux Keyboard's Polymath software.

The .flux format is not documented by Flux. Everything here was worked out from files
exported by Polymath, so treat it as a description of what those files contain, not as a
specification. The README has the full write-up; the short version is:

    uint32  byte length of the JSON payload          (all integers are little-endian)
    bytes   JSON payload, compact UTF-8
    uint32  number of attachments                    (0 in a shortcut-only file)
            for each attachment:
                uint32 name length,  name (UTF-8)
                uint32 data length,  data
    uint32  0                                        (terminator)

A shortcut-only file fills just the "shortcuts" section of the JSON. That section holds one
"shortcut set" per application, and each set holds a list of shortcut entries: one key plus
modifiers, a label, a group, and optionally the name of an icon built into Polymath.

Typical use (see build_claude.py for the smallest complete example):

    from fluxlib import Row, build_file

    rows = [
        Row("General", "New Session", "N", mac="cmd", win="ctrl"),
        Row("General", "Stop Response", "Esc", mac="", win=""),
    ]
    build_file("claude.flux", "Claude", ["General"], rows)

Only the Python standard library is needed.
"""
import json
import struct
from collections import Counter, namedtuple

# --------------------------------------------------------------------------- keys ---
# Each shortcut names its key five different ways, so every key needs all five spellings:
#
#   vk         Windows virtual-key constant        -> "win_us_key1_constant"
#   win_label  key name shown on Windows           -> "win_us_key1"
#   mac_const  key name used on the Mac side       -> "mac_us_key1_constant"
#   mac_label  key name shown on Mac               -> "mac_us_key1"
#   qmk        QMK-style key name                  -> "keyCode"
#   hid        USB HID keyboard usage ID           -> "HidKeyCode.keycode"
#
# Keys are physical US-layout positions: the HID code identifies the key itself, whatever
# layout the computer is set to.
Key = namedtuple("Key", "vk win_label mac_const mac_label qmk hid")

KEYS = {}

# Letters: HID usage 4 (A) through 29 (Z).
for _i, _ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    KEYS[_ch] = Key(f"VK_{_ch}", _ch, _ch, _ch, f"KC_{_ch}", 4 + _i)

# Digits: HID usage 30 (1) through 38 (9), then 39 for 0.
for _d in "123456789":
    KEYS[_d] = Key(f"VK_{_d}", _d, _d, _d, f"KC_{_d}", 29 + int(_d))
KEYS["0"] = Key("VK_0", "0", "0", "0", "KC_0", 39)

# Function keys: HID usage 58 (F1) through 69 (F12).
for _n in range(1, 13):
    KEYS[f"F{_n}"] = Key(f"VK_F{_n}", f"F{_n}", f"F{_n}", f"F{_n}", f"KC_F{_n}", 57 + _n)

KEYS.update({
    # These spellings are copied verbatim from Polymath's own Photoshop shortcut set.
    # Note the Mac side calls Backspace "Delete", and capitalises "Arrow" in the constant
    # but not in the label.
    "Space":     Key("VK_SPACE", "Spacebar", "Spacebar", "Spacebar", "KC_SPACE", 44),
    "Backspace": Key("VK_BACK", "Backspace", "Delete", "Delete", "KC_BACKSPACE", 42),
    "Left":      Key("VK_LEFT", "Left arrow", "Left Arrow", "Left arrow", "KC_LEFT", 80),
    "Right":     Key("VK_RIGHT", "Right arrow", "Right Arrow", "Right arrow", "KC_RIGHT", 79),
    "-":         Key("VK_OEM_MINUS", "-", "-", "-", "KC_MINUS", 45),
    "=":         Key("VK_OEM_PLUS", "=", "=", "=", "KC_EQUAL", 46),
    ",":         Key("VK_OEM_COMMA", ",", ",", ",", "KC_COMMA", 54),
    ".":         Key("VK_OEM_PERIOD", ".", ".", ".", "KC_DOT", 55),
    "/":         Key("VK_OEM_2", "/", "/", "/", "KC_SLASH", 56),
    "`":         Key("VK_OEM_3", "`", "`", "`", "KC_GRAVE", 53),
    "[":         Key("VK_OEM_4", "[", "[", "[", "KC_LEFT_BRACKET", 47),
    "]":         Key("VK_OEM_6", "]", "]", "]", "KC_RIGHT_BRACKET", 48),

    # Not in the Photoshop set, but they follow the same pattern as Left/Right above.
    "Up":        Key("VK_UP", "Up arrow", "Up Arrow", "Up arrow", "KC_UP", 82),
    "Down":      Key("VK_DOWN", "Down arrow", "Down Arrow", "Down arrow", "KC_DOWN", 81),

    # Not in the Photoshop set. The VK and QMK names are the standard ones; the display
    # labels are best guesses. If Polymath shows an odd name for one of these keys, export
    # a shortcut that uses the key from Polymath and copy its spelling here.
    "Esc":       Key("VK_ESCAPE", "Esc", "Esc", "Esc", "KC_ESCAPE", 41),
    "Enter":     Key("VK_RETURN", "Enter", "Return", "Return", "KC_ENTER", 40),
    "Tab":       Key("VK_TAB", "Tab", "Tab", "Tab", "KC_TAB", 43),
    "Delete":    Key("VK_DELETE", "Delete", "Forward Delete", "Forward delete", "KC_DELETE", 76),
    "Home":      Key("VK_HOME", "Home", "Home", "Home", "KC_HOME", 74),
    "End":       Key("VK_END", "End", "End", "End", "KC_END", 77),
    "PageUp":    Key("VK_PRIOR", "Page Up", "Page Up", "Page Up", "KC_PAGE_UP", 75),
    "PageDown":  Key("VK_NEXT", "Page Down", "Page Down", "Page Down", "KC_PAGE_DOWN", 78),
    "\\":        Key("VK_OEM_5", "\\", "\\", "\\", "KC_BACKSLASH", 49),
    ";":         Key("VK_OEM_1", ";", ";", ";", "KC_SEMICOLON", 51),
})

# -------------------------------------------------------------------------- icons ---
# A shortcut can name an icon that ships inside Polymath. The file carries no image data,
# so only names Polymath already knows will show up. These are the names that appear in
# Polymath's Photoshop shortcut set and that the builders in this repo use.
ICON_UNDO = "Smock_Undo_18_N.png"
ICON_REDO = "Smock_Redo_18_N.png"
ICON_SAVE = "Smock_SaveFloppy_18_N.png"
ICON_SAVE_AS = "Smock_SaveAsFloppy_18_N.png"
ICON_CUT = "Smock_Cut_18_N.png"
ICON_COPY = "Smock_Copy_18_N.png"
ICON_PASTE = "Smock_Paste_18_N.png"
ICON_ZOOM_IN = "Smock_ZoomIn_18_N.png"
ICON_ZOOM_OUT = "Smock_ZoomOut_18_N.png"
ICON_MAGNIFY = "Smock_Magnify_18_N.png"
ICON_RECT_SELECT = "Smock_RectSelect_18_N.png"
ICON_REGION_SELECT = "Smock_RegionSelect_18_N.png"
ICON_HELP = "Smock_Help_18_N.png"
ICON_INFO = "Smock_InfoOutline_18_N.png"
ICON_PLAY = "Smock_Play_18_N.png"
ICON_MOVE = "Smock_Move_18_N.png"
ICON_KEYBOARD = "Smock_Keyboard_18_N.png"
ICON_COLORS = "Smock_ColorPalette_18_N.png"
ICON_ROTATE_VIEW = "flux_Rotate View Tool.png"
ICON_SCREEN_MODE = "flux_Change Screen Mode.png"

# --------------------------------------------------------------------------- rows ---
# One Row describes one shortcut. `mac` and `win` are modifier strings such as "cmd+shift"
# or "ctrl+alt"; an empty string means the key on its own; None means the shortcut does not
# exist on that platform.
#
#   group   name of the group ("applicationContext") the shortcut is listed under
#   label   text shown on the key
#   key     a name from KEYS
#   mac     Mac modifiers:     any of cmd, ctrl, shift, opt
#   win     Windows modifiers: any of ctrl, shift, alt
#   icon    optional icon filename (see the ICON_ constants)
#   source  optional note on where the binding came from; never written to the file
Row = namedtuple("Row", "group label key mac win icon source", defaults=(None, None, None, None))

MAC_MODIFIERS = {"cmd": "MAC_CMD", "ctrl": "MAC_CTRL", "shift": "MAC_SHIFT", "opt": "MAC_OPT"}
WIN_MODIFIERS = {"ctrl": "WIN_CTRL", "shift": "WIN_SHIFT", "alt": "WIN_ALT"}

# The longest label in Polymath's Photoshop set. Longer labels may still work; this is
# only used to print a warning.
LONGEST_KNOWN_LABEL = 20


def _parse_mods(mods, allowed, where):
    """Turn "cmd+shift" into {"cmd", "shift"}, rejecting names the platform doesn't have."""
    names = {m for m in mods.lower().split("+") if m}
    unknown = names - allowed.keys()
    if unknown:
        raise ValueError(f"{where}: unknown modifier(s) {sorted(unknown)}; use {sorted(allowed)}")
    return names


def qt_to_mac(mods):
    """Translate a Qt-style shortcut's modifiers to what they mean on a Mac.

    Qt applications such as FreeCAD write shortcuts the Windows way ("Ctrl+S", "Alt+F11").
    On macOS, Qt maps Ctrl to Command and Alt to Option.
    """
    return "+".join({"ctrl": "cmd", "alt": "opt"}.get(m, m) for m in mods.split("+") if m)


def mac_to_win(mods):
    """Translate Mac modifiers to the usual Windows equivalent.

    Command becomes Ctrl and Option becomes Alt. Command+Control becomes Ctrl+Alt, because
    both would otherwise land on Ctrl. A lone Control stays Ctrl.
    """
    names = {m for m in mods.split("+") if m}
    out = []
    if {"cmd", "ctrl"} <= names:
        out += ["ctrl", "alt"]
    elif names & {"cmd", "ctrl"}:
        out.append("ctrl")
    if "opt" in names and "alt" not in out:
        out.append("alt")
    if "shift" in names:
        out.append("shift")
    return "+".join(out)


def chord_text(row, platform):
    """Human-readable chord for one platform, e.g. "Shift+Cmd+K"; "-" if not defined."""
    mods = row.mac if platform == "mac" else row.win
    if mods is None:
        return "-"
    key = KEYS[row.key]
    order = ["ctrl", "opt", "alt", "shift", "cmd"]
    names = sorted({m for m in mods.split("+") if m}, key=order.index)
    return "+".join([n.capitalize() for n in names] + [key.mac_label if platform == "mac" else key.win_label])


# ------------------------------------------------------------------------ entries ---
def shortcut_entry(app, number, row):
    """Build the JSON object for one shortcut.

    The field order matches Polymath's own files. Two details are easy to get wrong:

    * The modifier flags inside "HidKeyCode" are always false, even for a shortcut that
      uses modifiers. The modifiers live in "keyCombo".
    * A shortcut that exists on only one platform leaves the other platform's key strings
      empty and sets that platform's "*_US_KEY1_CONSTANT" flag to false.
    """
    if row.key not in KEYS:
        raise KeyError(f"{row.label!r}: no key named {row.key!r} in fluxlib.KEYS")
    if row.mac is None and row.win is None:
        raise ValueError(f"{row.label!r}: needs a binding on at least one platform")

    key = KEYS[row.key]
    has_mac, has_win = row.mac is not None, row.win is not None
    mac = _parse_mods(row.mac or "", MAC_MODIFIERS, row.label)
    win = _parse_mods(row.win or "", WIN_MODIFIERS, row.label)

    entry = {"id": f"{app}_{row.label}_{number}"}
    if row.icon:
        entry["iconFilename"] = row.icon
    entry.update({
        "applicationContext": row.group,
        "collectionName": app,
        "isSvg": False,
        "builtInIcon": True,
        "shortcutKey": {
            "win_us_key1_constant": key.vk if has_win else "",
            "HidKeyCode": {
                "lctrl": False, "lshift": False, "lalt": False, "lmeta": False,
                "rctrl": False, "rshift": False, "ralt": False, "rmeta": False,
                "keycode": key.hid, "type": 0,
            },
            "win_us_key1": key.win_label if has_win else "",
            "mac_us_key1_constant": key.mac_const if has_mac else "",
            "mac_us_key1": key.mac_label if has_mac else "",
            "keyCode": key.qmk,
        },
        "shortcutLabel": row.label,
        "keyCombo": {
            "WIN_CTRL": "ctrl" in win, "WIN_SHIFT": "shift" in win, "WIN_ALT": "alt" in win,
            "WIN_WINKEY": False, "WIN_US_KEY1_CONSTANT": has_win,
            "MAC_CMD": "cmd" in mac, "MAC_CTRL": "ctrl" in mac, "MAC_SHIFT": "shift" in mac,
            "MAC_OPT": "opt" in mac, "MAC_FN": False, "MAC_US_KEY1_CONSTANT": has_mac,
        },
    })
    return entry


def shortcut_document(app, groups, rows):
    """Build the whole JSON document for a shortcut-only file.

    `groups` lists the group names in the order Polymath should show them. "all" is added
    in front automatically, as in Polymath's own files.
    """
    used = {row.group for row in rows}
    if used != set(groups):
        raise ValueError(f"groups and rows disagree: unused {sorted(set(groups) - used)}, "
                         f"undeclared {sorted(used - set(groups))}")
    return {
        # A full profile export also fills these sections (theme, actuation, keymap...).
        # A shortcut-only file leaves them empty.
        "profile": [], "appearance": [], "actuation": [], "icons": [],
        "keymaps": [], "media": [],
        "shortcuts": [{
            "applicationName": app,
            "sourceTemplate": app,
            # Shortcut ids are numbered from 1 in row order.
            "shortcuts": [shortcut_entry(app, n, row) for n, row in enumerate(rows, 1)],
            "deltas": {},
            "applicationContexts": ["all", *groups],
        }],
    }


def warnings_for(rows):
    """Return a list of things worth a second look. None of them stop the file being written."""
    notes = []
    for row in rows:
        if len(row.label) > LONGEST_KNOWN_LABEL:
            notes.append(f"label longer than {LONGEST_KNOWN_LABEL} characters: {row.label!r}")
    # The same chord twice in one group usually means a typo. Across groups it is normal:
    # Ctrl+T is "Transpose" at the shell and "Task Checklist" in Claude Code.
    for platform in ("mac", "win"):
        seen = Counter((r.group, chord_text(r, platform)) for r in rows if chord_text(r, platform) != "-")
        for (group, chord), count in seen.items():
            if count > 1:
                notes.append(f"{chord} is used {count} times in group {group!r} ({platform})")
    return notes


# --------------------------------------------------------------------- file I/O ---
def write_flux(path, document, attachments=()):
    """Write a .flux file. `attachments` is a list of (name, bytes) pairs, usually empty."""
    # Polymath writes compact JSON and leaves non-ASCII characters unescaped.
    payload = json.dumps(document, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    parts = [struct.pack("<I", len(payload)), payload, struct.pack("<I", len(attachments))]
    for name, blob in attachments:
        encoded = name.encode("utf-8")
        parts += [struct.pack("<I", len(encoded)), encoded, struct.pack("<I", len(blob)), blob]
    parts.append(struct.pack("<I", 0))
    with open(path, "wb") as f:
        f.write(b"".join(parts))


def read_flux(path):
    """Read a .flux file. Returns (document, attachments) with attachments as (name, bytes)."""
    with open(path, "rb") as f:
        data = f.read()
    length = struct.unpack_from("<I", data, 0)[0]
    document = json.loads(data[4:4 + length].decode("utf-8"))
    pos = 4 + length
    count = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    attachments = []
    for _ in range(count):
        name_len = struct.unpack_from("<I", data, pos)[0]
        name = data[pos + 4:pos + 4 + name_len].decode("utf-8")
        pos += 4 + name_len
        blob_len = struct.unpack_from("<I", data, pos)[0]
        attachments.append((name, data[pos + 4:pos + 4 + blob_len]))
        pos += 4 + blob_len
    if data[pos:] != b"\x00\x00\x00\x00":
        raise ValueError(f"{path}: unexpected data after the last attachment")
    return document, attachments


def build_file(path, app, groups, rows):
    """Build a shortcut-only .flux file and print a short summary."""
    write_flux(path, shortcut_document(app, groups, rows))
    print(f"wrote {path}: {app}, {len(rows)} shortcuts")
    for group in groups:
        print(f"  {group}: {sum(row.group == group for row in rows)}")
    for note in warnings_for(rows):
        print(f"  warning: {note}")
