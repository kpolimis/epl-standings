"""
EPL League Positions — Animated Chart Generator
Run: python3 generate.py  →  index.html
"""
import json, re

# ─────────────────────────────────────────────────────────────────
# STANDINGS DATA  1991/92 → 2025/26
# ─────────────────────────────────────────────────────────────────
RAW_DATA = {
    "1991/92 (First Div.)": {"Leeds United":1,"Manchester United":2,"Sheffield Wednesday":3,"Arsenal":4,"Manchester City":5,"Liverpool":6,"Aston Villa":7,"Nottingham Forest":8,"Sheffield United":9,"Crystal Palace":10,"QPR":11,"Everton":12,"Wimbledon":13,"Chelsea":14,"Tottenham Hotspur":15,"Southampton":16,"Oldham Athletic":17,"Ipswich Town":18,"Coventry City":19,"Luton Town":20,"Notts County":21,"West Ham United":22},
    "1992/93": {"Manchester United":1,"Aston Villa":2,"Norwich City":3,"Blackburn Rovers":4,"QPR":5,"Liverpool":6,"Sheffield Wednesday":7,"Tottenham Hotspur":8,"Manchester City":9,"Arsenal":10,"Chelsea":11,"Wimbledon":12,"Everton":13,"Sheffield United":14,"Coventry City":15,"Ipswich Town":16,"Leeds United":17,"Southampton":18,"Oldham Athletic":19,"Crystal Palace":20,"Middlesbrough":21,"Nottingham Forest":22},
    "1993/94": {"Manchester United":1,"Blackburn Rovers":2,"Newcastle United":3,"Arsenal":4,"Leeds United":5,"Wimbledon":6,"Sheffield Wednesday":7,"Liverpool":8,"QPR":9,"Aston Villa":10,"Coventry City":11,"Norwich City":12,"West Ham United":13,"Chelsea":14,"Tottenham Hotspur":15,"Manchester City":16,"Everton":17,"Southampton":18,"Ipswich Town":19,"Sheffield United":20,"Oldham Athletic":21,"Swindon Town":22},
    "1994/95": {"Blackburn Rovers":1,"Manchester United":2,"Nottingham Forest":3,"Liverpool":4,"Leeds United":5,"Newcastle United":6,"Tottenham Hotspur":7,"QPR":8,"Wimbledon":9,"Southampton":10,"Chelsea":11,"Arsenal":12,"Sheffield Wednesday":13,"West Ham United":14,"Everton":15,"Coventry City":16,"Manchester City":17,"Aston Villa":18,"Crystal Palace":19,"Norwich City":20,"Leicester City":21,"Ipswich Town":22},
    "1995/96": {"Manchester United":1,"Newcastle United":2,"Liverpool":3,"Aston Villa":4,"Arsenal":5,"Everton":6,"Blackburn Rovers":7,"Tottenham Hotspur":8,"Nottingham Forest":9,"West Ham United":10,"Chelsea":11,"Middlesbrough":12,"Leeds United":13,"Wimbledon":14,"Sheffield Wednesday":15,"Coventry City":16,"Southampton":17,"Manchester City":18,"QPR":19,"Bolton Wanderers":20},
    "1996/97": {"Manchester United":1,"Newcastle United":2,"Arsenal":3,"Liverpool":4,"Aston Villa":5,"Chelsea":6,"Sheffield Wednesday":7,"Wimbledon":8,"Leicester City":9,"Tottenham Hotspur":10,"Leeds United":11,"Derby County":12,"Blackburn Rovers":13,"West Ham United":14,"Everton":15,"Southampton":16,"Coventry City":17,"Sunderland":18,"Middlesbrough":19,"Nottingham Forest":20},
    "1997/98": {"Arsenal":1,"Manchester United":2,"Liverpool":3,"Chelsea":4,"Leeds United":5,"Blackburn Rovers":6,"Aston Villa":7,"West Ham United":8,"Derby County":9,"Leicester City":10,"Coventry City":11,"Southampton":12,"Newcastle United":13,"Tottenham Hotspur":14,"Wimbledon":15,"Sheffield Wednesday":16,"Everton":17,"Bolton Wanderers":18,"Barnsley":19,"Crystal Palace":20},
    "1998/99": {"Manchester United":1,"Arsenal":2,"Chelsea":3,"Leeds United":4,"West Ham United":5,"Aston Villa":6,"Liverpool":7,"Derby County":8,"Middlesbrough":9,"Leicester City":10,"Tottenham Hotspur":11,"Sheffield Wednesday":12,"Newcastle United":13,"Everton":14,"Coventry City":15,"Wimbledon":16,"Southampton":17,"Charlton Athletic":18,"Blackburn Rovers":19,"Nottingham Forest":20},
    "1999/00": {"Manchester United":1,"Arsenal":2,"Leeds United":3,"Liverpool":4,"Chelsea":5,"Aston Villa":6,"Sunderland":7,"Leicester City":8,"West Ham United":9,"Tottenham Hotspur":10,"Newcastle United":11,"Middlesbrough":12,"Everton":13,"Coventry City":14,"Southampton":15,"Derby County":16,"Bradford City":17,"Wimbledon":18,"Sheffield Wednesday":19,"Watford":20},
    "2000/01": {"Manchester United":1,"Arsenal":2,"Liverpool":3,"Leeds United":4,"Ipswich Town":5,"Chelsea":6,"Sunderland":7,"Aston Villa":8,"Charlton Athletic":9,"Southampton":10,"Newcastle United":11,"Tottenham Hotspur":12,"Leicester City":13,"Middlesbrough":14,"West Ham United":15,"Everton":16,"Derby County":17,"Manchester City":18,"Coventry City":19,"Bradford City":20},
    "2001/02": {"Arsenal":1,"Liverpool":2,"Manchester United":3,"Newcastle United":4,"Leeds United":5,"Chelsea":6,"West Ham United":7,"Aston Villa":8,"Tottenham Hotspur":9,"Blackburn Rovers":10,"Southampton":11,"Middlesbrough":12,"Fulham":13,"Charlton Athletic":14,"Everton":15,"Bolton Wanderers":16,"Sunderland":17,"Ipswich Town":18,"Derby County":19,"Leicester City":20},
    "2002/03": {"Manchester United":1,"Arsenal":2,"Newcastle United":3,"Chelsea":4,"Liverpool":5,"Blackburn Rovers":6,"Everton":7,"Southampton":8,"Manchester City":9,"Tottenham Hotspur":10,"Middlesbrough":11,"Charlton Athletic":12,"Birmingham City":13,"Fulham":14,"Leeds United":15,"Aston Villa":16,"Bolton Wanderers":17,"West Ham United":18,"West Brom":19,"Sunderland":20},
    "2003/04": {"Arsenal":1,"Chelsea":2,"Manchester United":3,"Liverpool":4,"Newcastle United":5,"Aston Villa":6,"Charlton Athletic":7,"Bolton Wanderers":8,"Fulham":9,"Birmingham City":10,"Middlesbrough":11,"Southampton":12,"Portsmouth":13,"Tottenham Hotspur":14,"Blackburn Rovers":15,"Manchester City":16,"Everton":17,"Leicester City":18,"Leeds United":19,"Wolverhampton Wanderers":20},
    "2004/05": {"Chelsea":1,"Arsenal":2,"Manchester United":3,"Everton":4,"Liverpool":5,"Bolton Wanderers":6,"Middlesbrough":7,"Manchester City":8,"Tottenham Hotspur":9,"Aston Villa":10,"Charlton Athletic":11,"Birmingham City":12,"Fulham":13,"Newcastle United":14,"Blackburn Rovers":15,"Portsmouth":16,"West Brom":17,"Crystal Palace":18,"Norwich City":19,"Southampton":20},
    "2005/06": {"Chelsea":1,"Manchester United":2,"Liverpool":3,"Arsenal":4,"Tottenham Hotspur":5,"Blackburn Rovers":6,"Newcastle United":7,"Bolton Wanderers":8,"West Ham United":9,"Wigan Athletic":10,"Everton":11,"Fulham":12,"Charlton Athletic":13,"Middlesbrough":14,"Manchester City":15,"Aston Villa":16,"Portsmouth":17,"Birmingham City":18,"West Brom":19,"Sunderland":20},
    "2006/07": {"Manchester United":1,"Chelsea":2,"Liverpool":3,"Arsenal":4,"Tottenham Hotspur":5,"Everton":6,"Bolton Wanderers":7,"Reading":8,"Portsmouth":9,"Blackburn Rovers":10,"Aston Villa":11,"Middlesbrough":12,"Newcastle United":13,"Manchester City":14,"West Ham United":15,"Fulham":16,"Wigan Athletic":17,"Sheffield United":18,"Charlton Athletic":19,"Watford":20},
    "2007/08": {"Manchester United":1,"Chelsea":2,"Arsenal":3,"Liverpool":4,"Everton":5,"Aston Villa":6,"Blackburn Rovers":7,"Portsmouth":8,"Manchester City":9,"West Ham United":10,"Tottenham Hotspur":11,"Newcastle United":12,"Middlesbrough":13,"Wigan Athletic":14,"Sunderland":15,"Bolton Wanderers":16,"Fulham":17,"Reading":18,"Birmingham City":19,"Derby County":20},
    "2008/09": {"Manchester United":1,"Liverpool":2,"Chelsea":3,"Arsenal":4,"Everton":5,"Aston Villa":6,"Fulham":7,"Tottenham Hotspur":8,"West Ham United":9,"Manchester City":10,"Wigan Athletic":11,"Stoke City":12,"Bolton Wanderers":13,"Portsmouth":14,"Blackburn Rovers":15,"Sunderland":16,"Hull City":17,"Newcastle United":18,"Middlesbrough":19,"West Brom":20},
    "2009/10": {"Chelsea":1,"Manchester United":2,"Arsenal":3,"Tottenham Hotspur":4,"Manchester City":5,"Aston Villa":6,"Liverpool":7,"Everton":8,"Birmingham City":9,"Blackburn Rovers":10,"Stoke City":11,"Fulham":12,"Sunderland":13,"Bolton Wanderers":14,"Wolverhampton Wanderers":15,"Wigan Athletic":16,"West Ham United":17,"Burnley":18,"Hull City":19,"Portsmouth":20},
    "2010/11": {"Manchester United":1,"Chelsea":2,"Manchester City":3,"Arsenal":4,"Tottenham Hotspur":5,"Liverpool":6,"Everton":7,"Fulham":8,"Aston Villa":9,"Sunderland":10,"West Brom":11,"Newcastle United":12,"Stoke City":13,"Bolton Wanderers":14,"Blackburn Rovers":15,"Wigan Athletic":16,"Wolverhampton Wanderers":17,"Birmingham City":18,"Blackpool":19,"West Ham United":20},
    "2011/12": {"Manchester City":1,"Manchester United":2,"Arsenal":3,"Tottenham Hotspur":4,"Newcastle United":5,"Chelsea":6,"Everton":7,"Liverpool":8,"Fulham":9,"West Brom":10,"Swansea City":11,"Norwich City":12,"Sunderland":13,"Stoke City":14,"Wigan Athletic":15,"Aston Villa":16,"QPR":17,"Bolton Wanderers":18,"Blackburn Rovers":19,"Wolverhampton Wanderers":20},
    "2012/13": {"Manchester United":1,"Manchester City":2,"Chelsea":3,"Arsenal":4,"Tottenham Hotspur":5,"Everton":6,"Liverpool":7,"West Brom":8,"Swansea City":9,"West Ham United":10,"Norwich City":11,"Fulham":12,"Stoke City":13,"Southampton":14,"Aston Villa":15,"Newcastle United":16,"Sunderland":17,"Wigan Athletic":18,"Reading":19,"QPR":20},
    "2013/14": {"Manchester City":1,"Liverpool":2,"Chelsea":3,"Arsenal":4,"Everton":5,"Tottenham Hotspur":6,"Manchester United":7,"Southampton":8,"Stoke City":9,"Newcastle United":10,"Crystal Palace":11,"Swansea City":12,"West Ham United":13,"Sunderland":14,"Aston Villa":15,"Hull City":16,"West Brom":17,"Norwich City":18,"Fulham":19,"Cardiff City":20},
    "2014/15": {"Chelsea":1,"Manchester City":2,"Arsenal":3,"Manchester United":4,"Tottenham Hotspur":5,"Liverpool":6,"Southampton":7,"Swansea City":8,"Stoke City":9,"Crystal Palace":10,"Everton":11,"West Ham United":12,"West Brom":13,"Leicester City":14,"Newcastle United":15,"Sunderland":16,"Aston Villa":17,"Hull City":18,"Burnley":19,"QPR":20},
    "2015/16": {"Leicester City":1,"Arsenal":2,"Tottenham Hotspur":3,"Manchester City":4,"Manchester United":5,"Southampton":6,"West Ham United":7,"Liverpool":8,"Stoke City":9,"Chelsea":10,"Everton":11,"Swansea City":12,"Watford":13,"West Brom":14,"Crystal Palace":15,"Bournemouth":16,"Sunderland":17,"Newcastle United":18,"Norwich City":19,"Aston Villa":20},
    "2016/17": {"Chelsea":1,"Tottenham Hotspur":2,"Manchester City":3,"Liverpool":4,"Arsenal":5,"Manchester United":6,"Everton":7,"Southampton":8,"Bournemouth":9,"West Brom":10,"West Ham United":11,"Leicester City":12,"Stoke City":13,"Crystal Palace":14,"Swansea City":15,"Burnley":16,"Watford":17,"Hull City":18,"Middlesbrough":19,"Sunderland":20},
    "2017/18": {"Manchester City":1,"Manchester United":2,"Tottenham Hotspur":3,"Liverpool":4,"Chelsea":5,"Arsenal":6,"Burnley":7,"Everton":8,"Leicester City":9,"Newcastle United":10,"Crystal Palace":11,"Bournemouth":12,"West Ham United":13,"Watford":14,"Brighton & Hove Albion":15,"Huddersfield Town":16,"Southampton":17,"Swansea City":18,"Stoke City":19,"West Brom":20},
    "2018/19": {"Manchester City":1,"Liverpool":2,"Chelsea":3,"Tottenham Hotspur":4,"Arsenal":5,"Manchester United":6,"Wolverhampton Wanderers":7,"Everton":8,"Leicester City":9,"West Ham United":10,"Watford":11,"Crystal Palace":12,"Newcastle United":13,"Bournemouth":14,"Burnley":15,"Southampton":16,"Brighton & Hove Albion":17,"Cardiff City":18,"Fulham":19,"Huddersfield Town":20},
    "2019/20": {"Liverpool":1,"Manchester City":2,"Manchester United":3,"Chelsea":4,"Leicester City":5,"Tottenham Hotspur":6,"Wolverhampton Wanderers":7,"Arsenal":8,"Sheffield United":9,"Burnley":10,"Southampton":11,"Everton":12,"Newcastle United":13,"Crystal Palace":14,"Brighton & Hove Albion":15,"West Ham United":16,"Aston Villa":17,"Bournemouth":18,"Watford":19,"Norwich City":20},
    "2020/21": {"Manchester City":1,"Manchester United":2,"Liverpool":3,"Chelsea":4,"Leicester City":5,"West Ham United":6,"Tottenham Hotspur":7,"Arsenal":8,"Leeds United":9,"Everton":10,"Aston Villa":11,"Newcastle United":12,"Wolverhampton Wanderers":13,"Crystal Palace":14,"Southampton":15,"Brighton & Hove Albion":16,"Burnley":17,"Fulham":18,"West Brom":19,"Sheffield United":20},
    "2021/22": {"Manchester City":1,"Liverpool":2,"Chelsea":3,"Tottenham Hotspur":4,"Arsenal":5,"Manchester United":6,"West Ham United":7,"Leicester City":8,"Brighton & Hove Albion":9,"Wolverhampton Wanderers":10,"Newcastle United":11,"Crystal Palace":12,"Brentford":13,"Aston Villa":14,"Southampton":15,"Everton":16,"Leeds United":17,"Burnley":18,"Watford":19,"Norwich City":20},
    "2022/23": {"Manchester City":1,"Arsenal":2,"Manchester United":3,"Newcastle United":4,"Liverpool":5,"Brighton & Hove Albion":6,"Aston Villa":7,"Tottenham Hotspur":8,"Brentford":9,"Fulham":10,"Crystal Palace":11,"Chelsea":12,"Wolverhampton Wanderers":13,"West Ham United":14,"Bournemouth":15,"Nottingham Forest":16,"Everton":17,"Leicester City":18,"Leeds United":19,"Southampton":20},
    "2023/24": {"Manchester City":1,"Arsenal":2,"Liverpool":3,"Aston Villa":4,"Tottenham Hotspur":5,"Chelsea":6,"Newcastle United":7,"Manchester United":8,"West Ham United":9,"Brighton & Hove Albion":10,"Wolverhampton Wanderers":11,"Fulham":12,"Bournemouth":13,"Crystal Palace":14,"Brentford":15,"Nottingham Forest":16,"Everton":17,"Luton Town":18,"Burnley":19,"Sheffield United":20},
    "2024/25": {"Liverpool":1,"Arsenal":2,"Manchester City":3,"Chelsea":4,"Newcastle United":5,"Aston Villa":6,"Nottingham Forest":7,"Crystal Palace":8,"Tottenham Hotspur":9,"Brighton & Hove Albion":10,"Fulham":11,"Brentford":12,"Wolverhampton Wanderers":13,"West Ham United":14,"Manchester United":15,"Everton":16,"Bournemouth":17,"Ipswich Town":18,"Leicester City":19,"Southampton":20},
    "2025/26": {"Arsenal":1,"Manchester City":2,"Manchester United":3,"Aston Villa":4,"Liverpool":5,"Bournemouth":6,"Brighton & Hove Albion":7,"Chelsea":8,"Brentford":9,"Sunderland":10,"Newcastle United":11,"Everton":12,"Fulham":13,"Leeds United":14,"Crystal Palace":15,"Nottingham Forest":16,"Tottenham Hotspur":17,"West Ham United":18,"Burnley":19,"Wolverhampton Wanderers":20},
}

