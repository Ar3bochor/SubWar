from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math
import random
import sys
import time


# ============================================================
# Game settings and fixed data
# ============================================================

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 820
screen_width, screen_height = WINDOW_WIDTH, WINDOW_HEIGHT
viewport = (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

WORLD_HALF_SIZE = 720.0
SURFACE_LIMIT = 15.0
SAFE_DEPTH = 275.0
WORLD_BOTTOM = 360.0

FOV_Y = 72.0
PLAYER_RADIUS = 30.0
PLAYER_MAX_SPEED = 150.0
PLAYER_TURN_STEP = 7.0
PLAYER_DEPTH_STEP = 16.0

CAMERA_DISTANCE = 270.0
TOP_CAMERA_HEIGHT = 980.0

SONAR_MAX_RADIUS = 510.0
SONAR_SPEED = 390.0
SONAR_COOLDOWN = 6.5

STARTING_AMMO = {"STANDARD": 24, "HOMING": 10, "EMP": 6}
WEAPON_ORDER = ("STANDARD", "HOMING", "EMP")
WEAPON_STATS = {
    "STANDARD": {"damage": 58.0, "speed": 325.0, "color": (1.0, 0.78, 0.12)},
    "HOMING": {"damage": 44.0, "speed": 285.0, "color": (0.25, 1.0, 0.68)},
    "EMP": {"damage": 22.0, "speed": 255.0, "color": (0.55, 0.65, 1.0)},
}
UPGRADE_BASE_COST = 700
PLAYER_FIRE_COOLDOWN = 0.42
THROTTLE_LEVELS = (-0.35, 0.0, 0.25, 0.50, 0.75, 1.0)
MISSION_GOALS = (3, 3, 4, 5, 4, 4, 1, 1)

CONSOLE = "CONSOLE"
BRIEFING = "BRIEFING"
PLAYING = "PLAYING"
PAUSED = "PAUSED"
MISSION_COMPLETE = "MISSION_COMPLETE"
GAME_OVER = "GAME_OVER"
VICTORY = "VICTORY"

COLOR_PRESETS = (
    {"name": "ARCTIC TEAL", "body": (0.08, 0.46, 0.56), "dark": (0.025, 0.14, 0.20), "accent": (0.28, 0.95, 0.96), "hud": (0.20, 0.90, 1.0)},
    {"name": "CRIMSON TIDE", "body": (0.58, 0.09, 0.12), "dark": (0.20, 0.025, 0.035), "accent": (1.0, 0.42, 0.22), "hud": (1.0, 0.52, 0.32)},
    {"name": "GOLDEN TRIDENT", "body": (0.62, 0.43, 0.08), "dark": (0.22, 0.13, 0.025), "accent": (1.0, 0.86, 0.25), "hud": (1.0, 0.80, 0.22)},
    {"name": "PHANTOM", "body": (0.20, 0.23, 0.31), "dark": (0.035, 0.04, 0.07), "accent": (0.58, 0.72, 1.0), "hud": (0.52, 0.68, 1.0)},
    {"name": "CORAL RESCUE", "body": (0.82, 0.25, 0.16), "dark": (0.28, 0.055, 0.035), "accent": (1.0, 0.74, 0.40), "hud": (1.0, 0.62, 0.36)},
    {"name": "EMERALD CURRENT", "body": (0.08, 0.46, 0.30), "dark": (0.02, 0.16, 0.10), "accent": (0.32, 1.0, 0.60), "hud": (0.25, 1.0, 0.55)},
    {"name": "ROYAL ABYSS", "body": (0.38, 0.12, 0.56), "dark": (0.12, 0.025, 0.20), "accent": (0.86, 0.45, 1.0), "hud": (0.80, 0.48, 1.0)},
)

CALLSIGNS = ("NEREID-7", "TRIDENT-1", "BLUE GHOST", "KRAKEN-9", "NIGHT DIVER", "SEA LANCE")

DIFFICULTIES = (
    {"name": "CADET", "enemy_health": 0.82, "enemy_speed": 0.88, "enemy_damage": 0.72, "score": 0.8, "description": "Forgiving hull damage and lighter opposition"},
    {"name": "OFFICER", "enemy_health": 1.0, "enemy_speed": 1.0, "enemy_damage": 1.0, "score": 1.0, "description": "Balanced campaign and standard scoring"},
    {"name": "ADMIRAL", "enemy_health": 1.28, "enemy_speed": 1.16, "enemy_damage": 1.30, "score": 1.5, "description": "Aggressive fleets and elite score multiplier"},
)

MISSIONS = (
    {"code": "OP-01", "title": "THE DESCENT", "briefing": "Calibrate navigation by passing three abyssal gates in sequence.", "objective": "Pass the active navigation gates: {progress}/3", "reward": "Navigation computer calibrated"},
    {"code": "OP-02", "title": "GHOST CARGO", "briefing": "Recover three encrypted data pods from the wreck of research ship Calypso.", "objective": "Recover encrypted data pods: {progress}/3", "reward": "+4 standard torpedoes"},
    {"code": "OP-03", "title": "SILENT ECHOES", "briefing": "Use active sonar to classify four hidden hostile contacts.", "objective": "Classify sonar contacts: {progress}/4", "reward": "+2 homing torpedoes"},
    {"code": "OP-04", "title": "MINEBREAKER", "briefing": "Clear five naval mines. EMP torpedoes disarm them without a blast wave.", "objective": "Neutralize naval mines: {progress}/5", "reward": "Hull repaired by 20 points"},
    {"code": "OP-05", "title": "GUARDIAN CURRENT", "briefing": "Escort the research bathyscaphe Atlas through hostile water.", "objective": "Escort Atlas to waypoint: {progress}/4", "reward": "+3 decoys and full sonar recharge"},
    {"code": "OP-06", "title": "BREAK THE FORTRESS", "briefing": "Destroy three shield relays, then demolish the abyssal fortress core.", "objective": "Destroy shield relays and fortress: {progress}/4", "reward": "All weapon magazines replenished"},
    {"code": "OP-07", "title": "OPERATION LEVIATHAN", "briefing": "Hunt the command submarine Leviathan. Expect phase changes and reinforcements.", "objective": "Destroy Leviathan: {progress}/1", "reward": "Enemy command network disabled"},
    {"code": "OP-08", "title": "LAST LIGHT", "briefing": "Escape the collapsing sector and reach the extraction beacon.", "objective": "Reach extraction beacon: {progress}/1", "reward": "Campaign complete"},
)

ROCK_LAYOUT = (
    (-285.0, 105.0, 55.0, 58.0, 118.0, (1.0, 1.2, 1.45)),
    (175.0, 150.0, 235.0, 55.0, 138.0, (1.35, 0.9, 1.7)),
    (-45.0, 205.0, -310.0, 72.0, 105.0, (1.5, 1.0, 1.12)),
    (335.0, 100.0, 78.0, 50.0, 120.0, (0.9, 1.3, 1.55)),
    (-485.0, 190.0, -255.0, 60.0, 132.0, (1.12, 1.0, 1.72)),
    (60.0, 75.0, 470.0, 50.0, 88.0, (1.0, 1.2, 1.15)),
    (540.0, 255.0, 325.0, 67.0, 118.0, (1.4, 0.82, 1.5)),
    (-560.0, 120.0, 510.0, 47.0, 90.0, (0.9, 1.1, 1.25)),
    (480.0, 175.0, -560.0, 55.0, 115.0, (1.2, 0.85, 1.6)),
    (-160.0, 265.0, 560.0, 44.0, 72.0, (1.0, 1.25, 1.0)),
    (580.0, 95.0, -120.0, 42.0, 100.0, (0.85, 1.3, 1.4)),
)
GATE_LAYOUT = ((-135.0, 90.0, 185.0), (-350.0, 145.0, 365.0), (-555.0, 195.0, 530.0))
POD_LAYOUT = ((-430.0, 195.0, -365.0), (-70.0, 245.0, -520.0), (285.0, 135.0, -410.0))
MINE_LAYOUT = ((-510.0, 90.0, 325.0), (-335.0, 155.0, 390.0), (-135.0, 215.0, 450.0), (95.0, 130.0, 390.0), (300.0, 225.0, 470.0), (485.0, 170.0, 350.0), (560.0, 255.0, 115.0))
ESCORT_ROUTE = ((-475.0, 110.0, -475.0), (-260.0, 145.0, -270.0), (40.0, 190.0, -90.0), (335.0, 145.0, 125.0), (555.0, 100.0, 390.0))
FORTRESS_POSITION = (455.0, 225.0, -470.0)
FORTRESS_NODES = ((330.0, 185.0, -500.0), (515.0, 130.0, -350.0), (575.0, 255.0, -555.0))
EXTRACTION_POSITION = (-585.0, 75.0, 565.0)

BACKGROUND_COLOR = (0.008, 0.032, 0.070)
TEXT_COLOR = (0.78, 0.94, 1.0)
MUTED_TEXT = (0.48, 0.70, 0.78)
GREEN = (0.20, 1.0, 0.42)
RED = (1.0, 0.16, 0.10)
AMBER = (1.0, 0.76, 0.18)
ENEMY_BODY = (0.58, 0.10, 0.09)
ENEMY_DARK = (0.19, 0.025, 0.025)
BOSS_BODY = (0.50, 0.045, 0.42)

# Fixed-width bitmap fonts give the interface a compact naval-console style.
UI_FONT = GLUT_BITMAP_9_BY_15
COMPACT_UI_FONT = GLUT_BITMAP_8_BY_13

# World walls remain faintly visible while allowing scenery beyond them to show.
BOUNDARY_ALPHA = 0.14


# ============================================================
# Global game state
# ============================================================

profile = {"color_index": 0, "difficulty_index": 1, "callsign_index": 0, "cursor": 0}
player = {}
state = CONSOLE
console_return_state = None
camera_mode = 1
camera_height = 185.0
camera_orbit = 0.0
show_help = False
help_return_state = None
restart_return_state = None
held_keys = set()
pressed_keys = set()
mouse_dragging = False
mouse_ui = (-1.0, -1.0)
overlay_layer = 0
mesh_cache = {}
fish = []
fire_cooldown = 0.0
aim_ui = None

MISSION_TIPS = (
    "W sets forward throttle. Hold A/D to turn and Q/E to match the gate depth.",
    "Follow the cyan waypoint. Move within 42m of each pod to recover it.",
    "Press R to scan. Move closer to hidden contacts, then scan again.",
    "Press T to select EMP. Match mine depth, aim, then fire with SPACE.",
    "Stay within 260m of Atlas. Use sonar to reveal the approaching raiders.",
    "Destroy the three relays first. The fortress core is shielded until then.",
    "Use homing torpedoes on Leviathan. F deploys a decoy against incoming fire.",
    "Follow the extraction waypoint. Use V for stealth and F to evade pursuit.",
)

scene_time = 0.0
last_update_time = time.perf_counter()
mouse_last_x = None
mouse_last_y = None

ammo = dict(STARTING_AMMO)
weapon = "STANDARD"
weapon_levels = {name: 0 for name in WEAPON_ORDER}
decoy_count = 5
score = 0
total_kills = 0
shots_fired = 0
shots_hit = 0
damage_taken = 0.0
mines_disarmed = 0
missions_completed = 0
achievements = []

mission_index = 0
mission_progress = 0
mission_elapsed = 0.0
total_elapsed = 0.0
status_message = "Configure your vessel, then deploy."
status_timer = 999.0

sonar_active = False
sonar_radius = 0.0
sonar_cooldown = 0.0
sonar_overlay_timer = 0.0
sonar_contacts = set()

rocks = []
bubbles = []
kelp = []
enemies = []
torpedoes = []
mines = []
collectibles = []
gates = []
explosions = []
decoys = []
escort = None
fortress = None
extraction = None
quadric = None


# ============================================================
# Small helper functions
# ============================================================

def clamp(value, minimum, maximum):
    """Keep a numeric value within the inclusive minimum and maximum limits."""
    return max(minimum, min(maximum, value))


def distance_3d(x1, depth1, z1, x2, depth2, z2):
    """Return the Euclidean distance between two positions in game coordinates."""
    dx = x2 - x1
    dy = depth2 - depth1
    dz = z2 - z1
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def normalize_3d(dx, dy, dz):
    """Convert a 3D direction to unit length, safely handling a zero vector."""
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0.00001:
        return 0.0, 0.0, 0.0
    return dx / length, dy / length, dz / length


def heading_vector(angle):
    """Convert a heading in degrees into a horizontal movement vector."""
    # 0 degrees points toward +z.
    radians = math.radians(angle)
    return math.sin(radians), math.cos(radians)


def angle_to_target(source_x, source_z, target_x, target_z):
    """Calculate the compass heading from a source point to a target point."""
    return math.degrees(math.atan2(target_x - source_x, target_z - source_z))


def approach_angle(current, target, maximum_step):
    """Turn an angle toward a target without exceeding the requested step."""
    difference = (target - current + 180.0) % 360.0 - 180.0
    difference = clamp(difference, -maximum_step, maximum_step)
    return (current + difference) % 360.0


def world_to_render(x, depth, z):
    """Translate game depth coordinates into OpenGL's vertical-axis convention."""
    return x, z, -depth


def current_palette():
    """Return the color preset selected in the vessel configuration."""
    return COLOR_PRESETS[profile["color_index"]]


def current_difficulty():
    """Return the currently selected difficulty settings."""
    return DIFFICULTIES[profile["difficulty_index"]]


def current_callsign():
    """Return the callsign selected for the player vessel."""
    return CALLSIGNS[profile["callsign_index"]]



def mission_data():
    """Return the definition of the active campaign mission."""
    return MISSIONS[mission_index]


def objective_text():
    """Format the active mission objective with its current progress."""
    return mission_data()["objective"].format(progress=mission_progress)


def score_value(base):
    """Apply the selected difficulty multiplier to a base score reward."""
    return int(base * current_difficulty()["score"])


def inside_world(x, depth, z, margin=0.0):
    """Check whether a position lies inside the playable world and depth limits."""
    return (
        -WORLD_HALF_SIZE + margin <= x <= WORLD_HALF_SIZE - margin
        and -WORLD_HALF_SIZE + margin <= z <= WORLD_HALF_SIZE - margin
        and SURFACE_LIMIT <= depth <= WORLD_BOTTOM - margin
    )


def rock_hit(x, depth, z, margin=0.0):
    """Check whether a position overlaps any rock, including an optional margin."""
    for rock in rocks:
        if distance_3d(x, depth, z, rock["x"], rock["depth"], rock["z"]) <= rock["radius"] + margin:
            return True
    return False


def obstacle_hit(x, depth, z, margin=0.0):
    """Check whether a position collides with a rock or solid mission structure."""
    if rock_hit(x, depth, z, margin):
        return True
    if fortress is not None and not fortress["destroyed"]:
        return distance_3d(x, depth, z, fortress["x"], fortress["depth"], fortress["z"]) <= 78.0 + margin
    return False


def distance_to_player(item):
    """Measure the distance from a game entity to the player submarine."""
    return distance_3d(item["x"], item["depth"], item["z"], player["x"], player["depth"], player["z"])


def set_status(message, duration=2.5):
    """Show a temporary HUD status message for the requested duration."""
    global status_message, status_timer
    status_message = message
    status_timer = duration


def add_explosion(x, depth, z, radius, duration, emp=False):
    """Add an animated conventional or EMP explosion to the scene."""
    explosions.append({"x": x, "depth": depth, "z": z, "radius": radius, "timer": duration, "duration": duration, "emp": emp})


# ============================================================
# World setup and missions
# ============================================================

def create_rocks():
    """Build runtime rock objects from the fixed level layout."""
    keys = ("x", "depth", "z", "radius", "height", "scale")
    return [dict(zip(keys, row)) for row in ROCK_LAYOUT]


def create_bubbles():
    """Seed the ambient bubble field with deterministic random positions."""
    result = []
    span = int(WORLD_HALF_SIZE * 2.0 - 80.0)
    for index in range(72):
        result.append({
            "x": -WORLD_HALF_SIZE + 40 + (index * 97) % span,
            "depth": 35.0 + (index * 67) % int(WORLD_BOTTOM - 50),
            "z": -WORLD_HALF_SIZE + 40 + (index * 149) % span,
            "speed": 9.0 + (index % 6) * 3.2,
            "size": 1.5 + (index % 4) * 0.9,
            "phase": index * 0.83,
        })
    return result


def create_kelp():
    """Generate kelp and coral decorations around the seafloor."""
    result = []
    for index in range(38):
        result.append({
            "x": -650.0 + (index * 173) % 1300,
            "z": -650.0 + (index * 251) % 1300,
            "height": 34.0 + (index % 6) * 9.0,
            "phase": index * 0.71,
        })
    return result


def create_fish():
    """Create the ambient fish school and its animation parameters."""
    # Fish are only for the environment.
    result = []
    for school in range(5):
        for member in range(9):
            phase = member * 2.399 + school
            result.append({
                "school": school, "phase": phase,
                "x": math.sin(school * 1.7) * 380 + math.cos(phase) * 35,
                "z": math.cos(school * 1.7) * 180 + math.sin(phase) * 35,
                "depth": 80.0 + school * 38 + member % 3 * 6,
                "angle": school * 60.0, "size": 0.8 + member % 4 * 0.16,
            })
    return result


def make_enemy(kind, x, depth, z, angle, entity_id):
    """Construct a complete enemy record for the requested vessel type."""
    templates = {
        "scout": (82.0, 55.0, 29.0, 3.5, 12.0),
        "hunter": (125.0, 47.0, 35.0, 3.0, 16.0),
        "heavy": (205.0, 34.0, 43.0, 3.8, 22.0),
        "boss": (720.0, 37.0, 61.0, 2.15, 24.0),
    }
    health, speed, radius, fire_delay, damage = templates[kind]
    difficulty = current_difficulty()
    return {
        "id": entity_id,
        "kind": kind,
        "x": x,
        "depth": depth,
        "z": z,
        "angle": angle,
        "health": health * difficulty["enemy_health"],
        "max_health": health * difficulty["enemy_health"],
        "speed": speed * difficulty["enemy_speed"],
        "radius": radius,
        "fire_delay": fire_delay,
        "damage": damage * difficulty["enemy_damage"],
        "state": "PATROL",
        "alerted": False,
        "revealed": False,
        "fire_cooldown": 1.2 + random.random() * 2.2,
        "contact_cooldown": 0.0,
        "stunned": 0.0,
        "origin_x": x,
        "origin_z": z,
        "patrol_radius": 75.0 + random.random() * 65.0,
        "patrol_time": 0.0,
        "phase_seed": random.random() * math.pi * 2.0,
        "boss_phase": 1,
    }


def place_player(x, depth, z, angle):
    """Place and orient the player at a mission starting position."""
    player.update({"x": x, "depth": depth, "z": z, "angle": angle})


def prepare_mission(index):
    """Reset mission-specific entities and configure the selected operation."""
    global state, decoy_count
    global mission_index, mission_progress, mission_elapsed
    global sonar_active, sonar_radius, sonar_cooldown, sonar_overlay_timer
    global enemies, torpedoes, mines, collectibles, gates, explosions, decoys
    global escort, fortress, extraction
    global fire_cooldown

    held_keys.clear()
    fire_cooldown = 0.0

    if index >= len(MISSIONS):
        set_state(VICTORY)
        return

    mission_index = index
    mission_progress = 0
    mission_elapsed = 0.0
    set_status(MISSIONS[index]["briefing"], 999.0)
    sonar_active = False
    sonar_radius = 0.0
    sonar_cooldown = 0.0
    sonar_overlay_timer = 0.0
    sonar_contacts.clear()
    enemies = []
    torpedoes = []
    mines = []
    collectibles = []
    gates = []
    explosions = []
    decoys = []
    escort = None
    fortress = None
    extraction = None
    player["throttle_index"] = 1
    player["silent_running"] = False

    minimum_loadout = {
        0: (0, 0, 0),
        1: (4, 1, 1),
        2: (8, 3, 2),
        3: (8, 3, 5),
        4: (14, 5, 2),
        5: (18, 6, 3),
        6: (18, 8, 4),
        7: (12, 5, 2),
    }[index]
    for selected, minimum in zip(WEAPON_ORDER, minimum_loadout):
        ammo[selected] = max(ammo[selected], minimum)
    decoy_count = max(decoy_count, 2)
    player["hull"] = max(player["hull"], 35.0)

    if index == 0:
        place_player(0.0, 70.0, 0.0, 325.0)
        gates = [{"x": x, "depth": depth, "z": z, "passed": False} for x, depth, z in GATE_LAYOUT]
    elif index == 1:
        place_player(-570.0, 115.0, -80.0, 180.0)
        collectibles = [{"id": "POD-%d" % (n + 1), "x": x, "depth": depth, "z": z, "collected": False, "revealed": False} for n, (x, depth, z) in enumerate(POD_LAYOUT)]
        enemies = [
            make_enemy("scout", 470.0, 145.0, -350.0, 210.0, "GHOST-1"),
            make_enemy("scout", 60.0, 230.0, -610.0, 300.0, "GHOST-2"),
        ]
    elif index == 2:
        place_player(0.0, 125.0, 0.0, 0.0)
        contacts = (
            ("scout", -260.0, 100.0, 155.0, 90.0),
            ("hunter", 280.0, 170.0, 125.0, 245.0),
            ("scout", -135.0, 225.0, -300.0, 15.0),
            ("hunter", 330.0, 85.0, -255.0, 175.0),
            ("heavy", 35.0, 245.0, 410.0, 195.0),
        )
        enemies = [make_enemy(kind, x, depth, z, angle, "ECHO-%d" % (n + 1)) for n, (kind, x, depth, z, angle) in enumerate(contacts)]
    elif index == 3:
        place_player(-610.0, 95.0, 60.0, 35.0)
        mines = [{"id": "MINE-%d" % (n + 1), "x": x, "depth": depth, "base_depth": depth, "z": z, "radius": 23.0, "active": True, "revealed": False, "phase": n * 1.31} for n, (x, depth, z) in enumerate(MINE_LAYOUT)]
        enemies = [make_enemy("scout", 0.0, 125.0, 560.0, 180.0, "WARDEN-1"), make_enemy("hunter", 500.0, 210.0, 250.0, 255.0, "WARDEN-2")]
    elif index == 4:
        start = ESCORT_ROUTE[0]
        place_player(start[0] - 60.0, start[1], start[2] - 40.0, 45.0)
        escort = {"x": start[0], "depth": start[1], "z": start[2], "angle": 0.0, "health": 180.0, "max_health": 180.0, "route_index": 1, "waiting": False}
        layout = (("scout", -135.0, 150.0, -390.0, 155.0), ("hunter", 85.0, 205.0, -215.0, 220.0), ("hunter", 315.0, 120.0, -30.0, 265.0), ("heavy", 505.0, 185.0, 275.0, 300.0))
        enemies = [make_enemy(kind, x, depth, z, angle, "RAIDER-%d" % (n + 1)) for n, (kind, x, depth, z, angle) in enumerate(layout)]
    elif index == 5:
        place_player(-470.0, 135.0, 440.0, 135.0)
        fx, fdepth, fz = FORTRESS_POSITION
        fortress = {"x": fx, "depth": fdepth, "z": fz, "health": 420.0, "max_health": 420.0, "destroyed": False, "nodes": [{"id": "RELAY-%d" % (n + 1), "x": x, "depth": depth, "z": z, "health": 110.0, "max_health": 110.0, "destroyed": False} for n, (x, depth, z) in enumerate(FORTRESS_NODES)]}
        layout = (("scout", -40.0, 120.0, 250.0, 155.0), ("hunter", 190.0, 210.0, 20.0, 165.0), ("heavy", 360.0, 175.0, -230.0, 190.0), ("hunter", 600.0, 95.0, -430.0, 280.0), ("scout", 320.0, 255.0, -600.0, 35.0))
        enemies = [make_enemy(kind, x, depth, z, angle, "FORT-%d" % (n + 1)) for n, (kind, x, depth, z, angle) in enumerate(layout)]
    elif index == 6:
        place_player(430.0, 160.0, 420.0, 225.0)
        boss = make_enemy("boss", -390.0, 220.0, -415.0, 35.0, "LEVIATHAN")
        boss.update({"alerted": True, "revealed": True, "state": "CHASE"})
        enemies = [boss, make_enemy("hunter", -80.0, 135.0, -310.0, 40.0, "LANCER-A"), make_enemy("hunter", -510.0, 105.0, -80.0, 155.0, "LANCER-B")]
    elif index == 7:
        place_player(465.0, 225.0, -470.0, 320.0)
        extraction = EXTRACTION_POSITION
        layout = (("scout", 250.0, 130.0, -280.0, 315.0), ("hunter", 80.0, 205.0, -75.0, 320.0), ("scout", -180.0, 100.0, 100.0, 300.0), ("hunter", -390.0, 190.0, 315.0, 325.0), ("heavy", -550.0, 120.0, 480.0, 5.0))
        enemies = [make_enemy(kind, x, depth, z, angle, "PURSUER-%d" % (n + 1)) for n, (kind, x, depth, z, angle) in enumerate(layout)]
        for enemy in enemies:
            enemy.update({"alerted": True, "revealed": True, "state": "CHASE"})

    state = BRIEFING


def reset_campaign(to_console=True):
    """Restore all campaign progress, upgrades, statistics, and ammunition."""
    global state, console_return_state, ammo, weapon, weapon_levels, decoy_count
    global score, total_kills, shots_fired, shots_hit, damage_taken, mines_disarmed
    global missions_completed, achievements, mission_index, mission_progress
    global mission_elapsed, total_elapsed, status_message, status_timer
    global sonar_active, sonar_radius, sonar_cooldown, sonar_overlay_timer
    global enemies, torpedoes, mines, collectibles, gates, explosions, decoys
    global escort, fortress, extraction, rocks, bubbles, kelp, scene_time
    global fish, fire_cooldown, show_help, help_return_state, restart_return_state
    global camera_mode, camera_height, camera_orbit, mouse_dragging

    player.clear()
    player.update({"x": 0.0, "depth": 75.0, "z": 0.0, "angle": 0.0, "hull": 100.0, "max_hull": 100.0, "throttle_index": 1, "silent_running": False, "propeller_angle": 0.0, "damage_cooldown": 0.0})
    ammo = dict(STARTING_AMMO)
    weapon = "STANDARD"
    weapon_levels = {name: 0 for name in WEAPON_ORDER}
    decoy_count = 5
    score = 0
    total_kills = 0
    shots_fired = 0
    shots_hit = 0
    damage_taken = 0.0
    mines_disarmed = 0
    missions_completed = 0
    achievements = []
    mission_index = 0
    mission_progress = 0
    mission_elapsed = 0.0
    total_elapsed = 0.0
    status_message = "Configure your vessel, then deploy."
    status_timer = 999.0
    sonar_active = False
    sonar_radius = 0.0
    sonar_cooldown = 0.0
    sonar_overlay_timer = 0.0
    sonar_contacts.clear()
    enemies = []
    torpedoes = []
    mines = []
    collectibles = []
    gates = []
    explosions = []
    decoys = []
    escort = None
    fortress = None
    extraction = None
    rocks = create_rocks()
    bubbles = create_bubbles()
    kelp = create_kelp()
    fish = create_fish()
    fire_cooldown = 0.0
    show_help = False
    help_return_state = restart_return_state = None
    held_keys.clear()
    mouse_dragging = False
    camera_mode, camera_height, camera_orbit = 1, 185.0, 0.0
    scene_time = 0.0
    console_return_state = None
    state = CONSOLE if to_console else BRIEFING


def set_state(new_state):
    """Switch game screens while keeping related overlay state consistent."""
    global state
    held_keys.clear()
    state = new_state


def move_console_cursor(amount):
    """Move the configuration-menu selection and keep it in range."""
    profile["cursor"] = (profile["cursor"] + amount) % 3


def change_console_value(amount):
    """Cycle the selected vessel configuration option."""
    if profile["cursor"] == 0:
        profile["color_index"] = (profile["color_index"] + amount) % len(COLOR_PRESETS)
    elif profile["cursor"] == 1:
        profile["difficulty_index"] = (profile["difficulty_index"] + amount) % len(DIFFICULTIES)
    else:
        profile["callsign_index"] = (profile["callsign_index"] + amount) % len(CALLSIGNS)


def open_console():
    """Open vessel configuration and remember which screen should be restored."""
    global state, console_return_state
    if state in (PLAYING, PAUSED):
        held_keys.clear()
        console_return_state = state
        state = CONSOLE
        set_status("Player console opened; simulation suspended.", 999.0)


def confirm_console():
    """Apply configuration choices and return to the previous screen."""
    global state, console_return_state
    if console_return_state is not None:
        state = console_return_state
        console_return_state = None
        set_status("Vessel profile updated.", 2.0)
        return
    reset_campaign(to_console=False)
    prepare_mission(0)


def begin_or_continue():
    """Start the current mission or advance after a completed mission."""
    if state == CONSOLE:
        confirm_console()
    elif state == BRIEFING:
        set_state(PLAYING)
        set_status("Operation underway.", 2.0)
    elif state == MISSION_COMPLETE:
        prepare_mission(mission_index + 1)


def toggle_pause():
    """Pause or resume gameplay and update the persistent status message."""
    global state
    held_keys.clear()
    if state == PLAYING:
        state = PAUSED
        set_status("Simulation paused.", 999.0)
    elif state == PAUSED:
        state = PLAYING
        set_status("Simulation resumed.", 1.5)


# ============================================================
# Drawing and HUD
# ============================================================

def get_quadric():
    """Lazily create and reuse the GLU quadric used by curved models."""
    global quadric
    if quadric is None:
        quadric = gluNewQuadric()
    return quadric


def enter_overlay():
    """Save 3D matrices and enter the fixed-resolution 2D HUD coordinate system."""
    global overlay_layer
    overlay_layer += 1
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    # Small z offset keeps newer HUD items in front.
    glTranslatef(0, 0, overlay_layer * 0.0001)


def leave_overlay():
    """Restore projection and model-view matrices after drawing an overlay."""
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_text(x, y, text, color=TEXT_COLOR):
    """Render HUD text at virtual-screen coordinates using the selected bitmap font."""
    enter_overlay()
    glColor3f(*color)
    glRasterPos2f(x, y)
    font = UI_FONT if viewport[2] >= 1100 else COMPACT_UI_FONT
    for character in str(text):
        glutBitmapCharacter(font, ord(character))
    leave_overlay()


def draw_rect(x, y, width, height, color):
    """Draw a solid rectangle in the 2D overlay coordinate system."""
    enter_overlay()
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x, y, 0)
    glVertex3f(x + width, y, 0)
    glVertex3f(x + width, y + height, 0)
    glVertex3f(x, y + height, 0)
    glEnd()
    leave_overlay()


