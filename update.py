import urllib.request
import json
import html
import os
import shutil
import re
from datetime import datetime, timezone


# =========================================================
# LIENS ET PARAMÈTRES
# =========================================================

DISCORD_INVITE = "ujHH2bNzhn"
YOUTUBE_URL = "https://www.youtube.com/@Legodingo13"
SOCIALCOUNTS_URL = (
    "https://socialcounts.org/"
    "youtube-live-subscriber-count/"
    "UC_1T2zJa_uOU2xNeQHdPutQ"
)
FOE_URL = "https://fr0.forgeofempires.com/page/"
GUNS_URL = "https://guns.lol/legodingo13"

# Sites tiers Forge of Empires
FOE_WIKI_URL = "https://fr.wiki.forgeofempires.com/index.php?title=Accueil"
FORGEDB_URL = "https://foestats.com/"
FOE_SCOREDB_URL = "https://foe.scoredb.io/Worlds"
FOE_DATA_URL = "https://foe-data.ovh/"
BANANA_DB_URL = "https://foe-buildings-database.streamlit.app/"
FOE_TOOLS_URL = "https://foe.tools/fr/"

# Extensions
FOE_HAMMER_URL = "https://chromewebstore.google.com/detail/forge-hammer/kmicglnhmpaebfcoiojigbnepklclboa?hl=fr"
FOE_HELPER_URL = "https://foe-helper.com/"

# Chaînes YouTube tierces
UBERNERD14_URL = "https://www.youtube.com/@UBERnerd14"
SENSHI_URL = "https://www.youtube.com/@drikanorrin9697"
PIXELPULSE_URL = "https://www.youtube.com/@PixelVibes63"
MOOINGCAT_URL = "https://www.youtube.com/@MooingCatFoE"
GUIGEEKS_URL = "https://www.youtube.com/@GuigeekX"
ZOUMA_URL = "https://www.youtube.com/@PassionFoeforgeofempire"

SITE_BASE = "https://legodingo13.github.io/site-internet-legodingo13/"

# Compteur de vues public et gratuit (Page Views API)
PAGEVIEWS_SITE = "legodingo13.github.io"
# Clé historique conservée volontairement pour ne pas remettre les compteurs à zéro après le renommage du dépôt.
PAGEVIEWS_BASE_PATH = "/serveur-discord-legodingo13"

# Nous ajouterons la vraie balise Google Search Console plus tard.
GOOGLE_META = """<!-- Google Search Console -->"""


# =========================================================
# FONCTIONS DE DONNÉES
# =========================================================

