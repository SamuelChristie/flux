"""Build freecad.flux: FreeCAD keyboard shortcuts for the Flux Keyboard.

    python tools/build_freecad.py [output.flux]

Where the bindings come from
----------------------------
They are the defaults built into FreeCAD, read from its source at tag 1.1.4:

* C++ commands declare their default in the constructor:   sAccel = "Ctrl+R";
* Python commands (Draft, Assembly) declare it as:         "Accel": "Shift+S",
* a few standard actions ask Qt for the platform key:      keySequenceToAccel(QKeySequence::Save)

The last text column of each row below names the FreeCAD command, so a binding can be
checked by searching the FreeCAD source for that name. To update this file for a newer
FreeCAD, search the source for sAccel and "Accel" and compare.

What is left out
----------------
* Multi-key sequences. Most Sketcher, Draft and view tools use them ("G, L" for Line,
  "V, F" for Fit All). A .flux shortcut is one key plus modifiers, so they cannot be
  expressed.
* Next/Previous window, whose keys differ per platform and collide on the Mac.

Writing the modifiers
---------------------
FreeCAD is a Qt application, and its source writes every shortcut the Windows way
("Ctrl+Shift+S"). The rows below keep that spelling so they can be compared with the
source. On a Mac, Qt turns Ctrl into Command and Alt into Option; qt_to_mac() applies the
same conversion here.
"""
import sys

from fluxlib import (
    ICON_COPY, ICON_CUT, ICON_HELP, ICON_INFO, ICON_MAGNIFY, ICON_MOVE, ICON_PASTE, ICON_PLAY,
    ICON_RECT_SELECT, ICON_REDO, ICON_REGION_SELECT, ICON_ROTATE_VIEW, ICON_SAVE, ICON_SAVE_AS,
    ICON_SCREEN_MODE, ICON_UNDO, ICON_ZOOM_IN, ICON_ZOOM_OUT, Row, build_file, qt_to_mac,
)

APP = "FreeCAD"

# Group names, in the order Polymath lists them. "Popular shortcuts", "Use function keys"
# and "default" are names that Polymath's own Photoshop set uses.
POPULAR = "Popular shortcuts"
VIEWS = "Navigate views"
FKEYS = "Use function keys"
SKETCHER = "Sketcher tools"
ASSEMBLY = "Assembly tools"
DEFAULT = "default"
GROUPS = [POPULAR, VIEWS, FKEYS, SKETCHER, ASSEMBLY, DEFAULT]


# Three ways to write a row. `mods` is always in FreeCAD's own (Qt, Windows-style) spelling:
# any of ctrl, shift, alt joined with "+", or "" for the key alone.
def both(group, label, key, mods, command, icon=None):
    """Same physical key on Windows and Mac; only the modifier names differ."""
    return Row(group, label, key, mac=qt_to_mac(mods), win=mods, icon=icon, source=command)


def mac_only(group, label, key, mods, command, icon=None):
    """The Mac half of a shortcut whose key differs between platforms."""
    return Row(group, label, key, mac=qt_to_mac(mods), win=None, icon=icon, source=command)


def win_only(group, label, key, mods, command, icon=None):
    """The Windows/Linux half of a shortcut whose key differs between platforms."""
    return Row(group, label, key, mac=None, win=mods, icon=icon, source=command)