def draw_bar(x, y, width, height, ratio, foreground, background=(0.06, 0.10, 0.14)):
    """Draw a clamped progress bar with separate background and fill colors."""
    ratio = clamp(ratio, 0.0, 1.0)
    draw_rect(x, y, width, height, background)
    if ratio > 0:
        draw_rect(x + 2, y + 2, (width - 4) * ratio, height - 4, foreground)


def draw_cube(x, depth, z, scale, color, rotation=0.0):
    """Render a positioned, rotated, and scaled cube in world coordinates."""
    render_x, render_y, render_z = world_to_render(x, depth, z)
    glPushMatrix()
    glTranslatef(render_x, render_y, render_z)
    glRotatef(rotation, 0, 0, 1)
    glColor3f(*color)
    glScalef(*scale)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_ellipsoid(scale, color, detail=12):
    """Render a shaded ellipsoid using a cached low-poly quad mesh."""
    # Build a simple curved mesh from quads.
    if detail not in mesh_cache:
        mesh = []
        for ring in range(detail // 2):
            for segment in range(detail):
                face = []
                for r, s in ((ring, segment), (ring, segment + 1),
                             (ring + 1, segment + 1), (ring + 1, segment)):
                    lat = -math.pi / 2 + r * math.pi / (detail // 2)
                    lon = s * 2 * math.pi / detail
                    x, y, z = math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)
                    shade = 0.36 + 0.64 * max(0.0, x * -0.3 + y * 0.25 + z * 0.92)
                    face.append((x, y, z, shade))
                mesh.append(face)
        mesh_cache[detail] = mesh
    glPushMatrix()
    glScalef(*scale)
    glBegin(GL_QUADS)
    for face in mesh_cache[detail]:
        for x, y, z, shade in face:
            glColor3f(*(min(1.0, component * shade + 0.025) for component in color))
            glVertex3f(x, y, z)
    glEnd()
    glPopMatrix()


def draw_seafloor():
    """Render the tiled, animated seafloor and its long rock ridges."""
    tile = 60.0
    half = WORLD_HALF_SIZE
    row = 0
    y = -half
    glBegin(GL_QUADS)
    while y < half:
        column = 0
        x = -half
        while x < half:
            for vx, vy in ((x, y), (x + tile, y), (x + tile, y + tile), (x, y + tile)):
                ripple = math.sin(vx * 0.024 + vy * 0.011) * math.cos(vy * 0.022)
                caustic = max(0.0, math.sin(vx * 0.041 + scene_time * 0.65)
                              * math.cos(vy * 0.036 - scene_time * 0.45)) ** 8
                glColor3f(0.08 + ripple * 0.018 + caustic * 0.08,
                          0.23 + ripple * 0.025 + caustic * 0.18,
                          0.25 + ripple * 0.018 + caustic * 0.18)
                glVertex3f(vx, vy, -WORLD_BOTTOM + ripple * 5)
            x += tile
            column += 1
        y += tile
        row += 1
    glEnd()
    for index in range(18):
        x = -650.0 + (index * 173) % 1300
        z = -610.0 + (index * 239) % 1220
        draw_cube(x, WORLD_BOTTOM - 2.0, z, (95.0 + (index % 3) * 25.0, 8.0, 2.5), (0.055, 0.19, 0.19), (index * 29.0) % 180.0)


def draw_boundaries():
    """Render translucent walls around the playable area without writing depth."""
    top = -SURFACE_LIMIT
    bottom = -WORLD_BOTTOM
    half = WORLD_HALF_SIZE

    # Blend the enclosing walls over the scene instead of hiding objects behind
    # opaque quads. Disabling depth writes prevents a translucent wall from
    # incorrectly concealing geometry that is drawn later in the frame.
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glBegin(GL_QUADS)
    glColor4f(0.018, 0.10, 0.16, BOUNDARY_ALPHA)
    glVertex3f(-half, half, bottom)
    glVertex3f(half, half, bottom)
    glVertex3f(half, half, top)
    glVertex3f(-half, half, top)
    glColor4f(0.012, 0.075, 0.13, BOUNDARY_ALPHA)
    glVertex3f(-half, -half, bottom)
    glVertex3f(half, -half, bottom)
    glVertex3f(half, -half, top)
    glVertex3f(-half, -half, top)
    glColor4f(0.015, 0.085, 0.14, BOUNDARY_ALPHA)
    glVertex3f(-half, -half, bottom)
    glVertex3f(-half, half, bottom)
    glVertex3f(-half, half, top)
    glVertex3f(-half, -half, top)
    glVertex3f(half, -half, bottom)
    glVertex3f(half, half, bottom)
    glVertex3f(half, half, top)
    glVertex3f(half, -half, top)
    glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)


