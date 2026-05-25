"""Single source of truth for team display metadata.

Each team has zero or more of: color, logo, wiki, initials, highlight, light_badge.
Access via the lookup helpers — they handle missing teams with sensible fallbacks.
"""
from __future__ import annotations


def _wl(f: str) -> str:
    return f"https://en.wikipedia.org/wiki/Special:FilePath/{f}"


DEFAULT_COLOR = "#6b7280"
_INITIAL_STOP_WORDS = {"&", "FC", "AFC", "City", "United", "Town",
                       "Athletic", "County", "Wanderers", "Rovers"}


TEAMS: dict[str, dict] = {
    # ── Highlight teams (foreground) ────────────────────────────────────────────
    "Arsenal":                  {"color": "#EF0107", "logo": _wl("Arsenal_FC.svg"),                  "wiki": "Arsenal_F.C.",                  "highlight": True},
    "Aston Villa":              {"color": "#95BFE5", "logo": "",                                     "wiki": "Aston_Villa_F.C.",              "highlight": True, "initials": "AVL"},
    "Blackburn Rovers":         {"color": "#009EE0", "logo": _wl("Blackburn_Rovers.svg"),            "wiki": "Blackburn_Rovers_F.C.",         "highlight": True, "initials": "BLB"},
    "Bournemouth":              {"color": "#E62333", "logo": _wl("AFC_Bournemouth_(2013).svg"),      "wiki": "AFC_Bournemouth",               "highlight": True},
    "Brentford":                {"color": "#E30613", "logo": _wl("Brentford_FC_crest.svg"),          "wiki": "Brentford_F.C.",                "highlight": True},
    "Brighton & Hove Albion":   {"color": "#0057B8", "logo": _wl("Brighton_%26_Hove_Albion_logo.svg"), "wiki": "Brighton_%26_Hove_Albion_F.C.", "highlight": True, "initials": "BHA"},
    "Burnley":                  {"color": "#6C1D45", "logo": _wl("Burnley_FC_Logo.svg"),             "wiki": "Burnley_F.C.",                  "highlight": True},
    "Chelsea":                  {"color": "#034694", "logo": _wl("Chelsea_FC.svg"),                  "wiki": "Chelsea_F.C.",                  "highlight": True},
    "Crystal Palace":           {"color": "#C4122E", "logo": _wl("Crystal_Palace_FC_logo_(2022).svg"), "wiki": "Crystal_Palace_F.C.",         "highlight": True, "initials": "CPA"},
    "Everton":                  {"color": "#003399", "logo": _wl("Everton_FC_logo.svg"),             "wiki": "Everton_F.C.",                  "highlight": True},
    "Fulham":                   {"color": "#CCCCCC", "logo": _wl("Fulham_FC_(shield).svg"),          "wiki": "Fulham_F.C.",                   "highlight": True},
    "Leeds United":             {"color": "#FFCD00", "logo": _wl("Leeds_United_F.C._logo.svg"),      "wiki": "Leeds_United_F.C.",             "highlight": True, "initials": "LEE"},
    "Leicester City":           {"color": "#0053A0", "logo": _wl("Leicester_City_crest.svg"),        "wiki": "Leicester_City_F.C.",           "highlight": True, "initials": "LEI"},
    "Liverpool":                {"color": "#C8102E", "logo": _wl("Liverpool_FC.svg"),                "wiki": "Liverpool_F.C.",                "highlight": True},
    "Manchester City":          {"color": "#6CABDD", "logo": _wl("Manchester_City_FC_badge.svg"),    "wiki": "Manchester_City_F.C.",          "highlight": True, "initials": "MCI"},
    "Manchester United":        {"color": "#DA291C", "logo": _wl("Manchester_United_FC_crest.svg"),  "wiki": "Manchester_United_F.C.",        "highlight": True, "initials": "MUN"},
    "Newcastle United":         {"color": "#AAAAAA", "logo": _wl("Newcastle_United_Logo.svg"),       "wiki": "Newcastle_United_F.C.",         "highlight": True, "initials": "NEW"},
    "Nottingham Forest":        {"color": "#DD0000", "logo": _wl("Nottingham_Forest_F.C._logo.svg"), "wiki": "Nottingham_Forest_F.C.",        "highlight": True, "initials": "NFO"},
    "Southampton":              {"color": "#D71920", "logo": _wl("FC_Southampton.svg"),              "wiki": "Southampton_F.C.",              "highlight": True},
    "Sunderland":               {"color": "#EB172B", "logo": _wl("Sunderland_AFC_logo.svg"),         "wiki": "Sunderland_A.F.C.",             "highlight": True, "initials": "SUN"},
    "Tottenham Hotspur":        {"color": "#132257", "logo": _wl("Tottenham_Hotspur.svg"),           "wiki": "Tottenham_Hotspur_F.C.",        "highlight": True, "light_badge": True},
    "West Ham United":          {"color": "#7A263A", "logo": _wl("West_Ham_United_FC_logo.svg"),     "wiki": "West_Ham_United_F.C.",          "highlight": True, "initials": "WHU"},
    "Wolverhampton Wanderers":  {"color": "#FDB913", "logo": _wl("Wolverhampton_Wanderers.svg"),     "wiki": "Wolverhampton_Wanderers_F.C.",  "highlight": True, "initials": "WOL"},

    # ── Background teams ────────────────────────────────────────────────────────
    "Barnsley":                 {"color": "#D71920", "logo": _wl("Barnsley_FC.svg"),                 "wiki": "Barnsley_F.C.",                 "initials": "BAR"},
    "Birmingham City":          {"color": "#0000FF", "logo": _wl("Birmingham_City_FC_logo.svg"),     "wiki": "Birmingham_City_F.C.",          "initials": "BIR"},
    "Blackpool":                {"color": "#F68712", "logo": _wl("Blackpool_FC_logo.svg"),           "wiki": "Blackpool_F.C.",                "initials": "BPL"},
    "Bolton Wanderers":         {"color": "#263065", "logo": _wl("Bolton_Wanderers_FC_logo.svg"),    "wiki": "Bolton_Wanderers_F.C.",         "initials": "BOL"},
    "Bradford City":            {"color": "#8B0000", "logo": _wl("Bradford_City_AFC.svg"),           "wiki": "Bradford_City_A.F.C.",          "initials": "BRA"},
    "Cardiff City":             {"color": "#0070B5", "logo": _wl("Cardiff_City_FC_crest.svg"),       "wiki": "Cardiff_City_F.C.",             "initials": "CAR"},
    "Charlton Athletic":        {"color": "#D4021D", "logo": _wl("Charlton_Athletic_FC.svg"),        "wiki": "Charlton_Athletic_F.C.",        "initials": "CHA"},
    "Coventry City":            {"color": "#78BBFF", "logo": _wl("Coventry_City_FC_logo.svg"),       "wiki": "Coventry_City_F.C.",            "initials": "COV"},
    "Derby County":             {"color": "#FFFFFF", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/374.png", "wiki": "Derby_County_F.C.", "initials": "DER"},
    "Huddersfield Town":        {"color": "#0E63AD", "logo": _wl("Huddersfield_Town_AFC_logo.svg"),  "wiki": "Huddersfield_Town_A.F.C.",      "initials": "HUD"},
    "Hull City":                {"color": "#F18A01", "logo": _wl("Hull_City_Crest_2014.svg"),        "wiki": "Hull_City_A.F.C.",              "initials": "HUL"},
    "Ipswich Town":             {"color": "#0044A9", "logo": _wl("Ipswich_Town.svg"),                "wiki": "Ipswich_Town_F.C.",             "initials": "IPS"},
    "Luton Town":               {"color": "#F78F1E", "logo": _wl("Luton_Town_FC_logo.svg"),          "wiki": "Luton_Town_F.C.",               "initials": "LUT"},
    "Middlesbrough":            {"color": "#D71920", "logo": _wl("Middlesbrough_FC_crest.svg"),      "wiki": "Middlesbrough_F.C.",            "initials": "MID"},
    "Norwich City":             {"color": "#00A650", "logo": _wl("Norwich_City_FC_logo.svg"),        "wiki": "Norwich_City_F.C.",             "initials": "NOR"},
    "Notts County":             {"color": "#000000", "logo": "https://a.espncdn.com/i/teamlogos/soccer/500/340.png", "wiki": "Notts_County_F.C.", "initials": "NC"},
    "Oldham Athletic":          {"color": "#005BAB", "logo": _wl("Oldham_Athletic_AFC.svg"),         "wiki": "Oldham_Athletic_A.F.C.",        "initials": "OLD"},
    "Portsmouth":               {"color": "#001489", "logo": _wl("Portsmouth_FC.svg"),               "wiki": "Portsmouth_F.C.",               "initials": "POM"},
    "QPR":                      {"color": "#1D5BA4", "logo": _wl("Queens_Park_Rangers_crest.svg"),   "wiki": "Queens_Park_Rangers_F.C.",      "initials": "QPR"},
    "Reading":                  {"color": "#004494", "logo": _wl("Reading_FC.svg"),                  "wiki": "Reading_F.C.",                  "initials": "REA"},
    "Sheffield United":         {"color": "#EE2737", "logo": _wl("Sheffield_United_FC_logo.svg"),    "wiki": "Sheffield_United_F.C.",         "initials": "SHU"},
    "Sheffield Wednesday":      {"color": "#0066B2", "logo": _wl("Sheffield_Wednesday_badge.svg"),   "wiki": "Sheffield_Wednesday_F.C.",      "initials": "SWF"},
    "Stoke City":               {"color": "#E03A3E", "logo": _wl("Stoke_City_FC.svg"),               "wiki": "Stoke_City_F.C.",               "initials": "STK"},
    "Swansea City":             {"color": "#A0A8B0", "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Swansea_City_AFC_logo.svg/1920px-Swansea_City_AFC_logo.svg.png", "wiki": "Swansea_City_A.F.C.", "initials": "SWA", "light_badge": True},
    "Swindon Town":             {"color": "#EE3524", "logo": _wl("Swindon_Town_FC.svg"),             "wiki": "Swindon_Town_F.C.",             "initials": "SWI", "light_badge": True},
    "Watford":                  {"color": "#FBEE23", "logo": _wl("Watford.svg"),                     "wiki": "Watford_F.C.",                  "initials": "WAT"},
    "West Brom":                {"color": "#122F67", "logo": _wl("West_Bromwich_Albion.svg"),        "wiki": "West_Bromwich_Albion_F.C.",     "initials": "WBA"},
    "Wigan Athletic":           {"color": "#1B5DAE", "logo": _wl("Wigan_Athletic.svg"),              "wiki": "Wigan_Athletic_F.C.",           "initials": "WIG"},
    "Wimbledon":                {"color": "#002B5C", "logo": _wl("Wimbledon_FC.svg"),                "wiki": "Wimbledon_F.C.",                "light_badge": True},
}


def meta(name: str) -> dict:
    """Return the metadata dict for a team, or empty dict if unknown."""
    return TEAMS.get(name, {})


def get_initials(name: str) -> str:
    """Return the explicit initials override, or derive from the team name."""
    if "initials" in meta(name):
        return meta(name)["initials"]
    words = [w for w in name.split() if w not in _INITIAL_STOP_WORDS]
    if not words:
        words = name.split()
    return "".join(w[0] for w in words[:3]).upper()