SEASONS = list(RAW_DATA.keys())

# ── Colors ─────────────────────────────────────────────────────
TEAM_COLORS = {
    "Arsenal":"#EF0107","Chelsea":"#034694","Liverpool":"#C8102E",
    "Manchester City":"#6CABDD","Manchester United":"#DA291C",
    "Tottenham Hotspur":"#132257","Everton":"#003399","Aston Villa":"#95BFE5",
    "Newcastle United":"#AAAAAA","Blackburn Rovers":"#009EE0",
    "Leicester City":"#0053A0","Leeds United":"#FFCD00",
    "Wolverhampton Wanderers":"#FDB913","Nottingham Forest":"#DD0000",
    "West Ham United":"#7A263A","Southampton":"#D71920",
    "Brighton & Hove Albion":"#0057B8","Sunderland":"#EB172B",
    "Brentford":"#E30613","Fulham":"#CCCCCC","Crystal Palace":"#C4122E",
    "Bournemouth":"#E62333","Burnley":"#6C1D45",
    # background teams with known colors
    "Middlesbrough":"#D71920","Stoke City":"#E03A3E","Hull City":"#F18A01",
    "Swansea City":"#A0A8B0","Charlton Athletic":"#D4021D","Watford":"#FBEE23",
    "Birmingham City":"#0000FF","Derby County":"#FFFFFF","Sheffield Wednesday":"#0066B2",
    "Sheffield United":"#EE2737","Norwich City":"#00A650","QPR":"#1D5BA4",
    "Coventry City":"#78BBFF","Reading":"#004494","Wigan Athletic":"#1B5DAE",
    "Blackpool":"#F68712","Portsmouth":"#001489","Oldham Athletic":"#005BAB",
    "Wimbledon":"#002B5C","Bradford City":"#8B0000","Cardiff City":"#0070B5",
    "Huddersfield Town":"#0E63AD","Swindon Town":"#EE3524","Barnsley":"#D71920",
    "Luton Town":"#F78F1E","Ipswich Town":"#0044A9","West Brom":"#122F67",
    "Notts County":"#000000","Bolton Wanderers":"#263065","West Brom":"#122F67",
}