def draw_light_shafts():
    """Render drifting particles that suggest filtered light in the water."""
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for index in range(9):
        x = -600.0 + index * 150.0
        z = -500.0 + (index * 211) % 1000
        for mote in range(28):
            depth = 22 + (mote * 11 + scene_time * 9) % 295
            brightness = 1 - depth / 440
            glColor3f(0.20 * brightness, 0.58 * brightness, 0.64 * brightness)
            glVertex3f(x + depth * 0.24 + math.sin(mote * 4.1) * 12,
                       z + math.cos(mote * 2.3) * 18, -depth)
    glEnd()


def draw_rocks():
    """Render collision rocks with layered shapes and surface details."""
    for rock in rocks:
        render_x, render_y, render_z = world_to_render(rock["x"], rock["depth"], rock["z"])
        scale_x, scale_y, scale_z = rock["scale"]
        radius = rock["radius"]
        height = rock["height"]
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glRotatef((rock["x"] * 0.23) % 360.0, 0, 0, 1)
        draw_ellipsoid((radius * scale_x * 0.65, radius * scale_y * 0.65, height * scale_z * 0.55), (0.29, 0.40, 0.40), 10)
        for offset_x, offset_y, offset_z, size in ((-0.28, -0.15, 0.30, 0.30), (0.24, 0.18, 0.05, 0.22), (-0.10, 0.27, -0.24, 0.17)):
            glPushMatrix()
            glTranslatef(radius * offset_x, radius * offset_y, height * offset_z)
            draw_ellipsoid((radius * size, radius * size, height * size), (0.31, 0.46, 0.43), 8)
            glPopMatrix()
        glPopMatrix()


def draw_kelp_and_coral():
    """Render animated kelp strands and coral decorations."""
    q = get_quadric()
    for index, plant in enumerate(kelp):
        render_x, render_y, render_z = world_to_render(plant["x"], WORLD_BOTTOM - 3, plant["z"])
        sway = math.sin(scene_time * 1.15 + plant["phase"]) * 8.0
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glRotatef(sway, 0, 1, 0)
        glColor3f(0.035, 0.31 + (index % 3) * 0.035, 0.19)
        gluCylinder(q, 2.2, 1.1, plant["height"], 7, 5)
        glColor3f(0.07, 0.48, 0.27)
        for height_ratio, side in ((0.35, -1), (0.58, 1), (0.78, -1)):
            glPushMatrix()
            glTranslatef(side * 7.0, 0, plant["height"] * height_ratio)
            glScalef(15.0, 4.0, 3.0)
            glutSolidCube(1.0)
            glPopMatrix()
        glPopMatrix()
    for index in range(14):
        x = -590.0 + (index * 197) % 1180
        z = -570.0 + (index * 277) % 1140
        render_x, render_y, render_z = world_to_render(x, WORLD_BOTTOM - 15.0, z)
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glColor3f(0.58, 0.14 + (index % 3) * 0.07, 0.18 + (index % 2) * 0.12)
        for branch in (-16.0, 0.0, 16.0):
            glPushMatrix()
            glTranslatef(branch, 0, 0)
            glRotatef(branch * 1.6, 0, 1, 0)
            gluCylinder(q, 4.0, 1.8, 30.0 + abs(branch) * 0.4, 7, 4)
            glPopMatrix()
        glPopMatrix()


def draw_bubbles():
    """Render rising ambient bubbles and reset them when they reach the surface."""
    q = get_quadric()
    glColor3f(0.30, 0.72, 0.84)
    for bubble in bubbles:
        render_x, render_y, render_z = world_to_render(bubble["x"], bubble["depth"], bubble["z"])
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        gluSphere(q, bubble["size"], 7, 5)
        glPopMatrix()


def draw_fish_school():
    """Render the animated ambient fish school around its moving center."""
    colors = ((0.30, 0.88, 0.94), (1.0, 0.61, 0.20), (0.58, 0.73, 1.0),
              (0.93, 0.40, 0.40), (0.41, 0.94, 0.65))
    for animal in fish:
        glPushMatrix()
        glTranslatef(*world_to_render(animal["x"], animal["depth"], animal["z"]))
        glRotatef(-animal["angle"], 0, 0, 1)
        size = animal["size"]
        glScalef(size, size, size)
        color = colors[animal["school"]]
        draw_ellipsoid((3.6, 11.0, 5.5), color)
        # Two small eyes so the front of the fish is easy to see.
        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(side * 2.8, 6.5, 2.0)
            draw_ellipsoid((0.7, 1.1, 1.1), (0.025, 0.04, 0.05), 8)
            glPopMatrix()
        glColor3f(*(component * 0.85 for component in color))
        glBegin(GL_QUADS)
        for vertices in (((0, -5, 3), (0, -4, 11), (0, 4, 4), (0, 4, 4)),
                         ((-2, 0, 0), (-9, -4, -1), (-3, -6, 0), (-3, -6, 0)),
                         ((2, 0, 0), (9, -4, -1), (3, -6, 0), (3, -6, 0))):
            for vertex in vertices:
                glVertex3f(*vertex)
        glEnd()
        glTranslatef(0, -9, 0)
        glRotatef(math.sin(scene_time * 9 + animal["phase"]) * 28, 0, 0, 1)
        glBegin(GL_QUADS)
        for vertex in ((0, 0, 0), (0, -9, 8), (0, -6, 0), (0, -9, -8)):
            glVertex3f(*vertex)
        glEnd()
        glPopMatrix()


def draw_wreck():
    """Render the Calypso wreck used as scenery and a mission landmark."""
    if mission_index != 1:
        return
    q = get_quadric()
    render_x, render_y, render_z = world_to_render(-70.0, 292.0, -470.0)
    glPushMatrix()
    glTranslatef(render_x, render_y, render_z)
    glRotatef(28.0, 0, 0, 1)
    glColor3f(0.17, 0.24, 0.25)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 25.0, 18.0, 95.0, 13, 7)
    glPopMatrix()
    glColor3f(0.30, 0.18, 0.10)
    glPushMatrix()
    glTranslatef(0, 20.0, 28.0)
    glScalef(35.0, 26.0, 18.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()


def draw_submarine(x, depth, z, angle, palette, scale=1.0, variant="player", propeller=0.0):
    """Render a submarine model with colors and details appropriate to its variant."""
    q = get_quadric()
    render_x, render_y, render_z = world_to_render(x, depth, z)
    body, dark, accent = palette["body"], palette["dark"], palette["accent"]
    glPushMatrix()
    glTranslatef(render_x, render_y, render_z)
    glRotatef(-angle, 0, 0, 1)
    glScalef(scale, scale, scale)
    draw_ellipsoid((25.0, 65.0, 23.0), body, 24)
    for side in (-1, 1):
        for port in range(4):
            glPushMatrix()
            glTranslatef(side * 23.0, -22.0 + port * 13, 6.0)
            draw_ellipsoid((2.3, 3.8, 3.8), accent, 8)
            glPopMatrix()
    glColor3f(*dark)
    glPushMatrix()
    glTranslatef(0, -2.0, 29.0)
    glScalef(25.0, 34.0, 18.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glColor3f(*accent)
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(side * 10.0, 10.0, 35.0)
        gluSphere(q, 4.0, 8, 5)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 2.0, 42.0)
    gluCylinder(q, 3.2, 3.0, 23.0, 9, 5)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 2.0, 65.0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(q, 3.1, 3.1, 15.0, 9, 5)
    glPopMatrix()
    glColor3f(*dark)
    glPushMatrix()
    glTranslatef(0, 6.0, 0)
    glScalef(76.0, 17.0, 4.5)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, -50.0, 16.0)
    glScalef(7.0, 24.0, 35.0)
    glutSolidCube(1.0)
    glPopMatrix()
    glColor3f(*dark)
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(side * 12.0, 48.0, -4.0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(q, 4.8, 4.2, 18.0, 9, 5)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0, -63.0, 0)
    glColor3f(*accent)
    gluSphere(q, 7.0, 10, 6)
    glRotatef(propeller, 0, 1, 0)
    for blade in (0, 60, 120, 180, 240, 300):
        glPushMatrix()
        glRotatef(blade, 0, 1, 0)
        glTranslatef(0, 0, 14.0)
        glScalef(3.0, 2.3, 10.0)
        glutSolidCube(1.0)
        glPopMatrix()
    glPopMatrix()
    if variant == "boss":
        glColor3f(1.0, 0.62, 0.10)
        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(side * 34.0, -7.0, 8.0)
            glScalef(17.0, 72.0, 12.0)
            glutSolidCube(1.0)
            glPopMatrix()
    elif variant == "escort":
        glColor3f(1.0, 0.86, 0.20)
        glPushMatrix()
        glTranslatef(0, 2.0, 55.0)
        glutSolidCube(10.0)
        glPopMatrix()
    glPopMatrix()


