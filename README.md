# Bow Overmatch Indicator

A World of Warships mod that answers the AP overmatch question in both directions, on the ship
markers, without you having to remember armour values.

Two icons appear on enemy ship markers:

| Icon | Meaning |
|---|---|
| **amber shell pointing out** | your main battery overmatches that ship's bow plating |
| **red shell pointing in** | that ship's main battery overmatches *your* bow plating |

Both are 18 px and sit next to each other in the marker's status-icon row, so the pair reads as
one indicator with two directions.

Neither icon depends on the shell you have loaded. Both report what a main battery *can* do, so
switching to HE or SAP changes nothing on screen. Read the amber icon as "my guns can overmatch
that bow", not "this salvo will".

## Screenshots

<!--
Replace the three images below. Suggested shots:
  1. overmatch.png  - an enemy marker showing only the amber icon
  2. threat.png     - an enemy marker showing only the red icon
  3. both.png       - a marker showing both, ideally Yamato vs Yamato
Optionally a fourth with BOWOM_DEBUG_TEXT enabled, showing the numeric readout.
-->

**You can overmatch them**

![Amber icon on an enemy marker](docs/overmatch.png)

**They can overmatch you**

![Red icon on an enemy marker](docs/threat.png)

**Both directions at once**

![Both icons on one marker](docs/both.png)

## The mechanic

An AP shell overmatches an armour plate — penetrates it regardless of impact angle, with no
chance of ricochet — when the shell's calibre is at least 14.3 times the plate's thickness. So a
gun's overmatch threshold in millimetres is:

```
floor(calibre_mm / 14.3)
```

A 460 mm Yamato gun overmatches up to 32 mm, which is exactly the bow plating of most tier 8–10
battleships. A 406 mm gun manages only 28 mm, so it does not. That single millimetre difference
decides whether bow-tanking works, and it is the thing this mod surfaces.

## What it deliberately does not do

- **No penetration, angle, normalisation or ricochet maths.** This is purely calibre versus
  plate thickness. For impact angle and penetration at range, use the `PenetrationCalculator`
  mod instead — the two coexist happily, and this one was built to complement it.
