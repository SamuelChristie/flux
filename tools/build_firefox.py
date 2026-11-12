"""Build firefox.flux: Firefox and Firefox DevTools shortcuts for the Flux Keyboard.

    python tools/build_firefox.py [output.flux]

Where the bindings come from
----------------------------
Three sources, in order of authority. They were read in November 2026 from the `beta`
branch of https://github.com/mozilla-firefox/firefox, which was at version 161.0b3.

1. Firefox's own key definitions:
       browser/base/content/browser-sets.inc.xhtml      which modifiers, per platform
       browser/locales/en-US/browser/browserSets.ftl    which letter
   Rows from here carry the <key> element's id (for example "key_newNavigatorTab").

2. The DevTools key definitions, for the shortcuts that open a tool:
       devtools/startup/DevToolsStartup.sys.mjs
       devtools/startup/locales/en-US/key-shortcuts.ftl
   Rows from here are marked "devtools:<id>".

3. Documentation, for shortcuts that are handled in code and have no <key> element:
       "sumo"  = support.mozilla.org "Keyboard shortcuts - Perform common Firefox tasks quickly"
       "docs"  = devtools/docs/user/keyboard_shortcuts/index.md  (shortcuts inside the toolbox)

Where the documentation and the source disagree, the source wins. Two examples in 161:
Add-ons is Cmd+Shift+E on Mac and Ctrl+Shift+F elsewhere (the support page still says A,
which is now Search Tabs), and the Browser Console is Cmd+Shift+J on Mac, not Cmd+Opt+J.

To update for another Firefox version, re-read the files above on the matching branch
(`release`, `beta` or `main`) and compare.

Writing the modifiers
---------------------
The rows use Firefox's own modifier names so they can be compared with the source:

    accel     Command on Mac, Ctrl on Windows and Linux
    control   the physical Control key on every platform
    alt       Option on Mac, Alt elsewhere
    shift     Shift

fx() gives a shortcut the same key on both platforms. mac() and win() are for the cases
where the source has a platform-specific definition. "win" here means Windows; Linux
mostly matches it but has a few differences of its own that are not covered.

What is left out
----------------
Mouse actions, plain typing keys (arrows, Space, Tab), media-player keys, and shortcuts
that only apply while a particular field has focus, apart from a few address-bar ones.
"""
import sys

from fluxlib import (
    ICON_COPY, ICON_CUT, ICON_INFO, ICON_MAGNIFY, ICON_PASTE, ICON_REDO, ICON_SAVE,
    ICON_SCREEN_MODE, ICON_UNDO, ICON_ZOOM_IN, ICON_ZOOM_OUT, Row, build_file,
)

APP = "Firefox"

# Group names, in the order Polymath lists them.
POPULAR = "Popular shortcuts"
NAVIGATION = "Navigation"
TABS = "Tabs and windows"
EDIT = "Find and edit"
BOOKMARKS = "Bookmarks and history"
VIEW = "View and tools"
DEVTOOLS = "Developer tools"
TOOLBOX = "DevTools toolbox"
PDF = "PDF viewer"
DEFAULT = "default"
GROUPS = [POPULAR, NAVIGATION, TABS, EDIT, BOOKMARKS, VIEW, DEVTOOLS, TOOLBOX, PDF, DEFAULT]

# Firefox modifier name -> fluxlib modifier name, per platform.
_TO_MAC = {"accel": "cmd", "control": "ctrl", "alt": "opt", "shift": "shift"}
_TO_WIN = {"accel": "ctrl", "control": "ctrl", "alt": "alt", "shift": "shift"}


def _convert(mods, table):
    # dict.fromkeys drops the duplicate when accel and control both become ctrl on Windows.
    return "+".join(dict.fromkeys(table[m] for m in mods.split("+") if m))


def fx(group, label, key, mods, source, icon=None):
    """Same key and the same Firefox modifiers on Mac and Windows."""
    return Row(group, label, key, mac=_convert(mods, _TO_MAC), win=_convert(mods, _TO_WIN),
               icon=icon, source=source)