# ── Initials ───────────────────────────────────────────────────
INITIALS_OVERRIDE = {
    "QPR":"QPR","West Brom":"WBA","Notts County":"NC",
    "Brighton & Hove Albion":"BHA","Sheffield Wednesday":"SWF",
    "Sheffield United":"SHU","Wolverhampton Wanderers":"WOL",
    "Nottingham Forest":"NFO","Huddersfield Town":"HUD",
    "Birmingham City":"BIR","Swansea City":"SWA","Charlton Athletic":"CHA",
    "Bradford City":"BRA","Oldham Athletic":"OLD","Swindon Town":"SWI",
    "Cardiff City":"CAR","Derby County":"DER","Luton Town":"LUT",
    "Wigan Athletic":"WIG","Manchester City":"MCI","Manchester United":"MUN",
    "Aston Villa":"AVL","Crystal Palace":"CPA","West Ham United":"WHU",
    "Blackburn Rovers":"BLB","Blackpool":"BPL","Bolton Wanderers":"BOL",
    "Stoke City":"STK","Norwich City":"NOR","Coventry City":"COV",
    "Leicester City":"LEI","Newcastle United":"NEW","Leeds United":"LEE",
    "Ipswich Town":"IPS","Middlesbrough":"MID","Portsmouth":"POM",
    "Notts County":"NCS","Barnsley":"BAR","West Brom":"WBA",
    "Reading":"REA","Watford":"WAT","Hull City":"HUL","Sunderland":"SUN",
}

def get_initials(name):
    if name in INITIALS_OVERRIDE:
        return INITIALS_OVERRIDE[name]
    words = [w for w in name.split() if w not in ('&','FC','AFC','City','United','Town','Athletic','County','Wanderers','Rovers')]
    if not words:
        words = name.split()
    return ''.join(w[0] for w in words[:3]).upper()

# ── Direct logo URLs (Special:FilePath) ────────────────────────
# Used first; REST API is fallback for any not listed or that 404.
def wl(f): return f"https://en.wikipedia.org/wiki/Special:FilePath/{f}"

DIRECT_LOGOS = {
    # Highlighted teams
    "Arsenal":                  wl("Arsenal_FC.svg"),
    "Chelsea":                  wl("Chelsea_FC.svg"),
    "Liverpool":                wl("Liverpool_FC.svg"),
    "Manchester City":          wl("Manchester_City_FC_badge.svg"),
    "Manchester United":        wl("Manchester_United_FC_crest.svg"),
    "Tottenham Hotspur":        wl("Tottenham_Hotspur.svg"),
    "Everton":                  wl("Everton_FC_logo.svg"),
    "Newcastle United":         wl("Newcastle_United_Logo.svg"),
    "Blackburn Rovers":         wl("Blackburn_Rovers.svg"),
    "Leicester City":           wl("Leicester_City_crest.svg"),
    "Leeds United":             wl("Leeds_United_F.C._logo.svg"),
    "Wolverhampton Wanderers":  wl("Wolverhampton_Wanderers.svg"),
    "Nottingham Forest":        wl("Nottingham_Forest_F.C._logo.svg"),
    "West Ham United":          wl("West_Ham_United_FC_logo.svg"),
    "Southampton":              wl("FC_Southampton.svg"),
    "Brighton & Hove Albion":   wl("Brighton_%26_Hove_Albion_logo.svg"),
    "Brentford":                wl("Brentford_FC_crest.svg"),
    "Fulham":                   wl("Fulham_FC_(shield).svg"),
    "Crystal Palace":           wl("Crystal_Palace_FC_logo_(2022).svg"),
    "Bournemouth":              wl("AFC_Bournemouth_(2013).svg"),
    # Background teams — confirmed filenames
    "Swansea City":             "https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Swansea_City_AFC_logo.svg/1920px-Swansea_City_AFC_logo.svg.png",
    "Derby County":             "https://a.espncdn.com/i/teamlogos/soccer/500/374.png",
    "Middlesbrough":            wl("Middlesbrough_FC_crest.svg"),
    "Stoke City":               wl("Stoke_City_FC.svg"),
    "Hull City":                wl("Hull_City_Crest_2014.svg"),
    "Bolton Wanderers":         wl("Bolton_Wanderers_FC_logo.svg"),
    "Charlton Athletic":        wl("Charlton_Athletic_FC.svg"),
    "Watford":                  wl("Watford.svg"),  # confirmed: File:Watford.svg
    "Birmingham City":          wl("Birmingham_City_FC_logo.svg"),
    "Sheffield Wednesday":      wl("Sheffield_Wednesday_badge.svg"),
    "Sheffield United":         wl("Sheffield_United_FC_logo.svg"),
    "Norwich City":             wl("Norwich_City_FC_logo.svg"),
    "QPR":                      wl("Queens_Park_Rangers_crest.svg"),
    "Coventry City":            wl("Coventry_City_FC_logo.svg"),
    "Reading":                  wl("Reading_FC.svg"),
    "Wigan Athletic":           wl("Wigan_Athletic.svg"),
    "Blackpool":                wl("Blackpool_FC_logo.svg"),
    "Portsmouth":               wl("Portsmouth_FC.svg"),
    "Wimbledon":                wl("Wimbledon_FC.svg"),
    "Bradford City":            wl("Bradford_City_AFC.svg"),
    "Cardiff City":             wl("Cardiff_City_FC_crest.svg"),
    "Huddersfield Town":        wl("Huddersfield_Town_AFC_logo.svg"),
    "Swindon Town":             wl("Swindon_Town_FC.svg"),
    "Barnsley":                 wl("Barnsley_FC.svg"),
    "Luton Town":               wl("Luton_Town_FC_logo.svg"),
    "Ipswich Town":             wl("Ipswich_Town.svg"),
    "West Brom":                wl("West_Bromwich_Albion.svg"),
    "Notts County":             "https://a.espncdn.com/i/teamlogos/soccer/500/340.png",
    "Oldham Athletic":          wl("Oldham_Athletic_AFC.svg"),
    "Sunderland":               wl("Sunderland_AFC_logo.svg"),
    "Burnley":                  wl("Burnley_FC_Logo.svg"),
    "Aston Villa":              "",  # 2023 rebrand — REST API resolves
}