#   (group, label, key, modifiers, FreeCAD command[, icon])
ROWS = [
    # Everyday actions.
    both(POPULAR, "Toggle Visibility", "Space", "", "Std_ToggleVisibility"),
    both(POPULAR, "Recompute", "R", "ctrl", "Std_Recompute"),
    both(POPULAR, "Undo", "Z", "ctrl", "Std_Undo", ICON_UNDO),
    # The standard Qt Redo key is Ctrl+Y on Windows but Cmd+Shift+Z on Mac: two physical
    # keys, so two entries.
    mac_only(POPULAR, "Redo", "Z", "ctrl+shift", "Std_Redo", ICON_REDO),
    win_only(POPULAR, "Redo", "Y", "ctrl", "Std_Redo", ICON_REDO),
    both(POPULAR, "Save", "S", "ctrl", "Std_Save", ICON_SAVE),
    # FreeCAD binds Delete on Windows/Linux and Backspace on Mac (src/Gui/Tools.h).
    mac_only(POPULAR, "Delete", "Backspace", "", "Std_Delete"),
    win_only(POPULAR, "Delete", "Delete", "", "Std_Delete"),
    both(POPULAR, "Select All", "A", "ctrl", "Std_SelectAll"),
    both(POPULAR, "Box Selection", "B", "shift", "Std_BoxSelection", ICON_RECT_SELECT),
    both(POPULAR, "Box Element Select", "E", "shift", "Std_BoxElementSelection", ICON_REGION_SELECT),
    both(POPULAR, "Box Zoom", "B", "ctrl", "Std_ViewBoxZoom", ICON_MAGNIFY),
    both(POPULAR, "Nav/Edit Mode", "Esc", "", "Std_ToggleNavigation"),
    both(POPULAR, "Properties", "Enter", "alt", "Std_Properties"),
    both(POPULAR, "Preferences", ",", "ctrl", "Std_DlgPreferences"),
    both(POPULAR, "Export", "E", "ctrl", "Std_Export"),
    both(POPULAR, "Import", "I", "ctrl+shift", "Std_Import"),

    # Standard views and view navigation. The digit keys are the top-row digits.
    both(VIEWS, "Isometric View", "0", "", "Std_ViewIsometric"),
    both(VIEWS, "Front View", "1", "", "Std_ViewFront"),
    both(VIEWS, "Top View", "2", "", "Std_ViewTop"),
    both(VIEWS, "Right View", "3", "", "Std_ViewRight"),
    both(VIEWS, "Rear View", "4", "", "Std_ViewRear"),
    both(VIEWS, "Bottom View", "5", "", "Std_ViewBottom"),
    both(VIEWS, "Left View", "6", "", "Std_ViewLeft"),
    both(VIEWS, "Home View", "Home", "", "Std_ViewHome"),
    both(VIEWS, "Rotate View Left", "Left", "shift", "Std_ViewRotateLeft", ICON_ROTATE_VIEW),
    both(VIEWS, "Rotate View Right", "Right", "shift", "Std_ViewRotateRight", ICON_ROTATE_VIEW),
    # The FreeCAD binding is "Ctrl++". On a US layout "+" is Shift+=, so the chord here
    # is Ctrl+Shift+=.
    both(VIEWS, "Zoom In", "=", "ctrl+shift", "Std_ViewZoomIn", ICON_ZOOM_IN),
    both(VIEWS, "Zoom Out", "-", "ctrl", "Std_ViewZoomOut", ICON_ZOOM_OUT),
    both(VIEWS, "Store Working View", "End", "shift", "Std_StoreWorkingView"),
    both(VIEWS, "Recall Working View", "End", "", "Std_RecallWorkingView"),
    both(VIEWS, "Freeze Display", "F", "shift", "Std_FreezeViews"),
    both(VIEWS, "Fullscreen View", "F11", "", "Std_ViewFullscreen", ICON_SCREEN_MODE),
    both(VIEWS, "Fullscreen Window", "F11", "alt", "Std_MainFullscreen"),

    # Function keys: help, tree-view rename, and the macro debugger.
    # The standard Qt Help key is F1 on Windows and Cmd+? (Cmd+Shift+/) on Mac.
    win_only(FKEYS, "Help", "F1", "", "Std_OnlineHelp", ICON_HELP),
    mac_only(FKEYS, "Help", "/", "ctrl+shift", "Std_OnlineHelp", ICON_HELP),
    both(FKEYS, "What's This?", "F1", "shift", "Std_WhatsThis", ICON_INFO),
    # F2 is set directly on the tree view rename action (src/Gui/Tree.cpp), not via sAccel.
    both(FKEYS, "Rename Object", "F2", "", "tree view rename"),
    # The standard Qt Refresh key is F5 on Windows/Linux. On Mac it is Cmd+R, the same
    # chord as Recompute above, so there is no separate Mac entry.
    win_only(FKEYS, "Recompute Document", "F5", "", "Std_Refresh"),
    both(FKEYS, "Debug Macro", "F6", "", "Std_MacroStartDebug"),
    both(FKEYS, "Stop Debugging", "F6", "shift", "Std_MacroStopDebug"),
    both(FKEYS, "Execute Macro", "F6", "ctrl", "Std_DlgMacroExecuteDirect", ICON_PLAY),
    both(FKEYS, "Toggle Breakpoint", "F9", "", "Std_ToggleBreakpoint"),
    both(FKEYS, "Step Over", "F10", "", "Std_MacroStepOver"),
    # F11 is also Fullscreen View above; Step Into only applies while debugging a macro.
    both(FKEYS, "Step Into", "F11", "", "Std_MacroStepInto"),

    # Single-key Sketcher shortcuts. They work while a sketch is open for editing.
    # Geometry tools (Line is "G, L" and so on) are multi-key sequences and are left out.
    both(SKETCHER, "Dimension", "D", "", "Sketcher_Dimension"),
    both(SKETCHER, "Horizontal Dim", "L", "", "Sketcher_ConstrainDistanceX"),
    both(SKETCHER, "Vertical Dim", "I", "", "Sketcher_ConstrainDistanceY"),
    both(SKETCHER, "Radius/Diameter Dim", "R", "", "Sketcher_CompConstrainRadDia"),
    # "C" is Coincident when the unified coincident constraint is on, which is the default.
    both(SKETCHER, "Coincident", "C", "", "Sketcher_ConstrainCoincidentUnified"),
    both(SKETCHER, "Point on Object", "O", "", "Sketcher_ConstrainPointOnObject"),
    both(SKETCHER, "Horiz/Vertical", "A", "", "Sketcher_ConstrainHorVer"),
    both(SKETCHER, "Horizontal", "H", "", "Sketcher_ConstrainHorizontal"),
    both(SKETCHER, "Vertical", "V", "", "Sketcher_ConstrainVertical"),
    both(SKETCHER, "Parallel", "P", "", "Sketcher_ConstrainParallel"),
    both(SKETCHER, "Perpendicular", "N", "", "Sketcher_ConstrainPerpendicular"),
    both(SKETCHER, "Tangent/Collinear", "T", "", "Sketcher_ConstrainTangent"),
    both(SKETCHER, "Equal", "E", "", "Sketcher_ConstrainEqual"),
    both(SKETCHER, "Symmetric", "S", "", "Sketcher_ConstrainSymmetric"),
    both(SKETCHER, "Move/Array", "W", "", "Sketcher_Translate", ICON_MOVE),

    # The Assembly workbench binds single letters to its tools.
    both(ASSEMBLY, "New Assembly", "A", "", "Assembly_CreateAssembly"),
    both(ASSEMBLY, "Insert Component", "I", "", "Assembly_InsertLink"),
    both(ASSEMBLY, "New Part", "P", "", "Assembly_InsertNewPart"),
    both(ASSEMBLY, "Solve Assembly", "Z", "", "Assembly_SolveAssembly"),
    both(ASSEMBLY, "Toggle Grounded", "G", "", "Assembly_ToggleGrounded"),
    both(ASSEMBLY, "Fixed Joint", "F", "", "Assembly_CreateJointFixed"),
    both(ASSEMBLY, "Revolute Joint", "R", "", "Assembly_CreateJointRevolute"),
    both(ASSEMBLY, "Cylindrical Joint", "C", "", "Assembly_CreateJointCylindrical"),
    both(ASSEMBLY, "Slider Joint", "S", "", "Assembly_CreateJointSlider"),
    both(ASSEMBLY, "Ball Joint", "B", "", "Assembly_CreateJointBall"),
    both(ASSEMBLY, "Distance Joint", "D", "", "Assembly_CreateJointDistance"),
    both(ASSEMBLY, "Parallel Joint", "N", "", "Assembly_CreateJointParallel"),
    both(ASSEMBLY, "Perpendicular Joint", "M", "", "Assembly_CreateJointPerpendicular"),
    both(ASSEMBLY, "Angle Joint", "X", "", "Assembly_CreateJointAngle"),
    both(ASSEMBLY, "Rack and Pinion", "Q", "", "Assembly_CreateJointRackPinion"),
    both(ASSEMBLY, "Screw Joint", "W", "", "Assembly_CreateJointScrew"),
    both(ASSEMBLY, "Gears Joint", "T", "", "Assembly_CreateJointGears"),
    both(ASSEMBLY, "Belt Joint", "L", "", "Assembly_CreateJointBelt"),
    both(ASSEMBLY, "Exploded View", "E", "", "Assembly_CreateView"),
    both(ASSEMBLY, "Bill of Materials", "O", "", "Assembly_CreateBom"),
    both(ASSEMBLY, "Simulation", "V", "", "Assembly_CreateSimulation"),

    # Everything else: files, clipboard, overlay panels, and a few workbench-specific
    # shortcuts, prefixed with the workbench name.
    both(DEFAULT, "New Document", "N", "ctrl", "Std_New"),
    both(DEFAULT, "Open", "O", "ctrl", "Std_Open"),
    both(DEFAULT, "Save As", "S", "ctrl+shift", "Std_SaveAs", ICON_SAVE_AS),
    both(DEFAULT, "Print", "P", "ctrl", "Std_Print"),
    both(DEFAULT, "Cut", "X", "ctrl", "Std_Cut", ICON_CUT),
    both(DEFAULT, "Copy", "C", "ctrl", "Std_Copy", ICON_COPY),
    both(DEFAULT, "Paste", "V", "ctrl", "Std_Paste", ICON_PASTE),
    # The standard Qt Close key is Cmd+W on Mac and Ctrl+F4 on Windows.
    mac_only(DEFAULT, "Close Window", "W", "ctrl", "Std_CloseActiveWindow"),
    win_only(DEFAULT, "Close Window", "F4", "ctrl", "Std_CloseActiveWindow"),
    both(DEFAULT, "Send to Python", "P", "ctrl+shift", "Std_SendToPythonConsole"),
    both(DEFAULT, "Overlay: Left", "Left", "ctrl", "Std_DockOverlayToggleLeft"),
    both(DEFAULT, "Overlay: Right", "Right", "ctrl", "Std_DockOverlayToggleRight"),
    both(DEFAULT, "Overlay: Top", "Up", "ctrl", "Std_DockOverlayToggleTop"),
    both(DEFAULT, "Overlay: Bottom", "Down", "ctrl", "Std_DockOverlayToggleBottom"),
    both(DEFAULT, "TechDraw: Dimension", "D", "", "TechDraw_Dimension"),
    both(DEFAULT, "TechDraw: Horiz Dim", "H", "shift", "TechDraw_HorizontalDimension"),
    both(DEFAULT, "TechDraw: Vert Dim", "V", "shift", "TechDraw_VerticalDimension"),
    both(DEFAULT, "Draft: Snap Lock", "S", "shift", "Draft_Snap_Lock"),
    both(DEFAULT, "Draft: Wireframe", "Space", "shift", "Draft_ToggleDisplayMode"),
    both(DEFAULT, "Sheet: Bold", "B", "ctrl", "Spreadsheet_StyleBold"),
    both(DEFAULT, "Sheet: Italic", "I", "ctrl", "Spreadsheet_StyleItalic"),
    both(DEFAULT, "Sheet: Underline", "U", "ctrl", "Spreadsheet_StyleUnderline"),
    both(DEFAULT, "Sheet: Set Alias", "A", "ctrl+shift", "Spreadsheet_SetAlias"),
]

if __name__ == "__main__":
    build_file(sys.argv[1] if len(sys.argv) > 1 else "freecad.flux", APP, GROUPS, ROWS)
