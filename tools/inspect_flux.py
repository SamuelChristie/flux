"""Print what is inside a .flux file.

    python tools/inspect_flux.py some.flux             summary of every section
    python tools/inspect_flux.py some.flux --keys      also list every shortcut

Works on any .flux file, including full profile exports from Polymath. Use it on a file
exported from your own Polymath to see how it spells key names and icon filenames before
adding new ones to fluxlib.KEYS.
"""
import sys

from fluxlib import read_flux


def chord(entry, platform):
    """Rebuild a readable chord such as "Shift+Cmd+K" from an entry's keyCombo flags."""
    combo, key = entry["keyCombo"], entry["shortcutKey"]
    if platform == "mac":
        if not combo["MAC_US_KEY1_CONSTANT"]:
            return "-"
        flags = [("Ctrl", "MAC_CTRL"), ("Opt", "MAC_OPT"), ("Shift", "MAC_SHIFT"), ("Cmd", "MAC_CMD"), ("Fn", "MAC_FN")]
        name = key["mac_us_key1"]
    else:
        if not combo["WIN_US_KEY1_CONSTANT"]:
            return "-"
        flags = [("Ctrl", "WIN_CTRL"), ("Alt", "WIN_ALT"), ("Shift", "WIN_SHIFT"), ("Win", "WIN_WINKEY")]
        name = key["win_us_key1"]
    return "+".join([label for label, flag in flags if combo[flag]] + [name])


def main(path, list_keys):
    document, attachments = read_flux(path)

    # Sections other than "shortcuts" are only filled in a full profile export.
    for section in ("profile", "appearance", "actuation", "icons", "keymaps", "media"):
        print(f"{section}: {len(document.get(section, []))} item(s)")
    for profile in document.get("profile", []):
        # The profile is what links a shortcut set to a program.
        print(f"  profile {profile.get('name')!r}: associatedProcess={profile.get('associatedProcess')!r}, "
              f"selectedShortcutApplication={profile.get('selectedShortcutApplication')!r}")
    print(f"attachments: {len(attachments)}")
    for name, blob in attachments:
        print(f"  {name} ({len(blob)} bytes)")

    for app in document.get("shortcuts", []):
        entries = app["shortcuts"]
        with_icons = sum("iconFilename" in e for e in entries)
        print(f"\nshortcut set {app['applicationName']!r}: {len(entries)} shortcuts, {with_icons} with icons")
        for group in app["applicationContexts"]:
            count = sum(e["applicationContext"] == group for e in entries)
            if count:
                print(f"  {group}: {count}")
        if list_keys:
            print()
            for e in entries:
                print(f"  {e['applicationContext']:20} {e['shortcutLabel']:22} "
                      f"mac: {chord(e, 'mac'):24} win: {chord(e, 'win'):24} {e.get('iconFilename', '')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], "--keys" in sys.argv[2:])