# ── Wikipedia article titles for ALL teams ─────────────────────
WIKI_TITLES = {
    "Arsenal":"Arsenal_F.C.","Chelsea":"Chelsea_F.C.","Liverpool":"Liverpool_F.C.",
    "Manchester City":"Manchester_City_F.C.","Manchester United":"Manchester_United_F.C.",
    "Tottenham Hotspur":"Tottenham_Hotspur_F.C.","Everton":"Everton_F.C.",
    "Aston Villa":"Aston_Villa_F.C.","Newcastle United":"Newcastle_United_F.C.",
    "Blackburn Rovers":"Blackburn_Rovers_F.C.","Leicester City":"Leicester_City_F.C.",
    "Leeds United":"Leeds_United_F.C.","Wolverhampton Wanderers":"Wolverhampton_Wanderers_F.C.",
    "Nottingham Forest":"Nottingham_Forest_F.C.","West Ham United":"West_Ham_United_F.C.",
    "Southampton":"Southampton_F.C.","Brighton & Hove Albion":"Brighton_%26_Hove_Albion_F.C.",
    "Sunderland":"Sunderland_A.F.C.","Brentford":"Brentford_F.C.","Fulham":"Fulham_F.C.",
    "Crystal Palace":"Crystal_Palace_F.C.","Bournemouth":"AFC_Bournemouth","Burnley":"Burnley_F.C.",
    "Middlesbrough":"Middlesbrough_F.C.","Stoke City":"Stoke_City_F.C.",
    "Hull City":"Hull_City_A.F.C.","Swansea City":"Swansea_City_A.F.C.",
    "Charlton Athletic":"Charlton_Athletic_F.C.","Watford":"Watford_F.C.",
    "Birmingham City":"Birmingham_City_F.C.","Derby County":"Derby_County_F.C.",
    "Sheffield Wednesday":"Sheffield_Wednesday_F.C.","Sheffield United":"Sheffield_United_F.C.",
    "Norwich City":"Norwich_City_F.C.","QPR":"Queens_Park_Rangers_F.C.",
    "Coventry City":"Coventry_City_F.C.","Reading":"Reading_F.C.",
    "Wigan Athletic":"Wigan_Athletic_F.C.","Blackpool":"Blackpool_F.C.",
    "Portsmouth":"Portsmouth_F.C.","Oldham Athletic":"Oldham_Athletic_A.F.C.",
    "Wimbledon":"Wimbledon_F.C.","Bradford City":"Bradford_City_A.F.C.",
    "Cardiff City":"Cardiff_City_F.C.","Huddersfield Town":"Huddersfield_Town_A.F.C.",
    "Swindon Town":"Swindon_Town_F.C.","Barnsley":"Barnsley_F.C.",
    "Luton Town":"Luton_Town_F.C.","Ipswich Town":"Ipswich_Town_F.C.",
    "West Brom":"West_Bromwich_Albion_F.C.","Notts County":"Notts_County_F.C.",
    "Bolton Wanderers":"Bolton_Wanderers_F.C.","Blackburn Rovers":"Blackburn_Rovers_F.C.",
}

# ── Build payload ──────────────────────────────────────────────
all_teams = sorted(set().union(*[d.keys() for d in RAW_DATA.values()]))
HL_TEAMS  = set(["Arsenal","Chelsea","Liverpool","Manchester City","Manchester United",
                 "Tottenham Hotspur","Everton","Aston Villa","Newcastle United",
                 "Blackburn Rovers","Leicester City","Leeds United",
                 "Wolverhampton Wanderers","Nottingham Forest","West Ham United",
                 "Southampton","Brighton & Hove Albion","Sunderland","Brentford",
                 "Fulham","Crystal Palace","Bournemouth","Burnley"])

# Teams whose crest is designed for light backgrounds — give marker a white bg
LIGHT_BADGE = {"Swansea City", "Swindon Town", "Wimbledon", "Tottenham Hotspur"}

teams_js = {
    team: {
        "color":      TEAM_COLORS.get(team, "#6b7280"),
        "logo":       DIRECT_LOGOS.get(team, ""),
        "wiki":       WIKI_TITLES.get(team, ""),
        "hl":         team in HL_TEAMS,
        "lightBadge": team in LIGHT_BADGE,
        "initials":   get_initials(team),
        "pos":        [RAW_DATA[s].get(team, None) for s in SEASONS],
    }
    for team in all_teams
}

payload = {"seasons": SEASONS, "teams": teams_js, "raw": RAW_DATA}
JS_DATA  = json.dumps(payload, ensure_ascii=False, separators=(",",":"))

# ─────────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EPL League Positions — Animated</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#07090d;--surface:#0d1117;--border:#21262d;--text:#c9d1d9;--muted:#6e7681;--accent:#3fb950}}
body{{background:var(--bg);color:var(--text);font-family:'IBM Plex Mono',monospace;
  display:flex;flex-direction:column;align-items:center;min-height:100vh;overflow-x:hidden}}
header{{width:100%;max-width:1440px;padding:28px 40px 0}}
h1{{font-family:'Playfair Display',serif;font-size:clamp(20px,2.6vw,38px);font-weight:900;
  color:#f0f4f8;letter-spacing:-.02em;line-height:1.1}}
h1 span{{color:var(--accent)}}
.subtitle{{font-size:11px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;padding-bottom:4px}}
#banner{{display:flex;align-items:center;gap:14px;padding:10px 20px 10px 14px;
  background:var(--surface);border:1px solid var(--border);border-radius:8px;
  margin:14px 40px 0;width:calc(100% - 80px);max-width:1360px;transition:border-color .4s;min-height:58px}}
#banner-logo{{width:36px;height:36px;border-radius:50%;object-fit:contain;
  background:#111;border:2px solid #333;flex-shrink:0}}
#banner-text{{flex:1;display:flex;flex-direction:column;gap:1px}}
#banner-season{{font-size:10px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase}}
#banner-name{{font-size:15px;font-weight:600;transition:color .4s}}
#banner-suffix{{font-size:10px;color:var(--muted)}}
.zone-legend{{display:flex;align-items:center;gap:16px;flex-shrink:0}}
.zone-pip{{display:flex;align-items:center;gap:5px;font-size:9px;
  color:var(--muted);letter-spacing:.05em;white-space:nowrap}}
.zone-pip span{{width:10px;height:10px;border-radius:2px;flex-shrink:0}}
#chart-wrap{{width:100%;max-width:1440px;padding:10px 20px 0;overflow-x:auto}}
#chart svg{{display:block;width:100%;height:auto}}
#controls{{display:flex;align-items:center;gap:14px;flex-wrap:wrap;
  padding:14px 40px 20px;width:100%;max-width:1440px}}
.btn{{background:var(--surface);border:1px solid var(--border);color:var(--text);
  font-family:'IBM Plex Mono',monospace;font-size:12px;padding:7px 16px;border-radius:6px;
  cursor:pointer;transition:background .15s,border-color .15s;white-space:nowrap}}
