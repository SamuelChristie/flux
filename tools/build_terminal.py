"""Build terminal.flux: Apple Terminal and Claude Code shortcuts for the Flux Keyboard.

    python tools/build_terminal.py [output.flux]

Where the bindings come from
----------------------------
* Terminal:    "Keyboard shortcuts in Terminal on Mac" (Apple Support)
               https://support.apple.com/guide/terminal/trmlshtcts
* Claude Code: the interactive mode reference
               https://code.claude.com/docs/en/interactive-mode

Both were read in November 2026. Mouse-only actions and plain keys that need no label
(arrow keys, Delete, Tab completion) are left out.

Terminal only exists on macOS, so every row has a Mac binding and no Windows one. In the
modifier strings, "ctrl" is the physical Control key on the Mac and "cmd" is Command.
"""
import sys

from fluxlib import (
    ICON_COLORS, ICON_COPY, ICON_CUT, ICON_INFO, ICON_KEYBOARD, ICON_MAGNIFY, ICON_PASTE,
    ICON_SCREEN_MODE, ICON_ZOOM_IN, ICON_ZOOM_OUT, Row, build_file,
)

APP = "Terminal"

# Group names, in the order Polymath lists them.
POPULAR = "Popular shortcuts"
WINDOWS = "Windows and tabs"
COMMAND_LINE = "Command line"
CLAUDE_CODE = "Claude Code"
SELECT = "Select and find"
MARKS = "Marks and bookmarks"
DEFAULT = "default"
GROUPS = [POPULAR, WINDOWS, COMMAND_LINE, CLAUDE_CODE, SELECT, MARKS, DEFAULT]


def mac(group, label, key, mods, icon=None):
    """A Mac-only shortcut. `mods` uses cmd, ctrl, shift, opt; "" means the key alone."""
    return Row(group, label, key, mac=mods, win=None, icon=icon)