def draw_player():
    """Render the player submarine with its current palette and propeller motion."""
    if camera_mode == 2:
        return
    draw_submarine(player["x"], player["depth"], player["z"], player["angle"], current_palette(), propeller=player["propeller_angle"])
    if abs(player_throttle()) > 0.01:
        back_x, back_z = heading_vector(player["angle"] + 180.0)
        glColor3f(0.28, 0.70, 0.83)
        q = get_quadric()
        for index in range(5):
            render_x, render_y, render_z = world_to_render(player["x"] + back_x * (68.0 + index * 13.0), player["depth"] - (index % 2) * 3.0, player["z"] + back_z * (68.0 + index * 13.0))
            glPushMatrix()
            glTranslatef(render_x, render_y, render_z)
            gluSphere(q, 2.5 + index * 0.35, 7, 5)
            glPopMatrix()


def player_throttle():
    """Return the player's signed throttle value from the selected throttle level."""
    return THROTTLE_LEVELS[player["throttle_index"]]


def enemy_palette(enemy):
    """Choose hull colors for a normal enemy, elite vessel, or boss."""
    if enemy["kind"] == "boss":
        return {"body": BOSS_BODY, "dark": (0.15, 0.015, 0.15), "accent": (1.0, 0.28, 0.78)}
    if enemy["kind"] == "heavy":
        return {"body": (0.52, 0.16, 0.07), "dark": ENEMY_DARK, "accent": (1.0, 0.48, 0.12)}
    return {"body": ENEMY_BODY, "dark": ENEMY_DARK, "accent": (1.0, 0.30, 0.17)}


def draw_world_health_bar(x, depth, z, ratio, height):
    """Project an entity's position and draw its health bar in screen space."""
    render_x, render_y, render_z = world_to_render(x, depth, z)
    glPushMatrix()
    glTranslatef(render_x, render_y, render_z + height)
    glColor3f(0.18, 0.025, 0.025)
    glPushMatrix()
    glScalef(52.0, 6.0, 4.0)
    glutSolidCube(1.0)
    glPopMatrix()
    ratio = clamp(ratio, 0.0, 1.0)
    glColor3f(*(GREEN if ratio > 0.38 else RED))
    glPushMatrix()
    glTranslatef(-26.0 + 26.0 * ratio, 0, 0)
    glScalef(52.0 * ratio, 6.0, 4.2)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()


def draw_enemies():
    """Render every active enemy and a health bar for damaged vessels."""
    for enemy in enemies:
        if not (enemy["revealed"] or enemy["alerted"] or enemy["kind"] == "boss" or distance_to_player(enemy) <= 105.0):
            continue
        scale = {"scout": 0.84, "hunter": 1.0, "heavy": 1.18, "boss": 1.52}[enemy["kind"]]
        draw_submarine(enemy["x"], enemy["depth"], enemy["z"], enemy["angle"], enemy_palette(enemy), scale, "boss" if enemy["kind"] == "boss" else "enemy", scene_time * (560.0 if enemy["stunned"] <= 0 else 80.0))
        draw_world_health_bar(enemy["x"], enemy["depth"], enemy["z"], enemy["health"] / enemy["max_health"], 55.0 * scale)
        if enemy["stunned"] > 0:
            draw_point_ring(enemy["x"], enemy["depth"], enemy["z"], 42.0 * scale, (0.45, 0.65, 1.0), vertical=True)


def draw_escort():
    """Render the Atlas escort vessel when that mission is active."""
    if escort is None:
        return
    palette = {"body": (0.55, 0.46, 0.11), "dark": (0.16, 0.13, 0.035), "accent": (1.0, 0.88, 0.25)}
    draw_submarine(escort["x"], escort["depth"], escort["z"], escort["angle"], palette, 0.82, "escort", scene_time * 480.0)
    draw_world_health_bar(escort["x"], escort["depth"], escort["z"], escort["health"] / escort["max_health"], 48.0)
    if escort["route_index"] < len(ESCORT_ROUTE):
        draw_beacon(*ESCORT_ROUTE[escort["route_index"]], color=(1.0, 0.82, 0.18), radius=34.0)


def draw_point_ring(x, depth, z, radius, color, vertical=False):
    """Render a segmented horizontal or vertical marker ring in the world."""
    render_x, render_y, render_z = world_to_render(x, depth, z)
    glPointSize(4.0)
    glColor3f(*color)
    glBegin(GL_POINTS)
    for index in range(72):
        angle = math.pi * 2.0 * index / 72.0
        if vertical:
            glVertex3f(render_x + math.cos(angle) * radius, render_y, render_z + math.sin(angle) * radius)
        else:
            glVertex3f(render_x + math.cos(angle) * radius, render_y + math.sin(angle) * radius, render_z)
    glEnd()


def draw_beacon(x, depth, z, color, radius):
    """Render an animated beacon with concentric rings and a light column."""
    draw_point_ring(x, depth, z, radius, color)
    draw_point_ring(x, depth, z, radius * 0.65, color, vertical=True)
    draw_cube(x, depth, z, (8.0, 8.0, 58.0), color)


def draw_gates():
    """Render navigation gates and emphasize the currently active gate."""
    for index, gate in enumerate(gates):
        color = (0.12, 0.30, 0.25) if gate["passed"] else current_palette()["hud"] if index == mission_progress else (0.10, 0.28, 0.34)
        pulse = 56.0 + math.sin(scene_time * 3.0 + index) * 4.0
        draw_point_ring(gate["x"], gate["depth"], gate["z"], pulse, color, vertical=True)
        draw_cube(gate["x"] - pulse, gate["depth"], gate["z"], (5.0, 5.0, pulse * 1.35), color)
        draw_cube(gate["x"] + pulse, gate["depth"], gate["z"], (5.0, 5.0, pulse * 1.35), color)


def draw_collectibles():
    """Render uncollected data pods and other mission pickups."""
    q = get_quadric()
    for index, item in enumerate(collectibles):
        if item["collected"] or not (item["revealed"] or distance_to_player(item) <= 155.0):
            continue
        bob = math.sin(scene_time * 2.0 + index) * 5.0
        render_x, render_y, render_z = world_to_render(item["x"], item["depth"] + bob, item["z"])
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glRotatef(scene_time * 75.0 + index * 30.0, 0, 0, 1)
        glColor3f(0.12, 0.72, 0.78)
        glScalef(14.0, 22.0, 14.0)
        glutSolidCube(1.0)
        glPopMatrix()
        draw_point_ring(item["x"], item["depth"] + bob, item["z"], 29.0, (0.20, 0.95, 1.0))


def draw_mines():
    """Render active naval mines, spikes, and their alert indicators."""
    q = get_quadric()
    for mine in mines:
        if not mine["active"] or not (mine["revealed"] or distance_to_player(mine) <= 125.0):
            continue
        render_x, render_y, render_z = world_to_render(mine["x"], mine["depth"], mine["z"])
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glColor3f(0.72, 0.10, 0.045)
        gluSphere(q, mine["radius"], 12, 8)
        glColor3f(1.0, 0.42, 0.08)
        for spike in (0, 45, 90, 135, 180, 225, 270, 315):
            glPushMatrix()
            glRotatef(spike, 0, 0, 1)
            glTranslatef(0, 0, 30.0)
            glScalef(2.5, 2.5, 10.0)
            glutSolidCube(1.0)
            glPopMatrix()
        glPopMatrix()


def draw_fortress():
    """Render the fortress core, shield effect, and destructible relay nodes."""
    if fortress is None:
        return
    q = get_quadric()
    if not fortress["destroyed"]:
        render_x, render_y, render_z = world_to_render(fortress["x"], fortress["depth"], fortress["z"])
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glColor3f(0.085, 0.24, 0.29)
        glPushMatrix()
        glScalef(145.0, 125.0, 92.0)
        glutSolidCube(1.0)
        glPopMatrix()
        glColor3f(0.14, 0.48, 0.52)
        for side_x in (-1, 1):
            for side_y in (-1, 1):
                glPushMatrix()
                glTranslatef(side_x * 58.0, side_y * 47.0, 72.0)
                glScalef(26.0, 26.0, 108.0)
                glutSolidCube(1.0)
                glPopMatrix()
        glColor3f(*(RED if fortress_shielded() else AMBER))
        glPushMatrix()
        glTranslatef(0, 0, 95.0)
        gluSphere(q, 24.0, 12, 8)
        glPopMatrix()
        glPopMatrix()
        draw_world_health_bar(fortress["x"], fortress["depth"], fortress["z"], fortress["health"] / fortress["max_health"], 135.0)
    for index, node in enumerate(fortress["nodes"]):
        if node["destroyed"]:
            continue
        pulse = 1.0 + math.sin(scene_time * 4.0 + index) * 0.12
        render_x, render_y, render_z = world_to_render(node["x"], node["depth"], node["z"])
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glColor3f(0.16, 0.56, 0.75)
        glPushMatrix()
        glScalef(23.0, 23.0, 55.0)
        glutSolidCube(1.0)
        glPopMatrix()
        glColor3f(0.38, 0.90, 1.0)
        glPushMatrix()
        glTranslatef(0, 0, 35.0)
        gluSphere(q, 12.0 * pulse, 10, 7)
        glPopMatrix()
        glPopMatrix()
        draw_point_ring(node["x"], node["depth"], node["z"], 36.0, (0.25, 0.78, 1.0))


def fortress_shielded():
    """Return whether any live relay is still protecting the fortress core."""
    return fortress is not None and any(not node["destroyed"] for node in fortress["nodes"])


def draw_extraction():
    """Render the final extraction beacon when it is active."""
    if extraction is not None:
        draw_beacon(*extraction, color=GREEN, radius=52.0 + math.sin(scene_time * 4.0) * 7.0)


def draw_torpedoes_and_decoys():
    """Render all active projectiles, trails, and deployed decoys."""
    q = get_quadric()
    for torpedo in torpedoes:
        render_x, render_y, render_z = world_to_render(torpedo["x"], torpedo["depth"], torpedo["z"])
        horizontal_angle = math.degrees(math.atan2(torpedo["dx"], torpedo["dz"]))
        color = WEAPON_STATS[torpedo["weapon"]]["color"] if torpedo["weapon"] in WEAPON_STATS else (1.0, 0.12, 0.06)
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glRotatef(-horizontal_angle, 0, 0, 1)
        glColor3f(*color)
        glPushMatrix()
        glScalef(5.0, 19.0, 5.0)
        glutSolidCube(1.0)
        glPopMatrix()
        glTranslatef(0, -14.0, 0)
        gluSphere(q, 3.5, 7, 5)
        glPopMatrix()
    for decoy in decoys:
        pulse = 8.0 + math.sin(scene_time * 9.0 + decoy["phase"]) * 2.0
        render_x, render_y, render_z = world_to_render(decoy["x"], decoy["depth"], decoy["z"])
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glColor3f(0.42, 0.82, 1.0)
        gluSphere(q, pulse, 9, 6)
        glPopMatrix()
        draw_point_ring(decoy["x"], decoy["depth"], decoy["z"], 25.0 + pulse, (0.32, 0.70, 1.0))


def draw_explosions():
    """Render and animate expanding conventional and EMP blast effects."""
    q = get_quadric()
    for explosion in explosions:
        remaining = clamp(explosion["timer"] / explosion["duration"], 0.0, 1.0)
        growth = 0.25 + (1.0 - remaining) * 1.25
        render_x, render_y, render_z = world_to_render(explosion["x"], explosion["depth"], explosion["z"])
        glPushMatrix()
        glTranslatef(render_x, render_y, render_z)
        glColor3f(0.30, 0.55 + remaining * 0.25, 1.0) if explosion["emp"] else glColor3f(1.0, 0.18 + remaining * 0.58, 0.035)
        gluSphere(q, explosion["radius"] * growth, 14, 9)
        glColor3f(0.70, 0.90, 1.0) if explosion["emp"] else glColor3f(1.0, 0.82, 0.22)
        glPushMatrix()
        glScalef(0.48, 0.48, 0.48)
        gluSphere(q, explosion["radius"] * growth, 11, 7)
        glPopMatrix()
        glPopMatrix()


def draw_sonar_world():
    """Render the expanding sonar pulse and revealed contact markers."""
    if not sonar_active:
        return
    for offset in (0.0, -18.0, -36.0):
        radius = max(0.0, sonar_radius + offset)
        if radius > 0:
            draw_point_ring(player["x"], player["depth"], player["z"], radius, current_palette()["hud"])


def objective_target():
    """Return the most relevant world-space target for navigation guidance."""
    if mission_index == 0 and mission_progress < len(gates):
        gate = gates[mission_progress]
        return gate["x"], gate["depth"], gate["z"]
    if mission_index == 1:
        remaining = [item for item in collectibles if not item["collected"]]
        if remaining:
            target = min(remaining, key=distance_to_player)
            return target["x"], target["depth"], target["z"]
    if mission_index == 3:
        remaining = [mine for mine in mines if mine["active"]]
        if remaining:
            target = min(remaining, key=distance_to_player)
            return target["x"], target["depth"], target["z"]
    if mission_index == 4 and escort is not None and escort["route_index"] < len(ESCORT_ROUTE):
        return ESCORT_ROUTE[escort["route_index"]]
    if mission_index == 5 and fortress is not None:
        remaining = [node for node in fortress["nodes"] if not node["destroyed"]]
        if remaining:
            target = min(remaining, key=distance_to_player)
            return target["x"], target["depth"], target["z"]
        return fortress["x"], fortress["depth"], fortress["z"]
    if mission_index == 6:
        boss = next((enemy for enemy in enemies if enemy["kind"] == "boss"), None)
        if boss:
            return boss["x"], boss["depth"], boss["z"]
    return extraction if mission_index == 7 else None


def draw_wrapped(x, y, text, width=70, color=TEXT_COLOR, spacing=25):
    """Wrap a long message by words and draw it as multiple HUD lines."""
    line = ""
    for word in str(text).split():
        if len(line) + len(word) + 1 > width:
            draw_text(x, y, line, color)
            y -= spacing
            line = ""
        line = (line + " " + word).strip()
    if line:
        draw_text(x, y, line, color)
    return y - spacing


def draw_panel(x, y, width, height, accent=None):
    """Draw a dark HUD panel with an optional colored accent edge."""
    draw_rect(x, y, width, height, (0.014, 0.057, 0.078))
    draw_rect(x, y + height - 3, width, 3, accent or current_palette()["hud"])


