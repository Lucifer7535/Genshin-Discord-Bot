from typing import Dict, Optional, Union

fight_prop_map = {
    'FIGHT_PROP_BASE_HP': 1,
    'FIGHT_PROP_HP': 2,
    'FIGHT_PROP_HP_PERCENT': 3,
    'FIGHT_PROP_BASE_ATTACK': 4,
    'FIGHT_PROP_ATTACK': 5,
    'FIGHT_PROP_ATTACK_PERCENT': 6,
    'FIGHT_PROP_BASE_DEFENSE': 7,
    'FIGHT_PROP_DEFENSE': 8,
    'FIGHT_PROP_DEFENSE_PERCENT': 9,
    'FIGHT_PROP_BASE_SPEED': 10,
    'FIGHT_PROP_SPEED_PERCENT': 11,
    'FIGHT_PROP_HP_MP_PERCENT': 12,
    'FIGHT_PROP_ATTACK_MP_PERCENT': 13,
    'FIGHT_PROP_CRITICAL': 20,
    'FIGHT_PROP_ANTI_CRITICAL': 21,
    'FIGHT_PROP_CRITICAL_HURT': 22,
    'FIGHT_PROP_CHARGE_EFFICIENCY': 23,
    'FIGHT_PROP_ADD_HURT': 24,
    'FIGHT_PROP_SUB_HURT': 25,
    'FIGHT_PROP_HEAL_ADD': 26,
    'FIGHT_PROP_HEALED_ADD': 27,
    'FIGHT_PROP_ELEMENT_MASTERY': 28,
    'FIGHT_PROP_PHYSICAL_SUB_HURT': 29,
    'FIGHT_PROP_PHYSICAL_ADD_HURT': 30,
    'FIGHT_PROP_DEFENCE_IGNORE_RATIO': 31,
    'FIGHT_PROP_DEFENCE_IGNORE_DELTA': 32,
    'FIGHT_PROP_FIRE_ADD_HURT': 40,
    'FIGHT_PROP_ELEC_ADD_HURT': 41,
    'FIGHT_PROP_WATER_ADD_HURT': 42,
    'FIGHT_PROP_GRASS_ADD_HURT': 43,
    'FIGHT_PROP_WIND_ADD_HURT': 44,
    'FIGHT_PROP_ROCK_ADD_HURT': 45,
    'FIGHT_PROP_ICE_ADD_HURT': 46,
    'FIGHT_PROP_HIT_HEAD_ADD_HURT': 47,
    'FIGHT_PROP_FIRE_SUB_HURT': 50,
    'FIGHT_PROP_ELEC_SUB_HURT': 51,
    'FIGHT_PROP_WATER_SUB_HURT': 52,
    'FIGHT_PROP_GRASS_SUB_HURT': 53,
    'FIGHT_PROP_WIND_SUB_HURT': 54,
    'FIGHT_PROP_ROCK_SUB_HURT': 55,
    'FIGHT_PROP_ICE_SUB_HURT': 56,
    'FIGHT_PROP_EFFECT_HIT': 60,
    'FIGHT_PROP_EFFECT_RESIST': 61,
    'FIGHT_PROP_FREEZE_RESIST': 62,
    'FIGHT_PROP_TORPOR_RESIST': 63,
    'FIGHT_PROP_DIZZY_RESIST': 64,
    'FIGHT_PROP_FREEZE_SHORTEN': 65,
    'FIGHT_PROP_TORPOR_SHORTEN': 66,
    'FIGHT_PROP_DIZZY_SHORTEN': 67,
    'FIGHT_PROP_MAX_FIRE_ENERGY': 70,
    'FIGHT_PROP_MAX_ELEC_ENERGY': 71,
    'FIGHT_PROP_MAX_WATER_ENERGY': 72,
    'FIGHT_PROP_MAX_GRASS_ENERGY': 73,
    'FIGHT_PROP_MAX_WIND_ENERGY': 74,
    'FIGHT_PROP_MAX_ICE_ENERGY': 75,
    'FIGHT_PROP_MAX_ROCK_ENERGY': 76,
    'FIGHT_PROP_SKILL_CD_MINUS_RATIO': 80,
    'FIGHT_PROP_SHIELD_COST_MINUS_RATIO': 81,
    'FIGHT_PROP_CUR_FIRE_ENERGY': 1000,
    'FIGHT_PROP_CUR_ELEC_ENERGY': 1001,
    'FIGHT_PROP_CUR_WATER_ENERGY': 1002,
    'FIGHT_PROP_CUR_GRASS_ENERGY': 1003,
    'FIGHT_PROP_CUR_WIND_ENERGY': 1004,
    'FIGHT_PROP_CUR_ICE_ENERGY': 1005,
    'FIGHT_PROP_CUR_ROCK_ENERGY': 1006,
    'FIGHT_PROP_CUR_HP': 1010,
    'FIGHT_PROP_MAX_HP': 2000,
    'FIGHT_PROP_CUR_ATTACK': 2001,
    'FIGHT_PROP_CUR_DEFENSE': 2002,
    'FIGHT_PROP_CUR_SPEED': 2003,
    'FIGHT_PROP_NONEXTRA_ATTACK': 3000,
    'FIGHT_PROP_NONEXTRA_DEFENSE': 3001,
    'FIGHT_PROP_NONEXTRA_CRITICAL': 3002,
    'FIGHT_PROP_NONEXTRA_ANTI_CRITICAL': 3003,
    'FIGHT_PROP_NONEXTRA_CRITICAL_HURT': 3004,
    'FIGHT_PROP_NONEXTRA_CHARGE_EFFICIENCY': 3005,
    'FIGHT_PROP_NONEXTRA_ELEMENT_MASTERY': 3006,
    'FIGHT_PROP_NONEXTRA_PHYSICAL_SUB_HURT': 3007,
    'FIGHT_PROP_NONEXTRA_FIRE_ADD_HURT': 3008,
    'FIGHT_PROP_NONEXTRA_ELEC_ADD_HURT': 3009,
    'FIGHT_PROP_NONEXTRA_WATER_ADD_HURT': 3010,
    'FIGHT_PROP_NONEXTRA_GRASS_ADD_HURT': 3011,
    'FIGHT_PROP_NONEXTRA_WIND_ADD_HURT': 3012,
    'FIGHT_PROP_NONEXTRA_ROCK_ADD_HURT': 3013,
    'FIGHT_PROP_NONEXTRA_ICE_ADD_HURT': 3014,
    'FIGHT_PROP_NONEXTRA_FIRE_SUB_HURT': 3015,
    'FIGHT_PROP_NONEXTRA_ELEC_SUB_HURT': 3016,
    'FIGHT_PROP_NONEXTRA_WATER_SUB_HURT': 3017,
    'FIGHT_PROP_NONEXTRA_GRASS_SUB_HURT': 3018,
    'FIGHT_PROP_NONEXTRA_WIND_SUB_HURT': 3019,
    'FIGHT_PROP_NONEXTRA_ROCK_SUB_HURT': 3020,
    'FIGHT_PROP_NONEXTRA_ICE_SUB_HURT': 3021,
    'FIGHT_PROP_NONEXTRA_SKILL_CD_MINUS_RATIO': 3022,
    'FIGHT_PROP_NONEXTRA_SHIELD_COST_MINUS_RATIO': 3023,
    'FIGHT_PROP_NONEXTRA_PHYSICAL_ADD_HURT': 3024,
    1: 'BASE_HP',
    2: 'FIGHT_PROP_HP',
    3: 'FIGHT_PROP_HP_PERCENT',
    4: 'FIGHT_PROP_BASE_ATTACK',
    5: 'FIGHT_PROP_ATTACK',
    6: 'FIGHT_PROP_ATTACK_PERCENT',
    7: 'FIGHT_PROP_BASE_DEFENSE',
    8: 'FIGHT_PROP_DEFENSE',
    9: 'FIGHT_PROP_DEFENSE_PERCENT',
    10: 'FIGHT_PROP_BASE_SPEED',
    11: 'FIGHT_PROP_SPEED_PERCENT',
    12: 'FIGHT_PROP_HP_MP_PERCENT',
    13: 'FIGHT_PROP_ATTACK_MP_PERCENT',
    20: 'FIGHT_PROP_CRITICAL',
    21: 'FIGHT_PROP_ANTI_CRITICAL',
    22: 'FIGHT_PROP_CRITICAL_HURT',
    23: 'FIGHT_PROP_CHARGE_EFFICIENCY',
    24: 'FIGHT_PROP_ADD_HURT',
    25: 'FIGHT_PROP_SUB_HURT',
    26: 'FIGHT_PROP_HEAL_ADD',
    27: 'FIGHT_PROP_HEALED_ADD',
    28: 'FIGHT_PROP_ELEMENT_MASTERY',
    29: 'FIGHT_PROP_PHYSICAL_SUB_HURT',
    30: 'FIGHT_PROP_PHYSICAL_ADD_HURT',
    31: 'FIGHT_PROP_DEFENCE_IGNORE_RATIO',
    32: 'FIGHT_PROP_DEFENCE_IGNORE_DELTA',
    40: 'FIGHT_PROP_FIRE_ADD_HURT',
    41: 'FIGHT_PROP_ELEC_ADD_HURT',
    42: 'FIGHT_PROP_WATER_ADD_HURT',
    43: 'FIGHT_PROP_GRASS_ADD_HURT',
    44: 'FIGHT_PROP_WIND_ADD_HURT',
    45: 'FIGHT_PROP_ROCK_ADD_HURT',
    46: 'FIGHT_PROP_ICE_ADD_HURT',
    47: 'FIGHT_PROP_HIT_HEAD_ADD_HURT',
    50: 'FIGHT_PROP_FIRE_SUB_HURT',
    51: 'FIGHT_PROP_ELEC_SUB_HURT',
    52: 'FIGHT_PROP_WATER_SUB_HURT',
    53: 'FIGHT_PROP_GRASS_SUB_HURT',
    54: 'FIGHT_PROP_WIND_SUB_HURT',
    55: 'FIGHT_PROP_ROCK_SUB_HURT',
    56: 'FIGHT_PROP_ICE_SUB_HURT',
    60: 'FIGHT_PROP_EFFECT_HIT',
    61: 'FIGHT_PROP_EFFECT_RESIST',
    62: 'FIGHT_PROP_FREEZE_RESIST',
    63: 'FIGHT_PROP_TORPOR_RESIST',
    64: 'FIGHT_PROP_DIZZY_RESIST',
    65: 'FIGHT_PROP_FREEZE_SHORTEN',
    66: 'FIGHT_PROP_TORPOR_SHORTEN',
    67: 'FIGHT_PROP_DIZZY_SHORTEN',
    70: 'FIGHT_PROP_MAX_FIRE_ENERGY',
    71: 'FIGHT_PROP_MAX_ELEC_ENERGY',
    72: 'FIGHT_PROP_MAX_WATER_ENERGY',
    73: 'FIGHT_PROP_MAX_GRASS_ENERGY',
    74: 'FIGHT_PROP_MAX_WIND_ENERGY',
    75: 'FIGHT_PROP_MAX_ICE_ENERGY',
    76: 'FIGHT_PROP_MAX_ROCK_ENERGY',
    80: 'FIGHT_PROP_SKILL_CD_MINUS_RATIO',
    81: 'FIGHT_PROP_SHIELD_COST_MINUS_RATIO',
    1000: 'FIGHT_PROP_CUR_FIRE_ENERGY',
    1001: 'FIGHT_PROP_CUR_ELEC_ENERGY',
    1002: 'FIGHT_PROP_CUR_WATER_ENERGY',
    1003: 'FIGHT_PROP_CUR_GRASS_ENERGY',
    1004: 'FIGHT_PROP_CUR_WIND_ENERGY',
    1005: 'FIGHT_PROP_CUR_ICE_ENERGY',
    1006: 'FIGHT_PROP_CUR_ROCK_ENERGY',
    1010: 'FIGHT_PROP_CUR_HP',
    2000: 'FIGHT_PROP_MAX_HP',
    2001: 'FIGHT_PROP_CUR_ATTACK',
    2002: 'FIGHT_PROP_CUR_DEFENSE',
    2003: 'FIGHT_PROP_CUR_SPEED',
    3000: 'FIGHT_PROP_NONEXTRA_ATTACK',
    3001: 'FIGHT_PROP_NONEXTRA_DEFENSE',
    3002: 'FIGHT_PROP_NONEXTRA_CRITICAL',
    3003: 'FIGHT_PROP_NONEXTRA_ANTI_CRITICAL',
    3004: 'FIGHT_PROP_NONEXTRA_CRITICAL_HURT',
    3005: 'FIGHT_PROP_NONEXTRA_CHARGE_EFFICIENCY',
    3006: 'FIGHT_PROP_NONEXTRA_ELEMENT_MASTERY',
    3007: 'FIGHT_PROP_NONEXTRA_PHYSICAL_SUB_HURT',
    3008: 'FIGHT_PROP_NONEXTRA_FIRE_ADD_HURT',
    3009: 'FIGHT_PROP_NONEXTRA_ELEC_ADD_HURT',
    3010: 'FIGHT_PROP_NONEXTRA_WATER_ADD_HURT',
    3011: 'FIGHT_PROP_NONEXTRA_GRASS_ADD_HURT',
    3012: 'FIGHT_PROP_NONEXTRA_WIND_ADD_HURT',
    3013: 'FIGHT_PROP_NONEXTRA_ROCK_ADD_HURT',
    3014: 'FIGHT_PROP_NONEXTRA_ICE_ADD_HURT',
    3015: 'FIGHT_PROP_NONEXTRA_FIRE_SUB_HURT',
    3016: 'FIGHT_PROP_NONEXTRA_ELEC_SUB_HURT',
    3017: 'FIGHT_PROP_NONEXTRA_WATER_SUB_HURT',
    3018: 'FIGHT_PROP_NONEXTRA_GRASS_SUB_HURT',
    3019: 'FIGHT_PROP_NONEXTRA_WIND_SUB_HURT',
    3020: 'FIGHT_PROP_NONEXTRA_ROCK_SUB_HURT',
    3021: 'FIGHT_PROP_NONEXTRA_ICE_SUB_HURT',
    3022: 'FIGHT_PROP_NONEXTRA_SKILL_CD_MINUS_RATIO',
    3023: 'FIGHT_PROP_NONEXTRA_SHIELD_COST_MINUS_RATIO',
    3024: 'FIGHT_PROP_NONEXTRA_PHYSICAL_ADD_HURT'
}