#   (group, label, key, Mac modifiers[, icon])
ROWS = [
    # The ones used all day.
    mac(POPULAR, "New Window", "N", "cmd"),
    mac(POPULAR, "New Tab", "T", "cmd"),
    mac(POPULAR, "Close Tab", "W", "cmd"),
    mac(POPULAR, "Next Tab", "Tab", "ctrl"),
    mac(POPULAR, "Previous Tab", "Tab", "ctrl+shift"),
    mac(POPULAR, "Split Pane", "D", "cmd"),
    mac(POPULAR, "Clear to Start", "K", "cmd"),
    mac(POPULAR, "Find", "F", "cmd", ICON_MAGNIFY),
    mac(POPULAR, "Copy", "C", "cmd", ICON_COPY),
    mac(POPULAR, "Paste", "V", "cmd", ICON_PASTE),
    # Apple lists this as Command-Plus; the plus sign shares the = key.
    mac(POPULAR, "Bigger Font", "=", "cmd", ICON_ZOOM_IN),
    mac(POPULAR, "Smaller Font", "-", "cmd", ICON_ZOOM_OUT),
    mac(POPULAR, "Settings", ",", "cmd"),

    # From the "Work with Terminal windows and tabs" section of the Apple page.
    mac(WINDOWS, "New Window Same Cmd", "N", "ctrl+cmd"),
    mac(WINDOWS, "New Tab Same Command", "T", "ctrl+cmd"),
    mac(WINDOWS, "Show/Hide Tab Bar", "T", "shift+cmd"),
    mac(WINDOWS, "Tab Overview", "\\", "shift+cmd"),
    mac(WINDOWS, "New Command", "N", "shift+cmd"),
    mac(WINDOWS, "Remote Connection", "K", "shift+cmd"),
    mac(WINDOWS, "Inspector", "I", "cmd", ICON_INFO),
    mac(WINDOWS, "Edit Title", "I", "shift+cmd"),
    mac(WINDOWS, "Edit Background", "I", "opt+cmd"),
    mac(WINDOWS, "Next Window", "`", "cmd"),
    mac(WINDOWS, "Previous Window", "`", "shift+cmd"),
    mac(WINDOWS, "Close Split Pane", "D", "shift+cmd"),
    mac(WINDOWS, "Close Window", "W", "shift+cmd"),
    mac(WINDOWS, "Close Other Tabs", "W", "opt+cmd"),
    mac(WINDOWS, "Close All", "W", "opt+shift+cmd"),
    mac(WINDOWS, "Scroll to Top", "Home", "cmd"),
    mac(WINDOWS, "Scroll to Bottom", "End", "cmd"),
    mac(WINDOWS, "Page Up", "PageUp", "cmd"),
    mac(WINDOWS, "Page Down", "PageDown", "cmd"),
    mac(WINDOWS, "Line Up", "PageUp", "opt+cmd"),
    mac(WINDOWS, "Line Down", "PageDown", "opt+cmd"),
    mac(WINDOWS, "Full Screen", "F", "ctrl+cmd", ICON_SCREEN_MODE),

    # From the "Edit a command line" section. These are shell line-editing keys, and Claude
    # Code honours the same ones, so they are listed once here and not repeated below.
    mac(COMMAND_LINE, "Line Start", "A", "ctrl"),
    mac(COMMAND_LINE, "Line End", "E", "ctrl"),
    mac(COMMAND_LINE, "Word Forward", "Right", "opt"),
    mac(COMMAND_LINE, "Word Back", "Left", "opt"),
    mac(COMMAND_LINE, "Delete Line", "U", "ctrl"),
    mac(COMMAND_LINE, "Delete to Line End", "K", "ctrl"),
    # Needs "Use Option as Meta Key" (Terminal > Settings > Profiles > Keyboard).
    mac(COMMAND_LINE, "Delete Word Forward", "D", "opt"),
    mac(COMMAND_LINE, "Delete Word Back", "W", "ctrl"),
    mac(COMMAND_LINE, "Transpose Chars", "T", "ctrl"),
    mac(COMMAND_LINE, "History Search", "R", "ctrl"),
    # Apple: Command-Period is equivalent to Control-C on the command line.
    mac(COMMAND_LINE, "Break", ".", "cmd"),

    # Keys specific to Claude Code, from its interactive-mode reference. Claude Code runs
    # inside Terminal, so it cannot have a profile of its own; it is a group in this file.
    # Multi-key chords (Esc Esc to rewind, Ctrl+X Ctrl+K to stop background agents) cannot
    # be expressed in a .flux file and are left out.
    mac(CLAUDE_CODE, "Interrupt / Clear", "C", "ctrl"),
    mac(CLAUDE_CODE, "Stop Response", "Esc", ""),
    mac(CLAUDE_CODE, "Exit Session", "D", "ctrl"),
    mac(CLAUDE_CODE, "Permission Mode", "Tab", "shift"),
    # Option+P needs "Use Option as Meta Key". Option+T (next row) works without it.
    mac(CLAUDE_CODE, "Switch Model", "P", "opt"),
    mac(CLAUDE_CODE, "Extended Thinking", "T", "opt"),
    mac(CLAUDE_CODE, "Fast Mode", "O", "opt"),
    mac(CLAUDE_CODE, "Transcript Viewer", "O", "ctrl"),
    # Same chord as "Transpose Chars" in the Command line group: Ctrl+T means something
    # different inside Claude Code. Repeating a chord across groups is fine.
    mac(CLAUDE_CODE, "Task Checklist", "T", "ctrl"),
    mac(CLAUDE_CODE, "Background Task", "B", "ctrl"),
    mac(CLAUDE_CODE, "Stash Prompt", "S", "ctrl"),
    mac(CLAUDE_CODE, "External Editor", "G", "ctrl"),
    mac(CLAUDE_CODE, "Paste Image", "V", "ctrl"),
    mac(CLAUDE_CODE, "Redraw Screen", "L", "ctrl"),
    mac(CLAUDE_CODE, "Suspend", "Z", "ctrl"),
    mac(CLAUDE_CODE, "Paste Deleted Text", "Y", "ctrl"),
    # Documented as Ctrl+_ , which is Ctrl+Shift+- on a US layout.
    mac(CLAUDE_CODE, "Undo Edit", "-", "ctrl+shift"),
    mac(CLAUDE_CODE, "New Line", "Enter", "shift"),
    mac(CLAUDE_CODE, "New Line (Ctrl+J)", "J", "ctrl"),
    mac(CLAUDE_CODE, "History Previous", "P", "ctrl"),
    mac(CLAUDE_CODE, "History Next", "N", "ctrl"),
    # The next four are prefix characters typed at the start of a prompt, not chords,
    # but they are worth a label: / commands, ! shell mode, @ file mention, ? help.
    mac(CLAUDE_CODE, "Slash Command", "/", ""),
    mac(CLAUDE_CODE, "Shell Mode", "1", "shift"),
    mac(CLAUDE_CODE, "File Mention", "2", "shift"),
    mac(CLAUDE_CODE, "Shortcut Help", "/", "shift", ICON_KEYBOARD),

    # From the "Select and find text in a Terminal window" section.
    mac(SELECT, "Cut", "X", "cmd", ICON_CUT),
    mac(SELECT, "Copy No Background", "C", "ctrl+shift+cmd"),
    mac(SELECT, "Copy Plain Text", "C", "opt+shift+cmd"),
    mac(SELECT, "Paste Selection", "V", "shift+cmd"),
    mac(SELECT, "Paste Escaped", "V", "ctrl+cmd"),
    mac(SELECT, "Paste Escaped Select", "V", "ctrl+shift+cmd"),
    mac(SELECT, "Find Next", "G", "cmd"),
    mac(SELECT, "Find Previous", "G", "shift+cmd"),
    mac(SELECT, "Find Selection", "E", "cmd"),
    mac(SELECT, "Jump to Selection", "J", "cmd"),
    mac(SELECT, "Select All", "A", "cmd"),
    mac(SELECT, "Character Viewer", "Space", "ctrl+cmd"),

    # From the "Work with marks and bookmarks" section.
    mac(MARKS, "Mark", "U", "cmd"),
    mac(MARKS, "Mark as Bookmark", "U", "opt+cmd"),
    mac(MARKS, "Unmark", "U", "shift+cmd"),
    mac(MARKS, "Mark Line + Return", "Enter", "cmd"),
    mac(MARKS, "Return, No Mark", "Enter", "shift+cmd"),
    mac(MARKS, "Insert Bookmark", "M", "shift+cmd"),
    mac(MARKS, "Named Bookmark", "M", "opt+shift+cmd"),
    mac(MARKS, "Previous Mark", "Up", "cmd"),
    mac(MARKS, "Next Mark", "Down", "cmd"),
    mac(MARKS, "Previous Bookmark", "Up", "opt+cmd"),
    mac(MARKS, "Next Bookmark", "Down", "opt+cmd"),
    mac(MARKS, "Clear to Mark", "L", "cmd"),
    mac(MARKS, "Clear to Bookmark", "L", "opt+cmd"),
    mac(MARKS, "Select Between Marks", "A", "shift+cmd"),

    # From the "Other shortcuts" section.
    mac(DEFAULT, "Show/Hide Colors", "C", "shift+cmd", ICON_COLORS),
    mac(DEFAULT, "Print", "P", "cmd"),
    mac(DEFAULT, "Export Text", "S", "cmd"),
    mac(DEFAULT, "Export Selection", "S", "shift+cmd"),
    mac(DEFAULT, "Soft Reset", "R", "opt+cmd"),
    mac(DEFAULT, "Hard Reset", "R", "ctrl+opt+cmd"),
    mac(DEFAULT, "Mouse Reporting", "R", "cmd"),
    mac(DEFAULT, "Option as Meta", "O", "opt+cmd"),
    mac(DEFAULT, "Show Alt Screen", "Down", "shift+cmd"),
    mac(DEFAULT, "Hide Alt Screen", "Up", "shift+cmd"),
    # Apple lists this as Control-Shift-Command-Question Mark.
    mac(DEFAULT, "Man Page", "/", "ctrl+shift+cmd"),
    mac(DEFAULT, "Search Man Index", "/", "ctrl+opt+cmd"),
]

if __name__ == "__main__":
    build_file(sys.argv[1] if len(sys.argv) > 1 else "terminal.flux", APP, GROUPS, ROWS)