def mac(group, label, key, mods, source, icon=None):
    """A binding the source defines for macOS only."""
    return Row(group, label, key, mac=_convert(mods, _TO_MAC), win=None, icon=icon, source=source)


def win(group, label, key, mods, source, icon=None):
    """A binding the source defines for Windows (and usually Linux) only."""
    return Row(group, label, key, mac=None, win=_convert(mods, _TO_WIN), icon=icon, source=source)


def dev(group, label, key, source):
    """A DevTools "open this tool" shortcut: Cmd+Opt+key on Mac, Ctrl+Shift+key elsewhere."""
    return Row(group, label, key, mac="cmd+opt", win="ctrl+shift", source=source)


#   (group, label, key, Firefox modifiers, source[, icon])
ROWS = [
    # The ones used all day. Each action appears once in the file, so these are not
    # repeated in the groups below.
    fx(POPULAR, "New Tab", "T", "accel", "key_newNavigatorTab"),
    fx(POPULAR, "Close Tab", "W", "accel", "key_close"),
    fx(POPULAR, "Reopen Closed Tab", "T", "accel+shift", "key_restoreLastClosedTabOrWindowOrSession"),
    fx(POPULAR, "New Window", "N", "accel", "key_newNavigator"),
    fx(POPULAR, "New Private Window", "P", "accel+shift", "key_privatebrowsing"),
    fx(POPULAR, "Address Bar", "L", "accel", "focusURLBar"),
    fx(POPULAR, "Web Search", "K", "accel", "key_search"),
    fx(POPULAR, "Find in Page", "F", "accel", "key_find", ICON_MAGNIFY),
    fx(POPULAR, "Reload", "R", "accel", "key_reload"),
    # Back and Forward are Cmd+arrow on Mac but Alt+arrow elsewhere.
    mac(POPULAR, "Back", "Left", "accel", "goBackKb"),
    win(POPULAR, "Back", "Left", "alt", "goBackKb"),
    mac(POPULAR, "Forward", "Right", "accel", "goForwardKb"),
    win(POPULAR, "Forward", "Right", "alt", "goForwardKb"),
    fx(POPULAR, "Bookmark Page", "D", "accel", "addBookmarkAsKb"),
    fx(POPULAR, "Downloads", "J", "accel", "key_openDownloads"),
    # The source binds both "+" and "=" to Zoom In, so the = key works without Shift.
    fx(POPULAR, "Zoom In", "=", "accel", "key_fullZoomEnlarge", ICON_ZOOM_IN),
    fx(POPULAR, "Zoom Out", "-", "accel", "key_fullZoomReduce", ICON_ZOOM_OUT),
    fx(POPULAR, "Zoom Reset", "0", "accel", "key_fullZoomReset"),

    # Moving around pages and the address bar.
    # The bracket keys are defined under XP_UNIX, which covers macOS and Linux but not Windows.
    mac(NAVIGATION, "Back", "[", "accel", "goBackKb2"),
    mac(NAVIGATION, "Forward", "]", "accel", "goForwardKb2"),
    fx(NAVIGATION, "Home Page", "Home", "alt", "goHome"),
    fx(NAVIGATION, "Reload", "F5", "", "key_reload2"),
    fx(NAVIGATION, "Hard Reload", "R", "accel+shift", "key_reload_skip_cache"),
    win(NAVIGATION, "Hard Reload", "F5", "accel", "key_reload_skip_cache2"),
    fx(NAVIGATION, "Stop", "Esc", "", "key_stop"),
    mac(NAVIGATION, "Stop", ".", "accel", "key_stop_mac"),
    fx(NAVIGATION, "Top of Page", "Up", "accel", "sumo"),
    fx(NAVIGATION, "Bottom of Page", "Down", "accel", "sumo"),
    fx(NAVIGATION, "Next Pane", "F6", "", "sumo"),
    fx(NAVIGATION, "Previous Pane", "F6", "shift", "sumo"),
    fx(NAVIGATION, "Caret Browsing", "F7", "", "sumo"),
    win(NAVIGATION, "Address Bar", "D", "alt", "focusURLBar2"),
    # The second search-focus key is Cmd+Opt+F on Mac and Ctrl+E on Windows.
    mac(NAVIGATION, "Web Search", "F", "accel+alt", "key_search2"),
    win(NAVIGATION, "Web Search", "E", "accel", "key_search2"),
    # These two act on what is typed in the address bar.
    fx(NAVIGATION, "Open in New Tab", "Enter", "alt", "sumo"),
    fx(NAVIGATION, "Complete .com", "Enter", "accel", "sumo"),

    # Tabs and windows. Tab switching is handled in code, so most of these are from the
    # support page.
    fx(TABS, "Next Tab", "Tab", "control", "sumo"),
    # With "Ctrl+Tab cycles through tabs in recently used order" turned on in Settings,
    # Ctrl+Shift+Tab shows all tabs instead (key_showAllTabs).
    fx(TABS, "Previous Tab", "Tab", "control+shift", "sumo"),
    fx(TABS, "Next Tab", "PageDown", "control", "sumo"),
    fx(TABS, "Previous Tab", "PageUp", "control", "sumo"),
    mac(TABS, "Next Tab", "Right", "accel+alt", "sumo"),
    mac(TABS, "Previous Tab", "Left", "accel+alt", "sumo"),
    win(TABS, "Move Tab Left", "PageUp", "control+shift", "sumo"),
    win(TABS, "Move Tab Right", "PageDown", "control+shift", "sumo"),
    fx(TABS, "Move Tab to Start", "Home", "accel+shift", "sumo"),
    fx(TABS, "Move Tab to End", "End", "accel+shift", "sumo"),
    fx(TABS, "Search Tabs", "A", "accel+shift", "key_searchTabs"),
    fx(TABS, "Mute Tab", "M", "control", "key_toggleMute"),
    fx(TABS, "Close Window", "W", "accel+shift", "key_closeWindow"),
    fx(TABS, "Reopen Window", "N", "accel+shift", "key_undoCloseWindow"),
    mac(TABS, "Minimize", "M", "accel", "key_minimizeWindow"),
    mac(TABS, "Quit", "Q", "accel", "key_quitApplication"),
    win(TABS, "Quit", "Q", "accel+shift", "key_quitApplication"),

    # Find bar and text editing.
    fx(EDIT, "Find Next", "G", "accel", "key_findAgain"),
    fx(EDIT, "Find Previous", "G", "accel+shift", "key_findPrevious"),
    fx(EDIT, "Find Next", "F3", "", "key_findAgain2"),
    fx(EDIT, "Find Previous", "F3", "shift", "key_findPrevious2"),
    mac(EDIT, "Find Selection", "E", "accel", "key_findSelection"),
    fx(EDIT, "Undo", "Z", "accel", "key_undo", ICON_UNDO),
    # Redo is Cmd+Shift+Z on Mac (and Linux) but Ctrl+Y on Windows.
    mac(EDIT, "Redo", "Z", "accel+shift", "key_redo", ICON_REDO),
    win(EDIT, "Redo", "Y", "accel", "key_redo", ICON_REDO),
    fx(EDIT, "Cut", "X", "accel", "key_cut", ICON_CUT),
    fx(EDIT, "Copy", "C", "accel", "key_copy", ICON_COPY),
    fx(EDIT, "Paste", "V", "accel", "key_paste", ICON_PASTE),
    fx(EDIT, "Paste as Plain Text", "V", "accel+shift", "sumo"),
    fx(EDIT, "Select All", "A", "accel", "key_selectAll"),

    # Bookmarks and history. The history keys differ by platform.
    fx(BOOKMARKS, "Bookmark All Tabs", "D", "accel+shift", "bookmarkAllTabsKb"),
    fx(BOOKMARKS, "Bookmarks Sidebar", "B", "accel", "viewBookmarksSidebarKb"),
    fx(BOOKMARKS, "Bookmarks Toolbar", "B", "accel+shift", "viewBookmarksToolbarKb"),
    fx(BOOKMARKS, "Show All Bookmarks", "O", "accel+shift", "manBookmarkKb"),
    mac(BOOKMARKS, "History Sidebar", "H", "accel+shift", "key_gotoHistory"),
    win(BOOKMARKS, "History Sidebar", "H", "accel", "key_gotoHistory"),
    mac(BOOKMARKS, "Show All History", "Y", "accel", "showAllHistoryKb"),
    win(BOOKMARKS, "Show All History", "H", "accel+shift", "showAllHistoryKb"),
    # Mac keyboards usually have no forward Delete key, so the source adds a Backspace form.
    mac(BOOKMARKS, "Clear History", "Backspace", "accel+shift", "key_sanitize_mac"),
    win(BOOKMARKS, "Clear History", "Delete", "accel+shift", "key_sanitize"),

    # View options, sidebars, and page tools.
    mac(VIEW, "Full Screen", "F", "accel+control", "key_enterFullScreen", ICON_SCREEN_MODE),
    win(VIEW, "Full Screen", "F11", "", "key_enterFullScreen", ICON_SCREEN_MODE),
    mac(VIEW, "Reader View", "R", "accel+alt", "key_toggleReaderMode"),
    win(VIEW, "Reader View", "F9", "", "key_toggleReaderMode"),
    mac(VIEW, "Picture-in-Picture", "]", "accel+alt+shift", "key_togglePictureInPicture"),
    win(VIEW, "Picture-in-Picture", "]", "accel+shift", "key_togglePictureInPicture"),
    # The sidebar keys use the physical Control key on Mac and Ctrl+Alt elsewhere.
    mac(VIEW, "Toggle Sidebar", "Z", "control", "toggleSidebarKb"),
    win(VIEW, "Toggle Sidebar", "Z", "control+alt", "toggleSidebarKb"),
    mac(VIEW, "AI Chatbot", "X", "control", "viewGenaiChatSidebarKb"),
    win(VIEW, "AI Chatbot", "X", "accel+alt", "viewGenaiChatSidebarKb"),
    fx(VIEW, "Screenshot", "S", "accel+shift", "key_screenshot"),
    fx(VIEW, "Page Source", "U", "accel", "key_viewSource"),
    fx(VIEW, "Page Info", "I", "accel", "key_viewInfo", ICON_INFO),
    fx(VIEW, "Task Manager", "Esc", "shift", "key_aboutProcesses"),
    # In 161 the Add-ons key is E on Mac and F elsewhere; Shift+A is now Search Tabs.
    mac(VIEW, "Add-ons", "E", "accel+shift", "key_openAddons"),
    win(VIEW, "Add-ons", "F", "accel+shift", "key_openAddons"),
    fx(VIEW, "Print", "P", "accel", "printKb"),
    fx(VIEW, "Save Page", "S", "accel", "key_savePage", ICON_SAVE),
    fx(VIEW, "Open File", "O", "accel", "openFileKb"),
    mac(VIEW, "Settings", ",", "accel", "key_preferencesCmdMac"),
    fx(VIEW, "Text Direction", "X", "accel+shift", "key_switchTextDirection"),

    # Opening the developer tools. These work from the main browser window.
    dev(DEVTOOLS, "Toggle Tools", "I", "devtools:toggleToolbox"),
    fx(DEVTOOLS, "Toggle Tools", "F12", "", "devtools:toggleToolboxF12"),
    dev(DEVTOOLS, "Inspector", "C", "devtools:inspector"),
    # Mac also accepts Cmd+Shift+C for the Inspector.
    mac(DEVTOOLS, "Inspector", "C", "accel+shift", "devtools:inspectorMac"),
    dev(DEVTOOLS, "Web Console", "K", "devtools:webconsole"),
    dev(DEVTOOLS, "Debugger", "Z", "devtools:jsdebugger"),
    dev(DEVTOOLS, "Network", "E", "devtools:netmonitor"),
    dev(DEVTOOLS, "Responsive Design", "M", "devtools:responsiveDesignMode"),
    dev(DEVTOOLS, "DOM", "W", "devtools:dom"),
    fx(DEVTOOLS, "Style Editor", "F7", "shift", "devtools:styleeditor"),
    fx(DEVTOOLS, "Profiler", "F5", "shift", "devtools:performance"),
    fx(DEVTOOLS, "Storage", "F9", "shift", "devtools:storage"),
    fx(DEVTOOLS, "Accessibility", "F12", "shift", "devtools:accessibility"),
    fx(DEVTOOLS, "Browser Console", "J", "accel+shift", "devtools:browserConsole"),
    fx(DEVTOOLS, "Browser Toolbox", "I", "accel+alt+shift", "devtools:browserToolbox"),
    fx(DEVTOOLS, "Start/Stop Profiler", "1", "control+shift", "devtools:profilerStartStop"),
    fx(DEVTOOLS, "Capture Profile", "2", "control+shift", "devtools:profilerCapture"),
    fx(DEVTOOLS, "JS Tracing", "5", "control+shift", "devtools:javascriptTracingToggle"),

    # Inside the toolbox once it is open, including the Debugger's stepping keys. Several of
    # these reuse a browser chord (Cmd+[ is Back in a page but Previous Tool in the toolbox).
    fx(TOOLBOX, "Next Tool", "]", "accel", "docs"),
    fx(TOOLBOX, "Previous Tool", "[", "accel", "docs"),
    fx(TOOLBOX, "Toolbox Settings", "F1", "", "docs"),
    fx(TOOLBOX, "Toggle Docking", "D", "accel+shift", "docs"),
    fx(TOOLBOX, "Split Console", "Esc", "", "docs"),
    fx(TOOLBOX, "Resume", "F8", "", "docs"),
    fx(TOOLBOX, "Step Over", "F10", "", "docs"),
    fx(TOOLBOX, "Step In", "F11", "", "docs"),
    fx(TOOLBOX, "Step Out", "F11", "shift", "docs"),
    fx(TOOLBOX, "Find File", "P", "accel", "docs"),
    fx(TOOLBOX, "Search All Files", "F", "accel+shift", "docs"),
    fx(TOOLBOX, "Toggle Breakpoint", "B", "accel", "docs"),
    fx(TOOLBOX, "Cond. Breakpoint", "B", "accel+shift", "docs"),
    # Clear the Web Console: Ctrl+L on Mac (physical Control), Ctrl+Shift+L elsewhere.
    mac(TOOLBOX, "Clear Console", "L", "control", "docs"),
    win(TOOLBOX, "Clear Console", "L", "accel+shift", "docs"),

    # The built-in PDF viewer. The single letters only apply while a PDF has focus.
    fx(PDF, "Next Page", "N", "", "sumo"),
    fx(PDF, "Previous Page", "P", "", "sumo"),
    fx(PDF, "Rotate Clockwise", "R", "", "sumo"),
    fx(PDF, "Rotate Counterclock", "R", "shift", "sumo"),
    fx(PDF, "Text Selection Tool", "S", "", "sumo"),
    fx(PDF, "Hand Tool", "H", "", "sumo"),
    fx(PDF, "Presentation Mode", "P", "accel+alt", "sumo"),
    fx(PDF, "Go to Page Number", "G", "accel+alt", "sumo"),

    # Jump straight to a tab by position; 9 always goes to the last tab.
    *[fx(DEFAULT, f"Tab {digit}", digit, "accel", f"key_selectTab{digit}") for digit in "12345678"],
    fx(DEFAULT, "Last Tab", "9", "accel", "key_selectLastTab"),
]

if __name__ == "__main__":
    build_file(sys.argv[1] if len(sys.argv) > 1 else "firefox.flux", APP, GROUPS, ROWS)