def ui_buttons():
    """Build clickable button rectangles for the current game screen."""
    # The same button list is used for drawing and mouse clicks.
    if restart_return_state is not None:
        return [("cancel_restart", "KEEP PLAYING", 365, 280, 260, 48),
                ("confirm_restart", "RESTART CAMPAIGN", 650, 280, 270, 48)]
    if show_help:
        return [("help", "BACK  [H / ESC]", 490, 185, 300, 48)]
    if state == CONSOLE:
        buttons = []
        for index in range(3):
            y = 475 - index * 78
            buttons.extend([("prev%d" % index, "<", 855, y, 48, 44),
                            ("next%d" % index, ">", 922, y, 48, 44)])
        buttons += [("continue", "APPLY & RETURN  [ENTER]" if console_return_state else "DEPLOY VESSEL  [ENTER]", 290, 185, 450, 48),
                    ("help", "HOW TO PLAY  [H]", 760, 185, 230, 48)]
        if console_return_state is None:
            buttons.append(("quit", "QUIT", 1100, 30, 150, 40))
        return buttons
    if state == PLAYING:
        return [("pause", "PAUSE [P]", 1010, 745, 120, 42),
                ("help", "HELP [H]", 1142, 745, 112, 42)] + [
            ("weapon%d" % i, "%s  %02d" % (name, ammo[name]), 24 + i * 170, 28, 158, 48)
            for i, name in enumerate(WEAPON_ORDER)
        ] + [("sonar", "SONAR [R]", 534, 28, 150, 48),
             ("decoy", "DECOY [F]  %d" % decoy_count, 696, 28, 170, 48),
             ("upgrade", "UPGRADE [U]  %d" % (UPGRADE_BASE_COST * (weapon_levels[weapon] + 1)), 878, 28, 250, 48)]
    if state == PAUSED:
        return [("pause", "RESUME  [P / ESC]", 350, 455, 580, 50),
                ("console", "VESSEL PROFILE  [C]", 350, 385, 280, 48),
                ("help", "HOW TO PLAY  [H]", 650, 385, 280, 48),
                ("restart", "RESTART  [X]", 350, 315, 280, 48),
                ("quit", "QUIT GAME", 650, 315, 280, 48)]
    if state in (BRIEFING, MISSION_COMPLETE):
        return [("continue", "LAUNCH OPERATION  [ENTER]" if state == BRIEFING else "NEXT OPERATION  [ENTER]", 290, 185, 450, 48),
                ("help", "HOW TO PLAY  [H]", 760, 185, 230, 48)]
    return [("restart", "NEW CAMPAIGN  [ENTER]", 290, 185, 450, 48),
            ("quit", "QUIT GAME", 760, 185, 230, 48)]


def draw_buttons():
    """Render the current screen's buttons with hover and selection feedback."""
    for action, label, x, y, width, height in ui_buttons():
        hovered = x <= mouse_ui[0] <= x + width and y <= mouse_ui[1] <= y + height
        selected = action.startswith("weapon") and WEAPON_ORDER[int(action[-1])] == weapon
        color = current_palette()["hud"] if hovered or selected else (0.10, 0.27, 0.32)
        draw_rect(x, y, width, height, color)
        draw_rect(x + 2, y + 2, width - 4, height - 4,
                  (0.06, 0.20, 0.25) if hovered else (0.025, 0.10, 0.14))
        draw_text(x + 13, y + height / 2 - 6, label, TEXT_COLOR if hovered or selected else MUTED_TEXT)


def draw_tactical_map():
    """Render the north-up sonar map, contacts, player, and objective marker."""
    left, bottom, size = 1000, 160, 254
    cx, cy, radius = 1127, 280, 100
    draw_panel(left, bottom, size, size)
    draw_text(left + 15, bottom + size - 28, "SONAR / NORTH UP", current_palette()["hud"])
    for offset in (-50, 0, 50):
        draw_rect(cx + offset, cy - radius, 1, radius * 2, (0.035, 0.15, 0.18))
        draw_rect(cx - radius, cy + offset, radius * 2, 1, (0.035, 0.15, 0.18))
    enter_overlay()
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for ring in (50, 100):
        glColor3f(0.08, 0.33, 0.36)
        for point in range(90):
            angle = point * math.pi / 45
            glVertex3f(cx + math.sin(angle) * ring, cy + math.cos(angle) * ring, 0)
    if sonar_active:
        glColor3f(*GREEN)
        for point in range(120):
            angle = point * math.pi / 60
            r = sonar_radius / SONAR_MAX_RADIUS * radius
            glVertex3f(cx + math.sin(angle) * r, cy + math.cos(angle) * r, 0)
    glEnd()
    glPointSize(6.0)
    glBegin(GL_POINTS)
    contacts = [(enemy, RED) for enemy in enemies if enemy["revealed"]]
    contacts += [(mine, AMBER) for mine in mines if mine["active"] and mine["revealed"]]
    contacts += [(item, GREEN) for item in collectibles if item["revealed"] and not item["collected"]]
    if escort is not None:
        contacts.append((escort, AMBER))
    for item, color in contacts:
        dx, dz = item["x"] - player["x"], item["z"] - player["z"]
        if math.hypot(dx, dz) <= SONAR_MAX_RADIUS:
            glColor3f(*color)
            glVertex3f(cx + dx / SONAR_MAX_RADIUS * radius, cy + dz / SONAR_MAX_RADIUS * radius, 0)
    target = objective_target()
    if target:
        dx, dz = target[0] - player["x"], target[2] - player["z"]
        factor = radius / max(SONAR_MAX_RADIUS, math.hypot(dx, dz))
        glColor3f(*current_palette()["hud"])
        glVertex3f(cx + dx * factor, cy + dz * factor, 0)
    glColor3f(1, 1, 1)
    glVertex3f(cx, cy, 0)
    dx, dz = heading_vector(player["angle"])
    glVertex3f(cx + dx * 9, cy + dz * 9, 0)
    glEnd()
    leave_overlay()
    draw_text(left + 15, bottom + 10, "CYAN GOAL / RED ENEMY", MUTED_TEXT)


def draw_console():
    """Render the vessel configuration screen and current option values."""
    draw_text(290, 605, "VESSEL CONFIGURATION", current_palette()["hud"])
    draw_text(290, 565, "Choose your profile. Arrow keys or click < / > to change.", MUTED_TEXT)
    fields = (("HULL PALETTE", current_palette()["name"]),
              ("DIFFICULTY", current_difficulty()["name"]), ("CALLSIGN", current_callsign()))
    for index, (label, value) in enumerate(fields):
        y = 475 - index * 78
        draw_rect(290, y, 545, 44, (0.035, 0.15, 0.19) if profile["cursor"] == index else (0.02, 0.09, 0.12))
        draw_text(306, y + 15, label, MUTED_TEXT)
        draw_text(520, y + 15, value, current_palette()["hud"])
    draw_wrapped(290, 280, current_difficulty()["description"], 70)
    draw_text(290, 246, "Profile changes apply now; difficulty applies to the next operation.", MUTED_TEXT)


def draw_briefing():
    """Render the active operation's briefing, objective, notes, and reward."""
    mission = mission_data()
    draw_text(290, 605, "%s / %s" % (mission["code"], mission["title"]), current_palette()["hud"])
    draw_text(290, 554, "YOUR MISSION", AMBER)
    draw_wrapped(290, 520, mission["briefing"], 69)
    draw_text(290, 432, objective_text(), TEXT_COLOR)
    draw_text(290, 375, "FIELD NOTES", AMBER)
    draw_wrapped(290, 340, MISSION_TIPS[mission_index], 69)
    draw_text(290, 255, "REWARD / " + mission["reward"], GREEN)


def draw_help_panel():
    """Render the paused control-reference overlay."""
    draw_panel(250, 155, 780, 510)
    draw_text(290, 612, "HOW TO PLAY / SIMULATION SUSPENDED", current_palette()["hud"])
    left = (("NAVIGATE", "W / S   Set throttle (stays on)", "A / D   Hold to steer", "Q / E   Hold to ascend / dive", "B       Stop engines", "V       Toggle silent running"),
            ("COMBAT", "SPACE / Left click   Fire", "T   Change weapon", "R / Right click   Scan sonar", "F   Deploy decoy", "U   Upgrade using score"))
    for column, lines in enumerate(left):
        for row, line in enumerate(lines):
            draw_text(290 + column * 370, 548 - row * 34, line, AMBER if row == 0 else TEXT_COLOR)
    draw_text(290, 303, "1 / 2 / 3  Camera views     Middle-drag  Orbit     Arrows  Camera", MUTED_TEXT)
    draw_text(290, 270, "C  Vessel profile     P / ESC  Pause     X  Restart confirmation", MUTED_TEXT)


def draw_navigation():
    """Render bearing, distance, steering, and depth guidance to the objective."""
    target = objective_target()
    draw_panel(480, 695, 495, 92)
    if target is None:
        draw_text(498, 753, "HEADING %03d / SEARCH CONTACTS" % player["angle"], current_palette()["hud"])
        draw_text(498, 721, "R to scan. Sonar reveals nearby hostiles.", MUTED_TEXT)
        return
    bearing = angle_to_target(player["x"], player["z"], target[0], target[2]) % 360
    delta = (bearing - player["angle"] + 180) % 360 - 180
    vertical = target[1] - player["depth"]
    steering = "ON COURSE" if abs(delta) < 8 else ("LEFT A" if delta < 0 else "RIGHT D") + " %03d" % abs(delta)
    depth_hint = "DEPTH OK" if abs(vertical) < 8 else ("DIVE E" if vertical > 0 else "ASCEND Q") + " %dm" % abs(vertical)
    distance = distance_3d(player["x"], player["depth"], player["z"], *target)
    draw_text(498, 753, "WAYPOINT  %04dm  /  BEARING %03d" % (distance, bearing), current_palette()["hud"])
    draw_text(498, 721, steering + "   /   " + depth_hint, TEXT_COLOR)


def draw_hud():
    """Render gameplay instruments or the full overlay for the current game state."""
    global overlay_layer
    overlay_layer = 0
    glClear(GL_DEPTH_BUFFER_BIT)
    hud = current_palette()["hud"]
    if state == PLAYING and not show_help and restart_return_state is None:
        if aim_ui is not None:
            ax, ay = aim_ui
            color = WEAPON_STATS[weapon]["color"] if ammo[weapon] else RED
            for side in (-1, 1):
                draw_rect(ax + side * 15 - 4, ay, 8, 2, color)
                draw_rect(ax, ay + side * 15 - 4, 2, 8, color)
            draw_bar(ax - 20, ay - 29, 40, 6, 1 - fire_cooldown / PLAYER_FIRE_COOLDOWN, color)
        draw_panel(24, 695, 430, 92)
        draw_text(40, 756, current_callsign() + " / HULL %d%%" % player["hull"], hud)
        draw_bar(40, 733, 396, 10, player["hull"] / player["max_hull"], GREEN if player["hull"] > 35 else RED)
        draw_text(40, 710, "DEPTH %03dm   THRUST %+d%%   %s" % (player["depth"], player_throttle() * 100, "SILENT" if player["silent_running"] else "ACTIVE"), TEXT_COLOR)
        draw_panel(24, 556, 430, 121)
        draw_text(40, 648, "%s / %s" % (mission_data()["code"], mission_data()["title"]), AMBER)
        draw_wrapped(40, 617, objective_text(), 43)
        draw_bar(40, 570, 395, 9, mission_progress / MISSION_GOALS[mission_index], hud)
        draw_navigation()
        draw_tactical_map()
        sonar_text = "SCANNING" if sonar_active else "READY" if sonar_cooldown <= 0 else "%.1fs" % sonar_cooldown
        draw_text(1010, 700, "SONAR " + sonar_text, GREEN if sonar_cooldown <= 0 else MUTED_TEXT)
        draw_bar(1010, 679, 244, 8, 1 - sonar_cooldown / SONAR_COOLDOWN, hud)
        draw_text(1010, 652, "SCORE %07d" % score, TEXT_COLOR)
        draw_text(1010, 624, "TIME " + format_time(mission_elapsed), MUTED_TEXT)
        if escort is not None:
            draw_text(500, 650, "ATLAS / " + ("WAITING - RETURN TO ESCORT" if escort["waiting"] else "UNDERWAY"), AMBER)
            draw_bar(500, 627, 450, 10, escort["health"] / escort["max_health"], GREEN)
        warning = ""
        if player["depth"] > SAFE_DEPTH:
            warning = "CRUSH DEPTH / HOLD Q TO ASCEND"
        elif player["hull"] <= 35:
            warning = "HULL CRITICAL / EVADE HOSTILE FIRE"
        elif any(t["owner"] == "ENEMY" and distance_to_player(t) < 220 for t in torpedoes):
            warning = "INCOMING TORPEDO / F TO DEPLOY DECOY"
        if warning:
            draw_panel(480, 557, 495, 48, RED)
            draw_text(496, 575, warning, AMBER)
        draw_panel(24, 151, 940, 57)
        draw_wrapped(40, 184, MISSION_TIPS[mission_index], 91, MUTED_TEXT, 22)
        if status_timer > 0:
            draw_wrapped(40, 126, status_message, 88, TEXT_COLOR, 22)
        draw_text(25, 88, "T: WEAPON   SPACE: FIRE   LEVEL %d   |   %s CAMERA / 1 2 3 TO SWITCH" % (weapon_levels[weapon], ("CHASE", "PERISCOPE", "TACTICAL")[camera_mode - 1]), MUTED_TEXT)
    else:
        draw_text(38, 766, "SUBMARINE WARFARE", hud)
        draw_text(38, 733, "A B Y S S A L   C O M M A N D", MUTED_TEXT)
        draw_panel(250, 155, 780, 510)
        if restart_return_state is not None:
            draw_text(365, 555, "RESTART THE CAMPAIGN?", AMBER)
            draw_wrapped(365, 491, "Your current mission, score, upgrades and campaign progress will be reset.", 53)
            draw_text(365, 391, "ENTER confirms / ESC keeps your current game.", MUTED_TEXT)
        elif show_help:
            draw_help_panel()
        elif state == CONSOLE:
            draw_console()
        elif state == BRIEFING:
            draw_briefing()
        elif state == PAUSED:
            draw_text(350, 587, "PATROL PAUSED", AMBER)
            draw_text(350, 544, "Take your time. Your vessel and the ocean are paused.", MUTED_TEXT)
            draw_text(350, 255, "Progress is kept for this session while paused.", MUTED_TEXT)
        elif state == MISSION_COMPLETE:
            draw_text(290, 605, "OPERATION COMPLETE / " + mission_data()["code"], GREEN)
            draw_text(290, 547, mission_data()["title"], hud)
            draw_text(290, 483, "MISSION TIME  " + format_time(mission_elapsed), TEXT_COLOR)
            draw_text(290, 440, "SCORE  %07d     ACCURACY  %d%%" % (score, accuracy()), TEXT_COLOR)
            draw_text(290, 395, "HOSTILES SUNK  %d" % total_kills, TEXT_COLOR)
            draw_wrapped(290, 302, "REWARD / " + mission_data()["reward"], 68, GREEN)
        elif state == GAME_OVER:
            draw_text(290, 605, "MISSION FAILED", RED)
            draw_wrapped(290, 527, status_message, 68)
            draw_text(290, 431, "SCORE %07d / %d OPERATIONS COMPLETED" % (score, missions_completed), AMBER)
            draw_wrapped(290, 344, "Try Cadet difficulty for lighter opposition. Scan often and deploy decoys when torpedoes approach.", 65, MUTED_TEXT)
        elif state == VICTORY:
            draw_text(290, 605, "ABYSS SECURED / CAMPAIGN COMPLETE", GREEN)
            draw_text(290, 545, current_callsign() + " / " + current_difficulty()["name"], hud)
            draw_text(290, 484, "FINAL SCORE %07d / TIME %s" % (score, format_time(total_elapsed)), AMBER)
            draw_text(290, 432, "HOSTILES SUNK %d / ACCURACY %d%%" % (total_kills, accuracy()), TEXT_COLOR)
            draw_wrapped(290, 352, "COMMENDATIONS / " + (", ".join(achievements) or "Campaign graduate"), 66, GREEN)
    draw_buttons()


