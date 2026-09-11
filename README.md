# Bow Overmatch Indicator

A World of Warships mod that answers the AP overmatch question in both directions, on the ship
markers, without you having to remember armour values.

Three icons can appear on an enemy ship marker:

| Icon | Meaning |
|---|---|
| ![amber shell pointing out](https://github.com/wows-dart/wows-bow-overmatch/blob/master/res_mods/PnFMods/BowOvermatch/icon_overmatch.png) | your main battery overmatches that ship's bow plating |
| ![red shell pointing in](https://github.com/wows-dart/wows-bow-overmatch/blob/master/res_mods/PnFMods/BowOvermatch/icon_threat.png) | that ship's main battery overmatches *your* bow plating |
| ![**grey question mark**](https://github.com/wows-dart/wows-bow-overmatch/blob/master/res_mods/PnFMods/BowOvermatch/icon_unknown.png) | an armour value is missing, so neither answer is knowable |

All three are 18 px and sit next to each other in the marker's status-icon row, so they read as
one indicator. The question mark can appear alongside either arrow: "I overmatch them, and
whether they overmatch me is unknown" is a real state.

Neither arrow depends on the shell you have loaded. Both report what a main battery *can* do, so
switching to HE or SAP changes nothing on screen. Read the amber icon as "my guns can overmatch
that bow", not "this salvo will".

## Screenshots

<!--
Replace the images below. Suggested shots:
  1. overmatch.png  - an enemy marker showing only the amber icon
  2. threat.png     - an enemy marker showing only the red icon
  3. both.png       - a marker showing both, ideally Yamato vs Yamato
Optional extras, if you can get them: a marker showing the grey question mark, and one with
BOWOM_DEBUG_TEXT enabled showing the numeric readout.
-->

**You can overmatch them**

<img width="251" height="148" alt="image" src="https://github.com/user-attachments/assets/a43c5a98-f0e1-49fe-a640-c6bf9787c439" />


**They can overmatch you**

<img width="350" height="192" alt="image" src="https://github.com/user-attachments/assets/e82505bf-6979-4209-abde-eab06dfd6734" />


**Both directions at once**

<img width="236" height="143" alt="image" src="https://github.com/user-attachments/assets/0265a302-5d80-49eb-93fc-1c59c6fccd70" />


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
- Pure UI layer: declarative `.unbound` markup and PNG images. No Python component, no DLL
  injection, no memory reading, no patched or replaced game files.

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
   res_mods\PnFMods\BowOvermatch\icon_overmatch.png
   res_mods\PnFMods\BowOvermatch\icon_threat.png
   res_mods\PnFMods\BowOvermatch\icon_unknown.png
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

The mod has no Python component, so it writes nothing to `python.log`. Verify it visually
instead: open a training room, add an enemy battleship, and look for the icons. Setting
`BOWOM_DEBUG_TEXT` to `true` makes this quicker — it prints the numbers next to every enemy
marker whether or not an icon is showing, so you can tell "loaded and correctly silent" apart
from "not loaded".

If nothing appears at all, the likely causes are a file that did not land in the right place, or
another mod that also redefines `EntityStatesItem` — see [Compatibility](#compatibility).

### Uninstalling

Delete `res_mods\PnFMods\BowOvermatch\` and
`res_mods\gui\unbound2\PnFMods\BowOvermatch*.unbound`, then restart the client.

Note that a new client build creates a new `bin\<build>\res_mods\` folder, so the mod needs
copying again after a game update.

## Configuration

All in `res_mods/gui/unbound2/PnFMods/BowOvermatch.unbound`, at the top of the file:

| Constant | Default | Effect |
|---|---|---|
| `BOWOM_ICON_SIZE` | `18` | displayed size of all three icons, in px |
| `BOWOM_DEBUG_TEXT` | `false` | set `true` to print `<my threshold>/<their bow> v <their threshold>/<my bow>` next to every enemy marker |
| `BOWOM_RATIO` | `14.3` | the overmatch ratio, in case Wargaming ever changes it |

`BOWOM_DEBUG_TEXT` is the tool for checking the mod against a wiki value: it shows the numbers
behind both decisions, so a missing icon can always be traced to the arithmetic.

`BOWOM_RATIO` is exposed because 14.3 is a game balance constant, not a law of physics.

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

Four inputs, two live and two from a static table:

| Input | Source |
|---|---|
| your calibre | live from `CC.mods_ShipParamsInBattle`, keyed on your own avatar id |
| their calibre | live from `CC.mods_ShipParamsInBattle`, keyed on the marker's avatar id |
| your bow armour | the static `BOW_ARMOUR` table, keyed on your own avatar's `nameIDS` |
| their bow armour | the same table, keyed on the marker's `nameIDS` |

Gun calibres need no table at all, yours included. `Mods_ShipParamsInBattle` carries a full
`shipTTX` for every ship in the battle, including `artillery.mainGun[0].caliber.value` in
millimetres, keyed by avatar id. Your own avatar id comes from
`$datahub.getSingleEntity(CC.playerAvatar).avatar.id`.

Armour is the only thing that needs a table, because the client does not expose per-plate armour
anywhere. The port's technical spec panel shows only a whole-ship minimum and maximum, and the
in-port armour inspector is keyed by material id with no notion of "bow".

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

There is no Python component. An earlier version read your calibre through the Mods API
(`battle.getSelectedAmmoId` → `getAmmoParams` → `bulletDiametr`) and published it to the datahub
for the unbound layer to pick up. Once neither direction depended on the loaded shell, that was
a slower route to a number already sitting in the TTX component, so it went. `ConsumablesMonitor2`,
`SmokeMarker` and `BuildViewer` are all unbound-only mods, so this is a normal shape.

The comparisons have to happen in the unbound layer regardless: the Mods API's Python `Ship`
object exposes no ship index or id — only a localised display name — so it cannot identify a
ship well enough to look one up in the armour table. The marker entity can, via
`avatar.ship.ref.ship.nameIDS`.

```
res_mods/
  PnFMods/BowOvermatch/
    icon_overmatch.png         amber, outgoing
    icon_threat.png            red, incoming
    icon_unknown.png           grey, armour value missing
  gui/unbound2/PnFMods/
    BowOvermatch.unbound       the hook, both comparisons, the icons - all the logic
    BowOvermatchTable.unbound  armour table, 844 ships
```

## Updating the armour table

`BowOvermatchTable.unbound` holds **1100 rows**: 844 ships with a real bow plating value, and
256 placeholders awaiting one.

A row with a value of `-1` means "this ship exists, but nobody has looked its armour up yet".
The mod treats any value of zero or less as unknown, so a `-1` row renders the grey question
mark exactly as an absent row would — the point is that the gap is visible and editable in one
place instead of being invisible.

**To fill one in**, find it in the block at the end of the file and replace the `-1` with the
bow plating in millimetres:

```
	'IDS_PASB801': -1,	# South Carolina      before
	'IDS_PASB801': 16,	# South Carolina      after
```

The 256 placeholders are battleships, cruisers, carriers and auxiliary/scenario ships. Rows for
destroyers and submarines are deliberately absent: the mod never consults their armour, so
filling those in would be wasted effort.

The 844 real values break down as:

| Bow plating | Ships | | Bow plating | Ships |
|---|---|---|---|---|
| 6 mm | 29 | | 21 mm | 9 |
| 10 mm | 28 | | 25 mm | 143 |
| 13 mm | 55 | | 26 mm | 46 |
| 16 mm | 156 | | 27 mm | 50 |
| 19 mm | 189 | | 32 mm | 139 |

A ship released after this table was built will not be in it at all, not even as a `-1`, and
shows the question mark. Adding it is the same single line:

```
	'IDS_PJSB018': 32,	# Yamato
```

The key is `IDS_` followed by the ship's index — the internal identifier, not its display name.
Every ship's index is in the client's own English text catalogue at
`res/texts/en/LC_MESSAGES/global.mo`, which maps `IDS_<index>` to the ship's name and is the
authority on whether an index is real and which ship owns it. Indices look like `PJSB018` or
`PASC004`: `P`, a nation code, `S`, a type letter (`A` carrier, `B` battleship, `C` cruiser,
`D` destroyer), then three digits.

Three constraints when editing the file:

- **The value is bow plating in millimetres**, a positive integer. Zero would read as "not in
  the table" and produce a question mark.
- **One row per index.** A duplicate key silently overwrites, which is how the source dataset
  managed to hide three ships behind other ships' indices.
- **Keep the file pure ASCII.** Not one of the client's own `.unbound` files contains a single
  non-ASCII byte, which is why ship names in the comments are transliterated (`Republique`,
  `Cordoba`, `Zao`). A stray UTF-8 byte risks the file failing to parse, which would leave
  `BOW_ARMOUR` undefined and the whole mod silently dead.

Opening an issue with the ship name and its bow plating is just as welcome.

Ships with no armour value show the grey question mark rather than nothing. A silent absence
would be indistinguishable from "no, you cannot overmatch that bow", which is a different and
misleading answer. So a question mark means that ship needs a value — either a `-1` row waiting
to be filled in, or a ship too new to be in the file at all. Pull requests and issues both
welcome.

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
- **New ships need a table row** until the table is regenerated. They show the grey question
  mark in the meantime, so this is visible rather than silent.
- **The question mark covers missing armour only, not missing calibre.** A calibre of zero means
  either a ship with no main battery, which genuinely cannot overmatch anything, or a
  specification collection that has not populated yet, which resolves a moment into the battle.
  Neither deserves a question mark on every marker.
- **The `createParamsForAllShipsInBattle` action is undocumented, and both arrows depend on
  it.** It populates the ship specification data that supplies every calibre in the mod, yours
  and theirs, and it is not in Wargaming's published Mods API documentation. This is the cost of
  the mod having no Python component: there is a single point of failure where there used to be
  two independent data paths, so if that action ever stops working the whole mod goes quiet
  rather than half of it. The component it fills is first-party and at least six other mods rely
  on the same action, so it is unlikely to vanish silently, but it is not a contract. If no
  icons appear at all, that call is the first suspect.

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

- Bow armour values come from [this](https://github.com/17900Shimakaze/ArmorInfo/blob/main/PnFMods/ArmorInfo/DataEnum.py) armour dataset.
- [Wargaming Mods API documentation](https://github.com/wgmods/Mods-API-Documentation).