.btn:hover{{background:#161b22;border-color:#444}}
.btn.active{{background:#1f6feb;border-color:#1f6feb;color:#fff}}
#play-btn{{font-size:14px;padding:7px 20px;min-width:90px}}
#play-btn.playing{{background:#238636;border-color:#238636;color:#fff}}
#slider-wrap{{flex:1;min-width:160px;display:flex;align-items:center;gap:10px}}
#slider{{-webkit-appearance:none;appearance:none;width:100%;height:4px;border-radius:4px;
  background:var(--border);outline:none;cursor:pointer}}
#slider::-webkit-slider-thumb{{-webkit-appearance:none;width:14px;height:14px;
  border-radius:50%;background:var(--accent);cursor:pointer}}
#season-lbl{{font-size:13px;font-weight:600;color:#f0f4f8;white-space:nowrap;min-width:72px}}
.speed-group{{display:flex;gap:4px}}
.speed-group .btn{{padding:5px 10px;font-size:11px}}
#roster{{width:100%;max-width:1440px;padding:0 40px 50px}}
#roster-hdr{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;
  gap:12px;margin-bottom:14px;padding-top:4px;border-top:1px solid var(--border)}}
#roster-hdr h2{{font-family:'Playfair Display',serif;font-size:18px;font-weight:900;
  color:#f0f4f8;padding-top:14px}}
#roster-hdr h2 span{{color:var(--muted);font-size:13px;font-family:'IBM Plex Mono',monospace;
  font-weight:400;margin-left:6px}}