def accuracy():
    """Return the player's hit percentage, treating zero shots as zero accuracy."""
    if shots_fired == 0:
        return 0
    return int((shots_hit / shots_fired) * 100.0)


def format_time(seconds):
    """Format elapsed seconds as a zero-padded minutes-and-seconds string."""
    return "%02d:%02d" % (int(seconds // 60), int(seconds % 60))


# ============================================================
# Gameplay and combat
# ============================================================

def adjust_throttle(amount):
    """Move the throttle selector by one or more discrete levels."""
    if state != PLAYING:
        return
    player["throttle_index"] = int(clamp(player["throttle_index"] + amount, 0, 5))
    set_status("Throttle set to %d%%." % int(player_throttle() * 100), 1.2)


def stop_engines():
    """Set neutral throttle and report that the engines have stopped."""
    if state == PLAYING:
        player["throttle_index"] = 1
        set_status("All stop.", 1.2)


def turn_player(amount):
    """Change the player's heading and normalize it to a full circle."""
    if state == PLAYING:
        multiplier = 0.65 if abs(player_throttle()) >= 0.75 else 1.0
        player["angle"] = (player["angle"] + amount * multiplier) % 360.0


def change_depth(amount):
    """Move the requested depth while respecting surface, floor, and obstacles."""
    if state != PLAYING:
        return
    new_depth = clamp(player["depth"] + amount, SURFACE_LIMIT, WORLD_BOTTOM - PLAYER_RADIUS)
    if not obstacle_hit(player["x"], new_depth, player["z"], PLAYER_RADIUS):
        player["depth"] = new_depth
    else:
        set_status("Depth change blocked by terrain.", 1.5)


def toggle_silent_running():
    """Toggle stealth mode and report its gameplay tradeoff."""
    if state != PLAYING:
        return
    player["silent_running"] = not player["silent_running"]
    set_status("Silent running engaged: speed and detection reduced." if player["silent_running"] else "Silent running disengaged.", 2.0)


def cycle_weapon():
    """Select the next weapon type that still has ammunition."""
    global weapon
    if state != PLAYING:
        return
    weapon = WEAPON_ORDER[(WEAPON_ORDER.index(weapon) + 1) % len(WEAPON_ORDER)]
    set_status("Weapon selected: %s." % weapon, 1.4)


def upgrade_selected_weapon():
    """Spend score to upgrade the selected weapon when affordable."""
    global score
    if state != PLAYING:
        return
    level = weapon_levels[weapon]
    cost = UPGRADE_BASE_COST * (level + 1)
    if score < cost:
        set_status("Need %d points to upgrade %s." % (cost, weapon), 1.8)
        return
    score -= cost
    weapon_levels[weapon] += 1
    set_status("%s upgraded to level %d." % (weapon, weapon_levels[weapon]), 2.0)


def fire_player_torpedo():
    """Create a player torpedo if ammunition and cooldown permit firing."""
    global shots_fired, fire_cooldown
    if state != PLAYING or fire_cooldown > 0:
        return False
    if ammo[weapon] <= 0:
        set_status("%s magazine empty." % weapon.title(), 1.7)
        return False
    direction_x, direction_z = heading_vector(player["angle"])
    stats = WEAPON_STATS[weapon]
    target_id = ""
    if weapon == "HOMING":
        targets = [enemy for enemy in enemies if enemy["revealed"] and distance_to_player(enemy) <= 540.0]
        if targets:
            target_id = min(targets, key=distance_to_player)["id"]
    torpedoes.append({"owner": "PLAYER", "weapon": weapon, "x": player["x"] + direction_x * 64.0, "depth": player["depth"], "z": player["z"] + direction_z * 64.0, "dx": direction_x, "dy": 0.0, "dz": direction_z, "speed": stats["speed"], "damage": stats["damage"] * (1.0 + weapon_levels[weapon] * 0.15), "travelled": 0.0, "target_id": target_id})
    ammo[weapon] -= 1
    shots_fired += 1
    fire_cooldown = PLAYER_FIRE_COOLDOWN
    set_status("%s torpedo launched%s." % (weapon.title(), " / target locked" if target_id else ""), 1.2)
    alert_nearby(player["x"], player["depth"], player["z"], 370.0)
    return True


def deploy_decoy():
    """Launch a decoy behind the player when one is available."""
    global decoy_count
    if state != PLAYING:
        return False
    if decoy_count <= 0:
        set_status("No acoustic decoys remaining.", 1.6)
        return False
    back_x, back_z = heading_vector(player["angle"] + 180.0)
    decoys.append({"x": player["x"] + back_x * 42.0, "depth": player["depth"], "z": player["z"] + back_z * 42.0, "timer": 5.0, "phase": scene_time})
    decoy_count -= 1
    set_status("Acoustic decoy deployed.", 1.5)
    return True


def activate_sonar():
    """Start an active sonar sweep unless the system is cooling down."""
    global sonar_active, sonar_radius, sonar_overlay_timer
    if state != PLAYING or player["silent_running"] or sonar_active:
        if player["silent_running"]:
            set_status("Disable silent running before active sonar.", 1.8)
        return False
    if sonar_cooldown > 0:
        set_status("Sonar recharging: %.1fs." % sonar_cooldown, 1.5)
        return False
    sonar_active = True
    sonar_radius = 0.0
    sonar_overlay_timer = 3.2
    set_status("Active sonar pulse transmitted.", 1.5)
    return True


def alert_nearby(x, depth, z, radius):
    """Reveal and alert enemies within a radius of a world position."""
    for enemy in enemies:
        if distance_3d(x, depth, z, enemy["x"], enemy["depth"], enemy["z"]) <= radius:
            enemy["alerted"] = True
            enemy["state"] = "CHASE"


def take_player_damage(amount, message, cooldown=True):
    """Apply hull damage with invulnerability timing and failure handling."""
    global damage_taken, state
    if state != PLAYING or (cooldown and player["damage_cooldown"] > 0):
        return
    player["hull"] = max(0.0, player["hull"] - amount)
    damage_taken += amount
    player["damage_cooldown"] = 0.18 if cooldown else 0.0
    set_status(message, 1.8)
    if player["hull"] <= 0:
        state = GAME_OVER
        player["throttle_index"] = 1
        set_status("VESSEL LOST - press X to restart campaign", 999.0)


def update_ambient(dt):
    """Advance looping bubble, fish, and kelp ambient animations."""
    for bubble in bubbles:
        bubble["depth"] -= bubble["speed"] * dt
        bubble["x"] += math.sin(scene_time * 0.7 + bubble["phase"]) * dt * 1.8
        if bubble["depth"] < SURFACE_LIMIT:
            bubble["depth"] = WORLD_BOTTOM - 4.0
    for animal in fish:
        school, phase = animal["school"], animal["phase"]
        orbit = scene_time * 0.10 + school * 1.7
        target_x = math.sin(school * 1.7) * 330 + math.sin(orbit) * 120 + math.cos(phase) * 40
        target_z = math.cos(school * 1.7) * 230 + math.cos(orbit) * 125 + math.sin(phase) * 40
        dx, dz = target_x - animal["x"], target_z - animal["z"]
        flee = distance_to_player(animal) < 125
        if flee:
            dx += (animal["x"] - player["x"]) * 6
            dz += (animal["z"] - player["z"]) * 6
        for rock in rocks:
            distance = distance_3d(animal["x"], animal["depth"], animal["z"], rock["x"], rock["depth"], rock["z"])
            if distance < rock["radius"] + 45:
                dx += (animal["x"] - rock["x"]) * 8
                dz += (animal["z"] - rock["z"]) * 8
        target_angle = math.degrees(math.atan2(dx, dz))
        animal["angle"] = approach_angle(animal["angle"], target_angle, (180 if flee else 80) * dt)
        vx, vz = heading_vector(animal["angle"])
        speed = 52 if flee else 24 + school * 3
        animal["x"] = clamp(animal["x"] + vx * speed * dt, -660, 660)
        animal["z"] = clamp(animal["z"] + vz * speed * dt, -660, 660)
        target_depth = 80 + school * 38 + math.sin(scene_time * 0.7 + phase) * 9
        animal["depth"] += (target_depth - animal["depth"]) * min(1.0, dt * 2)


def update_player(dt):
    """Advance player movement, collisions, cooldowns, and held-key steering."""
    speed = PLAYER_MAX_SPEED * player_throttle()
    if player["silent_running"]:
        speed *= 0.52
    direction_x, direction_z = heading_vector(player["angle"])
    proposed_x = player["x"] + direction_x * speed * dt
    proposed_z = player["z"] + direction_z * speed * dt
    if abs(speed) > 0.01:
        if inside_world(proposed_x, player["depth"], proposed_z, PLAYER_RADIUS) and not obstacle_hit(proposed_x, player["depth"], proposed_z, PLAYER_RADIUS):
            player["x"], player["z"] = proposed_x, proposed_z
        else:
            player["throttle_index"] = 1
            set_status("Collision avoidance: engines stopped.", 1.8)
        player["propeller_angle"] = (player["propeller_angle"] + abs(speed) * dt * 7.5) % 360.0
    if player["depth"] > SAFE_DEPTH:
        take_player_damage(5.0 * dt, "CRUSH DEPTH: hull integrity falling", cooldown=False)
        if "DEEP DIVER" not in achievements:
            achievements.append("DEEP DIVER")


def update_sonar(dt):
    """Expand the sonar wave and reveal contacts reached by its radius."""
    global sonar_cooldown, sonar_overlay_timer, sonar_radius, sonar_active
    sonar_cooldown = max(0.0, sonar_cooldown - dt)
    sonar_overlay_timer = max(0.0, sonar_overlay_timer - dt)
    if not sonar_active:
        return
    sonar_radius += SONAR_SPEED * dt
    for enemy in enemies:
        if distance_to_player(enemy) <= sonar_radius:
            enemy["revealed"] = True
            enemy["alerted"] = True
            enemy["state"] = "CHASE"
            sonar_contacts.add(enemy["id"])
    for mine in mines:
        if mine["active"] and distance_to_player(mine) <= sonar_radius:
            mine["revealed"] = True
    for item in collectibles:
        if not item["collected"] and distance_to_player(item) <= sonar_radius:
            item["revealed"] = True
    if sonar_radius >= SONAR_MAX_RADIUS:
        sonar_radius = SONAR_MAX_RADIUS
        sonar_active = False
        sonar_cooldown = SONAR_COOLDOWN
        sonar_overlay_timer = 3.0
        set_status("Sonar sweep complete: %d contacts logged." % len(sonar_contacts), 2.0)


def update_escort(dt):
    """Move Atlas along its route and manage waiting and escort failure rules."""
    global mission_progress
    if escort is None or escort["route_index"] >= len(ESCORT_ROUTE):
        return
    separation = distance_to_player(escort)
    escort["waiting"] = separation > 260.0
    if escort["waiting"]:
        return
    target = ESCORT_ROUTE[escort["route_index"]]
    dx = target[0] - escort["x"]
    dy = target[1] - escort["depth"]
    dz = target[2] - escort["z"]
    direction_x, direction_y, direction_z = normalize_3d(dx, dy, dz)
    escort["angle"] = approach_angle(escort["angle"], angle_to_target(escort["x"], escort["z"], target[0], target[2]), 55.0 * dt)
    escort["x"] += direction_x * 58.0 * dt
    escort["depth"] += direction_y * 58.0 * dt
    escort["z"] += direction_z * 58.0 * dt
    if distance_3d(escort["x"], escort["depth"], escort["z"], *target) < 20.0:
        escort["x"], escort["depth"], escort["z"] = target
        escort["route_index"] += 1
        mission_progress = min(4, escort["route_index"] - 1)
        if escort["route_index"] < len(ESCORT_ROUTE):
            set_status("Atlas reached escort waypoint %d/4." % mission_progress, 2.0)


def update_enemies(dt):
    """Advance enemy detection, pursuit, attacks, and collision avoidance."""
    for enemy in list(enemies):
        enemy["fire_cooldown"] = max(0.0, enemy["fire_cooldown"] - dt)
        enemy["contact_cooldown"] = max(0.0, enemy["contact_cooldown"] - dt)
        enemy["stunned"] = max(0.0, enemy["stunned"] - dt)
        if enemy["stunned"] > 0:
            continue
        player_distance = distance_to_player(enemy)
        detection = 175.0 if player["silent_running"] else 315.0
        if player_distance <= detection or enemy["alerted"] or enemy["kind"] == "boss":
            enemy["alerted"] = True
            if enemy["state"] == "PATROL":
                enemy["state"] = "CHASE"
        target_x, target_depth, target_z, target_name, target_distance = player["x"], player["depth"], player["z"], "PLAYER", player_distance
        if escort is not None:
            escort_distance = distance_3d(enemy["x"], enemy["depth"], enemy["z"], escort["x"], escort["depth"], escort["z"])
            if escort_distance < target_distance * 1.15:
                target_x, target_depth, target_z, target_name, target_distance = escort["x"], escort["depth"], escort["z"], "ESCORT", escort_distance
        if enemy["state"] == "PATROL":
            enemy["patrol_time"] += dt
            patrol_x = enemy["origin_x"] + math.cos(enemy["patrol_time"] * 0.55 + enemy["phase_seed"]) * enemy["patrol_radius"]
            patrol_z = enemy["origin_z"] + math.sin(enemy["patrol_time"] * 0.55 + enemy["phase_seed"]) * enemy["patrol_radius"]
            enemy["angle"] = approach_angle(enemy["angle"], angle_to_target(enemy["x"], enemy["z"], patrol_x, patrol_z), 42.0 * dt)
            move_x, move_z = heading_vector(enemy["angle"])
            enemy["x"] += move_x * enemy["speed"] * 0.45 * dt
            enemy["z"] += move_z * enemy["speed"] * 0.45 * dt
        elif enemy["state"] in ("CHASE", "ATTACK"):
            attack_range = 270.0 if enemy["kind"] == "boss" else 235.0
            enemy["angle"] = approach_angle(enemy["angle"], angle_to_target(enemy["x"], enemy["z"], target_x, target_z), (32.0 if enemy["kind"] in ("heavy", "boss") else 62.0) * dt)
            enemy["depth"] += clamp(target_depth - enemy["depth"], -18.0 * dt, 18.0 * dt)
            if target_distance > attack_range:
                enemy["state"] = "CHASE"
                move_x, move_z = heading_vector(enemy["angle"])
                enemy["x"] += move_x * enemy["speed"] * dt
                enemy["z"] += move_z * enemy["speed"] * dt
            else:
                enemy["state"] = "ATTACK"
                if enemy["fire_cooldown"] <= 0.0:
                    fire_enemy(enemy, target_x, target_depth, target_z, target_name)
                    enemy["fire_cooldown"] = enemy["fire_delay"] * (0.72 if enemy["kind"] == "boss" and enemy["boss_phase"] >= 2 else 1.0)
        enemy["x"] = clamp(enemy["x"], -WORLD_HALF_SIZE + 45.0, WORLD_HALF_SIZE - 45.0)
        enemy["z"] = clamp(enemy["z"], -WORLD_HALF_SIZE + 45.0, WORLD_HALF_SIZE - 45.0)
        enemy["depth"] = clamp(enemy["depth"], SURFACE_LIMIT + 15.0, WORLD_BOTTOM - 40.0)
        if player_distance <= enemy["radius"] + PLAYER_RADIUS and enemy["contact_cooldown"] <= 0:
            take_player_damage(8.0 * current_difficulty()["enemy_damage"], "Enemy hull collision")
            enemy["contact_cooldown"] = 1.2
        if enemy["kind"] == "boss":
            update_boss_phase(enemy)


def update_boss_phase(boss):
    """Change Leviathan's combat phase and trigger phase reinforcements."""
    health_ratio = boss["health"] / boss["max_health"]

    if health_ratio <= 0.34:
        desired_phase = 3
    elif health_ratio <= 0.67:
        desired_phase = 2
    else:
        desired_phase = 1

    desired = desired_phase
    if desired <= boss["boss_phase"]:
        return
    boss["boss_phase"] = desired
    boss["speed"] *= 1.15
    boss["fire_delay"] *= 0.88
    set_status("LEVIATHAN PHASE %d: reinforcements incoming!" % desired, 4.0)
    add_explosion(boss["x"], boss["depth"], boss["z"], 55.0, 0.9, emp=True)
    side = -1.0 if desired == 2 else 1.0
    reinforcement = make_enemy("hunter", clamp(boss["x"] + side * 170.0, -620.0, 620.0), clamp(boss["depth"] - 45.0, 45.0, 300.0), clamp(boss["z"] + 145.0, -620.0, 620.0), boss["angle"] + 180.0, "LEVIATHAN-WING-%d" % desired)
    reinforcement.update({"alerted": True, "revealed": True, "state": "CHASE"})
    enemies.append(reinforcement)


def fire_enemy(enemy, target_x, target_depth, target_z, target_name):
    """Create an enemy torpedo aimed at a named target position."""
    dx, dy, dz = normalize_3d(target_x - enemy["x"], target_depth - enemy["depth"], target_z - enemy["z"])
    directions = [(dx, dy, dz)]
    if enemy["kind"] == "boss" and enemy["boss_phase"] >= 2:
        base_angle = math.atan2(dx, dz)
        spread = math.radians(7.5)
        directions = [(math.sin(base_angle - spread), dy, math.cos(base_angle - spread)), (dx, dy, dz), (math.sin(base_angle + spread), dy, math.cos(base_angle + spread))]
    for direction_x, direction_y, direction_z in directions:
        direction_x, direction_y, direction_z = normalize_3d(direction_x, direction_y, direction_z)
        torpedoes.append({"owner": "ENEMY", "weapon": "ENEMY", "x": enemy["x"], "depth": enemy["depth"], "z": enemy["z"], "dx": direction_x, "dy": direction_y, "dz": direction_z, "speed": 235.0 if enemy["kind"] != "boss" else 260.0, "damage": enemy["damage"], "travelled": 0.0, "target_id": target_name})


def steer_homing(torpedo, dt):
    """Turn a homing player torpedo toward its closest valid target."""
    target = next((enemy for enemy in enemies if enemy["id"] == torpedo["target_id"]), None)
    if target is None:
        candidates = [enemy for enemy in enemies if enemy["revealed"]]
        if not candidates:
            return
        target = min(candidates, key=lambda enemy: distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], enemy["x"], enemy["depth"], enemy["z"]))
        torpedo["target_id"] = target["id"]
    desired = normalize_3d(target["x"] - torpedo["x"], target["depth"] - torpedo["depth"], target["z"] - torpedo["z"])
    factor = clamp(dt * 2.8, 0.0, 1.0)
    torpedo["dx"], torpedo["dy"], torpedo["dz"] = normalize_3d(torpedo["dx"] * (1.0 - factor) + desired[0] * factor, torpedo["dy"] * (1.0 - factor) + desired[1] * factor, torpedo["dz"] * (1.0 - factor) + desired[2] * factor)