fight_prop_name: Dict[str, Optional[str]] = {
    'FIGHT_PROP_BASE_HP': None,
    'FIGHT_PROP_HP': 'HP',
    'FIGHT_PROP_HP_PERCENT': 'HP %',
    'FIGHT_PROP_BASE_ATTACK': None,
    'FIGHT_PROP_ATTACK': 'Attack',
    'FIGHT_PROP_ATTACK_PERCENT': 'Attack %',
    'FIGHT_PROP_BASE_DEFENSE': None,
    'FIGHT_PROP_DEFENSE': 'Defense',
    'FIGHT_PROP_DEFENSE_PERCENT': 'Defense %',
    'FIGHT_PROP_BASE_SPEED': None,
    'FIGHT_PROP_SPEED_PERCENT': None,
    'FIGHT_PROP_HP_MP_PERCENT': None,
    'FIGHT_PROP_ATTACK_MP_PERCENT': None,
    'FIGHT_PROP_CRITICAL': 'Critical Rate %',
    'FIGHT_PROP_ANTI_CRITICAL': None,
    'FIGHT_PROP_CRITICAL_HURT': 'Critical Damage %',
    'FIGHT_PROP_CHARGE_EFFICIENCY': 'Energy Recharge %',
    'FIGHT_PROP_ADD_HURT': None,
    'FIGHT_PROP_SUB_HURT': None,
    'FIGHT_PROP_HEAL_ADD': 'Healing bonus %',
    'FIGHT_PROP_HEALED_ADD': None,
    'FIGHT_PROP_ELEMENT_MASTERY': 'Elemental Mastery',
    'FIGHT_PROP_PHYSICAL_SUB_HURT': None,
    'FIGHT_PROP_PHYSICAL_ADD_HURT': 'Physical damage bonus %',
    'FIGHT_PROP_DEFENCE_IGNORE_RATIO': None,
    'FIGHT_PROP_DEFENCE_IGNORE_DELTA': None,
    'FIGHT_PROP_FIRE_ADD_HURT': 'Pyro damage bonus %',
    'FIGHT_PROP_ELEC_ADD_HURT': 'Electro damage bonus %',
    'FIGHT_PROP_WATER_ADD_HURT': 'Hydro damage bonus %',
    'FIGHT_PROP_GRASS_ADD_HURT': 'Dendro damage bonus %',
    'FIGHT_PROP_WIND_ADD_HURT': 'Anemo damage bonus %',
    'FIGHT_PROP_ROCK_ADD_HURT': 'Geo damage bonus %',
    'FIGHT_PROP_ICE_ADD_HURT': 'Cryo damage bonus %',
}


def get_prop_name(prop: Union[int, str]) -> str:
    if isinstance(prop, int):
        prop = fight_prop_map.get(prop)
    name = fight_prop_name.get(prop)
    return name