.sort-group{{display:flex;gap:4px;padding-top:14px}}
.sort-group .btn{{padding:4px 10px;font-size:10px}}
#team-grid{{display:flex;flex-wrap:wrap;gap:7px}}
.chip{{display:inline-flex;align-items:center;gap:7px;padding:5px 11px;
  background:var(--surface);border:1px solid var(--border);border-radius:20px;
  cursor:pointer;font-size:11px;color:var(--text);
  transition:background .12s,border-color .12s,transform .1s;user-select:none;--cc:#556070}}
.chip:hover{{background:#161b22;border-color:#555;transform:translateY(-1px)}}
.chip.selected{{border-color:var(--cc);background:color-mix(in srgb,var(--cc) 15%,transparent);color:#f0f4f8}}
.chip .dot{{width:7px;height:7px;border-radius:50%;background:var(--cc);flex-shrink:0}}
.chip .meta{{color:var(--muted);font-size:9px;margin-left:1px}}
.tip{{position:fixed;pointer-events:none;background:#161b22;border:1px solid #30363d;
  border-radius:6px;padding:10px 14px;font-size:12px;color:var(--text);
  box-shadow:0 8px 24px rgba(0,0,0,.6);z-index:999;display:none;line-height:1.7;max-width:240px}}
.tip strong{{display:block;color:#f0f4f8;font-size:13px;margin-bottom:1px}}
footer{{font-size:10px;color:#484f58;text-align:center;padding:4px 20px 30px;line-height:1.8}}
footer a{{color:#58a6ff;text-decoration:none}}
</style>
</head>
<body>
<header>
  <div>
    <h1>Premier League — <span>Every Season</span></h1>
    <p class="subtitle">1991/92 (pre-EPL) → 2025/26 · one season at a time</p>
  </div>
</header>
<div id="banner">
  <img id="banner-logo" src="" alt="">
  <div id="banner-text">
    <span id="banner-season">Season</span>
    <span id="banner-name">—</span>
    <span id="banner-suffix"></span>
  </div>
  <div class="zone-legend">
    <div class="zone-pip"><span style="background:#1f6feb55"></span>Champions League</div>
    <div class="zone-pip"><span style="background:#f59e0b55"></span>Europa League</div>
    <div class="zone-pip"><span style="background:#10b98155"></span>Conference League</div>
    <div class="zone-pip"><span style="background:#ff000033"></span>Relegation</div>
  </div>
</div>
<div id="chart-wrap"><div id="chart"></div></div>
<div id="controls">
  <button class="btn" id="reset-btn">↺</button>
  <button class="btn" id="play-btn">▶ Play</button>
  <div class="speed-group">
    <button class="btn speed-btn" data-ms="1400">0.5×</button>
    <button class="btn speed-btn active" data-ms="750">1×</button>
    <button class="btn speed-btn" data-ms="380">2×</button>
    <button class="btn speed-btn" data-ms="120">5×</button>
  </div>
  <div id="slider-wrap">
    <input type="range" id="slider" min="0" max="34" step="1" value="0">
  </div>
  <span id="season-lbl">1991/92 (First Div.)</span>
</div>
<section id="roster">
  <div id="roster-hdr">
    <h2>All EPL clubs <span id="club-count"></span></h2>
    <div class="sort-group">
      <button class="btn sort-btn active" data-sort="seasons">By seasons</button>
      <button class="btn sort-btn" data-sort="best">Best finish</button>
      <button class="btn sort-btn" data-sort="alpha">A–Z</button>
    </div>
  </div>
  <div id="team-grid"></div>
</section>
<div class="tip" id="tip"></div>
<footer>
  Data from official Premier League records · 1991/92 pre-EPL season included as context · 2025/26 with one matchweek remaining (May 2026)<br>
  <a href="https://github.com/kpolimis/epl-standings" target="_blank">github.com/kpolimis/epl-standings</a>
</footer>
<script>
const EPL = {JS_DATA};

(function(){{
  const seasons = EPL.seasons;
  const teams   = EPL.teams;
  const N       = seasons.length;

  const champ = seasons.map(s => {{
    const e = Object.entries(EPL.raw[s]).find(([,v])=>v===1);
    return e ? e[0] : null;
  }});

  let frame=0, playing=false, speed=750, timer=null, selectedTeam=null;

  // ── Dimensions ───────────────────────────────────────────────
  const TW=1380, TH=760, M={{t:70,r:200,b:68,l:46}};
  const W=TW-M.l-M.r, H=TH-M.t-M.b;

  const svg = d3.select("#chart").append("svg")
    .attr("viewBox",`0 0 ${{TW}} ${{TH}}`).attr("width","100%");
  const defs = svg.append("defs");

  const filt = defs.append("filter").attr("id","glow")
    .attr("x","-30%").attr("y","-30%").attr("width","160%").attr("height","160%");
  filt.append("feGaussianBlur").attr("stdDeviation","3").attr("result","b");
  const fm = filt.append("feMerge");
  fm.append("feMergeNode").attr("in","b");
  fm.append("feMergeNode").attr("in","SourceGraphic");

  const g = svg.append("g").attr("transform",`translate(${{M.l}},${{M.t}})`);

  // ── Scales ────────────────────────────────────────────────────
  const xSc = d3.scalePoint().domain(seasons).range([0,W]).padding(.05);
  const ySc = d3.scaleLinear().domain([.3,22.5]).range([0,H]);

  // ── Background shapes ─────────────────────────────────────────
  g.append("rect").attr("width",W).attr("height",H).attr("fill","#0d1117").attr("rx",4);

  // Relegation zone (static)
  g.append("rect").attr("x",0).attr("width",W).attr("y",ySc(17.5))
    .attr("height",ySc(22.5)-ySc(17.5)).attr("fill","#ff00000a");

  // European zone bands (dynamic — update each frame)
  const clBand   = g.append("rect").attr("x",0).attr("width",W).attr("fill","#1f6feb0d");
  const elBand   = g.append("rect").attr("x",0).attr("width",W).attr("fill","#f59e0b0b");
  const confBand = g.append("rect").attr("x",0).attr("width",W).attr("fill","#10b9810b");

  // Dynamic zone divider lines (CL/EL boundary)
  const clLine   = g.append("line").attr("x1",0).attr("x2",W)
    .attr("stroke","#1f6feb30").attr("stroke-width",.8).attr("stroke-dasharray","4,6");
  const elLine   = g.append("line").attr("x1",0).attr("x2",W)
    .attr("stroke","#f59e0b30").attr("stroke-width",.6).attr("stroke-dasharray","3,7");
  const confLine = g.append("line").attr("x1",0).attr("x2",W)
    .attr("stroke","#10b98130").attr("stroke-width",.6).attr("stroke-dasharray","3,7");

  // Dynamic zone labels
  const clLabel   = g.append("text").attr("x",W-8).attr("text-anchor","end")
    .attr("dominant-baseline","middle").attr("font-size",8.5)
    .attr("fill","#1f6feb35").attr("font-family","IBM Plex Mono,monospace");
  const elLabel   = g.append("text").attr("x",W-8).attr("text-anchor","end")
    .attr("dominant-baseline","middle").attr("font-size",8.5)
    .attr("fill","#f59e0b35").attr("font-family","IBM Plex Mono,monospace");
  const confLabel = g.append("text").attr("x",W-8).attr("text-anchor","end")
    .attr("dominant-baseline","middle").attr("font-size",8.5)
    .attr("fill","#10b98135").attr("font-family","IBM Plex Mono,monospace");

  // Static relegation label
  g.append("text").attr("x",W-8).attr("y",ySc(19.5))
    .attr("text-anchor","end").attr("dominant-baseline","middle")
    .attr("font-size",8.5).attr("fill","#ff000028").attr("font-family","IBM Plex Mono,monospace")
    .text("RELEGATION ZONE");

  // ── getZones — European spots by era ──────────────────────────
  // CL: 1 spot (1992/93-1996/97), 2 (1997/98-2002/03), 4 (2003/04+)
  // EL: positions cl+1 to 6 (UEFA Cup pre-2009, Europa League 2009+)
  // Conference League: position 7 only (2021/22+)
  function getZones(idx) {{
    if (idx === 0) return {{cl:0, el:0, conf:0}};          // pre-EPL, no European spots shown
    const cl   = idx <= 5 ? 1 : idx <= 11 ? 2 : 4;        // idx 1-5=1, 6-11=2, 12+=4
    const el   = Math.max(0, 6 - cl);                      // fills up to 6th
    const conf = idx >= 30 ? 1 : 0;                        // 2021/22 = index 30
    return {{cl, el, conf}};
  }}

  function updateZoneBands(idx, animate, dur, ease) {{
    const z = getZones(idx);

    function setBand(rect, line, label, topPos, botPos, labelTxt, visible) {{
      const bandTr  = animate ? rect.transition().duration(dur).ease(ease)  : rect;
      const lineTr  = animate ? line.transition().duration(dur).ease(ease)  : line;
      const labelTr = animate ? label.transition().duration(dur).ease(ease) : label;
      if (visible && botPos > topPos) {{
        const y = ySc(topPos), h = Math.max(0, ySc(botPos) - ySc(topPos));
        const mid = ySc((topPos + botPos) / 2);
        bandTr.attr("y",y).attr("height",h).attr("opacity",1);
        lineTr.attr("y1",ySc(topPos)).attr("y2",ySc(topPos)).attr("opacity",1);
        labelTr.attr("y", mid).text(labelTxt).attr("opacity",1);
      }} else {{
        bandTr.attr("height",0).attr("opacity",0);
        lineTr.attr("opacity",0);
        labelTr.attr("opacity",0);
      }}
    }}

    // Champions League band: pos 0.3 → cl+0.5
    const clTxt = idx <= 5 ? "CHAMPIONS LEAGUE (1 SPOT)" :
                  idx <= 11 ? "CHAMPIONS LEAGUE (2 SPOTS)" : "CHAMPIONS LEAGUE";
    setBand(clBand, clLine, clLabel, 0.3, z.cl + 0.5, clTxt, z.cl > 0);

    // Europa League band: pos cl+0.5 → cl+el+0.5
    const elTxt = idx <= 11 ? "UEFA CUP" : idx < 30 ? "EUROPA LEAGUE" : "EUROPA LEAGUE";
    setBand(elBand, elLine, elLabel, z.cl + 0.5, z.cl + z.el + 0.5, elTxt, z.el > 0);

    // Conference League band: pos cl+el+0.5 → cl+el+1.5 (only 2021/22+)
    const clBot = z.cl + z.el + 0.5;
    setBand(confBand, confLine, confLabel, clBot, clBot + 1, "CONFERENCE LEAGUE", z.conf > 0);
  }}

  [17].forEach(p => g.append("line").attr("x1",0).attr("x2",W).attr("y1",ySc(p)).attr("y2",ySc(p))
    .attr("stroke","#30363d").attr("stroke-width",.8).attr("stroke-dasharray","4,6"));
  [1,10,20].forEach(p => g.append("line").attr("x1",0).attr("x2",W).attr("y1",ySc(p)).attr("y2",ySc(p))
    .attr("stroke","#1a1f28").attr("stroke-width",.5));

  // Pre-EPL divider
  const divX = (xSc(seasons[0])+xSc(seasons[1]))/2;
  g.append("line").attr("x1",divX).attr("x2",divX).attr("y1",-18).attr("y2",H)
    .attr("stroke","#f0ad4e33").attr("stroke-width",1.5).attr("stroke-dasharray","5,4");
  g.append("text").attr("x",divX+6).attr("y",-8)
    .attr("text-anchor","start").attr("font-size",8)
    .attr("fill","#f0ad4e88").attr("font-family","IBM Plex Mono,monospace")
    .text("Premier League →");

  const playhead = g.append("line").attr("y1",0).attr("y2",H)
    .attr("stroke","#ffffff18").attr("stroke-width",1.5);

  // ── computeDisplayData ────────────────────────────────────────
  function computeDisplayData(rawPos, slice) {{
    let lastKnown=null, firstSeen=false, lastReal=null;
    const solid=[], full=[], realPts=[];
    for (let i=0; i<slice; i++) {{
      const p=rawPos[i];
      if (p!==null) {{
        solid.push(p); full.push(p);
        lastReal={{i,s:seasons[i],p}}; lastKnown=p; firstSeen=true;
      }} else if (firstSeen) {{
        solid.push(null); full.push(lastKnown);
      }} else {{
        solid.push(null); full.push(null);
      }}
    }}
    const isRelegd = firstSeen && rawPos[slice-1]===null;
    return {{solid,full,realPts:solid.map((p,i)=>p!==null?{{i,s:seasons[i],p}}:null).filter(Boolean),lastReal,isRelegd}};
  }}

  const lineGen = d3.line()
    .defined(d=>d!==null).x((_,i)=>xSc(seasons[i])).y(d=>ySc(d))
    .curve(d3.curveCatmullRom.alpha(.5));

  // ── Build paths and markers for ALL teams ─────────────────────
  const allNames = Object.keys(teams);
  const hlNames  = allNames.filter(t=>teams[t].hl);
  const bgNames  = allNames.filter(t=>!teams[t].hl);

  // Paths: bg teams
  const bgPaths={{}}, bgGhost={{}};
  bgNames.forEach(t => {{
    bgGhost[t] = g.append("path").attr("fill","none")
      .attr("stroke","#4a5568").attr("stroke-width",.5)
      .attr("stroke-dasharray","2,6").attr("opacity",.15);
    bgPaths[t] = g.append("path").attr("fill","none")
      .attr("stroke","#4a5568").attr("stroke-width",.8).attr("opacity",.22);
  }});

  // Paths: hl teams
  const hlGhost={{}}, hlPaths={{}}, hlDots={{}};
  hlNames.forEach(t => {{
    const c=teams[t].color;
    hlGhost[t]=g.append("path").attr("fill","none").attr("stroke",c)
      .attr("stroke-width",1.1).attr("stroke-dasharray","3,6").attr("opacity",.22);
    hlPaths[t]=g.append("path").attr("fill","none").attr("stroke",c)
      .attr("stroke-width",2.2).attr("opacity",.9).attr("filter","url(#glow)");
    hlDots[t]=g.append("g");
  }});

  // ── Marker groups — ALL teams get one ─────────────────────────
  // Structure: <g> → <circle> ring + <text> initials + <image> logo
  // Initials are always drawn; logo replaces them if it loads.
  const markerGrps={{}};

  allNames.forEach(t => {{
    const info=teams[t];
    const sn=t.replace(/[^a-zA-Z0-9]/g,"-");
    const r=info.hl?14:9;
    const fontSize=info.hl?8:6;
    const clipId=`clip-${{sn}}`;

    defs.append("clipPath").attr("id",clipId)
      .append("circle").attr("r",r-1);

    const grp=g.append("g")
      .style("opacity","0")
      .style("cursor","pointer")
      .on("mouseenter",ev=>showTip(ev,t))
      .on("mousemove",ev=>moveTip(ev))
      .on("mouseleave",hideTip);

    // Ring — white background for clubs whose badge needs a light canvas
    const bgFill = info.lightBadge ? "#ffffff" : "#0d1117";
    grp.append("circle").attr("r",r)
      .attr("fill",bgFill).attr("stroke",info.color)
      .attr("stroke-width",info.hl?1.8:1.2);

    // Initials text — always present as fallback
    grp.append("text").attr("class","initials")
      .attr("text-anchor","middle").attr("dominant-baseline","central")
      .attr("font-size",fontSize).attr("font-weight","600")
      .attr("font-family","IBM Plex Mono,monospace")
      .attr("fill",info.hl?info.color:"#9ca3af")
      .attr("pointer-events","none")
      .text(info.initials);

    // Logo image — hidden until loaded
    grp.append("image").attr("class","logo-img")
      .attr("href","").attr("x",-(r-1)).attr("y",-(r-1))
      .attr("width",(r-1)*2).attr("height",(r-1)*2)
      .attr("clip-path",`url(#${{clipId}})`)
      .attr("preserveAspectRatio","xMidYMid meet")
      .attr("pointer-events","none")
      .style("display","none");

    markerGrps[t]=grp;
  }});

  // Hit areas for hl teams (wide invisible stroke for easier hover)
  hlNames.forEach(t => {{
    g.append("path").attr("fill","none").attr("stroke","transparent")
      .attr("stroke-width",12).attr("class","hit").attr("data-team",t)
      .style("cursor","pointer")
      .on("mouseenter",ev=>showTip(ev,t))
      .on("mousemove",ev=>moveTip(ev))
      .on("mouseleave",hideTip);
  }});

  // ── Axes ──────────────────────────────────────────────────────
  const xAx=g.append("g").attr("transform",`translate(0,${{H}})`);
  xAx.call(d3.axisBottom(xSc).tickValues(seasons.filter((_,i)=>i%2===0)).tickSize(5))
     .select(".domain").remove();
  xAx.selectAll("text")
    .attr("transform","rotate(-40)").attr("text-anchor","end")
    .attr("dx","-4px").attr("dy","3px").attr("font-size",9)
    .attr("fill",d=>d.includes("First Div")?"#f0ad4e":"#6e7681")
    .attr("font-weight",d=>d.includes("First Div")?"600":"400")
    .attr("font-family","IBM Plex Mono,monospace");
  xAx.selectAll(".tick line").attr("stroke","#30363d");
  g.append("g").call(d3.axisLeft(ySc).tickValues(d3.range(1,23)).tickSize(0).tickFormat(d=>d))
   .select(".domain").remove();
  g.select("g").selectAll("text").attr("x",-9).attr("font-size",9)
    .attr("fill","#484f58").attr("font-family","IBM Plex Mono,monospace");

  // ── Tooltip ───────────────────────────────────────────────────
  const tip=document.getElementById("tip");

  function showTip(ev,name) {{
    const info=teams[name];
    const pts=info.pos.map((p,i)=>p!==null?{{s:seasons[i],p}}:null).filter(Boolean);
    const vis=pts.filter(d=>seasons.indexOf(d.s)<=frame);
    if (!vis.length) return;
    const cur=vis[vis.length-1];
    const best=vis.reduce((a,b)=>a.p<b.p?a:b);
    const ttls=vis.filter(d=>d.p===1).map(d=>d.s);
    let h=`<strong style="color:${{info.color}}">${{name}}</strong>`;
    h+=`${{cur.s}}: <b>P${{cur.p}}</b><br>${{vis.length}} EPL seasons`;
    if (ttls.length) h+=`<br>🏆 ${{ttls.join(", ")}}`;
    h+=`<br>Best: P${{best.p}} (${{best.s}})`;
    tip.innerHTML=h; tip.style.display="block"; moveTip(ev);
    dimAll(name);
  }}
  function moveTip(ev){{ tip.style.left=(ev.clientX+14)+"px"; tip.style.top=(ev.clientY-30)+"px"; }}
  function hideTip(){{ tip.style.display="none"; selectedTeam?dimAll(selectedTeam):undimAll(); }}

  // ── Dim/undim ─────────────────────────────────────────────────
  function setMarkerOpacity(t, op) {{
    markerGrps[t].interrupt().style("opacity", String(op));
  }}

  function dimAll(active) {{
    bgNames.forEach(t => {{
      const on=(t===active);
      bgPaths[t].attr("opacity",on?.85:.01).attr("stroke",on?"#88aadd":"#4a5568").attr("stroke-width",on?2:.8);
      bgGhost[t].attr("opacity",on?.5:.01);
      setMarkerOpacity(t, on?1:.04);
    }});
    hlNames.forEach(t => {{
      const on=(t===active);
      hlPaths[t].attr("opacity",on?1:.04);
      hlGhost[t].attr("opacity",on?.3:.01);
      hlDots[t].attr("opacity",on?1:.03);
      setMarkerOpacity(t, on?1:.04);
    }});
  }}

  function undimAll() {{
    bgNames.forEach(t => {{
      bgPaths[t].attr("opacity",.22).attr("stroke","#4a5568").attr("stroke-width",.8);
      bgGhost[t].attr("opacity",.15);
      const {{lastReal,isRelegd}}=computeDisplayData(teams[t].pos,frame+1);
      setMarkerOpacity(t, (lastReal&&isRelegd)?.7:(!isRelegd&&lastReal&&lastReal.i===frame)?.8:0);
    }});
    hlNames.forEach(t => {{
      hlPaths[t].attr("opacity",.9); hlGhost[t].attr("opacity",.22); hlDots[t].attr("opacity",1);
      const {{lastReal,isRelegd}}=computeDisplayData(teams[t].pos,frame+1);
      setMarkerOpacity(t, lastReal?(isRelegd?.85:1):0);
    }});
  }}

  // ── Banner ────────────────────────────────────────────────────
  const bannerEl=document.getElementById("banner");
  const bannerLogo=document.getElementById("banner-logo");
  const bannerSeason=document.getElementById("banner-season");
  const bannerName=document.getElementById("banner-name");
  const bannerSuffix=document.getElementById("banner-suffix");

  function updateBanner(idx) {{
    const s=seasons[idx], c=champ[idx], info=c?teams[c]:null;
    bannerSeason.textContent=s.includes("First Div")?"1991/92 First Division (pre-EPL)":s+" Champion";
    if (c&&info) {{
      bannerName.textContent="🏆 "+c; bannerName.style.color=info.color;
      bannerSuffix.textContent=`P1 of ${{Object.keys(EPL.raw[s]).length}} teams`;
      bannerEl.style.borderColor=info.color+"55";
      bannerLogo.dataset.team=c;
      const src=info.logo||"";
      if (src) {{ bannerLogo.src=src; bannerLogo.style.opacity="1"; bannerLogo.style.borderColor=info.color; }}
      else bannerLogo.style.opacity="0";
    }} else {{
      bannerName.textContent="—"; bannerName.style.color="#6e7681";
      bannerLogo.style.opacity="0"; bannerEl.style.borderColor="";
    }}
  }}

  // ── positionMarker — shared for all teams ─────────────────────
  // Marker always sits exactly on its season column — no rightward offset.
  // Active: column of current frame at their position.
  // Relegated: pinned at their last real season column, stays forever.
  function positionMarker(t, idx) {{
    const info=teams[t];
    const {{lastReal,isRelegd}}=computeDisplayData(info.pos, idx+1);
    const grp=markerGrps[t];
    grp.interrupt();

    if (!lastReal) {{ grp.style("opacity","0"); return; }}

    let lx, ly, targetOp;
    if (!isRelegd && lastReal.i===idx) {{
      lx = xSc(seasons[idx]);
      ly = ySc(lastReal.p);
      targetOp = "1";
    }} else if (isRelegd) {{
      lx = xSc(lastReal.s);
      ly = ySc(lastReal.p);
      targetOp = info.hl ? "0.85" : "0.75";
    }} else {{
      grp.style("opacity","0"); return;
    }}

    grp.attr("transform",`translate(${{lx}},${{ly}})`).style("opacity",targetOp);
  }}

  // ── renderFrame ───────────────────────────────────────────────
  function renderFrame(idx, animate) {{
    const dur=animate?Math.min(speed*.75,550):0, ease=d3.easeCubicInOut;
    const slice=idx+1;

    // Playhead
    playhead.attr("x1",xSc(seasons[idx])).attr("x2",xSc(seasons[idx]));

    document.getElementById("slider").value=idx;
    document.getElementById("season-lbl").textContent=seasons[idx];
    updateBanner(idx);
    updateZoneBands(idx, animate, dur, ease);

    // Background teams: solid line (breaks at relegation) + dashed ghost (carry-forward)
    bgNames.forEach(t => {{
      const {{solid,full}}=computeDisplayData(teams[t].pos,slice);
      (animate?bgPaths[t].transition().duration(dur).ease(ease):bgPaths[t]).attr("d",lineGen(solid));
      (animate?bgGhost[t].transition().duration(dur).ease(ease):bgGhost[t]).attr("d",lineGen(full));
    }});

    // Highlighted teams: solid + ghost + dots
    hlNames.forEach(t => {{
      const info=teams[t];
      const {{solid,full,realPts}}=computeDisplayData(info.pos,slice);

      (animate?hlPaths[t].transition().duration(dur).ease(ease):hlPaths[t]).attr("d",lineGen(solid));
      (animate?hlGhost[t].transition().duration(dur).ease(ease):hlGhost[t]).attr("d",lineGen(full));
      d3.selectAll(`.hit[data-team="${{t}}"]`).attr("d",lineGen(solid));

      hlDots[t].selectAll("circle").interrupt();
      const dots=hlDots[t].selectAll("circle").data(realPts,d=>d.i);
      dots.exit().remove();
      dots.enter().append("circle")
        .attr("cx",d=>xSc(d.s)).attr("cy",d=>ySc(d.p)).attr("r",0)
        .attr("fill",info.color).attr("opacity",.8)
        .transition().duration(300).ease(d3.easeBackOut).attr("r",d=>d.i===idx?4.5:2.2);
      dots.transition().duration(dur).ease(ease)
        .attr("cx",d=>xSc(d.s)).attr("cy",d=>ySc(d.p)).attr("r",d=>d.i===idx?4.5:2.2);
    }});

    // All markers
    allNames.forEach(t => positionMarker(t, idx));

    if (selectedTeam) dimAll(selectedTeam);
  }}

  // ── Playback ──────────────────────────────────────────────────
  function step(){{ if(!playing)return; if(frame>=N-1){{pause();return;}} frame++; renderFrame(frame,true); timer=setTimeout(step,speed); }}
  function play(){{ if(frame>=N-1)frame=0; playing=true; document.getElementById("play-btn").textContent="⏸ Pause"; document.getElementById("play-btn").classList.add("playing"); timer=setTimeout(step,speed); }}
  function pause(){{ playing=false; clearTimeout(timer); document.getElementById("play-btn").textContent="▶ Play"; document.getElementById("play-btn").classList.remove("playing"); }}

  document.getElementById("play-btn").addEventListener("click",()=>playing?pause():play());
  document.getElementById("reset-btn").addEventListener("click",()=>{{pause();frame=0;renderFrame(0,false);}});
  document.getElementById("slider").addEventListener("input",function(){{pause();frame=+this.value;renderFrame(frame,false);}});
  document.querySelectorAll(".speed-btn").forEach(b=>b.addEventListener("click",function(){{
    document.querySelectorAll(".speed-btn").forEach(x=>x.classList.remove("active"));
    this.classList.add("active"); speed=+this.dataset.ms;
  }}));
  document.addEventListener("keydown",ev=>{{
    if(ev.code==="Space"){{ev.preventDefault();playing?pause():play();}}
    if(ev.code==="ArrowRight"&&!playing){{frame=Math.min(frame+1,N-1);renderFrame(frame,true);}}
    if(ev.code==="ArrowLeft"&&!playing){{frame=Math.max(frame-1,0);renderFrame(frame,true);}}
  }});

  // ── Roster table ──────────────────────────────────────────────
  function eplSeasons(t){{ return teams[t].pos.slice(1).filter(p=>p!==null).length; }}
  function allSeasons(t){{ return teams[t].pos.filter(p=>p!==null).length; }}
  function bestFinish(t){{ const ps=teams[t].pos.filter(p=>p!==null); return ps.length?Math.min(...ps):99; }}

  let sortKey="seasons";
  function buildRoster(){{
    // Include ALL teams that appear in any season (including pre-EPL)
    const list=Object.keys(teams).filter(t=>allSeasons(t)>0)
      .map(t=>(({{t,
        seasons:eplSeasons(t),
        preEPLOnly: eplSeasons(t)===0,
        best:bestFinish(t),
        color:teams[t].color,
        hl:teams[t].hl}})));
    if(sortKey==="alpha") list.sort((a,b)=>a.t.localeCompare(b.t));
    else if(sortKey==="best") list.sort((a,b)=>a.best-b.best||b.seasons-a.seasons);
    else list.sort((a,b)=>b.seasons-a.seasons||a.t.localeCompare(b.t));
    document.getElementById("club-count").textContent=`— ${{list.length}} clubs`;
    const grid=document.getElementById("team-grid");
    grid.innerHTML="";
    list.forEach(d=>{{
      const chip=document.createElement("div");
      chip.className="chip"+(selectedTeam===d.t?" selected":"");
      chip.style.setProperty("--cc",d.color);
      chip.dataset.team=d.t;
      const seasonsLabel = d.preEPLOnly
        ? `pre-EPL only · P${{d.best}}`
        : `${{d.seasons}}y · P${{d.best}}`;
      chip.innerHTML=`<span class="dot"></span><span>${{d.t}}</span><span class="meta">${{seasonsLabel}}</span>`;
      chip.addEventListener("click",()=>toggleSelect(d.t));
      grid.appendChild(chip);
    }});
  }}

  function toggleSelect(team){{
    selectedTeam=(selectedTeam===team)?null:team;
    selectedTeam?dimAll(selectedTeam):undimAll();
    document.querySelectorAll(".chip").forEach(c=>c.classList.toggle("selected",c.dataset.team===selectedTeam));
    document.getElementById("chart-wrap").scrollIntoView({{behavior:"smooth",block:"nearest"}});
  }}

  document.querySelectorAll(".sort-btn").forEach(b=>b.addEventListener("click",function(){{
    document.querySelectorAll(".sort-btn").forEach(x=>x.classList.remove("active"));
    this.classList.add("active"); sortKey=this.dataset.sort; buildRoster();
  }}));

  // ── Logo resolution — direct URL first, REST API fallback ───────
  // Initials are always visible; logo replaces them only if it loads cleanly.
  async function resolveLogos(){{
    const probe=src=>new Promise(res=>{{
      const img=new Image(); img.onload=()=>res(src); img.onerror=()=>res(null); img.src=src;
    }});

    const tasks=Object.entries(markerGrps).map(async([team,grp])=>{{
      const info=teams[team];
      const imgEl=grp.select("image.logo-img");
      if (imgEl.empty()) return;

      let src=null;

      // 1. Try direct URL if provided
      if (info.logo) src=await probe(info.logo);

      // 2. REST API fallback
      if (!src && info.wiki) {{
        try {{
          const resp=await fetch(
            `https://en.wikipedia.org/api/rest_v1/page/summary/${{info.wiki}}`,
            {{headers:{{"Api-User-Agent":"EPL-chart/1.0 (kpolimis)"}}}}
          );
          if (resp.ok) {{
            const data=await resp.json();
            // Prefer SVG (club badge) over JPG (might be stadium/player photo)
            const orig=data?.originalimage?.source||"";
            const thumb=data?.thumbnail?.source||"";
            const candidate=orig.endsWith(".svg")?orig:thumb.endsWith(".svg")?thumb:orig||thumb;
            if (candidate) src=await probe(candidate);
          }}
        }} catch(e){{}}
      }}

      if (src) {{
        info.logo=src;
        imgEl.attr("href",src).style("display",null);
        grp.select("text.initials").style("display","none");
        const bl=document.getElementById("banner-logo");
        if (bl.dataset.team===team){{ bl.src=src; bl.style.opacity="1"; }}
      }}
      // If no src: initials stay visible (already rendered)
    }});
    Promise.allSettled(tasks);
  }}

  // ── Init ──────────────────────────────────────────────────────
  renderFrame(0,false);
  buildRoster();
  resolveLogos();
}})();
</script>
</body>
</html>
"""

with open("index.html","w",encoding="utf-8") as f: f.write(HTML)
print("✓ index.html")

import os, json
os.makedirs("data",exist_ok=True)
with open("data/standings.json","w",encoding="utf-8") as f:
    json.dump({"seasons":SEASONS,"raw":RAW_DATA,"teams":{t:{"pos":v["pos"],"initials":v["initials"]} for t,v in teams_js.items()}},f,ensure_ascii=False,indent=2)
print("✓ data/standings.json")