def steer_to_decoy(torpedo, dt):
    """Redirect an enemy torpedo toward a nearby active decoy."""
    if not decoys:
        return
    nearest = min(decoys, key=lambda item: distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], item["x"], item["depth"], item["z"]))
    separation = distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], nearest["x"], nearest["depth"], nearest["z"])
    if separation > 220.0:
        return
    desired = normalize_3d(nearest["x"] - torpedo["x"], nearest["depth"] - torpedo["depth"], nearest["z"] - torpedo["z"])
    factor = clamp(dt * 3.4, 0.0, 1.0)
    torpedo["dx"], torpedo["dy"], torpedo["dz"] = normalize_3d(torpedo["dx"] * (1.0 - factor) + desired[0] * factor, torpedo["dy"] * (1.0 - factor) + desired[1] * factor, torpedo["dz"] * (1.0 - factor) + desired[2] * factor)


def destroy_enemy(enemy):
    """Mark an enemy destroyed and award effects, score, and mission progress."""
    global total_kills
    if enemy not in enemies:
        return
    enemies.remove(enemy)
    total_kills += 1
    values = {"scout": 220, "hunter": 350, "heavy": 520, "boss": 2500}
    score_add(values[enemy["kind"]])
    add_explosion(enemy["x"], enemy["depth"], enemy["z"], 75.0 if enemy["kind"] == "boss" else 37.0 if enemy["kind"] == "heavy" else 29.0, 1.5 if enemy["kind"] == "boss" else 0.85)
    if enemy["kind"] == "boss":
        set_status("LEVIATHAN DESTROYED - command network offline", 5.0)
        if "LEVIATHAN SLAYER" not in achievements:
            achievements.append("LEVIATHAN SLAYER")
    else:
        set_status("Hostile %s destroyed." % enemy["kind"], 1.6)


def score_add(amount):
    """Add a difficulty-adjusted amount to the nonnegative campaign score."""
    global score
    score += score_value(amount)


def neutralize_mine(mine, safe=False, triggered=False):
    """Resolve a mine as disarmed or detonated and update mission progress."""
    global mission_progress, mines_disarmed
    if not mine["active"]:
        return
    mine["active"] = False
    if mission_index == 3:
        mission_progress += 1
    if safe:
        mines_disarmed += 1
        score_add(220)
        add_explosion(mine["x"], mine["depth"], mine["z"], 25.0, 0.65, emp=True)
        set_status("Mine safely disarmed by EMP: %d/5." % min(mission_progress, 5), 1.8)
    else:
        score_add(120)
        add_explosion(mine["x"], mine["depth"], mine["z"], 46.0, 0.85)
        if triggered or distance_to_player(mine) <= 100.0:
            take_player_damage(24.0, "Naval mine detonation")
        alert_nearby(mine["x"], mine["depth"], mine["z"], 390.0)


def player_torpedo_collision(torpedo):
    """Resolve one player torpedo against enemies and mission objects."""
    global shots_hit, mission_progress
    for enemy in list(enemies):
        if distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], enemy["x"], enemy["depth"], enemy["z"]) <= enemy["radius"] + 9.0:
            enemy["health"] -= torpedo["damage"]
            enemy.update({"alerted": True, "revealed": True, "state": "CHASE"})
            shots_hit += 1
            add_explosion(torpedo["x"], torpedo["depth"], torpedo["z"], 19.0 if enemy["kind"] != "boss" else 27.0, 0.48, torpedo["weapon"] == "EMP")
            if torpedo["weapon"] == "EMP":
                enemy["stunned"] = max(enemy["stunned"], 4.2)
            if enemy["health"] <= 0:
                destroy_enemy(enemy)
            return True
    for mine in mines:
        if mine["active"] and distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], mine["x"], mine["depth"], mine["z"]) <= mine["radius"] + 8.0:
            shots_hit += 1
            neutralize_mine(mine, safe=torpedo["weapon"] == "EMP")
            return True
    if fortress is not None:
        for node in fortress["nodes"]:
            if not node["destroyed"] and distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], node["x"], node["depth"], node["z"]) <= 34.0:
                node["health"] -= torpedo["damage"]
                shots_hit += 1
                add_explosion(node["x"], node["depth"], node["z"], 20.0, 0.5, torpedo["weapon"] == "EMP")
                if node["health"] <= 0:
                    node["destroyed"] = True
                    score_add(350)
                    mission_progress = sum(item["destroyed"] for item in fortress["nodes"])
                    set_status("Shield relay destroyed: %d/3." % mission_progress, 2.0)
                return True
        if not fortress["destroyed"] and distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], fortress["x"], fortress["depth"], fortress["z"]) <= 82.0:
            shots_hit += 1
            if fortress_shielded():
                set_status("Fortress shield absorbed the strike.", 1.7)
                add_explosion(torpedo["x"], torpedo["depth"], torpedo["z"], 24.0, 0.45, emp=True)
            else:
                fortress["health"] -= torpedo["damage"]
                add_explosion(torpedo["x"], torpedo["depth"], torpedo["z"], 25.0, 0.5)
                if fortress["health"] <= 0:
                    fortress["destroyed"] = True
                    mission_progress = 4
                    score_add(900)
                    add_explosion(fortress["x"], fortress["depth"], fortress["z"], 95.0, 1.5)
            return True
    return False


def enemy_torpedo_collision(torpedo):
    """Resolve one enemy torpedo against the player or escort vessel."""
    global state
    for decoy in list(decoys):
        if distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], decoy["x"], decoy["depth"], decoy["z"]) <= 18.0:
            decoys.remove(decoy)
            score_add(75)
            add_explosion(decoy["x"], decoy["depth"], decoy["z"], 18.0, 0.4, emp=True)
            return True
    if escort is not None and torpedo["target_id"] == "ESCORT" and distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], escort["x"], escort["depth"], escort["z"]) <= 33.0:
        escort["health"] = max(0.0, escort["health"] - torpedo["damage"])
        add_explosion(escort["x"], escort["depth"], escort["z"], 21.0, 0.5)
        if escort["health"] <= 0:
            state = GAME_OVER
            set_status("MISSION FAILED: Atlas was destroyed.", 999.0)
        return True
    if distance_3d(torpedo["x"], torpedo["depth"], torpedo["z"], player["x"], player["depth"], player["z"]) <= PLAYER_RADIUS + 9.0:
        take_player_damage(torpedo["damage"], "Hostile torpedo impact")
        add_explosion(player["x"], player["depth"], player["z"], 24.0, 0.55)
        return True
    return False


def update_torpedoes(dt):
    """Advance all torpedoes, homing behavior, lifetime, and collisions."""
    global torpedoes
    remaining = []
    for torpedo in torpedoes:
        if torpedo["owner"] == "PLAYER" and torpedo["weapon"] == "HOMING":
            steer_homing(torpedo, dt)
        elif torpedo["owner"] == "ENEMY":
            steer_to_decoy(torpedo, dt)
        step = torpedo["speed"] * dt
        torpedo["x"] += torpedo["dx"] * step
        torpedo["depth"] += torpedo["dy"] * step
        torpedo["z"] += torpedo["dz"] * step
        torpedo["travelled"] += step
        if torpedo["travelled"] > 1350.0 or not inside_world(torpedo["x"], torpedo["depth"], torpedo["z"]):
            continue
        if rock_hit(torpedo["x"], torpedo["depth"], torpedo["z"], 5.0):
            add_explosion(torpedo["x"], torpedo["depth"], torpedo["z"], 13.0, 0.35)
            continue
        hit = player_torpedo_collision(torpedo) if torpedo["owner"] == "PLAYER" else enemy_torpedo_collision(torpedo)
        if not hit:
            remaining.append(torpedo)
    torpedoes = remaining


def update_mines(dt):
    """Trigger mines approached by the player and advance their countdowns."""
    for mine in mines:
        if not mine["active"]:
            continue
        mine["depth"] = mine["base_depth"] + math.sin(scene_time * 1.35 + mine["phase"]) * 5.0
        if distance_to_player(mine) <= PLAYER_RADIUS + mine["radius"]:
            neutralize_mine(mine, safe=False, triggered=True)


def update_collectibles():
    """Collect mission pickups reached by the player submarine."""
    global mission_progress
    for item in collectibles:
        if not item["collected"] and distance_to_player(item) <= 42.0:
            item["collected"] = True
            mission_progress += 1
            score_add(250)
            set_status("Encrypted data pod recovered: %d/3." % mission_progress, 2.0)


def update_decoys(dt):
    """Advance deployed decoys and discard expired ones."""
    global decoys
    remaining = []
    for decoy in decoys:
        decoy["timer"] -= dt
        decoy["depth"] = max(SURFACE_LIMIT, decoy["depth"] - 7.0 * dt)
        if decoy["timer"] > 0:
            remaining.append(decoy)
    decoys = remaining


def update_explosions(dt):
    """Advance explosion ages and discard completed effects."""
    global explosions
    for explosion in explosions:
        explosion["timer"] -= dt
    explosions = [item for item in explosions if item["timer"] > 0]


def update_mission():
    """Evaluate the active operation's objectives and completion conditions."""
    global mission_progress
    if mission_index == 0:
        if mission_progress < len(gates) and distance_to_player(gates[mission_progress]) <= 62.0:
            gates[mission_progress]["passed"] = True
            mission_progress += 1
            score_add(180)
            set_status("Navigation gate passed: %d/3." % mission_progress, 2.0)
        if mission_progress >= 3:
            complete_mission()
    elif mission_index == 1 and mission_progress >= 3:
        complete_mission()
    elif mission_index == 2:
        mission_progress = len(sonar_contacts & {enemy["id"] for enemy in enemies})
        if mission_progress >= 4:
            complete_mission()
    elif mission_index == 3 and mission_progress >= 5:
        complete_mission()
    elif mission_index == 4 and escort is not None and escort["route_index"] >= len(ESCORT_ROUTE):
        mission_progress = 4
        complete_mission()
    elif mission_index == 5 and fortress is not None and fortress["destroyed"]:
        complete_mission()
    elif mission_index == 6 and not any(enemy["kind"] == "boss" for enemy in enemies):
        mission_progress = 1
        complete_mission()
    elif mission_index == 7 and extraction is not None and distance_to_player({"x": extraction[0], "depth": extraction[1], "z": extraction[2]}) <= 72.0:
        mission_progress = 1
        complete_mission()


