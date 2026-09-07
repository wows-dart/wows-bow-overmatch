API_VERSION = 'API_v1.0'
MOD_NAME = 'BowOvermatch'
LOGGER_NAME = 'ModsAPI, {}'.format(MOD_NAME)

try:
    import events, ui, utils, constants, battle
except:
    pass

from math import floor

# Must match BOWOM_COMPONENT_KEY in gui/unbound2/PnFMods/BowOvermatch.unbound
COMPONENT_ID = 'modBowOvermatch'

# An AP shell overmatches any plate thinner than calibre / 14.3.
OVERMATCH_RATIO = 14.3

# Published when the threshold cannot be determined. The unbound side treats
# overmatchMm == 0 as "render nothing".
BLANK = {'overmatchMm': 0}

DEBUG = False


def log(message):
    try:
        utils.logInfo(LOGGER_NAME, message)
    except:
        pass


class BowOvermatch(object):
    """Publishes the player's main battery overmatch threshold to the datahub.

    That is the only input the unbound side cannot get for itself. The armour table is static
    and lives in BowOvermatchTable.unbound, and the per-marker comparison happens there,
    because ship identity is only reachable from the marker entity.

    The value depends on gun calibre alone, not on the loaded shell, so in practice it is
    written once per battle and then sits still.
    """

    def __init__(self):
        self.uiID = None
        # Cached so the value survives a missing datahub component. onArtilleryAmmoChanged
        # fires during battle load, before onBattleShown creates the component, so without
        # this the first shell selection of every battle would be dropped.
        self.data = dict(BLANK)

        events.onBattleShown(self.start)
        events.onBattleQuit(self.stop)
        events.onArtilleryAmmoChanged(self.onAmmoChanged)
        events.onWeaponTypeChanged(self.onWeaponChanged)
        events.onArtilleryFireModeChanged(self.onFireModeChanged)

    # ------------------------------------------------------------------ datahub

    def _createComponent(self):
        self._deleteComponent()
        try:
            self.uiID = ui.createUiElement()
            ui.addDataComponentWithId(self.uiID, COMPONENT_ID, self.data)
        except:
            self.uiID = None
            log('failed to create the datahub component')

    def _deleteComponent(self):
        if self.uiID is None:
            return
        try:
            # Undocumented but used by PenetrationCalculator on this build.
            ui.deleteUiElement(self.uiID)
        except:
            try:
                ui.deleteComponent(self.uiID, COMPONENT_ID)
            except:
                pass
        self.uiID = None

    def _publish(self, data):
        # Cache first, so the value is correct whenever the component does get created.
        self.data = data
        if self.uiID is None:
            return
        try:
            ui.updateUiElementData(self.uiID, data)
        except:
            log('failed to publish {!r}'.format(data))

    # ------------------------------------------------------------------ maths

    def _thresholdFor(self, ammoId):
        """{'overmatchMm': int} for the gun that fires this shell, or BLANK.

        Deliberately independent of ammoType. Overmatch is a property of the gun's calibre, and
        every shell type a gun fires shares that calibre, so the indicator reports what the
        ship's main battery can do rather than what happens to be loaded. Switching to HE or
        SAP does not change the answer and must not blank the icon.

        The shell is still the route to the number: the API exposes calibre as the diameter of
        the currently selected shell, and there is no separate "what calibre are my guns" call.
        """
        if ammoId is None or ammoId == -1:
            return dict(BLANK)
        try:
            ammo = battle.getAmmoParams(ammoId)
        except:
            return dict(BLANK)
        if ammo is None:
            return dict(BLANK)
        try:
            diameterMm = ammo.bulletDiametr * 1000.0
        except:
            return dict(BLANK)
        if diameterMm <= 0:
            return dict(BLANK)
        return {'overmatchMm': int(floor(diameterMm / OVERMATCH_RATIO))}

    def _refreshFromSelection(self, reason):
        try:
            ammoId = battle.getSelectedAmmoId(constants.WeaponType.ARTILLERY)
        except:
            return
        self._update(ammoId, reason)

    def _update(self, ammoId, reason):
        data = self._thresholdFor(ammoId)
        if not data['overmatchMm'] and self.data.get('overmatchMm'):
            # A failed read must not blank a threshold we already know. Calibre cannot change
            # mid-battle, so the last good value stays valid for the rest of it.
            if DEBUG:
                log('{}: ammoId={!r} unreadable, keeping {!r}'.format(
                    reason, ammoId, self.data))
            return
        self._publish(data)
        if DEBUG:
            log('{}: ammoId={!r} -> {!r}'.format(reason, ammoId, data))

    # ------------------------------------------------------------------ events

    def start(self, *args):
        self._createComponent()
        self._refreshFromSelection('onBattleShown')

    def stop(self, *args):
        self._deleteComponent()
        self.data = dict(BLANK)

    def onAmmoChanged(self, ammoId):
        self._update(ammoId, 'onArtilleryAmmoChanged')

    def onWeaponChanged(self, weaponType):
        # Only artillery is relevant, and a switch away from it never blanks the value.
        try:
            if weaponType != constants.WeaponType.ARTILLERY:
                return
        except:
            return
        self._refreshFromSelection('onWeaponTypeChanged')

    def onFireModeChanged(self, *args):
        # Burst and alt fire modes can swap the shell, e.g. Victoria.
        self._refreshFromSelection('onArtilleryFireModeChanged')


_gBowOvermatch = BowOvermatch()
log('created an instance')
