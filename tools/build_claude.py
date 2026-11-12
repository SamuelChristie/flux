"""Build claude.flux: Claude desktop app shortcuts for the Flux Keyboard.

    python tools/build_claude.py [output.flux]

This is the smallest of the three builders and the best one to copy when making a file
for another application.

Where the bindings come from
----------------------------
The "Keyboard shortcuts" panel inside the app (press Cmd+/ in Claude), macOS, November
2026. The panel is the authority: published lists and third-party cheat sheets disagree
with it and with each other, and the bindings change between app versions. To update this
file, open the panel in your copy of the app and compare.

How the panel maps to rows
--------------------------
* A panel row with "or" between two chords becomes two entries with the same label.
* A panel row shown as Cmd+1...9 becomes nine entries, one per digit.
* Windows bindings are not from the panel. They are derived with mac_to_win(): Command
  becomes Ctrl and Option becomes Alt. Check them against the Windows app before relying
  on them.
"""
import sys

from fluxlib import ICON_KEYBOARD, ICON_MAGNIFY, Row, build_file, mac_to_win

APP = "Claude"

# Group names, in the order Polymath lists them. "General" and "In sessions" are the
# section names the panel itself uses.
GENERAL = "General"
SESSIONS = "In sessions"
DICTATION = "Dictation"
BROWSER = "Browser"
DEFAULT = "default"
GROUPS = [GENERAL, SESSIONS, DICTATION, BROWSER, DEFAULT]


def row(group, label, key, mods, icon=None):
    """A shortcut given by its Mac modifiers (cmd, ctrl, shift, opt); Windows is derived."""
    return Row(group, label, key, mac=mods, win=mac_to_win(mods), icon=icon)


#   (group, label, key, Mac modifiers[, icon])
ROWS = [
    # The "General" section of the panel.
    row(GENERAL, "Quick Chat or Search", "K", "cmd"),
    row(GENERAL, "Search", "K", "shift+cmd", ICON_MAGNIFY),
    # Shown in the panel as Control-Tab "or" Control-Shift-Tab: forward and back.
    row(GENERAL, "Switch Recents", "Tab", "ctrl"),
    row(GENERAL, "Switch Recents Back", "Tab", "ctrl+shift"),
    row(GENERAL, "Incognito", "I", "shift+cmd"),
    row(GENERAL, "New Incognito Chat", "N", "shift+cmd"),
    row(GENERAL, "Toggle Sidebar", "B", "cmd"),
    row(GENERAL, "New Session", "N", "cmd"),
    row(GENERAL, "Close", "W", "cmd"),
    # A panel row with two alternatives becomes two entries with the same label.
    row(GENERAL, "Next", "]", "shift+cmd"),
    row(GENERAL, "Next", "Down", "opt"),
    row(GENERAL, "Previous", "[", "shift+cmd"),
    row(GENERAL, "Previous", "Up", "opt"),
    row(GENERAL, "Back", "[", "cmd"),
    row(GENERAL, "Forward", "]", "cmd"),
    row(GENERAL, "Next Sidebar Tab", "Right", "opt+cmd"),
    row(GENERAL, "Previous Sidebar Tab", "Left", "opt+cmd"),
    row(GENERAL, "Keyboard Shortcuts", "/", "cmd", ICON_KEYBOARD),
    row(GENERAL, "Settings", ",", "cmd"),
    row(GENERAL, "Focus Next Area", "F6", ""),
    row(GENERAL, "Focus Previous Area", "F6", "shift"),

    # The "In sessions" section of the panel, minus dictation and the browser rows.
    row(SESSIONS, "Send Message", "Enter", ""),
    row(SESSIONS, "New Line", "Enter", "shift"),
    row(SESSIONS, "Queue for Later", "Enter", "cmd"),
    row(SESSIONS, "Toggle Thinking", "E", "shift+cmd"),
    row(SESSIONS, "Model Menu", ".", "shift+cmd"),
    row(SESSIONS, "Add Files or Photos", "U", "cmd"),
    row(SESSIONS, "Reuse Message (Up)", "Up", ""),
    row(SESSIONS, "Reuse Message (Down)", "Down", ""),
    row(SESSIONS, "Stop Response", "Esc", ""),
    row(SESSIONS, "Find", "F", "cmd", ICON_MAGNIFY),
    row(SESSIONS, "Find Next", "G", "cmd"),
    row(SESSIONS, "Find Previous", "G", "shift+cmd"),
    row(SESSIONS, "Toggle Side Panel", ".", "cmd"),
    row(SESSIONS, "Pin / Unpin", "P", "opt+cmd"),
    row(SESSIONS, "Rename Session", "R", "opt+cmd"),
    row(SESSIONS, "Mark Read/Unread", "U", "opt+cmd"),

    # Split out of "In sessions": while dictating, Return finishes and Esc cancels, so the
    # same two keys would otherwise carry two labels in one group.
    row(DICTATION, "Toggle Dictation", "D", "cmd"),
    row(DICTATION, "Finish Dictation", "Enter", ""),
    row(DICTATION, "Cancel Dictation", "Esc", ""),

    # The panel lists "Jump to Browser tab" as Cmd+1...9.
    row(BROWSER, "Toggle Browser", "B", "shift+cmd"),
    *[row(BROWSER, f"Browser Tab {digit}", digit, "cmd") for digit in "123456789"],

    # The panel lists "Jump to..." as Cmd+1...9. These are the same chords as the browser
    # tabs; which one applies depends on what has focus in the app.
    *[row(DEFAULT, f"Jump to {digit}", digit, "cmd") for digit in "123456789"],
]

if __name__ == "__main__":
    build_file(sys.argv[1] if len(sys.argv) > 1 else "claude.flux", APP, GROUPS, ROWS)