def complete_mission():
    """Finish the operation once, record progress, and show its result screen."""
    global score, missions_completed, state
    if state != PLAYING:
        return
    score_add(1000 + max(0, int(1500.0 - mission_elapsed * 7.0)))
    missions_completed += 1
    player["throttle_index"] = 1
    torpedoes.clear()
    apply_reward(mission_index)
    if mission_index == len(MISSIONS) - 1:
        state = VICTORY
        set_status("CAMPAIGN COMPLETE - the abyss is secure", 999.0)
        if damage_taken <= 0.01:
            achievements.append("PERFECT PATROL")
    else:
        state = MISSION_COMPLETE
        set_status("Operation complete. Press ENTER for the next briefing.", 999.0)


def apply_reward(index):
    """Grant the ammunition, repair, or recharge reward for a completed mission."""
    global decoy_count, sonar_cooldown
    if index == 1:
        ammo["STANDARD"] += 4
    elif index == 2:
        ammo["HOMING"] += 2
    elif index == 3:
        player["hull"] = min(player["max_hull"], player["hull"] + 20.0)
    elif index == 4:
        decoy_count += 3
        sonar_cooldown = 0.0
    elif index == 5:
        for selected, amount in STARTING_AMMO.items():
            ammo[selected] = max(ammo[selected], amount)


def update_game(dt):
    """Advance timers and all simulation systems for one bounded frame step."""
    global scene_time, mission_elapsed, total_elapsed, status_timer, fire_cooldown
    dt = clamp(dt, 0.0, 0.05)
    if state == PAUSED or show_help or restart_return_state is not None:
        return
    scene_time += dt
    update_ambient(dt)
    if state != PLAYING:
        return
    mission_elapsed += dt
    total_elapsed += dt
    status_timer = max(0.0, status_timer - dt)
    player["damage_cooldown"] = max(0.0, player["damage_cooldown"] - dt)
    fire_cooldown = max(0.0, fire_cooldown - dt)
    turn_player(((b"d" in held_keys) - (b"a" in held_keys)) * 75.0 * dt)
    depth_step = ((b"e" in held_keys) - (b"q" in held_keys)) * 65.0 * dt
    if depth_step:
        change_depth(depth_step)
    if b" " in held_keys:
        fire_player_torpedo()
    # Stop here if this frame already caused a mission failure.
    for update in (update_player, update_sonar, update_escort, update_enemies,
                   update_torpedoes, update_mines):
        update(dt)
        if state != PLAYING:
            held_keys.clear()
            return
    update_collectibles()
    update_decoys(dt)
    update_explosions(dt)
    update_mission()


# ============================================================
# 6. Keyboard, special-key, and mouse controls
# ============================================================

def toggle_help():
    """Open or close the help overlay while preserving the underlying game state."""
    global show_help, help_return_state
    held_keys.clear()
    if show_help:
        show_help = False
        set_state(help_return_state)
        help_return_state = None
    else:
        help_return_state = state
        show_help = True
        if state == PLAYING:
            set_state(PAUSED)


def request_restart():
    """Open the campaign-restart confirmation or confirm an existing request."""
    global restart_return_state
    if state in (GAME_OVER, VICTORY) or (state == CONSOLE and console_return_state is None):
        reset_campaign(to_console=True)
    else:
        restart_return_state = state
        set_state(PAUSED)


def perform_ui_action(action):
    """Dispatch a named button action to the matching game command."""
    global restart_return_state, weapon
    held_keys.clear()
    if action == "cancel_restart":
        set_state(restart_return_state)
        restart_return_state = None
    elif action == "confirm_restart":
        reset_campaign(to_console=True)
    elif action == "restart":
        request_restart()
    elif action == "help":
        toggle_help()
    elif action == "pause":
        toggle_pause()
    elif action == "console":
        open_console()
    elif action == "continue":
        begin_or_continue()
    elif action == "quit":
        raise SystemExit(0)
    elif action.startswith(("prev", "next")):
        profile["cursor"] = int(action[-1])
        change_console_value(-1 if action.startswith("prev") else 1)
    elif action.startswith("weapon"):
        weapon = WEAPON_ORDER[int(action[-1])]
        set_status("%s selected. SPACE or left click to fire." % weapon.title(), 2)
    elif action == "sonar":
        activate_sonar()
    elif action == "decoy":
        deploy_decoy()
    elif action == "upgrade":
        upgrade_selected_weapon()


def keyboard_listener(key, x, y):
    """Handle normal-key presses for menus, gameplay, weapons, and overlays."""
    del x, y
    global camera_mode, camera_orbit
    key = key.lower()
    if key in pressed_keys:
        return
    pressed_keys.add(key)
    if restart_return_state is not None:
        if key == b"\x1b":
            perform_ui_action("cancel_restart")
        elif key in (b"\r", b"\n"):
            perform_ui_action("confirm_restart")
        return
    if show_help:
        if key in (b"h", b"\x1b"):
            toggle_help()
        return
    if key == b"h":
        toggle_help()
        return
    if key == b"\x1b":
        if state in (PLAYING, PAUSED):
            toggle_pause()
        elif state == CONSOLE and console_return_state is not None:
            confirm_console()
        return
    if key == b"x":
        request_restart()
        return
    if key == b"p" and state in (PLAYING, PAUSED):
        toggle_pause()
        return
    if key == b"c" and state in (PLAYING, PAUSED):
        open_console()
        return
    if key in (b"\r", b"\n"):
        if state in (GAME_OVER, VICTORY):
            request_restart()
        else:
            begin_or_continue()
        return
    if state == CONSOLE:
        if key in (b"w", b"s"):
            move_console_cursor(-1 if key == b"w" else 1)
        elif key in (b"a", b"d"):
            change_console_value(-1 if key == b"a" else 1)
        return
    if state != PLAYING:
        return
    if key in (b"1", b"2", b"3"):
        camera_mode = int(key)
        camera_orbit = 0
        return
    if key in (b"a", b"d", b"q", b"e", b" "):
        held_keys.add(key)
    if key == b"w":
        adjust_throttle(1)
    elif key == b"s":
        adjust_throttle(-1)
    elif key == b"b":
        stop_engines()
    elif key == b" ":
        fire_player_torpedo()
    elif key == b"t":
        cycle_weapon()
    elif key == b"r":
        activate_sonar()
    elif key == b"f":
        deploy_decoy()
    elif key == b"v":
        toggle_silent_running()
    elif key == b"u":
        upgrade_selected_weapon()


def keyboard_up_listener(key, x, y):
    """Stop continuous movement when a normal key is released."""
    del x, y
    held_keys.discard(key.lower())
    pressed_keys.discard(key.lower())


def special_key_listener(key, x, y):
    """Handle arrow-key navigation for menus, camera, and depth control."""
    del x, y
    global camera_height, camera_orbit
    if show_help or restart_return_state is not None:
        return
    if state == CONSOLE:
        if key == GLUT_KEY_UP:
            move_console_cursor(-1)
        elif key == GLUT_KEY_DOWN:
            move_console_cursor(1)
        elif key == GLUT_KEY_LEFT:
            change_console_value(-1)
        elif key == GLUT_KEY_RIGHT:
            change_console_value(1)
        return
    if state != PLAYING:
        return
    if key == GLUT_KEY_UP:
        camera_height = min(410.0, camera_height + 18.0)
    elif key == GLUT_KEY_DOWN:
        camera_height = max(90.0, camera_height - 18.0)
    elif key == GLUT_KEY_LEFT:
        camera_orbit = (camera_orbit - 6.0) % 360.0
    elif key == GLUT_KEY_RIGHT:
        camera_orbit = (camera_orbit + 6.0) % 360.0


def screen_to_ui(x, y):
    """Convert window mouse coordinates to the fixed virtual HUD coordinate system."""
    vx, vy, width, height = viewport
    return (x - vx) * WINDOW_WIDTH / width, (screen_height - y - vy) * WINDOW_HEIGHT / height


def mouse_listener(button, button_state, x, y):
    """Handle button clicks, HUD actions, firing, and camera-drag state."""
    global mouse_dragging, mouse_last_x, mouse_last_y, mouse_ui
    mouse_ui = screen_to_ui(x, y)
    if button == GLUT_MIDDLE_BUTTON:
        mouse_dragging = button_state == GLUT_DOWN and state == PLAYING and not show_help
        mouse_last_x, mouse_last_y = x, y
        return
    if button_state != GLUT_DOWN:
        return
    for action, label, bx, by, width, height in ui_buttons():
        if bx <= mouse_ui[0] <= bx + width and by <= mouse_ui[1] <= by + height:
            if button == GLUT_LEFT_BUTTON:
                perform_ui_action(action)
            return
    if state != PLAYING or show_help or restart_return_state is not None:
        return
    ux, uy = mouse_ui
    if not (0 <= ux <= WINDOW_WIDTH and 0 <= uy <= WINDOW_HEIGHT):
        return
    # Do not fire when the click is on the HUD.
    if uy < 210 or uy > 695 or (ux < 455 and uy > 556) or (ux > 995 and uy < 720):
        return
    if button == GLUT_LEFT_BUTTON:
        fire_player_torpedo()
    elif button == GLUT_RIGHT_BUTTON:
        activate_sonar()


def mouse_motion(x, y):
    """Track hover coordinates and update camera orbit during a drag."""
    global mouse_last_x, mouse_last_y, mouse_ui, camera_orbit, camera_height
    mouse_ui = screen_to_ui(x, y)
    if mouse_dragging and mouse_last_x is not None and state == PLAYING and not show_help:
        dx, dy = x - mouse_last_x, y - mouse_last_y
        camera_orbit = (camera_orbit + dx * 0.20) % 360.0
        camera_height = clamp(camera_height - dy * 0.80, 90.0, 410.0)
        if camera_mode == 2:
            player["angle"] = (player["angle"] + dx * 0.25) % 360.0
    mouse_last_x, mouse_last_y = x, y


def reshape(width, height):
    """Preserve the target aspect ratio by letterboxing the OpenGL viewport."""
    global screen_width, screen_height, viewport
    screen_width, screen_height = max(1, width), max(1, height)
    scale = min(screen_width / WINDOW_WIDTH, screen_height / WINDOW_HEIGHT)
    view_width, view_height = max(1, int(WINDOW_WIDTH * scale)), max(1, int(WINDOW_HEIGHT * scale))
    viewport = ((screen_width - view_width) // 2, (screen_height - view_height) // 2, view_width, view_height)
    glutPostRedisplay()


def visibility_changed(visible):
    """Reset frame timing when the window becomes visible again."""
    global mouse_dragging
    if visible != GLUT_VISIBLE:
        held_keys.clear()
        pressed_keys.clear()
        mouse_dragging = False
        if state == PLAYING:
            toggle_pause()


# ============================================================
# Camera, display and main loop
# ============================================================

def setup_camera():
    """Configure the perspective projection and selected gameplay camera."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 3200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    target_x, target_y, target_z = world_to_render(player["x"], player["depth"], player["z"])
    if camera_mode == 2:
        direction_x, direction_z = heading_vector(player["angle"])
        eye_x = player["x"] + direction_x * 34.0
        eye_y = player["z"] + direction_z * 34.0
        eye_z = -player["depth"] + 25.0
        gluLookAt(eye_x, eye_y, eye_z, eye_x + direction_x * 360.0, eye_y + direction_z * 360.0, eye_z - 5.0, 0, 0, 1)
    elif camera_mode == 3:
        gluLookAt(player["x"], player["z"], TOP_CAMERA_HEIGHT, target_x, target_y, target_z, 0, 1, 0)
    else:
        behind_x, behind_z = heading_vector(player["angle"] + 180.0 + camera_orbit)
        gluLookAt(player["x"] + behind_x * CAMERA_DISTANCE, player["z"] + behind_z * CAMERA_DISTANCE, -player["depth"] + camera_height, target_x, target_y, target_z + 8.0, 0, 0, 1)


def show_screen():
    """Clear the frame, render the ordered 3D scene and HUD, then swap buffers."""
    global aim_ui
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(*viewport)
    setup_camera()
    dx, dz = heading_vector(player["angle"])
    # Project a point in front of the submarine for the crosshair.
    projected = gluProject(*world_to_render(player["x"] + dx * 360, player["depth"], player["z"] + dz * 360))
    aim_ui = None
    if projected is not None and 0 < projected[2] < 1:
        ux, uy = screen_to_ui(projected[0], screen_height - projected[1])
        if 40 < ux < 1240 and 230 < uy < 680:
            aim_ui = (ux, uy)
    draw_seafloor()
    draw_boundaries()
    draw_light_shafts()
    draw_rocks()
    draw_kelp_and_coral()
    draw_wreck()
    draw_gates()
    draw_collectibles()
    draw_mines()
    draw_fortress()
    draw_extraction()
    draw_escort()
    draw_enemies()
    draw_torpedoes_and_decoys()
    draw_explosions()
    draw_sonar_world()
    draw_fish_school()
    draw_bubbles()
    draw_player()
    draw_hud()
    glutSwapBuffers()


def idle():
    """Run the fixed-rate update loop and request the next frame redraw."""
    global last_update_time
    current_time = time.perf_counter()
    dt = current_time - last_update_time
    if dt < 1.0 / 60.0:
        time.sleep(min(0.004, 1.0 / 60.0 - dt))
        return
    last_update_time = current_time
    update_game(dt)
    glutPostRedisplay()


def main():
    """Initialize GLUT and OpenGL callbacks, reset the campaign, and start the event loop."""
    global last_update_time
    if not bool(glutCreateWindow):
        print("Cannot start: PyOpenGL could not load the existing GLUT/freeglut runtime. "
              "Run with a Python environment where the GLUT runtime is available.", file=sys.stderr)
        return 1
    random.seed(423)
    reset_campaign(to_console=True)
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(20, 20)
    glutCreateWindow(b"Submarine Warfare - Abyssal Command")
    glClearColor(*BACKGROUND_COLOR, 1.0)
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(show_screen)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glutPassiveMotionFunc(mouse_motion)
    glutMotionFunc(mouse_motion)
    glutIdleFunc(idle)
    glutKeyboardUpFunc(keyboard_up_listener)
    glutIgnoreKeyRepeat(1)
    glutReshapeFunc(reshape)
    glutVisibilityFunc(visibility_changed)
    last_update_time = time.perf_counter()
    glutMainLoop()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