def format_number(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(value)


def read_previous_youtube_count():
    if not os.path.exists("last-update.txt"):
        return None

    try:
        with open("last-update.txt", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Abonnés YouTube :"):
                    value = line.split(":", 1)[1].strip()
                    if value not in ("", "indisponible", "inconnu"):
                        return value
    except Exception:
        pass

    return None


def get_youtube_subscribers():
    previous_count = read_previous_youtube_count()

    try:
        request = urllib.request.Request(
            SOCIALCOUNTS_URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/140.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            },
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8", errors="ignore")

        patterns = [
            r"Legodingo13(?:&#x27;|['’])s YouTube presence with\s*([\d,\s]+)\s*subscribers",
            r"Legodingo13.*?YouTube presence with\s*([\d,\s]+)\s*subscribers",
            r"with\s*([\d,\s]+)\s*subscribers\s+and\s+[\d,\s]+\s+videos",
        ]

        for pattern in patterns:
            match = re.search(pattern, page, flags=re.IGNORECASE | re.DOTALL)
            if match:
                number = re.sub(r"[^\d]", "", match.group(1))
                if number:
                    return format_number(int(number))

        json_patterns = [
            r'"subscriberCount"\s*:\s*"?(\d+)"?',
            r'"subscribers"\s*:\s*"?(\d+)"?',
            r'"subscriber_count"\s*:\s*"?(\d+)"?',
        ]

        for pattern in json_patterns:
            match = re.search(pattern, page, flags=re.IGNORECASE)
            if match:
                return format_number(int(match.group(1)))

        print("SocialCounts a répondu, mais le nombre d'abonnés n'a pas été trouvé.")

    except Exception as error:
        print("Impossible de lire SocialCounts :", error)

    if previous_count:
        return previous_count

    return "indisponible"


# =========================================================
# STATISTIQUES DISCORD
# =========================================================

discord_url = (
    "https://discord.com/api/v10/invites/"
    + DISCORD_INVITE
    + "?with_counts=true"
)

discord_request = urllib.request.Request(
    discord_url,
    headers={"User-Agent": "Mozilla/5.0"},
)

with urllib.request.urlopen(discord_request, timeout=30) as response:
    discord_data = json.loads(response.read().decode("utf-8"))

guild = discord_data.get("guild", {})
guild_name = html.escape(guild.get("name", "Legodingo13 - Serv FOE FR"))
member_count = format_number(discord_data.get("approximate_member_count", "inconnu"))
online_count = format_number(discord_data.get("approximate_presence_count", "inconnu"))


# =========================================================
# STATISTIQUES YOUTUBE
# =========================================================

youtube_subscribers = get_youtube_subscribers()
youtube_display = (
    "Compteur temporairement indisponible"
    if youtube_subscribers == "indisponible"
    else f"{youtube_subscribers} abonnés"
)


# =========================================================
# DATE
# =========================================================

updated = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")


# =========================================================
# STYLE COMMUN À TOUT LE SITE
# =========================================================

CSS = r"""
* { box-sizing: border-box; }
html { min-height: 100%; }
html, body { cursor: url("cursor_default.cur"), auto; }
body * { cursor: inherit; }
a, a *, button, button * { cursor: url("cursor_hover.cur"), pointer !important; }

body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, Helvetica, sans-serif;
    color: white;
    background:
        linear-gradient(rgba(6,10,18,.43), rgba(6,10,18,.76)),
        url("fond.png") center / cover no-repeat fixed;
    padding: 40px 20px;
}

.page { width: 100%; max-width: 1080px; margin: 0 auto; }
.card {
    position: relative;
    width: 100%;
    background: linear-gradient(145deg, rgba(17,21,31,.91), rgba(31,20,18,.87));
    border: 1px solid rgba(255,210,130,.23);
    border-radius: 28px;
    overflow: hidden;
    box-shadow: 0 30px 90px rgba(0,0,0,.58);
    backdrop-filter: blur(8px);
}
.card::before {
    content: "";
    position: absolute;
    top: 0; left: 10%; right: 10%; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,177,73,.9), transparent);
}

.site-head { text-align: center; padding: 30px 32px 16px; }
.logo { width: 165px; max-width: 72%; height: auto; display: block; margin: 0 auto 14px; filter: drop-shadow(0 8px 15px rgba(0,0,0,.42)); }
.badge {
    display: inline-block;
    padding: 8px 17px;
    border-radius: 999px;
    background: rgba(202,112,33,.20);
    border: 1px solid rgba(255,183,82,.40);
    color: #ffd69a;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
}

.nav {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin-top: 18px;
}
.nav a {
    text-decoration: none;
    color: #eceff5;
    padding: 10px 16px;
    border-radius: 11px;
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.055);
    font-weight: 700;
    font-size: 14px;
    transition: .2s ease;
}
.nav a:hover { transform: translateY(-2px); background: rgba(255,255,255,.10); border-color: rgba(255,210,130,.35); }
.nav a.active { color: #1d160f; background: linear-gradient(135deg,#ffd493,#e8a34b); border-color: transparent; }

.content { padding: 18px 38px 38px; text-align: center; }
h1 { margin: 8px 0 0; font-size: clamp(34px,5vw,56px); line-height: 1.05; text-shadow: 0 4px 20px rgba(0,0,0,.55); }
h2 { margin: 10px 0 16px; }
.gold { color: #ffd493; }
.lead { max-width: 820px; margin: 18px auto 28px; color: #e7e3df; font-size: 16px; line-height: 1.7; }

.discord-presentation-image {
    display: block;
    width: min(100%, 980px);
    height: auto;
    margin: 10px auto 28px;
    border-radius: 24px;
    box-shadow: 0 18px 45px rgba(0,0,0,.38);
}

.stats { display: grid; grid-template-columns: repeat(2,1fr); gap: 24px; margin: 26px 0; }
.stat {
    padding: 30px 20px;
    border-radius: 20px;
    background: linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.035));
    border: 1px solid rgba(255,255,255,.09);
}
.number { display: block; margin-bottom: 9px; font-size: clamp(42px,6vw,62px); line-height: 1; font-weight: 800; }
.label { color: #d4d7de; font-size: 16px; }
.online-dot { display:inline-block; width:10px; height:10px; margin-right:7px; border-radius:50%; background:#3ba55d; box-shadow:0 0 8px rgba(59,165,93,.8); }

.primary-button {
    display: inline-block;
    padding: 15px 27px;
    border-radius: 14px;
    text-decoration: none;
    color: white;
    font-size: 17px;
    font-weight: 700;
    background: linear-gradient(135deg,#5865F2,#7289da);
    box-shadow: 0 12px 30px rgba(88,101,242,.35);
    transition: .2s ease;
}
.primary-button:hover { transform: translateY(-3px); box-shadow:0 17px 35px rgba(88,101,242,.45); }
.gold-button { background: linear-gradient(135deg,#c47a2b,#f0b45c); color:#1b130d; box-shadow:0 12px 30px rgba(196,122,43,.25); }

.grid { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:24px; }
.grid.two { grid-template-columns: repeat(2,1fr); }
.tile {
    min-height: 185px;
    padding: 24px 18px;
    border-radius: 18px;
    text-decoration: none;
    color: white;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.10);
    transition:.2s ease;
}
.tile:hover { transform:translateY(-4px); background:rgba(255,255,255,.09); border-color:rgba(255,210,130,.42); }
.tile-logo { display:block; object-fit:contain; margin:0 auto 12px; filter:drop-shadow(0 5px 10px rgba(0,0,0,.35)); transition:.2s; }
.tile:hover .tile-logo { transform:scale(1.07); }
.youtube-logo { width:92px; height:58px; }
.foe-logo { width:90px; height:70px; }
.guns-logo { width:92px; height:92px; }
.server-logo-small { width:100px; height:auto; }
.profile-tableau-logo { width:110px; height:110px; object-fit:contain; }
.tutorials-logo { width:110px; height:110px; object-fit:contain; }

.section-block { margin-top: 44px; }
.section-block:first-of-type { margin-top: 30px; }
.section-title {
    margin: 0 0 8px;
    font-size: 28px;
    color: #ffffff;
}
.section-subtitle {
    max-width: 820px;
    margin: 0 auto 18px;
    color: #bfc5cf;
    font-size: 14px;
    line-height: 1.55;
}
.third-party-logo {
    width: 96px;
    height: 88px;
    object-fit: contain;
}
.third-party-logo.wide {
    width: 108px;
    height: 82px;
}
.third-party-logo.small {
    width: 82px;
    height: 82px;
}
.external-badge {
    display: inline-block;
    margin-top: 10px;
    padding: 5px 9px;
    border-radius: 999px;
    border: 1px solid rgba(255,212,147,.22);
    background: rgba(255,212,147,.07);
    color: #d9c39f;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .35px;
}
.tile-title { font-size:19px; font-weight:700; margin-bottom:7px; }
.tile-detail { color:#c4c9d2; font-size:14px; line-height:1.45; }
.tile-count { color:#ffd493; font-size:25px; font-weight:800; margin-bottom:7px; }

.table-frame {
    width: 100%;
    overflow: auto;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 18px;
    padding: 16px;
    margin: 24px auto;
}
.table-image { display:block; max-width:none; width:auto; min-width:100%; height:auto; margin:0 auto; border-radius:8px; }
.notice { max-width:760px; margin:22px auto; padding:18px; border-radius:15px; background:rgba(255,212,147,.08); border:1px solid rgba(255,212,147,.20); color:#e6dccd; line-height:1.6; }

.footer {
    margin: 0 38px;
    padding: 23px 0 30px;
    border-top:1px solid rgba(255,255,255,.08);
    color:#aeb4bf;
    font-size:13px;
    display:grid;
    grid-template-columns:1fr auto 1fr;
    align-items:end;
    gap:16px;
}
.footer-copy { grid-column:2; text-align:center; }
.footer small { color:#7f8794; }
.page-view-counter {
    grid-column:1;
    justify-self:start;
    display:inline-flex;
    align-items:center;
    gap:7px;
    min-height:22px;
    color:#d9dce3;
    font-size:13px;
    font-weight:600;
    line-height:1;
    opacity:.92;
}
.page-view-counter svg {
    width:18px;
    height:18px;
    display:block;
    fill:currentColor;
}
.page-view-number { min-width:1.5em; text-align:left; }
.footer-spacer { grid-column:3; }

/* =========================================================
   LOGO CLIQUABLE + ROI QUI TOMBE
   ========================================================= */

.logo-zone {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 0 14px 0;
}

.logo-trigger {
    display: block;
    flex: 0 0 165px;
    width: 165px;
    max-width: 72%;
    padding: 0;
    margin: 0;
    border: 0;
    background: transparent;
    line-height: 0;
}

.logo-trigger .logo {
    display: block;
    width: 100%;
    max-width: none;
    height: auto;
    margin: 0;
    transition: transform .18s ease, filter .18s ease;
}

.logo-trigger:hover .logo {
    transform: scale(1.045);
    filter:
        drop-shadow(0 8px 15px rgba(0,0,0,.42))
        drop-shadow(0 0 12px rgba(255,184,82,.22));
}

.logo-trigger:active .logo {
    transform: scale(.98);
}

.falling-king {
    position: fixed;
    left: 0;
    top: 0;
    width: clamp(125px, 15vw, 230px);
    height: auto;
    z-index: 99999;
    pointer-events: none;
    user-select: none;
    -webkit-user-drag: none;
    will-change: transform, opacity;
    filter: drop-shadow(0 12px 18px rgba(0,0,0,.38));
}

@media (prefers-reduced-motion: reduce) {
    .falling-king {
        display: none;
    }
}

.discord-presentation-image { border-radius: 18px; }


/* =========================================================
   PAGE TUTORIELS DE JEU
   ========================================================= */

.tutorial-page-intro {
    max-width: 820px;
    margin: 0 auto 26px;
    color: #cfd3dc;
    line-height: 1.65;
}

.tutorial-accordion {
    width: 100%;
    max-width: 900px;
    margin: 22px auto 0;
    text-align: left;
}

.tutorial-empty {
    padding: 34px 24px;
    border: 1px dashed rgba(255,255,255,.16);
    border-radius: 16px;
    color: #aeb4bf;
    text-align: center;
    background: rgba(255,255,255,.025);
}

.tutorial-menu {
    position: relative;
    border-top: 1px solid rgba(255,255,255,.13);
    scroll-margin-top: 22px;
}
.tutorial-menu:last-child {
    border-bottom: 1px solid rgba(255,255,255,.13);
}

.tutorial-menu-header {
    width: 100%;
    border: 0;
    background: transparent;
    color: #f5f6f8;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    padding: 17px 4px;
    font-size: 18px;
    font-weight: 700;
    text-align: left;
}

.tutorial-menu-header:hover {
    color: #ffd493;
}

.tutorial-anchor-link {
    position: absolute;
    top: 12px;
    right: 42px;
    width: 34px;
    height: 34px;
    border-radius: 9px;
    display: grid;
    place-items: center;
    color: #9fa8b7;
    text-decoration: none;
    font-size: 16px;
    opacity: .72;
    z-index: 2;
    transition: .18s ease;
}
.tutorial-anchor-link:hover,
.tutorial-anchor-link:focus-visible {
    color: #ffd493;
    background: rgba(255,212,147,.08);
    opacity: 1;
}

.tutorial-copy-toast {
    position: fixed;
    left: 50%;
    bottom: 26px;
    transform: translateX(-50%);
    z-index: 10020;
    max-width: calc(100vw - 32px);
    padding: 11px 16px;
    border-radius: 12px;
    border: 1px solid rgba(255,212,147,.28);
    background: rgba(22,23,29,.96);
    color: #f4f4f6;
    box-shadow: 0 10px 30px rgba(0,0,0,.35);
    font-size: 14px;
    font-weight: 700;
    text-align: center;
}
.tutorial-menu-header { padding-right: 82px; }

.tutorial-menu-updated {
    margin: 0 0 16px;
    color: #8f98a7;
    font-size: 12px;
    line-height: 1.4;
}

.tutorial-menu-arrow {
    flex: 0 0 auto;
    font-size: 24px;
    line-height: 1;
    color: #bcc2cd;
    transition: transform .18s ease;
}
.tutorial-menu.open .tutorial-menu-arrow { transform: rotate(90deg); }

.tutorial-menu-panel {
    display: none;
    padding: 0 4px 24px;
}
.tutorial-menu.open .tutorial-menu-panel { display: block; }

.tutorial-public-block + .tutorial-public-block { margin-top: 18px; }
.tutorial-text {
    color: #e5e8ee;
    font-size: 16px;
    line-height: 1.7;
    overflow-wrap: anywhere;
}
.tutorial-text p { margin: 0 0 10px; }
.tutorial-text a.tutorial-link {
    color: #8eb8ff;
    text-decoration: underline;
    text-underline-offset: 3px;
    font-weight: 600;
}
.tutorial-text a.tutorial-link:hover {
    color: #b9d2ff;
}
.tutorial-text img.tutorial-inline-emoji {
    width: 1.25em;
    height: 1.25em;
    object-fit: contain;
    vertical-align: -.23em;
}
.tutorial-content-image {
    display: block;
    max-width: 100%;
    height: auto;
    margin: 0 auto;
    border-radius: 14px;
    box-shadow: 0 12px 30px rgba(0,0,0,.28);
}

/* Parties Image : galerie côte à côte */
.tutorial-image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(230px, 100%), 1fr));
    gap: 12px;
    align-items: stretch;
}
.tutorial-image-open {
    display: block;
    width: 100%;
    padding: 0;
    border: 0;
    border-radius: 14px;
    overflow: hidden;
    background: rgba(255,255,255,.035);
    cursor: zoom-in !important;
}
.tutorial-image-grid .tutorial-content-image {
    width: 100%;
    height: 100%;
    min-height: 180px;
    max-height: 430px;
    object-fit: contain;
    box-shadow: none;
}

/* Parties Image : carrousel */
.tutorial-carousel {
    position: relative;
    width: 100%;
    min-height: 220px;
    border-radius: 16px;
    overflow: hidden;
    background: rgba(0,0,0,.18);
    border: 1px solid rgba(255,255,255,.08);
    touch-action: pan-y;
}
.tutorial-carousel-stage {
    position: relative;
    width: 100%;
    min-height: 220px;
}
.tutorial-carousel-slide {
    display: none;
    width: 100%;
    padding: 10px 58px 36px;
}
.tutorial-carousel-slide.active { display: block; }
.tutorial-carousel-slide .tutorial-image-open { background: transparent; }
.tutorial-carousel-slide .tutorial-content-image {
    width: 100%;
    max-height: 650px;
    object-fit: contain;
    box-shadow: none;
}
.tutorial-carousel-arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 3;
    width: 42px;
    height: 54px;
    display: grid;
    place-items: center;
    padding: 0;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,.14);
    background: rgba(13,15,21,.78);
    color: white;
    font-size: 29px;
    line-height: 1;
    backdrop-filter: blur(5px);
}
.tutorial-carousel-arrow:hover { background: rgba(38,41,52,.94); }
.tutorial-carousel-prev { left: 10px; }
.tutorial-carousel-next { right: 10px; }
.tutorial-carousel-position {
    position: absolute;
    left: 50%;
    bottom: 9px;
    transform: translateX(-50%);
    z-index: 3;
    padding: 4px 9px;
    border-radius: 999px;
    background: rgba(8,10,14,.75);
    color: #dfe3eb;
    font-size: 12px;
    pointer-events: none;
}

/* Agrandissement d'une image sans changer de page */
.tutorial-lightbox {
    position: fixed;
    inset: 0;
    z-index: 100300;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background: rgba(2,4,8,.88);
    backdrop-filter: blur(7px);
}
.tutorial-lightbox[hidden] { display: none; }
.tutorial-lightbox-image {
    display: block;
    max-width: min(96vw, 1500px);
    max-height: 91vh;
    width: auto;
    height: auto;
    object-fit: contain;
    border-radius: 12px;
    box-shadow: 0 24px 80px rgba(0,0,0,.58);
}
.tutorial-lightbox-close {
    position: absolute;
    top: 18px;
    right: 18px;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,.18);
    background: rgba(20,22,29,.86);
    color: white;
    font-size: 26px;
    line-height: 1;
}
.tutorial-video-wrap {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: 14px;
    overflow: hidden;
    background: #000;
}
.tutorial-video-wrap iframe {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    border: 0;
}

.tutorial-settings-wrap {
    position: relative;
    width: 100%;
    max-width: 900px;
    margin: 34px auto 0;
    min-height: 42px;
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
}
.tutorial-settings-button {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.035);
    color: #9098a5;
    font-size: 17px;
    display: grid;
    place-items: center;
    padding: 0;
    opacity: .70;
    transition: .18s ease;
}
.tutorial-settings-button:hover {
    opacity: 1;
    color: #ffd493;
    border-color: rgba(255,212,147,.28);
    background: rgba(255,212,147,.06);
}
.tutorial-settings-popover {
    position: absolute;
    right: 0;
    bottom: 42px;
    min-width: 170px;
    padding: 8px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(24,26,33,.98);
    box-shadow: 0 15px 35px rgba(0,0,0,.45);
    z-index: 30;
}
.tutorial-settings-popover[hidden] { display: none; }
.tutorial-settings-popover button {
    width: 100%;
    padding: 10px 12px;
    border-radius: 9px;
    border: 0;
    background: rgba(255,255,255,.06);
    color: white;
    font-weight: 700;
}
.tutorial-settings-popover button:hover { background: rgba(255,255,255,.11); }

.tutorial-admin-toolbar {
    width: 100%;
    max-width: 900px;
    margin: 0 auto 22px;
    padding: 14px;
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    justify-content: center;
    border-radius: 16px;
    border: 1px solid rgba(255,196,108,.20);
    background: rgba(255,196,108,.055);
}
.tutorial-admin-toolbar[hidden] { display: none; }
.tutorial-admin-toolbar button {
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.065);
    color: white;
    border-radius: 10px;
    padding: 10px 13px;
    font-weight: 700;
}
.tutorial-admin-toolbar button:hover {
    border-color: rgba(255,212,147,.38);
    background: rgba(255,212,147,.09);
}
.tutorial-admin-toolbar .tutorial-save-button {
    background: linear-gradient(135deg,#c47a2b,#f0b45c);
    color: #1b130d;
    border-color: transparent;
}
.tutorial-admin-status {
    flex: 1 1 100%;
    min-height: 18px;
    color: #c8ced8;
    font-size: 13px;
    text-align: center;
}
.tutorial-admin-status.error { color: #ff9c9c; }
.tutorial-admin-status.success { color: #8fe0a6; }

.tutorial-title-input {
    width: 100%;
    padding: 12px 13px;
    margin: 2px 0 12px;
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 10px;
    background: rgba(0,0,0,.19);
    color: white;
    font-size: 17px;
    font-weight: 700;
    outline: none;
}
.tutorial-title-input:focus { border-color: rgba(255,196,108,.55); }

.tutorial-add-blocks {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 4px 0 18px;
}
.tutorial-add-blocks button {
    padding: 9px 12px;
    border-radius: 9px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.06);
    color: white;
    font-weight: 700;
}

.tutorial-admin-block {
    position: relative;
    padding: 13px;
    margin-top: 13px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 13px;
    background: rgba(255,255,255,.035);
}
.tutorial-block-controls {
    position: absolute;
    top: 7px;
    right: 7px;
    display: flex;
    align-items: center;
    gap: 5px;
    z-index: 4;
}
.tutorial-block-move,
.tutorial-block-remove {
    width: 28px;
    height: 28px;
    padding: 0;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(0,0,0,.28);
    color: #d9dde5;
    font-size: 15px;
    line-height: 1;
}
.tutorial-block-move:hover:not(:disabled) {
    color: #ffffff;
    border-color: rgba(255,196,108,.42);
    background: rgba(255,196,108,.10);
}
.tutorial-block-move:disabled {
    opacity: .30;
    cursor: default !important;
}
.tutorial-block-remove:hover { color: #ffaaaa; border-color: rgba(255,120,120,.35); }

.tutorial-editor-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding-right: 105px;
    margin-bottom: 9px;
}
.tutorial-editor-toolbar button,
.tutorial-editor-toolbar select {
    min-height: 32px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(0,0,0,.24);
    color: white;
    padding: 5px 9px;
}
.tutorial-editor {
    min-height: 105px;
    padding: 12px;
    border-radius: 9px;
    border: 1px solid rgba(255,255,255,.11);
    background: rgba(0,0,0,.17);
    color: #eef0f4;
    line-height: 1.65;
    outline: none;
}
.tutorial-editor:focus { border-color: rgba(255,196,108,.42); }
.tutorial-editor img.tutorial-inline-emoji {
    width: 1.25em;
    height: 1.25em;
    object-fit: contain;
    vertical-align: -.23em;
}

.tutorial-emoji-picker {
    margin-top: 8px;
    padding: 10px;
    border-radius: 11px;
    border: 1px solid rgba(255,255,255,.11);
    background: rgba(15,17,23,.98);
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
}
.tutorial-emoji-picker[hidden] { display: none; }
.tutorial-emoji-button {
    min-width: 34px;
    height: 34px;
    padding: 4px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,.09);
    background: rgba(255,255,255,.05);
    font-size: 20px;
    display: grid;
    place-items: center;
}
.tutorial-emoji-button img {
    width: 24px;
    height: 24px;
    object-fit: contain;
}
.tutorial-emoji-import {
    width: auto;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 700;
    color: #ffd493;
}

.tutorial-admin-image-preview {
    display: block;
    width: 100%;
    height: 150px;
    object-fit: contain;
    margin: 0;
    border-radius: 9px;
    background: rgba(0,0,0,.12);
}
.tutorial-image-admin-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 9px;
    padding-right: 105px;
    margin-bottom: 12px;
}
.tutorial-image-admin-head strong { margin-right: auto; }
.tutorial-image-layout-select,
.tutorial-image-add-more {
    min-height: 34px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,.13);
    background: rgba(0,0,0,.24);
    color: white;
    padding: 6px 9px;
}
.tutorial-image-add-more { font-weight: 700; }
.tutorial-admin-image-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 10px;
}
.tutorial-admin-image-item {
    position: relative;
    min-width: 0;
    padding: 7px;
    border-radius: 11px;
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(0,0,0,.14);
}
.tutorial-admin-image-remove {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 28px;
    height: 28px;
    padding: 0;
    border-radius: 8px;
    border: 1px solid rgba(255,150,150,.25);
    background: rgba(15,15,19,.84);
    color: #ffb0b0;
    z-index: 2;
    font-size: 18px;
    line-height: 1;
}
.tutorial-admin-image-name {
    display: block;
    margin-top: 6px;
    color: #aeb5c1;
    font-size: 11px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.tutorial-admin-image-empty {
    padding: 18px;
    border: 1px dashed rgba(255,255,255,.13);
    border-radius: 10px;
    color: #aeb5c1;
    text-align: center;
}
.tutorial-admin-video-preview {
    color: #cbd1da;
    padding: 8px 34px 3px 0;
    overflow-wrap: anywhere;
}

.tutorial-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(3,5,9,.72);
    backdrop-filter: blur(5px);
    z-index: 100100;
    display: grid;
    place-items: center;
    padding: 18px;
}
.tutorial-modal-overlay[hidden] { display: none; }
.tutorial-modal {
    position: relative;
    width: min(100%, 480px);
    border-radius: 18px;
    border: 1px solid rgba(255,210,130,.24);
    background: linear-gradient(145deg, rgba(26,29,38,.99), rgba(34,23,21,.99));
    box-shadow: 0 30px 80px rgba(0,0,0,.64);
    padding: 25px;
    text-align: left;
}
.tutorial-modal h3 { margin: 0 40px 18px 0; font-size: 22px; }
.tutorial-modal-close {
    position: absolute;
    top: 11px;
    right: 11px;
    width: 32px;
    height: 32px;
    border-radius: 9px;
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.04);
    color: white;
    font-size: 19px;
}
.tutorial-modal label { display:block; margin-bottom:7px; color:#dfe2e8; }
.tutorial-modal input[type="password"],
.tutorial-modal input[type="text"],
.tutorial-modal input[type="url"],
.tutorial-modal select {
    width: 100%;
    padding: 11px 12px;
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 9px;
    background: rgba(0,0,0,.23);
    color: white;
    outline: none;
}
.tutorial-modal select option {
    background: #20232b;
    color: white;
}
.tutorial-order-list {
    display: grid;
    gap: 8px;
    max-height: min(52vh, 440px);
    overflow: auto;
    padding-right: 3px;
}
.tutorial-order-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 10px;
    align-items: center;
    padding: 10px 11px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.035);
}
.tutorial-order-name {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #eef0f4;
    font-weight: 700;
}
.tutorial-order-buttons {
    display: flex;
    gap: 6px;
}
.tutorial-order-buttons button {
    width: 34px;
    height: 34px;
    padding: 0;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.06);
    color: white;
    font-size: 18px;
    font-weight: 800;
}
.tutorial-order-buttons button:hover:not(:disabled) {
    border-color: rgba(255,212,147,.38);
    background: rgba(255,212,147,.09);
}
.tutorial-order-buttons button:disabled {
    opacity: .28;
    cursor: default !important;
}
.tutorial-order-help {
    margin: -5px 0 14px;
    color: #aeb4bf;
    font-size: 13px;
    line-height: 1.5;
}
.tutorial-modal-actions {
    display: flex;
    gap: 9px;
    justify-content: flex-end;
    margin-top: 18px;
}
.tutorial-modal-actions button {
    padding: 10px 14px;
    border-radius: 9px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.06);
    color: white;
    font-weight: 700;
}
.tutorial-modal-actions .primary {
    background: linear-gradient(135deg,#c47a2b,#f0b45c);
    color: #1b130d;
    border-color: transparent;
}
.tutorial-modal-message {
    color: #cbd0d9;
    line-height: 1.55;
}
.tutorial-modal-error {
    min-height: 18px;
    margin-top: 9px;
    color: #ff9e9e;
    font-size: 13px;
}


/* =========================================================
   PAGE 404
   ========================================================= */
.error-page {
    max-width: 760px;
    margin: 4px auto 10px;
    padding: 16px 8px 12px;
    text-align: center;
}
.error-king {
    display: block;
    width: min(230px, 56vw);
    height: auto;
    margin: 0 auto 8px;
    filter: drop-shadow(0 15px 28px rgba(0,0,0,.38));
}
.error-code {
    margin: 0;
    font-size: clamp(76px, 16vw, 145px);
    line-height: .9;
    font-weight: 900;
    letter-spacing: -5px;
    color: #ffd493;
    text-shadow: 0 8px 30px rgba(0,0,0,.4);
}
.error-page h1 { margin-top: 15px; }
.error-actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
}
.error-actions a { min-width: 180px; }

@media (max-width:760px) {
    .tutorial-menu-header { font-size: 16px; }
    .tutorial-admin-toolbar button { flex: 1 1 calc(50% - 9px); }
    .tutorial-modal { padding: 21px 18px; }
}

@media (max-width:760px) {
    body { padding:18px 10px; background-attachment:scroll; }
    .tutorial-carousel-slide { padding: 8px 44px 34px; }
    .tutorial-carousel-arrow { width: 34px; height: 48px; font-size: 24px; }
    .tutorial-image-admin-head { padding-right: 0; padding-top: 34px; }
    .card { border-radius:20px; }
    .site-head { padding:25px 16px 12px; }
    .logo { width:145px; }
    .logo-trigger { flex-basis:145px; width:145px; }
    .nav { gap:7px; }
    .nav a { flex:1 1 calc(50% - 8px); padding:10px 8px; }
    .content { padding:15px 18px 28px; }
    .stats, .grid, .grid.two { grid-template-columns:1fr; gap:15px; }
    .tile { min-height:155px; }
    .footer {
        margin:0 18px;
        display:flex;
        flex-direction:column;
        align-items:center;
        gap:13px;
    }
    .footer-copy { order:1; text-align:center; }
    .page-view-counter { order:2; align-self:flex-start; }
    .footer-spacer { display:none; }
}
"""

SCRIPT = r"""
<script>
(function () {
    const trigger = document.getElementById("logoKingTrigger");

    if (!trigger) return;

    trigger.addEventListener("click", function () {
        if (document.querySelector(".falling-king")) return;

        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

        const king = document.createElement("img");
        king.src = "roi_chute.png";
        king.alt = "";
        king.className = "falling-king";
        king.setAttribute("aria-hidden", "true");
        document.body.appendChild(king);

        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const size = Math.min(230, Math.max(125, vw * 0.15));

        const animation = king.animate(
            [
                {
                    transform: `translate(${-size * 0.85}px, ${-size * 1.15}px) rotate(-28deg)`,
                    opacity: 0,
                    offset: 0
                },
                {
                    transform: `translate(${vw * 0.02}px, ${vh * 0.02}px) rotate(18deg)`,
                    opacity: 1,
                    offset: 0.08
                },
                {
                    transform: `translate(${vw * 0.16}px, ${vh * 0.17}px) rotate(-22deg)`,
                    opacity: 1,
                    offset: 0.20
                },
                {
                    transform: `translate(${vw * 0.25}px, ${vh * 0.31}px) rotate(25deg)`,
                    opacity: 1,
                    offset: 0.34
                },
                {
                    transform: `translate(${vw * 0.43}px, ${vh * 0.43}px) rotate(-20deg)`,
                    opacity: 1,
                    offset: 0.48
                },
                {
                    transform: `translate(${vw * 0.53}px, ${vh * 0.58}px) rotate(21deg)`,
                    opacity: 1,
                    offset: 0.62
                },
                {
                    transform: `translate(${vw * 0.71}px, ${vh * 0.70}px) rotate(-17deg)`,
                    opacity: 1,
                    offset: 0.76
                },
                {
                    transform: `translate(${vw * 0.82}px, ${vh * 0.87}px) rotate(19deg)`,
                    opacity: 1,
                    offset: 0.89
                },
                {
                    transform: `translate(${vw + size * 0.85}px, ${vh + size * 0.65}px) rotate(-12deg)`,
                    opacity: 0,
                    offset: 1
                }
            ],
            {
                duration: 5200,
                easing: "ease-in-out",
                fill: "forwards"
            }
        );

        animation.onfinish = function () {
            king.remove();
        };

        animation.oncancel = function () {
            king.remove();
        };
    });
})();

(function () {
    const counter = document.querySelector(".page-view-counter");
    if (!counter) return;

    const number = counter.querySelector(".page-view-number");
    const site = counter.dataset.viewSite;
    const path = counter.dataset.viewPath;

    if (!site || !path || !number) return;

    const base = "https://page-views-api.ratneshc.com/api/v1";
    const query = `site=${encodeURIComponent(site)}&path=${encodeURIComponent(path)}`;

    async function updateViewCounter() {
        try {
            /*
               Le service déduplique automatiquement un même visiteur pendant
               30 minutes pour une même page. On compte donc de vraies visites
               plutôt que chaque simple rafraîchissement du navigateur.
            */
            await fetch(`${base}/track?${query}`, {
                method: "GET",
                cache: "no-store",
                keepalive: true
            });

            const response = await fetch(`${base}/views?${query}`, {
                method: "GET",
                cache: "no-store"
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            const views = Number(data.views);

            if (!Number.isFinite(views)) throw new Error("Compteur invalide");

            number.textContent = new Intl.NumberFormat("fr-FR").format(views);
            counter.title = `${number.textContent} vue${views > 1 ? "s" : ""} de cette page`;
        } catch (error) {
            console.warn("Compteur de vues indisponible :", error);
            number.textContent = "—";
            counter.title = "Compteur de vues temporairement indisponible";
        }
    }

    updateViewCounter();
})();
</script>
"""


TUTORIALS_SCRIPT = r'''<script src="admin-config.js"></script>
<script>
(function () {
    const DATA_URL = "tutoriels-data.json";
    const REPO_OWNER = "Legodingo13";
    const REPO_NAME = "site-internet-legodingo13";
    const REPO_BRANCH = "main";
    const DATA_PATH = "tutoriels-data.json";
    const API_URL = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${DATA_PATH}`;

    const builtinEmojis = ["😀","😄","😂","❤️","👍","🎉","🔥","👑","🏰","⚔️","💬","📢","✅","❗","❓","🎯","🛠️","📷","🎬","🌟"];

    let tutorialData = { version: 1, menus: [], customEmojis: [] };
    let savedDataSnapshot = "";
    let adminMode = false;
    let adminToken = null;
    let openMenuId = null;
    let activeEditor = null;

    const accordion = document.getElementById("tutorialAccordion");
    const adminToolbar = document.getElementById("tutorialAdminToolbar");
    const adminStatus = document.getElementById("tutorialAdminStatus");
    const copyToast = document.getElementById("tutorialCopyToast");
    const settingsButton = document.getElementById("tutorialSettingsButton");
    const settingsPopover = document.getElementById("tutorialSettingsPopover");
    const editPageButton = document.getElementById("tutorialEditPageButton");

    const passwordModal = document.getElementById("tutorialPasswordModal");
    const passwordInput = document.getElementById("tutorialPasswordInput");
    const passwordError = document.getElementById("tutorialPasswordError");
    const passwordValidate = document.getElementById("tutorialPasswordValidate");

    const confirmModal = document.getElementById("tutorialConfirmModal");
    const confirmTitle = document.getElementById("tutorialConfirmTitle");
    const confirmText = document.getElementById("tutorialConfirmText");
    const confirmAccept = document.getElementById("tutorialConfirmAccept");
    const confirmCancel = document.getElementById("tutorialConfirmCancel");
    let confirmCallback = null;

    const videoModal = document.getElementById("tutorialVideoModal");
    const videoUrlInput = document.getElementById("tutorialVideoUrlInput");
    const videoError = document.getElementById("tutorialVideoError");
    const videoAddButton = document.getElementById("tutorialVideoAdd");
    let videoTargetMenuId = null;

    const deleteMenuModal = document.getElementById("tutorialDeleteMenuModal");
    const deleteMenuSelect = document.getElementById("tutorialDeleteMenuSelect");
    const deleteMenuContinue = document.getElementById("tutorialDeleteMenuContinue");

    const orderMenuModal = document.getElementById("tutorialOrderMenuModal");
    const orderMenuList = document.getElementById("tutorialOrderMenuList");

    function uid(prefix) {
        return prefix + "_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 8);
    }

    function deepClone(value) {
        return JSON.parse(JSON.stringify(value));
    }

    function setStatus(message, kind) {
        if (!adminStatus) return;
        adminStatus.textContent = message || "";
        adminStatus.className = "tutorial-admin-status" + (kind ? " " + kind : "");
    }

    function dataChanged() {
        return JSON.stringify(tutorialData) !== savedDataSnapshot;
    }

    function normalizeData(data) {
        if (!data || typeof data !== "object") data = {};
        if (!Array.isArray(data.menus)) data.menus = [];
        if (!Array.isArray(data.customEmojis)) data.customEmojis = [];
        data.version = 1;
        data.menus.forEach(menu => {
            if (!menu.id) menu.id = uid("menu");
            if (typeof menu.title !== "string") menu.title = "";
            if (typeof menu.slug !== "string") menu.slug = "";
            if (typeof menu.updatedAt !== "string") menu.updatedAt = "";
            if (!Array.isArray(menu.blocks)) menu.blocks = [];
            menu.blocks.forEach(block => {
                if (!block.id) block.id = uid("block");
                if (block.type === "image") {
                    if (!Array.isArray(block.images)) {
                        block.images = [];
                        if (String(block.data || "").startsWith("data:image/")) {
                            block.images.push({
                                id: uid("img"),
                                data: block.data,
                                alt: block.alt || "Image du tutoriel"
                            });
                        }
                    }
                    block.images = block.images.filter(image => image && String(image.data || "").startsWith("data:image/")).map(image => ({
                        id: image.id || uid("img"),
                        data: image.data,
                        alt: image.alt || "Image du tutoriel"
                    }));
                    block.layout = block.layout === "carousel" ? "carousel" : "grid";
                    delete block.data;
                    delete block.alt;
                }
            });
        });
        return data;
    }

    async function loadTutorialData() {
        try {
            const response = await fetch(DATA_URL + "?v=" + Date.now(), { cache: "no-store" });
            if (!response.ok) throw new Error("HTTP " + response.status);
            tutorialData = normalizeData(await response.json());
        } catch (error) {
            console.warn("Impossible de charger les tutoriels :", error);
            tutorialData = normalizeData({ version: 1, menus: [], customEmojis: [] });
        }
        savedDataSnapshot = JSON.stringify(tutorialData);
        if (!openTutorialFromHash(false)) render();
        else requestAnimationFrame(() => {
            const hash = decodeURIComponent(String(location.hash || "").replace(/^#/, ""));
            const target = hash ? document.getElementById(hash) : null;
            if (target) target.scrollIntoView({ behavior: "auto", block: "start" });
        });
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function sanitizeRichHtml(htmlValue) {
        const template = document.createElement("template");
        template.innerHTML = String(htmlValue || "");
        const allowed = new Set(["B","STRONG","I","EM","U","SPAN","BR","DIV","P","IMG"]);
        const allowedStyles = new Set(["font-size","font-weight","font-style","text-decoration","text-align"]);

        function clean(node) {
            [...node.childNodes].forEach(child => {
                if (child.nodeType === Node.ELEMENT_NODE) {
                    if (!allowed.has(child.tagName)) {
                        child.replaceWith(document.createTextNode(child.textContent || ""));
                        return;
                    }
                    [...child.attributes].forEach(attr => {
                        const name = attr.name.toLowerCase();
                        if (child.tagName === "IMG") {
                            if (name === "src") {
                                if (!attr.value.startsWith("data:image/")) child.removeAttribute(attr.name);
                            } else if (name === "class") {
                                if (!attr.value.includes("tutorial-inline-emoji")) child.removeAttribute(attr.name);
                            } else if (name !== "alt") {
                                child.removeAttribute(attr.name);
                            }
                        } else if (name === "style") {
                            const safe = [];
                            attr.value.split(";").forEach(rule => {
                                const parts = rule.split(":");
                                if (parts.length < 2) return;
                                const prop = parts.shift().trim().toLowerCase();
                                const val = parts.join(":").trim();
                                if (allowedStyles.has(prop)) safe.push(prop + ":" + val);
                            });
                            if (safe.length) child.setAttribute("style", safe.join(";"));
                            else child.removeAttribute("style");
                        } else {
                            child.removeAttribute(attr.name);
                        }
                    });
                    clean(child);
                }
            });
        }
        clean(template.content);
        return template.innerHTML;
    }

    function normalizeTutorialLink(urlValue) {
        try {
            const parsed = new URL(String(urlValue || "").trim());
            if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return null;
            return parsed.href;
        } catch (error) {
            return null;
        }
    }

    function linkifyTutorialSyntax(htmlValue) {
        const template = document.createElement("template");
        template.innerHTML = sanitizeRichHtml(htmlValue);

        const walker = document.createTreeWalker(template.content, NodeFilter.SHOW_TEXT);
        const textNodes = [];
        while (walker.nextNode()) textNodes.push(walker.currentNode);

        /*
           Syntaxe de lien utilisée dans les tutoriels :
           (Nom du lien)[https://exemple.com/]
        */
        const linkPattern = /\(([^()\[\]\n]{1,200})\)\[(https?:\/\/[^\]\s]+)\]/g;

        textNodes.forEach(node => {
            const value = node.nodeValue || "";
            linkPattern.lastIndex = 0;

            let match;
            let lastIndex = 0;
            let hasLink = false;
            const fragment = document.createDocumentFragment();

            while ((match = linkPattern.exec(value)) !== null) {
                const href = normalizeTutorialLink(match[2]);
                if (!href) continue;

                fragment.appendChild(document.createTextNode(value.slice(lastIndex, match.index)));

                const link = document.createElement("a");
                link.className = "tutorial-link";
                link.href = href;
                link.target = "_blank";
                link.rel = "noopener noreferrer";
                link.textContent = match[1];
                fragment.appendChild(link);

                lastIndex = linkPattern.lastIndex;
                hasLink = true;
            }

            if (!hasLink) return;

            fragment.appendChild(document.createTextNode(value.slice(lastIndex)));
            node.replaceWith(fragment);
        });

        return template.innerHTML;
    }

    function youtubeId(url) {
        const value = String(url || "").trim();
        const patterns = [
            /youtu\.be\/([A-Za-z0-9_-]{6,})/,
            /youtube\.com\/watch\?[^#]*v=([A-Za-z0-9_-]{6,})/,
            /youtube\.com\/shorts\/([A-Za-z0-9_-]{6,})/,
            /youtube\.com\/embed\/([A-Za-z0-9_-]{6,})/
        ];
        for (const pattern of patterns) {
            const match = value.match(pattern);
            if (match) return match[1];
        }
        return null;
    }

    function slugifyTutorialTitle(value) {
        const base = String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "")
            .slice(0, 72);
        return base || "tutoriel";
    }

    function menuAnchor(menu) {
        if (menu && String(menu.slug || "").trim()) return String(menu.slug).trim();
        const suffix = String(menu?.id || "menu").replace(/[^a-zA-Z0-9]/g, "").slice(-6).toLowerCase();
        return slugifyTutorialTitle(menu?.title || "tutoriel") + (suffix ? "-" + suffix : "");
    }

    function ensureUniqueMenuSlugs(menus) {
        const used = new Set();
        (menus || []).forEach(menu => {
            let slug = String(menu.slug || "").trim();
            if (!slug) slug = slugifyTutorialTitle(menu.title);
            let candidate = slug;
            let index = 2;
            while (used.has(candidate)) {
                candidate = slug + "-" + index;
                index += 1;
            }
            menu.slug = candidate;
            used.add(candidate);
        });
    }

    function formatTutorialDate(value) {
        if (!value) return "";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "";
        return new Intl.DateTimeFormat("fr-FR", {
            day: "numeric",
            month: "long",
            year: "numeric"
        }).format(date);
    }

    function comparableMenu(menu) {
        const copy = deepClone(menu || {});
        delete copy.updatedAt;
        return copy;
    }

    function renderPublicBlock(block) {
        if (block.type === "text") {
            return `<div class="tutorial-public-block tutorial-text">${linkifyTutorialSyntax(block.html || "")}</div>`;
        }
        if (block.type === "image") {
            const images = Array.isArray(block.images) ? block.images.filter(image => String(image?.data || "").startsWith("data:image/")) : [];
            if (!images.length) return "";

            if (block.layout === "carousel") {
                const slides = images.map((image, index) => `<div class="tutorial-carousel-slide${index === 0 ? " active" : ""}" data-carousel-index="${index}">
                    <button type="button" class="tutorial-image-open" data-image-src="${escapeHtml(image.data)}" data-image-alt="${escapeHtml(image.alt || "Image du tutoriel")}" aria-label="Agrandir l'image ${index + 1}">
                        <img class="tutorial-content-image" src="${escapeHtml(image.data)}" alt="${escapeHtml(image.alt || "Image du tutoriel")}" loading="lazy" decoding="async">
                    </button>
                </div>`).join("");
                return `<div class="tutorial-public-block tutorial-carousel" data-carousel data-carousel-current="0">
                    <div class="tutorial-carousel-stage">${slides}</div>
                    ${images.length > 1 ? `<button type="button" class="tutorial-carousel-arrow tutorial-carousel-prev" data-carousel-prev aria-label="Image précédente">‹</button><button type="button" class="tutorial-carousel-arrow tutorial-carousel-next" data-carousel-next aria-label="Image suivante">›</button><div class="tutorial-carousel-position"><span data-carousel-position>1</span> / ${images.length}</div>` : ""}
                </div>`;
            }

            const cells = images.map((image, index) => `<button type="button" class="tutorial-image-open" data-image-src="${escapeHtml(image.data)}" data-image-alt="${escapeHtml(image.alt || "Image du tutoriel")}" aria-label="Agrandir l'image ${index + 1}">
                <img class="tutorial-content-image" src="${escapeHtml(image.data)}" alt="${escapeHtml(image.alt || "Image du tutoriel")}" loading="lazy" decoding="async">
            </button>`).join("");
            return `<div class="tutorial-public-block tutorial-image-grid">${cells}</div>`;
        }
        if (block.type === "video") {
            const id = youtubeId(block.url);
            if (!id) return "";
            return `<div class="tutorial-public-block tutorial-video-wrap"><iframe src="https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}" title="Vidéo YouTube" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>`;
        }
        return "";
    }

    function renderPublic() {
        if (!tutorialData.menus.length) {
            accordion.innerHTML = '<div class="tutorial-empty">Les tutoriels seront ajoutés prochainement.</div>';
            return;
        }
        accordion.innerHTML = tutorialData.menus.map(menu => {
            const isOpen = menu.id === openMenuId;
            const blocks = menu.blocks.map(renderPublicBlock).join("");
            const anchor = menuAnchor(menu);
            const updatedLabel = formatTutorialDate(menu.updatedAt);
            const updatedHtml = updatedLabel ? `<div class="tutorial-menu-updated">Dernière mise à jour : ${escapeHtml(updatedLabel)}</div>` : "";
            return `<section id="${escapeHtml(anchor)}" class="tutorial-menu${isOpen ? " open" : ""}" data-menu-id="${escapeHtml(menu.id)}">
                <a class="tutorial-anchor-link" href="#${escapeHtml(anchor)}" title="Copier le lien direct de ce tutoriel" aria-label="Copier le lien direct de ${escapeHtml(menu.title)}">🔗</a>
                <button type="button" class="tutorial-menu-header" data-action="toggle-menu" data-menu-id="${escapeHtml(menu.id)}" aria-expanded="${isOpen ? "true" : "false"}">
                    <span>${escapeHtml(menu.title)}</span><span class="tutorial-menu-arrow">›</span>
                </button>
                <div class="tutorial-menu-panel">${updatedHtml}${blocks}</div>
            </section>`;
        }).join("");
        bindAccordionEvents();
        bindAnchorEvents();
        bindTutorialImageEvents();
    }

    function renderAdminBlock(menu, block, blockIndex) {
        const controls = `<div class="tutorial-block-controls">
            <button type="button" class="tutorial-block-move" data-action="move-block-up" data-menu-id="${menu.id}" data-block-id="${block.id}" title="Monter cet élément" aria-label="Monter cet élément" ${blockIndex === 0 ? "disabled" : ""}>↑</button>
            <button type="button" class="tutorial-block-move" data-action="move-block-down" data-menu-id="${menu.id}" data-block-id="${block.id}" title="Descendre cet élément" aria-label="Descendre cet élément" ${blockIndex === menu.blocks.length - 1 ? "disabled" : ""}>↓</button>
            <button type="button" class="tutorial-block-remove" data-action="remove-block" data-menu-id="${menu.id}" data-block-id="${block.id}" title="Supprimer ce contenu" aria-label="Supprimer cet élément">×</button>
        </div>`;
        if (block.type === "text") {
            return `<div class="tutorial-admin-block" data-block-id="${block.id}">
                ${controls}
                <div class="tutorial-editor-toolbar" data-editor-id="editor_${block.id}">
                    <button type="button" data-command="bold"><strong>G</strong></button>
                    <button type="button" data-command="italic"><em>I</em></button>
                    <button type="button" data-command="underline"><u>S</u></button>
                    <select data-command="fontSize" title="Taille de la police">
                        <option value="3">16 px</option><option value="2">13 px</option><option value="4">18 px</option><option value="5">24 px</option><option value="6">32 px</option><option value="7">40 px</option>
                    </select>
                    <button type="button" data-command="justifyLeft">↤</button>
                    <button type="button" data-command="justifyCenter">↔</button>
                    <button type="button" data-command="justifyRight">↦</button>
                    <button type="button" data-action="toggle-emoji" data-editor-id="editor_${block.id}">Emoji</button>
                </div>
                <div id="editor_${block.id}" class="tutorial-editor" contenteditable="true" data-menu-id="${menu.id}" data-block-id="${block.id}">${sanitizeRichHtml(block.html || "")}</div>
                <div class="tutorial-emoji-picker" data-emoji-picker-for="editor_${block.id}" hidden></div>
            </div>`;
        }
        if (block.type === "image") {
            const images = Array.isArray(block.images) ? block.images : [];
            const previews = images.length ? images.map((image, imageIndex) => `<div class="tutorial-admin-image-item">
                <button type="button" class="tutorial-admin-image-remove" data-action="remove-image-from-block" data-menu-id="${menu.id}" data-block-id="${block.id}" data-image-id="${image.id}" title="Retirer cette image" aria-label="Retirer cette image">×</button>
                <img class="tutorial-admin-image-preview" src="${escapeHtml(image.data || "")}" alt="Aperçu de l'image ${imageIndex + 1}">
                <span class="tutorial-admin-image-name">${escapeHtml(image.alt || `Image ${imageIndex + 1}`)}</span>
            </div>`).join("") : '<div class="tutorial-admin-image-empty">Aucune image dans cette partie.</div>';
            return `<div class="tutorial-admin-block" data-block-id="${block.id}">
                ${controls}
                <div class="tutorial-image-admin-head">
                    <strong>Partie image</strong>
                    <select class="tutorial-image-layout-select" data-action="image-layout" data-menu-id="${menu.id}" data-block-id="${block.id}" title="Mode d'affichage">
                        <option value="grid" ${block.layout !== "carousel" ? "selected" : ""}>Photos côte à côte</option>
                        <option value="carousel" ${block.layout === "carousel" ? "selected" : ""}>Déroulant d'images</option>
                    </select>
                    <button type="button" class="tutorial-image-add-more" data-action="add-images-to-block" data-menu-id="${menu.id}" data-block-id="${block.id}">+ Ajouter des images</button>
                    <input type="file" accept="image/*" multiple data-image-block-input="${block.id}" data-menu-id="${menu.id}" hidden>
                </div>
                <div class="tutorial-admin-image-list">${previews}</div>
            </div>`;
        }
        if (block.type === "video") {
            return `<div class="tutorial-admin-block" data-block-id="${block.id}">${controls}<div class="tutorial-admin-video-preview">Vidéo YouTube : ${escapeHtml(block.url || "")}</div></div>`;
        }
        return "";
    }

    function renderAdmin() {
        if (!tutorialData.menus.length) {
            accordion.innerHTML = '<div class="tutorial-empty">Aucun menu déroulant. Utilise « Créer un menu déroulant » pour commencer.</div>';
            return;
        }
        accordion.innerHTML = tutorialData.menus.map(menu => {
            const isOpen = menu.id === openMenuId;
            const blocks = menu.blocks.map((block, blockIndex) => renderAdminBlock(menu, block, blockIndex)).join("");
            return `<section class="tutorial-menu${isOpen ? " open" : ""}" data-menu-id="${menu.id}">
                <button type="button" class="tutorial-menu-header" data-action="toggle-menu" data-menu-id="${menu.id}" aria-expanded="${isOpen ? "true" : "false"}">
                    <span>${escapeHtml(menu.title || "Menu sans titre")}</span><span class="tutorial-menu-arrow">›</span>
                </button>
                <div class="tutorial-menu-panel">
                    ${formatTutorialDate(menu.updatedAt) ? `<div class="tutorial-menu-updated">Dernière mise à jour : ${escapeHtml(formatTutorialDate(menu.updatedAt))}</div>` : ""}
                    <input class="tutorial-title-input" type="text" maxlength="140" placeholder="Titre du menu déroulant" value="${escapeHtml(menu.title)}" data-action="menu-title" data-menu-id="${menu.id}">
                    <div class="tutorial-add-blocks">
                        <button type="button" data-action="add-text" data-menu-id="${menu.id}">Texte</button>
                        <button type="button" data-action="add-image" data-menu-id="${menu.id}">Image</button>
                        <button type="button" data-action="add-video" data-menu-id="${menu.id}">Vidéo</button>
                    </div>
                    <input type="file" accept="image/*" multiple data-image-input-for="${menu.id}" hidden>
                    ${blocks}
                </div>
            </section>`;
        }).join("");
        bindAccordionEvents();
        bindAdminEvents();
    }

    function render() {
        if (adminMode) renderAdmin();
        else renderPublic();
    }

    function bindAccordionEvents() {
        accordion.querySelectorAll('[data-action="toggle-menu"]').forEach(button => {
            button.addEventListener("click", () => {
                const id = button.dataset.menuId;
                openMenuId = openMenuId === id ? null : id;
                render();
            });
        });
    }

    let copyToastTimer = null;

    function showCopyToast(message) {
        if (!copyToast) return;
        if (copyToastTimer) window.clearTimeout(copyToastTimer);
        copyToast.textContent = message;
        copyToast.hidden = false;
        copyToastTimer = window.setTimeout(() => {
            copyToast.hidden = true;
        }, 2200);
    }

    async function copyTextToClipboard(value) {
        const text = String(value || "");
        if (!text) return false;

        if (navigator.clipboard && window.isSecureContext) {
            try {
                await navigator.clipboard.writeText(text);
                return true;
            } catch (error) {
                // On tente ensuite la méthode de secours.
            }
        }

        const helper = document.createElement("textarea");
        helper.value = text;
        helper.setAttribute("readonly", "");
        helper.style.position = "fixed";
        helper.style.opacity = "0";
        helper.style.pointerEvents = "none";
        document.body.appendChild(helper);
        helper.select();
        helper.setSelectionRange(0, helper.value.length);
        let copied = false;
        try {
            copied = document.execCommand("copy");
        } catch (error) {
            copied = false;
        }
        helper.remove();
        return copied;
    }

    function bindAnchorEvents() {
        accordion.querySelectorAll(".tutorial-anchor-link").forEach(link => {
            link.addEventListener("click", async event => {
                event.preventDefault();
                const section = link.closest(".tutorial-menu");
                if (!section) return;
                const anchor = section.id;
                const directUrl = new URL(window.location.href);
                directUrl.hash = anchor;

                const copied = await copyTextToClipboard(directUrl.href);
                showCopyToast(copied ? "Lien du tutoriel copié dans le presse-papiers." : "Impossible de copier automatiquement le lien.");

                openMenuId = section.dataset.menuId || null;
                history.pushState(null, "", "#" + encodeURIComponent(anchor));
                renderPublic();
                requestAnimationFrame(() => {
                    const target = document.getElementById(anchor);
                    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
                });
            });
        });
    }

    function ensureTutorialLightbox() {
        let lightbox = document.getElementById("tutorialImageLightbox");
        if (lightbox) return lightbox;
        lightbox = document.createElement("div");
        lightbox.id = "tutorialImageLightbox";
        lightbox.className = "tutorial-lightbox";
        lightbox.hidden = true;
        lightbox.innerHTML = `<button type="button" class="tutorial-lightbox-close" aria-label="Fermer l'image agrandie">×</button><img class="tutorial-lightbox-image" alt="Image agrandie">`;
        document.body.appendChild(lightbox);
        const close = () => {
            lightbox.hidden = true;
            const image = lightbox.querySelector(".tutorial-lightbox-image");
            if (image) image.removeAttribute("src");
        };
        lightbox.querySelector(".tutorial-lightbox-close").addEventListener("click", close);
        lightbox.addEventListener("click", event => {
            if (event.target === lightbox) close();
        });
        document.addEventListener("keydown", event => {
            if (event.key === "Escape" && !lightbox.hidden) close();
        });
        return lightbox;
    }

    function openTutorialLightbox(src, alt) {
        const lightbox = ensureTutorialLightbox();
        const image = lightbox.querySelector(".tutorial-lightbox-image");
        image.src = src;
        image.alt = alt || "Image du tutoriel agrandie";
        lightbox.hidden = false;
    }

    function updateCarousel(carousel, nextIndex) {
        const slides = [...carousel.querySelectorAll(".tutorial-carousel-slide")];
        if (!slides.length) return;
        let index = Number(nextIndex);
        if (!Number.isFinite(index)) index = 0;
        index = (index % slides.length + slides.length) % slides.length;
        slides.forEach((slide, slideIndex) => slide.classList.toggle("active", slideIndex === index));
        carousel.dataset.carouselCurrent = String(index);
        const position = carousel.querySelector("[data-carousel-position]");
        if (position) position.textContent = String(index + 1);
    }

    function bindTutorialImageEvents() {
        accordion.querySelectorAll(".tutorial-image-open").forEach(button => {
            button.addEventListener("click", event => {
                const carousel = button.closest("[data-carousel]");
                if (carousel && carousel.dataset.carouselSwiped === "1") {
                    carousel.dataset.carouselSwiped = "0";
                    event.preventDefault();
                    return;
                }
                openTutorialLightbox(button.dataset.imageSrc || "", button.dataset.imageAlt || "Image du tutoriel");
            });
        });

        accordion.querySelectorAll("[data-carousel]").forEach(carousel => {
            const previous = carousel.querySelector("[data-carousel-prev]");
            const next = carousel.querySelector("[data-carousel-next]");
            const move = direction => {
                const current = Number(carousel.dataset.carouselCurrent || 0);
                updateCarousel(carousel, current + direction);
            };
            if (previous) previous.addEventListener("click", () => move(-1));
            if (next) next.addEventListener("click", () => move(1));

            let startX = null;
            carousel.addEventListener("pointerdown", event => {
                if (event.pointerType === "mouse" && event.button !== 0) return;
                carousel.dataset.carouselSwiped = "0";
                startX = event.clientX;
            });
            carousel.addEventListener("pointerup", event => {
                if (startX === null) return;
                const delta = event.clientX - startX;
                startX = null;
                if (Math.abs(delta) < 45) return;
                carousel.dataset.carouselSwiped = "1";
                move(delta < 0 ? 1 : -1);
            });
            carousel.addEventListener("pointercancel", () => { startX = null; });
        });
    }

    function openTutorialFromHash(scroll = true) {
        const hash = decodeURIComponent(String(location.hash || "").replace(/^#/, ""));
        if (!hash) return false;
        const menu = tutorialData.menus.find(item => menuAnchor(item) === hash);
        if (!menu) return false;
        openMenuId = menu.id;
        render();
        if (scroll) {
            requestAnimationFrame(() => {
                const target = document.getElementById(hash);
                if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
            });
        }
        return true;
    }

    function findMenu(menuId) {
        return tutorialData.menus.find(menu => menu.id === menuId);
    }

    function findBlock(menu, blockId) {
        return menu ? menu.blocks.find(block => block.id === blockId) : null;
    }

    function markDirty() {
        setStatus(dataChanged() ? "Modifications non enregistrées." : "", "");
    }

    function bindAdminEvents() {
        accordion.querySelectorAll('[data-action="menu-title"]').forEach(input => {
            input.addEventListener("input", () => {
                const menu = findMenu(input.dataset.menuId);
                if (menu) menu.title = input.value;
                const header = input.closest(".tutorial-menu").querySelector(".tutorial-menu-header span:first-child");
                if (header) header.textContent = input.value || "Menu sans titre";
                markDirty();
            });
        });

        accordion.querySelectorAll('[data-action="add-text"]').forEach(button => {
            button.addEventListener("click", () => {
                const menu = findMenu(button.dataset.menuId);
                if (!menu) return;
                menu.blocks.push({ id: uid("text"), type: "text", html: "" });
                openMenuId = menu.id;
                renderAdmin();
                markDirty();
            });
        });

        accordion.querySelectorAll('[data-action="add-image"]').forEach(button => {
            button.addEventListener("click", () => {
                const input = accordion.querySelector(`[data-image-input-for="${CSS.escape(button.dataset.menuId)}"]`);
                if (input) input.click();
            });
        });

        accordion.querySelectorAll('[data-image-input-for]').forEach(input => {
            input.addEventListener("change", async () => {
                const files = [...(input.files || [])];
                if (!files.length) return;
                try {
                    const menu = findMenu(input.dataset.imageInputFor);
                    if (!menu) return;
                    setStatus(`Préparation de ${files.length} image${files.length > 1 ? "s" : ""}…`, "");
                    const images = [];
                    for (const file of files) {
                        const data = await compressImage(file, 1600, 1600, .84, 650 * 1024);
                        images.push({ id: uid("img"), data, alt: file.name || "Image du tutoriel" });
                    }
                    menu.blocks.push({ id: uid("image"), type: "image", layout: "grid", images });
                    openMenuId = menu.id;
                    renderAdmin();
                    markDirty();
                } catch (error) {
                    console.error(error);
                    setStatus("Impossible d'importer une ou plusieurs images.", "error");
                }
                input.value = "";
            });
        });

        accordion.querySelectorAll('[data-action="add-images-to-block"]').forEach(button => {
            button.addEventListener("click", () => {
                const selector = `[data-image-block-input="${CSS.escape(button.dataset.blockId)}"]`;
                const input = accordion.querySelector(selector);
                if (input) input.click();
            });
        });

        accordion.querySelectorAll('[data-image-block-input]').forEach(input => {
            input.addEventListener("change", async () => {
                const files = [...(input.files || [])];
                if (!files.length) return;
                const menu = findMenu(input.dataset.menuId);
                const block = findBlock(menu, input.dataset.imageBlockInput);
                if (!menu || !block || block.type !== "image") return;
                try {
                    setStatus(`Ajout de ${files.length} image${files.length > 1 ? "s" : ""}…`, "");
                    if (!Array.isArray(block.images)) block.images = [];
                    for (const file of files) {
                        const data = await compressImage(file, 1600, 1600, .84, 650 * 1024);
                        block.images.push({ id: uid("img"), data, alt: file.name || "Image du tutoriel" });
                    }
                    openMenuId = menu.id;
                    renderAdmin();
                    markDirty();
                } catch (error) {
                    console.error(error);
                    setStatus("Impossible d'ajouter une ou plusieurs images.", "error");
                }
                input.value = "";
            });
        });

        accordion.querySelectorAll('[data-action="remove-image-from-block"]').forEach(button => {
            button.addEventListener("click", () => {
                const menu = findMenu(button.dataset.menuId);
                const block = findBlock(menu, button.dataset.blockId);
                if (!menu || !block || !Array.isArray(block.images)) return;
                block.images = block.images.filter(image => image.id !== button.dataset.imageId);
                openMenuId = menu.id;
                renderAdmin();
                markDirty();
            });
        });

        accordion.querySelectorAll('[data-action="image-layout"]').forEach(select => {
            select.addEventListener("change", () => {
                const menu = findMenu(select.dataset.menuId);
                const block = findBlock(menu, select.dataset.blockId);
                if (!block || block.type !== "image") return;
                block.layout = select.value === "carousel" ? "carousel" : "grid";
                markDirty();
            });
        });

        accordion.querySelectorAll('[data-action="add-video"]').forEach(button => {
            button.addEventListener("click", () => openVideoModal(button.dataset.menuId));
        });

        accordion.querySelectorAll('[data-action="move-block-up"], [data-action="move-block-down"]').forEach(button => {
            button.addEventListener("click", () => {
                const menu = findMenu(button.dataset.menuId);
                if (!menu) return;

                const currentIndex = menu.blocks.findIndex(block => block.id === button.dataset.blockId);
                if (currentIndex < 0) return;

                const direction = button.dataset.action === "move-block-up" ? -1 : 1;
                const targetIndex = currentIndex + direction;
                if (targetIndex < 0 || targetIndex >= menu.blocks.length) return;

                [menu.blocks[currentIndex], menu.blocks[targetIndex]] = [menu.blocks[targetIndex], menu.blocks[currentIndex]];
                openMenuId = menu.id;
                renderAdmin();
                markDirty();
            });
        });

        accordion.querySelectorAll('[data-action="remove-block"]').forEach(button => {
            button.addEventListener("click", () => {
                const menu = findMenu(button.dataset.menuId);
                if (!menu) return;
                menu.blocks = menu.blocks.filter(block => block.id !== button.dataset.blockId);
                renderAdmin();
                markDirty();
            });
        });

        accordion.querySelectorAll(".tutorial-editor").forEach(editor => {
            editor.addEventListener("focus", () => { activeEditor = editor; });
            editor.addEventListener("input", () => {
                const menu = findMenu(editor.dataset.menuId);
                const block = findBlock(menu, editor.dataset.blockId);
                if (block) block.html = editor.innerHTML;
                markDirty();
            });
        });

        accordion.querySelectorAll(".tutorial-editor-toolbar").forEach(toolbar => {
            toolbar.querySelectorAll("button[data-command]").forEach(button => {
                button.addEventListener("mousedown", event => event.preventDefault());
                button.addEventListener("click", () => {
                    const editor = document.getElementById(toolbar.dataset.editorId);
                    if (!editor) return;
                    editor.focus();
                    document.execCommand("styleWithCSS", false, true);
                    document.execCommand(button.dataset.command, false, null);
                    syncEditor(editor);
                });
            });
            const size = toolbar.querySelector('select[data-command="fontSize"]');
            if (size) size.addEventListener("change", () => {
                const editor = document.getElementById(toolbar.dataset.editorId);
                if (!editor) return;
                editor.focus();
                document.execCommand("styleWithCSS", false, true);
                document.execCommand("fontSize", false, size.value);
                syncEditor(editor);
            });
        });

        accordion.querySelectorAll('[data-action="toggle-emoji"]').forEach(button => {
            button.addEventListener("mousedown", event => event.preventDefault());
            button.addEventListener("click", () => {
                const picker = accordion.querySelector(`[data-emoji-picker-for="${CSS.escape(button.dataset.editorId)}"]`);
                if (!picker) return;
                const willOpen = picker.hidden;
                accordion.querySelectorAll(".tutorial-emoji-picker").forEach(p => p.hidden = true);
                if (willOpen) {
                    renderEmojiPicker(picker, button.dataset.editorId);
                    picker.hidden = false;
                }
            });
        });
    }

    function syncEditor(editor) {
        const menu = findMenu(editor.dataset.menuId);
        const block = findBlock(menu, editor.dataset.blockId);
        if (block) block.html = editor.innerHTML;
        markDirty();
    }

    function renderEmojiPicker(picker, editorId) {
        const nativeButtons = builtinEmojis.map(emoji => `<button type="button" class="tutorial-emoji-button" data-native-emoji="${escapeHtml(emoji)}">${emoji}</button>`).join("");
        const customButtons = tutorialData.customEmojis.map(emoji => `<button type="button" class="tutorial-emoji-button" data-custom-emoji-id="${escapeHtml(emoji.id)}" title="${escapeHtml(emoji.name || "Emoji personnalisé")}"><img src="${escapeHtml(emoji.data)}" alt=""></button>`).join("");
        picker.innerHTML = nativeButtons + customButtons + `<button type="button" class="tutorial-emoji-button tutorial-emoji-import" data-action="import-emoji">+ Ajouter un emoji</button><input type="file" accept="image/*" data-emoji-file hidden>`;

        picker.querySelectorAll("[data-native-emoji]").forEach(button => {
            button.addEventListener("mousedown", event => event.preventDefault());
            button.addEventListener("click", () => insertEmoji(editorId, button.dataset.nativeEmoji, false));
        });
        picker.querySelectorAll("[data-custom-emoji-id]").forEach(button => {
            button.addEventListener("mousedown", event => event.preventDefault());
            button.addEventListener("click", () => {
                const emoji = tutorialData.customEmojis.find(item => item.id === button.dataset.customEmojiId);
                if (emoji) insertEmoji(editorId, emoji, true);
            });
        });
        const importButton = picker.querySelector('[data-action="import-emoji"]');
        const fileInput = picker.querySelector("[data-emoji-file]");
        importButton.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", async () => {
            const file = fileInput.files && fileInput.files[0];
            if (!file) return;
            try {
                const data = await compressImage(file, 128, 128, .88, 55 * 1024);
                tutorialData.customEmojis.push({ id: uid("emoji"), name: file.name || "Emoji personnalisé", data });
                renderEmojiPicker(picker, editorId);
                markDirty();
            } catch (error) {
                setStatus("Impossible d'importer cet emoji.", "error");
            }
        });
    }

    function insertEmoji(editorId, emoji, custom) {
        const editor = document.getElementById(editorId);
        if (!editor) return;
        editor.focus();
        if (custom) {
            const htmlCode = `<img class="tutorial-inline-emoji" src="${emoji.data}" alt="${escapeHtml(emoji.name || "emoji")}">`;
            document.execCommand("insertHTML", false, htmlCode);
        } else {
            document.execCommand("insertText", false, emoji);
        }
        syncEditor(editor);
    }

    function dataUrlApproxBytes(dataUrl) {
        const comma = String(dataUrl || "").indexOf(",");
        const base64 = comma >= 0 ? String(dataUrl).slice(comma + 1) : String(dataUrl || "");
        return Math.ceil(base64.length * 0.75);
    }

    async function compressImage(file, maxWidth, maxHeight, quality, targetBytes = 650 * 1024) {
        if (!file.type.startsWith("image/")) throw new Error("Ce fichier n'est pas une image.");

        const dataUrl = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });

        const image = await new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = dataUrl;
        });

        let scale = Math.min(1, maxWidth / image.width, maxHeight / image.height);
        let width = Math.max(1, Math.round(image.width * scale));
        let height = Math.max(1, Math.round(image.height * scale));
        let currentQuality = Math.min(.9, Math.max(.55, Number(quality || .82)));
        let result = "";

        for (let attempt = 0; attempt < 9; attempt += 1) {
            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = "high";
            ctx.drawImage(image, 0, 0, width, height);
            result = canvas.toDataURL("image/webp", currentQuality);

            if (dataUrlApproxBytes(result) <= targetBytes) break;

            if (currentQuality > .62) {
                currentQuality = Math.max(.60, currentQuality - .07);
            } else {
                width = Math.max(640, Math.round(width * .88));
                height = Math.max(360, Math.round(height * .88));
                currentQuality = .72;
            }
        }

        return result;
    }

    function openPasswordModal() {
        settingsPopover.hidden = true;
        passwordError.textContent = "";
        passwordInput.value = "";
        passwordModal.hidden = false;
        setTimeout(() => passwordInput.focus(), 20);
    }

    function closePasswordModal() {
        passwordModal.hidden = true;
        passwordInput.value = "";
        passwordError.textContent = "";
    }

    function base64ToBytes(value) {
        const binary = atob(value);
        return Uint8Array.from(binary, char => char.charCodeAt(0));
    }

    async function decryptAdminToken(password) {
        const config = window.LEGODINGO13_ADMIN_CONFIG;
        if (!config || !config.ciphertext || !config.salt || !config.iv) {
            throw new Error("CONFIG_ABSENTE");
        }
        const encoder = new TextEncoder();
        const material = await crypto.subtle.importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveKey"]);
        const key = await crypto.subtle.deriveKey(
            { name: "PBKDF2", salt: base64ToBytes(config.salt), iterations: Number(config.iterations || 310000), hash: "SHA-256" },
            material,
            { name: "AES-GCM", length: 256 },
            false,
            ["decrypt"]
        );
        const clear = await crypto.subtle.decrypt({ name: "AES-GCM", iv: base64ToBytes(config.iv) }, key, base64ToBytes(config.ciphertext));
        return new TextDecoder().decode(clear).trim();
    }

    async function validatePassword() {
        const password = passwordInput.value;
        passwordError.textContent = "";
        if (!password) {
            passwordError.textContent = "Entre le mot de passe.";
            return;
        }
        passwordValidate.disabled = true;
        passwordValidate.textContent = "Vérification…";
        try {
            const token = await decryptAdminToken(password);
            if (!(token.startsWith("github_pat_") || token.startsWith("ghp_"))) throw new Error("TOKEN_INVALIDE");
            adminToken = token;
            adminMode = true;
            openMenuId = tutorialData.menus[0]?.id || null;
            adminToolbar.hidden = false;
            settingsButton.hidden = true;
            settingsPopover.hidden = true;
            closePasswordModal();
            setStatus("Vue gestion activée.", "success");
            renderAdmin();
        } catch (error) {
            if (String(error.message) === "CONFIG_ABSENTE") {
                passwordError.textContent = "La configuration administrateur n'est pas encore installée sur le site.";
            } else {
                passwordError.textContent = "Mot de passe incorrect.";
            }
        } finally {
            passwordValidate.disabled = false;
            passwordValidate.textContent = "Valider";
        }
    }

    function openConfirm(title, message, acceptLabel, callback) {
        confirmTitle.textContent = title;
        confirmText.textContent = message;
        confirmAccept.textContent = acceptLabel || "Valider";
        confirmCallback = callback;
        confirmModal.hidden = false;
    }
    function closeConfirm() {
        confirmModal.hidden = true;
        confirmCallback = null;
    }

    function createMenuRequest() {
        openConfirm("Créer un menu déroulant", "Confirmer la création d'un nouveau menu déroulant ?", "Créer", () => {
            const menu = { id: uid("menu"), title: "", blocks: [] };
            tutorialData.menus.push(menu);
            openMenuId = menu.id;
            closeConfirm();
            renderAdmin();
            markDirty();
            const input = accordion.querySelector(`[data-action="menu-title"][data-menu-id="${CSS.escape(menu.id)}"]`);
            if (input) input.focus();
        });
    }

    function deleteMenuRequest() {
        if (!tutorialData.menus.length) {
            setStatus("Aucun menu déroulant à supprimer.", "error");
            return;
        }
        deleteMenuSelect.innerHTML = tutorialData.menus.map((menu, index) => {
            const label = String(menu.title || "").trim() || `Menu sans titre ${index + 1}`;
            return `<option value="${escapeHtml(menu.id)}">${escapeHtml(label)}</option>`;
        }).join("");
        if (openMenuId && tutorialData.menus.some(menu => menu.id === openMenuId)) {
            deleteMenuSelect.value = openMenuId;
        }
        deleteMenuModal.hidden = false;
        setTimeout(() => deleteMenuSelect.focus(), 20);
    }

    function closeDeleteMenuModal() {
        deleteMenuModal.hidden = true;
    }

    function continueDeleteMenu() {
        const menu = findMenu(deleteMenuSelect.value);
        if (!menu) {
            closeDeleteMenuModal();
            setStatus("Le menu sélectionné est introuvable.", "error");
            return;
        }
        closeDeleteMenuModal();
        openConfirm(
            "Supprimer un menu déroulant",
            `Supprimer « ${menu.title || "Menu sans titre"} » ? Cette action ne sera définitive qu'après l'enregistrement.`,
            "Supprimer",
            () => {
                tutorialData.menus = tutorialData.menus.filter(item => item.id !== menu.id);
                if (openMenuId === menu.id) openMenuId = null;
                closeConfirm();
                renderAdmin();
                markDirty();
            }
        );
    }

    function openOrderMenuModal() {
        if (!tutorialData.menus.length) {
            setStatus("Aucun menu déroulant à réorganiser.", "error");
            return;
        }
        renderOrderMenuList();
        orderMenuModal.hidden = false;
    }

    function closeOrderMenuModal() {
        orderMenuModal.hidden = true;
    }

    function renderOrderMenuList() {
        orderMenuList.innerHTML = tutorialData.menus.map((menu, index) => {
            const label = String(menu.title || "").trim() || `Menu sans titre ${index + 1}`;
            return `<div class="tutorial-order-row" data-order-row-id="${escapeHtml(menu.id)}">
                <div class="tutorial-order-name">${escapeHtml(label)}</div>
                <div class="tutorial-order-buttons">
                    <button type="button" data-action="move-menu-up" data-menu-id="${escapeHtml(menu.id)}" title="Monter" aria-label="Monter ${escapeHtml(label)}" ${index === 0 ? "disabled" : ""}>↑</button>
                    <button type="button" data-action="move-menu-down" data-menu-id="${escapeHtml(menu.id)}" title="Descendre" aria-label="Descendre ${escapeHtml(label)}" ${index === tutorialData.menus.length - 1 ? "disabled" : ""}>↓</button>
                </div>
            </div>`;
        }).join("");

        orderMenuList.querySelectorAll('[data-action="move-menu-up"], [data-action="move-menu-down"]').forEach(button => {
            button.addEventListener("click", () => {
                const index = tutorialData.menus.findIndex(menu => menu.id === button.dataset.menuId);
                if (index < 0) return;
                const direction = button.dataset.action === "move-menu-up" ? -1 : 1;
                const target = index + direction;
                if (target < 0 || target >= tutorialData.menus.length) return;
                [tutorialData.menus[index], tutorialData.menus[target]] = [tutorialData.menus[target], tutorialData.menus[index]];
                renderOrderMenuList();
                renderAdmin();
                markDirty();
            });
        });
    }

    function openVideoModal(menuId) {
        videoTargetMenuId = menuId;
        videoUrlInput.value = "";
        videoError.textContent = "";
        videoModal.hidden = false;
        setTimeout(() => videoUrlInput.focus(), 20);
    }
    function closeVideoModal() {
        videoModal.hidden = true;
        videoTargetMenuId = null;
        videoError.textContent = "";
    }
    function addVideoFromModal() {
        const id = youtubeId(videoUrlInput.value);
        if (!id) {
            videoError.textContent = "Entre un lien YouTube valide.";
            return;
        }
        const menu = findMenu(videoTargetMenuId);
        if (!menu) return closeVideoModal();
        menu.blocks.push({ id: uid("video"), type: "video", url: videoUrlInput.value.trim() });
        openMenuId = menu.id;
        closeVideoModal();
        renderAdmin();
        markDirty();
    }

    function bytesToBase64(bytes) {
        let binary = "";
        const chunk = 0x8000;
        for (let i = 0; i < bytes.length; i += chunk) {
            binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
        }
        return btoa(binary);
    }

    function utf8ToBase64(value) {
        return bytesToBase64(new TextEncoder().encode(value));
    }

    async function githubRequest(url, options = {}) {
        const headers = Object.assign({
            "Accept": "application/vnd.github+json",
            "Authorization": `Bearer ${adminToken}`,
            "X-GitHub-Api-Version": "2022-11-28"
        }, options.headers || {});
        const response = await fetch(url, Object.assign({}, options, { headers }));
        if (!response.ok) {
            const details = await response.text();
            throw new Error(`GitHub ${response.status}: ${details}`);
        }
        return response.status === 204 ? null : response.json();
    }

    function validateBeforeSave() {
        for (const menu of tutorialData.menus) {
            if (!String(menu.title || "").trim()) {
                openMenuId = menu.id;
                renderAdmin();
                setStatus("Impossible d'enregistrer : chaque menu déroulant doit avoir un titre.", "error");
                const input = accordion.querySelector(`[data-action="menu-title"][data-menu-id="${CSS.escape(menu.id)}"]`);
                if (input) input.focus();
                return false;
            }
        }
        return true;
    }

    async function savePage() {
        if (!adminToken || !validateBeforeSave()) return;
        setStatus("Enregistrement sur GitHub…", "");
        const saveButton = document.getElementById("tutorialSavePage");
        if (saveButton) saveButton.disabled = true;
        try {
            let sha = null;
            try {
                const current = await githubRequest(API_URL + "?ref=" + encodeURIComponent(REPO_BRANCH));
                sha = current.sha;
            } catch (error) {
                if (!String(error.message).includes("GitHub 404")) throw error;
            }
            const cleanData = deepClone(tutorialData);
            const nowIso = new Date().toISOString();
            ensureUniqueMenuSlugs(cleanData.menus);

            let previousData = { menus: [] };
            try {
                previousData = JSON.parse(savedDataSnapshot || '{"menus":[]}');
            } catch (error) {
                previousData = { menus: [] };
            }
            const previousMenus = new Map((previousData.menus || []).map(menu => [menu.id, menu]));

            cleanData.menus.forEach(menu => {
                const previous = previousMenus.get(menu.id);
                const changed = !previous || JSON.stringify(comparableMenu(menu)) !== JSON.stringify(comparableMenu(previous));
                if (!menu.updatedAt || changed) menu.updatedAt = nowIso;
            });

            cleanData.updatedAt = nowIso;
            const payload = {
                message: "Mise à jour de la page Tutoriels de jeu",
                content: utf8ToBase64(JSON.stringify(cleanData, null, 2)),
                branch: REPO_BRANCH
            };
            if (sha) payload.sha = sha;
            await githubRequest(API_URL, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            tutorialData = cleanData;
            savedDataSnapshot = JSON.stringify(tutorialData);
            setStatus("Modifications enregistrées. GitHub republiera automatiquement le site dans quelques instants.", "success");
        } catch (error) {
            console.error(error);
            setStatus("Échec de l'enregistrement sur GitHub. Vérifie le token et sa permission Contents: Read and write.", "error");
        } finally {
            if (saveButton) saveButton.disabled = false;
        }
    }

    function quitAdmin() {
        const doQuit = () => {
            adminMode = false;
            adminToken = null;
            adminToolbar.hidden = true;
            settingsButton.hidden = false;
            openMenuId = null;
            tutorialData = normalizeData(JSON.parse(savedDataSnapshot || '{"version":1,"menus":[],"customEmojis":[]}'));
            setStatus("", "");
            renderPublic();
        };
        if (dataChanged()) {
            openConfirm("Quitter la vue gestion", "Des modifications ne sont pas enregistrées. Quitter quand même ?", "Quitter", () => { closeConfirm(); doQuit(); });
        } else {
            doQuit();
        }
    }

    settingsButton.addEventListener("click", () => { settingsPopover.hidden = !settingsPopover.hidden; });
    editPageButton.addEventListener("click", openPasswordModal);
    passwordValidate.addEventListener("click", validatePassword);
    passwordInput.addEventListener("keydown", event => { if (event.key === "Enter") validatePassword(); });
    document.querySelectorAll('[data-close-password]').forEach(button => button.addEventListener("click", closePasswordModal));

    document.getElementById("tutorialCreateMenu").addEventListener("click", createMenuRequest);
    document.getElementById("tutorialDeleteMenu").addEventListener("click", deleteMenuRequest);
    document.getElementById("tutorialReorderMenus").addEventListener("click", openOrderMenuModal);
    document.getElementById("tutorialSavePage").addEventListener("click", savePage);
    document.getElementById("tutorialQuitAdmin").addEventListener("click", quitAdmin);

    deleteMenuContinue.addEventListener("click", continueDeleteMenu);
    document.querySelectorAll('[data-close-delete-menu]').forEach(button => button.addEventListener("click", closeDeleteMenuModal));

    document.querySelectorAll('[data-close-order-menu]').forEach(button => button.addEventListener("click", closeOrderMenuModal));

    confirmAccept.addEventListener("click", () => { if (confirmCallback) confirmCallback(); });
    confirmCancel.addEventListener("click", closeConfirm);
    document.querySelectorAll('[data-close-confirm]').forEach(button => button.addEventListener("click", closeConfirm));

    videoAddButton.addEventListener("click", addVideoFromModal);
    videoUrlInput.addEventListener("keydown", event => { if (event.key === "Enter") addVideoFromModal(); });
    document.querySelectorAll('[data-close-video]').forEach(button => button.addEventListener("click", closeVideoModal));

    document.addEventListener("click", event => {
        if (!settingsPopover.hidden && !settingsPopover.contains(event.target) && event.target !== settingsButton) {
            settingsPopover.hidden = true;
        }
    });

    window.addEventListener("hashchange", () => {
        if (!adminMode) openTutorialFromHash(true);
    });

    loadTutorialData();
})();
</script>'''


# =========================================================
# GÉNÉRATION DES PAGES
# =========================================================

def navigation(active):
    links = [
        ("Accueil", "index.html", "accueil"),
        ("Discord", "discord.html", "discord"),
        ("YouTube", "youtube.html", "youtube"),
        ("Profil Legodingo13", "profil.html", "profil"),
        ("Tutoriels de jeu", "tutoriels.html", "tutoriels"),
    ]

    parts = []
    for label, href, key in links:
        cls = ' class="active"' if key == active else ""
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
    return "".join(parts)


def shell(filename, active, title, description, body, robots="index, follow"):
    canonical = SITE_BASE + ("" if filename == "index.html" else filename)
    view_path = (
        PAGEVIEWS_BASE_PATH + "/"
        if filename == "index.html"
        else PAGEVIEWS_BASE_PATH + "/" + filename
    )
    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Icône affichée dans l'onglet du navigateur -->
<link rel="icon" type="image/x-icon" href="favicon.ico?v=4">
<link rel="shortcut icon" type="image/x-icon" href="favicon.ico?v=4">
<link rel="icon" type="image/png" sizes="32x32" href="onglet_logo_optimise.png?v=4">
<link rel="apple-touch-icon" href="onglet_logo_optimise.png?v=4">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
{GOOGLE_META}
<style>{CSS}</style>
</head>
<body>
<main class="page">
<section class="card">
<header class="site-head">
    <div class="logo-zone">
        <button
            type="button"
            class="logo-trigger"
            id="logoKingTrigger"
            aria-label="Faire tomber le roi Legodingo13"
            title="Clique sur le logo"
        >
            <img src="logo.png" alt="Logo du serveur Discord Legodingo13" class="logo">
        </button>
    </div>
    <div class="badge">COMMUNAUTÉ LEGODINGO13</div>
    <nav class="nav" aria-label="Navigation principale">{navigation(active)}</nav>
</header>
<div class="content">{body}</div>
<footer class="footer">
    <div
        class="page-view-counter"
        data-view-site="{PAGEVIEWS_SITE}"
        data-view-path="{view_path}"
        aria-label="Nombre de vues de cette page"
        title="Nombre de vues de cette page"
    >
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M12 5c-5.5 0-9.6 4.6-10.8 6.2a1.3 1.3 0 0 0 0 1.6C2.4 14.4 6.5 19 12 19s9.6-4.6 10.8-6.2a1.3 1.3 0 0 0 0-1.6C21.6 9.6 17.5 5 12 5Zm0 11a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm0-2.2a1.8 1.8 0 1 0 0-3.6 1.8 1.8 0 0 0 0 3.6Z"/>
        </svg>
        <span class="page-view-number">—</span>
    </div>
    <div class="footer-copy">
        Dernière mise à jour automatique : <strong>{updated}</strong><br>
        <small>Site communautaire Legodingo13 • Forge of Empires</small>
    </div>
    <div class="footer-spacer" aria-hidden="true"></div>
</footer>
</section>
</main>
{SCRIPT}
</body>
</html>"""

    with open(os.path.join("_site", filename), "w", encoding="utf-8") as f:
        f.write(page)


if os.path.exists("_site"):
    shutil.rmtree("_site")
os.makedirs("_site", exist_ok=True)


# ACCUEIL
home_body = f"""
<h1>Legodingo13</h1>
<p class="lead">
Bienvenue sur le site de la communauté Legodingo13 autour de Forge of Empires.
Retrouve ici mes liens officiels, puis une sélection de sites, extensions et chaînes YouTube tierces utiles à la communauté Forge of Empires.
</p>

<div class="stats">
    <div class="stat"><span class="number">{member_count}</span><span class="label">membres sur le serveur Discord</span></div>
    <div class="stat"><span class="number">{youtube_subscribers}</span><span class="label">abonnés sur YouTube</span></div>
</div>

<section class="section-block">
<h2 class="section-title">Liens Legodingo13</h2>
<p class="section-subtitle">Mes pages, mon serveur et les accès directement liés à la communauté Legodingo13.</p>

<div class="grid">
    <a class="tile" href="discord.html"><img src="logo.png" loading="lazy" decoding="async" class="tile-logo server-logo-small" alt="Discord Legodingo13"><div class="tile-title">Discord</div><div class="tile-detail">Le plus gros serveur communautaire francophone autour de Forge of Empires.</div></a>
    <a class="tile" href="youtube.html"><img src="Youtube.png" loading="lazy" decoding="async" class="tile-logo youtube-logo" alt="YouTube"><div class="tile-title">YouTube</div><div class="tile-detail">Retrouver la chaîne YouTube de Legodingo13.</div></a>
    <a class="tile" href="{FOE_URL}" target="_blank" rel="noopener noreferrer"><img src="foe_logo.png" loading="lazy" decoding="async" class="tile-logo foe-logo" alt="Forge of Empires"><div class="tile-title">Forge of Empires</div><div class="tile-detail">Accéder au site officiel francophone du jeu.</div></a>
    <a class="tile" href="profil.html"><img src="profil_tableau.png" loading="lazy" decoding="async" class="tile-logo profile-tableau-logo" alt="Profil Legodingo13 - Tableau Excel des mondes FOE"><div class="tile-title">Profil Legodingo13</div><div class="tile-detail">Tableau Excel des mondes FOE</div></a>
    <a class="tile" href="tutoriels.html"><img src="tutoriels_logo.png" loading="lazy" decoding="async" class="tile-logo tutorials-logo" alt="Tutoriels de jeu Legodingo13"><div class="tile-title">Tutoriels de jeu</div><div class="tile-detail">Consulter les tutoriels et guides de jeu.</div></a>
    <a class="tile" href="{GUNS_URL}" target="_blank" rel="noopener noreferrer"><img src="guns.png" loading="lazy" decoding="async" class="tile-logo guns-logo" alt="guns.lol Legodingo13"><div class="tile-title">Guns</div><div class="tile-detail">Accéder à la page guns.lol de Legodingo13.</div></a>
</div>
</section>

<section class="section-block">
<h2 class="section-title">Sites tiers</h2>
<p class="section-subtitle">Outils, bases de données et ressources externes consacrés à Forge of Empires.</p>

<div class="grid">
    <a class="tile" href="{FOE_WIKI_URL}" target="_blank" rel="noopener noreferrer">
        <img src="foe_logo.png" loading="lazy" decoding="async" class="tile-logo foe-logo" alt="Wiki Forge of Empires">
        <div class="tile-title">Wiki Forge of Empires</div>
        <div class="tile-detail">Wiki francophone consacré à Forge of Empires.</div>
        <div class="external-badge">SITE TIERS</div>
    </a>

    <a class="tile" href="{FORGEDB_URL}" target="_blank" rel="noopener noreferrer">
        <img src="forgedb.png" loading="lazy" decoding="async" class="tile-logo third-party-logo" alt="ForgeDB">
        <div class="tile-title">ForgeDB</div>
        <div class="tile-detail">Base de données et statistiques autour de Forge of Empires.</div>
        <div class="external-badge">SITE TIERS</div>
    </a>

    <a class="tile" href="{FOE_SCOREDB_URL}" target="_blank" rel="noopener noreferrer">
        <img src="foe_scoredb.png" loading="lazy" decoding="async" class="tile-logo third-party-logo small" alt="FOE ScoreDB">
        <div class="tile-title">FOE ScoreDB</div>
        <div class="tile-detail">Base de données et classements Forge of Empires.</div>
        <div class="external-badge">SITE TIERS</div>
    </a>

    <a class="tile" href="{FOE_DATA_URL}" target="_blank" rel="noopener noreferrer">
        <img src="foe_data.png" loading="lazy" decoding="async" class="tile-logo third-party-logo" alt="FOE Data">
        <div class="tile-title">FOE Data</div>
        <div class="tile-detail">Base de données consacrée à Forge of Empires.</div>
        <div class="external-badge">SITE TIERS</div>
    </a>

    <a class="tile" href="{BANANA_DB_URL}" target="_blank" rel="noopener noreferrer">
        <img src="banana_db.png" loading="lazy" decoding="async" class="tile-logo third-party-logo" alt="Born To Be A Banana">
        <div class="tile-title">Born To Be A Banana</div>
        <div class="tile-detail">Base de données consacrée aux bâtiments de Forge of Empires.</div>
        <div class="external-badge">SITE TIERS</div>
    </a>

    <a class="tile" href="{FOE_TOOLS_URL}" target="_blank" rel="noopener noreferrer">
        <img src="foe_tools.png" loading="lazy" decoding="async" class="tile-logo third-party-logo" alt="FOE Tools">
        <div class="tile-title">FOE Tools</div>
        <div class="tile-detail">Assistant pour calculer les places et investissements des Grands Monuments.</div>
        <div class="external-badge">SITE TIERS</div>
    </a>
</div>
</section>

<section class="section-block">
<h2 class="section-title">Extensions du jeu</h2>
<p class="section-subtitle">Extensions tierces utiles pour accompagner Forge of Empires dans le navigateur.</p>

<div class="grid two">
    <a class="tile" href="{FOE_HAMMER_URL}" target="_blank" rel="noopener noreferrer">
        <img src="foe_hammer.png" loading="lazy" decoding="async" class="tile-logo third-party-logo" alt="FOE Hammer">
        <div class="tile-title">FOE Hammer</div>
        <div class="tile-detail">Extension Chrome pour Forge of Empires.</div>
        <div class="external-badge">EXTENSION TIERCE</div>
    </a>

    <a class="tile" href="{FOE_HELPER_URL}" target="_blank" rel="noopener noreferrer">
        <img src="foe_helper.png" loading="lazy" decoding="async" class="tile-logo third-party-logo" alt="FOE Helper">
        <div class="tile-title">FOE Helper</div>
        <div class="tile-detail">Extension et assistant communautaire pour Forge of Empires.</div>
        <div class="external-badge">EXTENSION TIERCE</div>
    </a>
</div>
</section>

<section class="section-block">
<h2 class="section-title">Chaînes YouTube tierces</h2>
<p class="section-subtitle">Quelques chaînes YouTube consacrées à Forge of Empires.</p>

<div class="grid">
    <a class="tile" href="{UBERNERD14_URL}" target="_blank" rel="noopener noreferrer">
        <img src="ubernerd14.png" loading="lazy" decoding="async" class="tile-logo third-party-logo" alt="UBERnerd14">
        <div class="tile-title">UBERnerd14</div>
        <div class="tile-detail">Le plus gros YouTuber Forge of Empires.</div>
        <div class="external-badge">CHAÎNE TIERCE</div>
    </a>

    <a class="tile" href="{SENSHI_URL}" target="_blank" rel="noopener noreferrer">
        <img src="Youtube.png" loading="lazy" decoding="async" class="tile-logo youtube-logo" alt="YouTube Senshi">
        <div class="tile-title">Senshi</div>
        <div class="tile-detail">Chaîne YouTube autour de Forge of Empires.</div>
        <div class="external-badge">CHAÎNE TIERCE</div>
    </a>

    <a class="tile" href="{PIXELPULSE_URL}" target="_blank" rel="noopener noreferrer">
        <img src="Youtube.png" loading="lazy" decoding="async" class="tile-logo youtube-logo" alt="YouTube PixelPulse">
        <div class="tile-title">PixelPulse</div>
        <div class="tile-detail">Chaîne YouTube autour de Forge of Empires.</div>
        <div class="external-badge">CHAÎNE TIERCE</div>
    </a>

    <a class="tile" href="{MOOINGCAT_URL}" target="_blank" rel="noopener noreferrer">
        <img src="Youtube.png" loading="lazy" decoding="async" class="tile-logo youtube-logo" alt="YouTube MooingCatFOE">
        <div class="tile-title">MooingCatFOE</div>
        <div class="tile-detail">Chaîne YouTube autour de Forge of Empires.</div>
        <div class="external-badge">CHAÎNE TIERCE</div>
    </a>

    <a class="tile" href="{GUIGEEKS_URL}" target="_blank" rel="noopener noreferrer">
        <img src="Youtube.png" loading="lazy" decoding="async" class="tile-logo youtube-logo" alt="YouTube Guigeeks">
        <div class="tile-title">Guigeeks</div>
        <div class="tile-detail">Chaîne YouTube autour de Forge of Empires.</div>
        <div class="external-badge">CHAÎNE TIERCE</div>
    </a>

    <a class="tile" href="{ZOUMA_URL}" target="_blank" rel="noopener noreferrer">
        <img src="Youtube.png" loading="lazy" decoding="async" class="tile-logo youtube-logo" alt="YouTube Zouma">
        <div class="tile-title">Zouma</div>
        <div class="tile-detail">Chaîne YouTube autour de Forge of Empires.</div>
        <div class="external-badge">CHAÎNE TIERCE</div>
    </a>
</div>
</section>
"""
shell(
    "index.html",
    "accueil",
    "Legodingo13 - Communauté Forge of Empires",
    f"Site de Legodingo13 : serveur Discord Forge of Empires avec {member_count} membres, chaîne YouTube et tableau communautaire.",
    home_body,
)


# DISCORD
discord_body = f"""
<h1>Serveur Discord de Legodingo13</h1>
<h2 class="gold">{guild_name}</h2>
<p class="lead">
Le plus gros serveur communautaire francophone autour de Forge of Empires.
Rejoins la communauté pour bénéficier des meilleures aides et de la meilleure activité
de la communauté francophone de Forge of Empires !
</p>
<img src="discord_presentation_1.png" class="discord-presentation-image" loading="lazy" decoding="async" alt="Présentation visuelle du serveur Discord Legodingo13 - Serv FOE FR">
<div class="stats">
    <div class="stat"><span class="number">{member_count}</span><span class="label">membres sur le serveur</span></div>
    <div class="stat"><span class="number">{online_count}</span><span class="label"><span class="online-dot"></span>membres actuellement en ligne</span></div>
</div>
<p class="lead">Le serveur Discord de Legodingo13 compte actuellement <strong class="gold">{member_count} membres</strong>, dont environ <strong class="gold">{online_count} membres en ligne</strong>.</p>
<a class="primary-button" href="https://discord.gg/{DISCORD_INVITE}" target="_blank" rel="noopener noreferrer">Rejoindre le serveur Discord</a>
<img src="discord_presentation_2.png" class="discord-presentation-image" loading="lazy" decoding="async" alt="Présentation des différentes parties du serveur Discord Legodingo13">
<div class="grid">
    <a class="tile" href="youtube.html"><img src="Youtube.png" loading="lazy" decoding="async" class="tile-logo youtube-logo" alt="YouTube"><div class="tile-title">YouTube</div><div class="tile-count">{youtube_display}</div><div class="tile-detail">Accéder à la page YouTube du site</div></a>
    <a class="tile" href="{FOE_URL}" target="_blank" rel="noopener noreferrer"><img src="foe_logo.png" loading="lazy" decoding="async" class="tile-logo foe-logo" alt="Forge of Empires"><div class="tile-title">Forge of Empires</div><div class="tile-detail">Accéder au site officiel francophone du jeu</div></a>
    <a class="tile" href="tutoriels.html"><img src="tutoriels_logo.png" loading="lazy" decoding="async" class="tile-logo tutorials-logo" alt="Tutoriels de jeu Legodingo13"><div class="tile-title">Tutoriels de jeu</div><div class="tile-detail">Accéder à la page des tutoriels de jeu</div></a>
</div>
"""
shell(
    "discord.html",
    "discord",
    f"Serveur Discord Legodingo13 - {member_count} membres",
    f"Le serveur Discord de Legodingo13 compte actuellement environ {member_count} membres, dont {online_count} membres en ligne.",
    discord_body,
)


# YOUTUBE
youtube_body = f"""
<img src="Youtube.png" loading="lazy" decoding="async" class="tile-logo youtube-logo" alt="Logo YouTube">
<h1>Chaîne YouTube Legodingo13</h1>
<p class="lead">Retrouve la chaîne YouTube officielle de Legodingo13 et les contenus autour de Forge of Empires et de sa communauté.</p>
<div class="stats">
    <div class="stat"><span class="number">{youtube_subscribers}</span><span class="label">abonnés YouTube</span></div>
    <div class="stat"><span class="number">FOE</span><span class="label">contenus Forge of Empires</span></div>
</div>
<a class="primary-button" href="{YOUTUBE_URL}" target="_blank" rel="noopener noreferrer">Ouvrir la chaîne YouTube</a>
<div class="grid">
    <a class="tile" href="discord.html"><img src="logo.png" loading="lazy" decoding="async" class="tile-logo server-logo-small" alt="Discord Legodingo13"><div class="tile-title">Discord</div><div class="tile-detail">Accéder à la page du serveur Discord Legodingo13</div></a>
    <a class="tile" href="{FOE_URL}" target="_blank" rel="noopener noreferrer"><img src="foe_logo.png" loading="lazy" decoding="async" class="tile-logo foe-logo" alt="Forge of Empires"><div class="tile-title">Forge of Empires</div><div class="tile-detail">Accéder au site officiel francophone du jeu</div></a>
    <a class="tile" href="tutoriels.html"><img src="tutoriels_logo.png" loading="lazy" decoding="async" class="tile-logo tutorials-logo" alt="Tutoriels de jeu Legodingo13"><div class="tile-title">Tutoriels de jeu</div><div class="tile-detail">Accéder à la page des tutoriels de jeu</div></a>
</div>
"""
shell(
    "youtube.html",
    "youtube",
    f"YouTube Legodingo13 - {youtube_display}",
    f"Chaîne YouTube officielle Legodingo13 avec {youtube_display}.",
    youtube_body,
)



# TUTORIELS DE JEU
# Le contenu est lu depuis tutoriels-data.json dans le navigateur.
tutoriels_body = f"""
<h1>Tutoriels de jeu</h1>
<p class="tutorial-page-intro">
Retrouve ici les tutoriels et guides de jeu publiés par Legodingo13.
</p>

<div id="tutorialAdminToolbar" class="tutorial-admin-toolbar" hidden>
    <button id="tutorialCreateMenu" type="button">Créer un menu déroulant</button>
    <button id="tutorialDeleteMenu" type="button">Supprimer un menu déroulant</button>
    <button id="tutorialReorderMenus" type="button">Changer l’ordre des menus</button>
    <button id="tutorialSavePage" class="tutorial-save-button" type="button">Enregistrer les modifications de la page</button>
    <button id="tutorialQuitAdmin" type="button">Quitter la vue gestion de la page</button>
    <div id="tutorialAdminStatus" class="tutorial-admin-status"></div>
</div>

<div id="tutorialAccordion" class="tutorial-accordion">
    <div class="tutorial-empty">Chargement des tutoriels…</div>
</div>

<div id="tutorialCopyToast" class="tutorial-copy-toast" role="status" aria-live="polite" hidden></div>

<div class="tutorial-settings-wrap">
    <button id="tutorialSettingsButton" class="tutorial-settings-button" type="button" aria-label="Paramètres de la page" title="Paramètres">⚙</button>
    <div id="tutorialSettingsPopover" class="tutorial-settings-popover" hidden>
        <button id="tutorialEditPageButton" type="button">Modifier la page</button>
    </div>
</div>

<div id="tutorialPasswordModal" class="tutorial-modal-overlay" hidden>
    <div class="tutorial-modal" role="dialog" aria-modal="true" aria-labelledby="tutorialPasswordTitle">
        <button type="button" class="tutorial-modal-close" data-close-password aria-label="Fermer">×</button>
        <h3 id="tutorialPasswordTitle">Modifier la page</h3>
        <label for="tutorialPasswordInput">Mot de passe :</label>
        <input id="tutorialPasswordInput" type="password" autocomplete="current-password">
        <div id="tutorialPasswordError" class="tutorial-modal-error"></div>
        <div class="tutorial-modal-actions">
            <button type="button" data-close-password>Annuler</button>
            <button id="tutorialPasswordValidate" class="primary" type="button">Valider</button>
        </div>
    </div>
</div>

<div id="tutorialDeleteMenuModal" class="tutorial-modal-overlay" hidden>
    <div class="tutorial-modal" role="dialog" aria-modal="true" aria-labelledby="tutorialDeleteMenuTitle">
        <button type="button" class="tutorial-modal-close" data-close-delete-menu aria-label="Fermer">×</button>
        <h3 id="tutorialDeleteMenuTitle">Choisir le menu à supprimer</h3>
        <label for="tutorialDeleteMenuSelect">Menu déroulant :</label>
        <select id="tutorialDeleteMenuSelect"></select>
        <div class="tutorial-modal-actions">
            <button type="button" data-close-delete-menu>Annuler</button>
            <button id="tutorialDeleteMenuContinue" class="primary" type="button">Continuer</button>
        </div>
    </div>
</div>

<div id="tutorialOrderMenuModal" class="tutorial-modal-overlay" hidden>
    <div class="tutorial-modal" role="dialog" aria-modal="true" aria-labelledby="tutorialOrderMenuTitle">
        <button type="button" class="tutorial-modal-close" data-close-order-menu aria-label="Fermer">×</button>
        <h3 id="tutorialOrderMenuTitle">Changer l’ordre des menus</h3>
        <p class="tutorial-order-help">Utilise les flèches pour déplacer chaque menu. Le nouvel ordre ne sera définitif qu’après « Enregistrer les modifications de la page ».</p>
        <div id="tutorialOrderMenuList" class="tutorial-order-list"></div>
        <div class="tutorial-modal-actions">
            <button type="button" data-close-order-menu>Fermer</button>
        </div>
    </div>
</div>

<div id="tutorialConfirmModal" class="tutorial-modal-overlay" hidden>
    <div class="tutorial-modal" role="dialog" aria-modal="true" aria-labelledby="tutorialConfirmTitle">
        <button type="button" class="tutorial-modal-close" data-close-confirm aria-label="Fermer">×</button>
        <h3 id="tutorialConfirmTitle">Confirmation</h3>
        <div id="tutorialConfirmText" class="tutorial-modal-message"></div>
        <div class="tutorial-modal-actions">
            <button id="tutorialConfirmCancel" type="button">Annuler</button>
            <button id="tutorialConfirmAccept" class="primary" type="button">Valider</button>
        </div>
    </div>
</div>

<div id="tutorialVideoModal" class="tutorial-modal-overlay" hidden>
    <div class="tutorial-modal" role="dialog" aria-modal="true" aria-labelledby="tutorialVideoTitle">
        <button type="button" class="tutorial-modal-close" data-close-video aria-label="Fermer">×</button>
        <h3 id="tutorialVideoTitle">Ajouter une vidéo YouTube</h3>
        <label for="tutorialVideoUrlInput">Lien YouTube :</label>
        <input id="tutorialVideoUrlInput" type="url" placeholder="https://www.youtube.com/watch?v=...">
        <div id="tutorialVideoError" class="tutorial-modal-error"></div>
        <div class="tutorial-modal-actions">
            <button type="button" data-close-video>Annuler</button>
            <button id="tutorialVideoAdd" class="primary" type="button">Ajouter</button>
        </div>
    </div>
</div>

{TUTORIALS_SCRIPT}
"""
shell(
    "tutoriels.html",
    "tutoriels",
    "Tutoriels de jeu - Legodingo13",
    "Tutoriels et guides de jeu publiés par Legodingo13.",
    tutoriels_body,
)


# PROFIL = TABLEAU EXCEL
if os.path.exists("tableau.png"):
    profil_tableau_view = """
    <div class="table-frame">
        <img src="tableau.png" class="table-image" loading="lazy" decoding="async" alt="Tableau Excel des mondes Forge of Empires de Legodingo13">
    </div>
    <a class="primary-button gold-button" href="tableau.png" target="_blank" rel="noopener noreferrer">Ouvrir le tableau en grand</a>
    """
else:
    profil_tableau_view = """
    <div class="notice">
        Aucun tableau n'a encore été envoyé sur le site. Il apparaîtra ici automatiquement
        après le prochain lancement de l'application Legodingo13 Bot4.
    </div>
    """

profil_body = f"""
<img src="profil_tableau.png" loading="lazy" decoding="async" class="tile-logo profile-tableau-logo" alt="Profil Legodingo13">
<h1>Profil Legodingo13</h1>
<p class="lead">
Tableau Excel des mondes Forge of Empires de Legodingo13. Cette page affiche la dernière
version publiée depuis l'application Legodingo13 Bot4. Enregistre le fichier Excel avant
d'ouvrir l'application pour publier les dernières modifications.
</p>
{profil_tableau_view}
"""
shell(
    "profil.html",
    "profil",
    "Profil Legodingo13 - Tableau Excel des mondes FOE",
    "Profil Legodingo13 : dernière version du tableau Excel des mondes Forge of Empires.",
    profil_body,
)


# TABLEAU - ANCIENNE URL CONSERVÉE POUR COMPATIBILITÉ
# Même contenu que profil.html afin que TOUS les anciens liens affichent aussi le tableau Excel.
shell(
    "tableau.html",
    "profil",
    "Profil Legodingo13 - Tableau Excel des mondes FOE",
    "Profil Legodingo13 : dernière version du tableau Excel des mondes Forge of Empires.",
    profil_body,
)


# =========================================================
# PAGE 404 PERSONNALISÉE
# =========================================================

error_404_body = f"""
<div class="error-page">
    <img src="erreur404_roi.png" class="error-king" alt="Roi Legodingo13 perplexe" decoding="async">
    <div class="error-code">404</div>
    <h1>Page introuvable</h1>
    <p class="lead">
        Cette page semble s’être perdue à travers les âges…
    </p>
    <div class="error-actions">
        <a class="primary-button gold-button" href="index.html">Retour à l’accueil</a>
    </div>
</div>
"""
shell(
    "404.html",
    "",
    "Page introuvable - Legodingo13",
    "La page demandée est introuvable sur le site Legodingo13.",
    error_404_body,
    robots="noindex, follow",
)


# =========================================================
# ROBOTS.TXT + SITEMAP.XML
# =========================================================

with open("_site/robots.txt", "w", encoding="utf-8") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE}sitemap.xml\n")

sitemap_urls = [
    SITE_BASE,
    SITE_BASE + "discord.html",
    SITE_BASE + "youtube.html",
    SITE_BASE + "profil.html",
    SITE_BASE + "tutoriels.html",
]

sitemap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for url in sitemap_urls:
    sitemap += f"  <url><loc>{url}</loc></url>\n"
sitemap += "</urlset>\n"

with open("_site/sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap)


# =========================================================
# COPIE DES ASSETS
# =========================================================

assets = [
    "fond.png",
    "logo.png",
    "onglet_logo.png",
    "onglet_logo_optimise.png",
    "favicon.ico",
    "Youtube.png",
    "foe_logo.png",
    "guns.png",
    "profil_tableau.png",
    "tutoriels_logo.png",
    "erreur404_roi.png",
    "roi_chute.png",
    "discord_presentation_1.png",
    "discord_presentation_2.png",
    "tutoriels-data.json",
    "admin-config.js",

    # Logos des sites tiers
    "forgedb.png",
    "foe_scoredb.png",
    "foe_data.png",
    "banana_db.png",
    "foe_tools.png",

    # Logos des extensions
    "foe_hammer.png",
    "foe_helper.png",

    # Logo de la chaîne UBERnerd14
    "ubernerd14.png",

    "cursor_default.cur",
    "cursor_hover.cur",
    "tableau.png",
]

for asset in assets:
    if os.path.exists(asset):
        shutil.copy2(asset, os.path.join("_site", asset))
    elif asset != "tableau.png":
        print(f"ATTENTION : {asset} est introuvable.")


# =========================================================
# FICHIER DE SUIVI
# =========================================================

with open("last-update.txt", "w", encoding="utf-8") as f:
    f.write(f"Dernière mise à jour : {updated}\n")
    f.write(f"Membres Discord : {member_count}\n")
    f.write(f"En ligne Discord : {online_count}\n")
    f.write(f"Abonnés YouTube : {youtube_subscribers}\n")

print(f"Discord : {member_count} membres / {online_count} en ligne")
print(f"YouTube via SocialCounts : {youtube_subscribers} abonnés")
print("Pages générées : Accueil, Discord, YouTube, Profil Legodingo13, Tutoriels de jeu, compatibilité tableau.html")