- **Bow plating only.** Not stern, deck, casemate, citadel or superstructure.
- **Main battery only.** Secondaries are ignored.
- **No destroyers or submarines.** They are never shown as targets of the amber icon, and the
  red icon is suppressed entirely while you are sailing one. See
  [Known limitations](#known-limitations) for why.
- **Spotted ships only.** The mod renders on ship markers, so it tells you nothing about ships
  you cannot see.

## Requirements

- World of Warships, PC client.
- Built and tested against **game version 15.7.0**, client build `13015811`.
- Uses only the official Wargaming Mods API (`API_v1.0`). No DLL injection, no memory reading,
  no patched game files.

## Installation

1. Find your game's mod folder. Inside your World of Warships install, go to `bin\` and pick
   the **highest-numbered** folder — that is the current client build. Inside it you want
   `res_mods\`:

   ```
   World_of_Warships\bin\13015811\res_mods\
   ```

2. Copy the **contents** of this repository's `res_mods\` into that folder, preserving the
   directory structure. You should end up with:

   ```
   res_mods\PnFMods\BowOvermatch\Main.py
   res_mods\PnFMods\BowOvermatch\icon_overmatch.png
   res_mods\PnFMods\BowOvermatch\icon_threat.png
   res_mods\gui\unbound2\PnFMods\BowOvermatch.unbound
   res_mods\gui\unbound2\PnFMods\BowOvermatchTable.unbound
   ```

3. **Restart the game client.** Mods are discovered at startup; copying files into a running
   client does nothing.

On Windows, from the repository root:

```
robocopy "res_mods" "C:\Games\World_of_Warships\bin\13015811\res_mods" /E
```

Adjust both paths for your install.

### Verifying it loaded

Open `World_of_Warships\profile\python.log` and search for `BowOvermatch`. You want:

```
ModsAPI, BowOvermatch, ('created an instance',)
```

If that line is absent, the Python half did not load and nothing else will work — check the file
landed at `res_mods\PnFMods\BowOvermatch\Main.py` exactly.

### Uninstalling

Delete `res_mods\PnFMods\BowOvermatch\` and
`res_mods\gui\unbound2\PnFMods\BowOvermatch*.unbound`, then restart the client.

Note that a new client build creates a new `bin\<build>\res_mods\` folder, so the mod needs
copying again after a game update.

## Configuration

All in `res_mods/gui/unbound2/PnFMods/BowOvermatch.unbound`, at the top of the file:

| Constant | Default | Effect |
|---|---|---|
| `BOWOM_ICON_SIZE` | `18` | displayed size of both icons, in px |
| `BOWOM_DEBUG_TEXT` | `false` | set `true` to print `<my threshold>/<their bow> v <their threshold>/<my bow>` next to every enemy marker |
| `BOWOM_RATIO` | `14.3` | the overmatch ratio, in case Wargaming ever changes it |

`BOWOM_DEBUG_TEXT` is the tool for checking the mod against a wiki value: it shows the numbers
behind both decisions, so a missing icon can always be traced to the arithmetic.

`Main.py` also has a `DEBUG` flag that logs every shell change and the published threshold to
`python.log`. With it on you will see the threshold recomputed on ammunition switches and land
on the same number every time — calibre does not change mid-battle, which is why the icons do
not either.

### Using the naval gun icon instead

`icon_threat_gun.png` is an alternative for the red icon, drawn as a side-view naval gun. It
needs roughly 26 px to read — below that the barrel and turret merge and it looks like a hammer.
To use it, point `BowOvermatchThreatIcon` at that filename and raise `BOWOM_ICON_SIZE`, keeping
in mind that constant sizes both icons.

## Compatibility

This mod **redefines the game's `EntityStatesItem`** element. That is the small element the game
instantiates on every ship marker to draw the status-icon row (heal, spotted, and so on). Only
one mod can define it. If another installed mod also defines `EntityStatesItem`, one of them
silently loses, and the symptom is a missing element rather than an error.

To check before installing, search your `res_mods` folder:

```
findstr /s /i "EntityStatesItem" "C:\Games\World_of_Warships\bin\13015811\res_mods\*.unbound"
```

Only this mod's own file should match. If something else does, you have two options: merge this
mod's `BowOvermatchItem` line into the other mod's definition, or move this mod to a different
marker element. These are all instantiated on every ship marker and take `_markerEntity`, so any
of them works as a host: `DistanceItem`, `TargetAnimationItem`, `PlayerNameItem`, `FlagshipItem`,
`RepairShipItem`, `ScenarioTagItem`, `SubmarineDepthItem`.

For reference, elements commonly claimed by other mods — do not use these as hosts:
`TargetLockItem`, `ShipNameItem`, `ShipMarkerIconItem`, `MarkerHealthBarItem`, `PriorityItem`,
`ShipMarkerBatteryBarItem`, `ShipMarkerBatteryDamageItem`.

If the mod stops working after a modpack update, this is the first thing to check.

## How it works

Four inputs, three of them live:

| Input | Source |
|---|---|
| your calibre | Python, from the selected artillery shell (`ammo.bulletDiametr`) |
| their bow armour | the static `BOW_ARMOUR` table, keyed on the marker's `nameIDS` |
| your bow armour | the same table, keyed on your own avatar's `nameIDS` |
| their calibre | live from `CC.mods_ShipParamsInBattle`, a first-party component the client provides for battle mods |

Enemy gun calibres need no table. `Mods_ShipParamsInBattle` carries a full `shipTTX` for every
ship in the battle, including `artillery.mainGun[0].caliber.value` in millimetres.

### No dependency on other mods

`Mods_ShipParamsInBattle` is a **game client component, not a mod**. It is declared in the
client's own `gui/data/Components.xml`, under the comment
`<!-- DO NOT REMOVE!!!!!! this component for battle mods -->`, and Wargaming provides it
specifically so battle mods can read ship specifications.

The collection is empty until something asks the client to fill it, which this mod does for
itself:

```
(bindcall externalCall 'inputMapping.onAction' "['createParamsForAllShipsInBattle', {}]" on='addedToStage')
```

Several other published mods use the same component and the same call — among them
`speed_indicator`, `InfoPanel`, `AdvancedTorpedoMarker`, `TTaroMinimap`, `TTaroTeamPanel` and
`autospy/battle_expert`. This mod does not rely on any of them being installed, because it
issues the call itself. Firing it more than once is harmless; the component is keyed by
`avatarId`.

Armour is the only thing that needs a table, because the client does not expose per-plate armour
anywhere. The port's technical spec panel shows only a whole-ship minimum and maximum, and the
in-port armour inspector is keyed by material id with no notion of "bow".

Both comparisons happen in the unbound layer rather than in Python. The Python `Ship` object
exposes no ship index or id — only a localised display name — so it cannot identify a ship well
enough to look one up. The marker entity can, via `avatar.ship.ref.ship.nameIDS`.

```
res_mods/
  PnFMods/BowOvermatch/
    Main.py                    publishes {overmatchMm} for your own guns
    icon_overmatch.png         amber, outgoing
    icon_threat.png            red, incoming
    icon_threat_gun.png        alternative artwork, not used by default
  gui/unbound2/PnFMods/
    BowOvermatch.unbound       the hook, both comparisons, both icons
    BowOvermatchTable.unbound  generated armour table, 844 ships
tools/
  gen_bow_armour_table.py      DataEnum.py -> BowOvermatchTable.unbound
  make_icon.py                 -> the icon PNGs
```

## Updating the armour table

`BowOvermatchTable.unbound` is generated, not hand-written. It currently holds **844 ships**:

| Bow plating | Ships | | Bow plating | Ships |
|---|---|---|---|---|
| 6 mm | 29 | | 21 mm | 9 |
| 10 mm | 28 | | 25 mm | 143 |
| 13 mm | 55 | | 26 mm | 46 |
| 16 mm | 156 | | 27 mm | 50 |
| 19 mm | 189 | | 32 mm | 139 |

To regenerate after new ships are released, edit the source armour data and run:

```
python tools/gen_bow_armour_table.py
```

The generator reads a `DataEnum.py` armour dataset and validates every ship index against the
client's own English text catalogue (`res/texts/en/LC_MESSAGES/global.mo`), which maps
`IDS_<index>` to ship name and is therefore the authority on whether an index is real and which
ship it belongs to. Paths are set at the top of the script.

Corrections live in three tables at the top of the generator — `REINDEX`, `OVERRIDE_BOW` and
`DROP` — keyed by `(line number, index as written)` so a fix cannot land on the wrong row. The
source dataset is never modified.

The generator refuses to write anything if any of these fail:

- an index is not in the client catalogue
- two rows claim the same index
- a bow value is not a positive integer
- a correction no longer matches a row, which means the source data changed underneath it
- the output is not pure ASCII

That last one matters: not one of the client's own `.unbound` files contains a single non-ASCII
byte, so ship names in the generated comments are transliterated (`Republique`, `Cordoba`,
`Zao`). A stray UTF-8 byte risks the file failing to parse, which would leave `BOW_ARMOUR`
undefined and the mod silently dead.

Ships missing from the table simply show no icon, which is the correct failure mode.

## Known limitations

- **Overmatch is not the whole story.** A shell that overmatches your bow still has to reach a
  vital part to hurt you, and a shell that does not overmatch can still penetrate at a good
  angle. Treat the icons as one input, not a verdict.
- **Neither icon checks ammunition, yours or theirs.** Both report what a main battery is
  capable of against a given bow. Overmatch itself only happens with AP, so an amber icon while
  you have HE loaded means "switch to AP and you will overmatch", not "this salvo will". This is
  deliberate: the indicator describes a ship pairing, which is stable, rather than a loadout,
  which changes every few seconds. `shipTTX.artillery.ammoAP` is available if you want to
  restrict the red icon to ships that actually carry AP.
- **Destroyers and submarines are excluded as targets, and while you sail one.** A 19 mm
  destroyer bow is overmatched by any gun of 272 mm or larger, so as targets almost every
  battleship would light the amber icon on almost every destroyer, and while sailing one almost
  every enemy would light the red icon. Both are true and neither is actionable.
- **Destroyers are *not* excluded as attackers, and at low tiers they will flag.** Eighteen
  tier 2–3 cruisers have 6 mm bow plating — St. Louis, Caledon, Kolberg, Tenryu, Bogatyr and
  similar — and 6 mm is overmatched by anything above 86 mm, which every destroyer gun in the
  game clears. So in a low-tier cruiser you will correctly see the red icon on enemy
  destroyers. That is the mechanic working, not a bug. From roughly tier 5 upward, bow plating
  is thick enough that no destroyer gun reaches it. Submarines never flag, since they have no
  main battery.
- **Bow plating is one number per ship here.** Real hulls have an icebreaker plate, upper bow
  plating and a bow deck at different thicknesses. The table uses the bow plating value, which
  is the one that matters for bow-on engagements.
- **New ships need a table row** until the table is regenerated.
- **The `createParamsForAllShipsInBattle` action is undocumented.** It is what populates the
  enemy specification data, and it is not in Wargaming's published Mods API documentation. The
  component it fills is first-party and several mods rely on the action, so it is unlikely to
  vanish quietly, but it is not a contract. If the red icon never appears, that call is the
  first suspect.

## Game client modification policy

Read this before installing, and especially before recommending the mod to anyone.

Wargaming's [mod policy](https://wargaming.net/support/en/products/wows/article/10720/)
prohibits modifications that "make otherwise unknown information available, except for those
mentioned and approved on the official portal", and separately anything that helps a player
"aim in any way that is not already available in the game".

Enemy bow armour thickness is not displayed anywhere in the standard client. That places this
mod in a grey area, and I cannot tell you which side of the line Wargaming would put it on. Two
things are worth weighing:

- Wargaming added `getBulletKrupp`, `getAmmoImpactSpeed`, `getSelfHoopRanging` and
  `getAmmoModifiers` to the official API specifically so mods can display the player's *own*
  penetration figures, and exposed no enemy armour data at all. The asymmetry is suggestive.
- The enemy calibre half of this mod uses `Mods_ShipParamsInBattle`, a component the client
  declares with the comment `<!-- DO NOT REMOVE!!!!!! this component for battle mods -->`, so
  that data is clearly intended to be available to mods.

Enforcement for prohibited mods is a three-strike ladder ending in permanent account suspension.
If you care about the answer, ask in the official Wargaming mods Discord before using this.

## Credits

- Bow armour values come from a community-maintained `DataEnum.py` armour dataset.
  <!-- TODO: add attribution and a link for the armour dataset before publishing. -->
- `PnFMods/PenetrationCalculator` was the reference for the Mods API patterns used here: the
  `mods_DataComponent` datahub watcher, the `url:` asset path form, and the shell-change event
  wiring.
- [Wargaming Mods API documentation](https://github.com/wgmods/Mods-API-Documentation).

## Licence

<!-- TODO: choose a licence before publishing. MIT is the usual choice for game mods. -->
