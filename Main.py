# ============================================
# Donut Clicker - Alpha 0.1.3
# System: 4 zakładki menu z ikonami
# ============================================

import pygame
import sys
import json
import os
import random
import math
from datetime import datetime, timedelta
import upgrades
import achievements

pygame.init()

# ============================================
# DONUT CLICKER - ALPHA 0.1.1
# Changelog v0.1.1:
# - Podzielono kod na 2 pliki: donut_clicker_alpha_0.1.1.py i upgrades.py
# - Moduł upgrades.py zawiera definicje budynków i ulepszeń
# - Główny plik zawiera pętlę gry i UI
# 
# Previous changes (v0.1.0):
# - Naprawiono: boxy upgrade'ów nie nachodzą na siebie
# - Dodano: upgrade Store, Settings, formatowanie liczb
# - Dodano: system Idle z nagrodami offline
# - Dodano: ulepszenie "Eating Power" i "Gastro Pill"
# ============================================

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Donut Clicker alpha 0.1.3")

PINK_BG = (255, 200, 210)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 90, 60)
BROWN_DARK = (101, 67, 33)
BROWN_LIGHT = (180, 130, 90)
BROWN_LIGHTER = (200, 150, 110)
LIGHT_YELLOW = (255, 240, 150)

SAVE_FILE = "donut_clicker_save.json"
ACHIEVEMENT_DESCRIPTIONS_FILE = "achievement_descriptions.json"

# Wczytaj opisy osiągnięć z pliku JSON
def load_achievement_descriptions():
    """Wczytuje opisy osiągnięć z pliku achievement_descriptions.json"""
    if os.path.exists(ACHIEVEMENT_DESCRIPTIONS_FILE):
        try:
            with open(ACHIEVEMENT_DESCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Achievement descriptions loaded from {ACHIEVEMENT_DESCRIPTIONS_FILE}")
                return data
        except Exception as e:
            print(f"Could not load achievement descriptions: {e}")
    else:
        print(f"No achievement descriptions file found ({ACHIEVEMENT_DESCRIPTIONS_FILE}), using defaults")
    return {}

achievement_descriptions = load_achievement_descriptions()

def load_game():
    global points, max_donuts, max_dps, time_played, eater_count, eater_premium_count, donut_house_count, donut_eating_hall_count, donut_co_count, total_donuts_earned, total_time_played, store_unlocked, eating_power_level, idle_donuts, idle_time_seconds, idle_window_open, gastro_pill_unlocked
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                points = data.get('points', 0)
                max_donuts = data.get('max_donuts', 0)
                max_dps = data.get('max_dps', 0)
                time_played = data.get('time_played', 0)
                eater_count = data.get('eater_count', 0)
                eater_premium_count = data.get('eater_premium_count', 0)
                donut_house_count = data.get('donut_house_count', data.get('eating_hall_count', 0))
                donut_eating_hall_count = data.get('donut_eating_hall_count', 0)
                donut_co_count = data.get('donut_co_count', 0)
                total_donuts_earned = data.get('total_donuts_earned', 0)
                total_time_played = data.get('total_time_played', 0)
                store_unlocked = data.get('store_unlocked', False)
                eating_power_level = data.get('eating_power_level', 0)
                gastro_pill_unlocked = data.get('gastro_pill_unlocked', False)
                sound_settings['enabled'] = data.get('sound_enabled', True)
                sound_settings['volume'] = data.get('sound_volume', 0.5)
                music_settings['enabled'] = data.get('music_enabled', True)
                music_settings['volume'] = data.get('music_volume', 0.3)
                
                # Zastosuj wczytane ustawienia muzyki
                if background_music_path:
                    pygame.mixer.music.set_volume(music_settings['volume'])
                    if music_settings['enabled']:
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.pause()
                
                # Oblicz idle rewards
                last_exit_time_str = data.get('last_exit_time')
                exit_dps = data.get('exit_dps', 0)
                
                print(f"DEBUG: last_exit_time_str = {last_exit_time_str}")
                print(f"DEBUG: exit_dps = {exit_dps}")
                
                if last_exit_time_str:
                    try:
                        last_exit_time = datetime.fromisoformat(last_exit_time_str)
                        current_time = datetime.now()
                        time_diff = current_time - last_exit_time
                        idle_seconds = int(time_diff.total_seconds())
                        
                        print(f"DEBUG: idle_seconds = {idle_seconds}")
                        
                        # Pokazuj okno idle tylko jeśli minęło więcej niż 10 sekund
                        if idle_seconds > 10:
                            # NOWA FORMUŁA: Za każde 10 minut (600s) = 1 sekunda DPS
                            # idle_donuts = (czas_w_sekundach / 600) * exit_dps
                            idle_time_seconds = idle_seconds
                            idle_donuts = int((idle_seconds / 600) * exit_dps)
                            idle_window_open = True
                            print(f"DEBUG: Opening idle window! idle_donuts={idle_donuts}, idle_time_seconds={idle_time_seconds}")
                            print(f"Idle rewards: {idle_donuts} donuts for {idle_seconds} seconds")
                        else:
                            print(f"DEBUG: Not showing idle window - only {idle_seconds} seconds passed")
                    except Exception as e:
                        print(f"Error calculating idle rewards: {e}")
                
                # Wczytaj osiągnięcia (musi być po inicjalizacji achievements)
                # To będzie wykonane później, po create_achievements()
                
                print("Game loaded successfully!")
        except Exception as e:
            print(f"Could not load save file: {e}, starting fresh")
    else:
        print("No save file found, starting new game")



def save_game():
    current_dps = get_total_dps()
    exit_time = datetime.now().isoformat()
    
    data = {
        'points': points,
        'max_donuts': max_donuts,
        'max_dps': max_dps,
        'time_played': time_played,
        'eater_count': eater_count,
        'eater_premium_count': eater_premium_count,
        'donut_house_count': donut_house_count,
        'donut_eating_hall_count': donut_eating_hall_count,
        'donut_co_count': donut_co_count,
        'total_donuts_earned': total_donuts_earned,
        'total_time_played': total_time_played,
        'store_unlocked': store_unlocked,
        'eating_power_level': eating_power_level,
        'gastro_pill_unlocked': gastro_pill_unlocked,
        'sound_enabled': sound_settings['enabled'],
        'sound_volume': sound_settings['volume'],
        'music_enabled': music_settings['enabled'],
        'music_volume': music_settings['volume'],
        'achievements': achievements.save_achievements(),
        'last_exit_time': exit_time,
        'exit_dps': current_dps
    }
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print("Game saved!")
    except:
        print("Could not save game")

points = 0
clock = pygame.time.Clock()
max_donuts = 0
max_dps = 0
time_played = 0
total_donuts_earned = 0
total_time_played = 0
game_start_time = pygame.time.get_ticks()

eater_count = 0
EATER_MAX = 10
EATER_BASE_COST = 100
EATER_DPS = 0.5

eater_premium_count = 0
EATER_PREMIUM_MAX = 10
EATER_PREMIUM_BASE_COST = 1000
EATER_PREMIUM_DPS = 2.5

donut_house_count = 0
DONUT_HOUSE_MAX = 10
DONUT_HOUSE_BASE_COST = 10000
DONUT_HOUSE_DPS = 5.0

donut_eating_hall_count = 0
DONUT_EATING_HALL_MAX = 25
DONUT_EATING_HALL_BASE_COST = 100000
DONUT_EATING_HALL_DPS = 10.0

donut_co_count = 0
DONUT_CO_MAX = 10
DONUT_CO_BASE_COST = 1000000
DONUT_CO_DPS = 100.0

store_unlocked = False
STORE_COST = 500

gastro_pill_unlocked = False
GASTRO_PILL_COST = 1000

eating_power_level = 0
EATING_POWER_BASE_COST = 50

idle_donuts = 0
idle_time_seconds = 0
idle_window_open = False

scale_plus_factor = 0.6
scale_minus_factor = 0.6

# Zmienne dla powiadomień osiągnięć
show_achievement_notification = False
achievement_to_show = None
achievement_notification_timer = 0
ACHIEVEMENT_NOTIFICATION_DURATION = 3000  # 3 sekundy

# Zmienne dla okna szczegółów osiągnięcia
achievement_detail_window_open = False
achievement_detail_to_show = None

def get_clicks_per_click():
    base_clicks = 1 + eating_power_level
    if gastro_pill_unlocked:
        return int(base_clicks * 1.3)  # +30% bonus
    return base_clicks

def get_eater_cost():
    cost = int(EATER_BASE_COST * (1.05 ** eater_count))
    if cost > 500:
        return int(500 + (cost - 500) * 0.25)
    return cost

def get_eater_premium_cost():
    return int(EATER_PREMIUM_BASE_COST * (1.08 ** eater_premium_count))

def get_donut_house_cost():
    return int(DONUT_HOUSE_BASE_COST * (1.1 ** donut_house_count))

def get_donut_eating_hall_cost():
    return int(DONUT_EATING_HALL_BASE_COST * (1.12 ** donut_eating_hall_count))

def get_donut_co_cost():
    return int(DONUT_CO_BASE_COST * (1.08 ** donut_co_count))

def get_eating_power_cost():
    return int(EATING_POWER_BASE_COST * (1.08 ** eating_power_level))

def get_total_dps():
    return (eater_count * EATER_DPS) + (eater_premium_count * EATER_PREMIUM_DPS) + (donut_house_count * DONUT_HOUSE_DPS) + (donut_eating_hall_count * DONUT_EATING_HALL_DPS) + (donut_co_count * DONUT_CO_DPS)

def format_number(num):
    num = int(num)
    if num < 1000:
        return str(num)
    elif num < 1_000_000:
        return f"{num / 1_000:.2f}K".rstrip('0').rstrip('.')
    elif num < 1_000_000_000:
        return f"{num / 1_000_000:.2f}M".rstrip('0').rstrip('.')
    elif num < 1_000_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num < 1_000_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    else:
        return f"{num / 1_000_000_000_000_000:.2e}Qd"

# ============================================
# WRAPPER FUNCTIONS - Compatibility ze starym kodem
 # ============================================

def check_all_achievements(achievements_list, stats):
    """Wrapper dla check_achievements z nowego modułu"""
    return achievements.check_achievements(stats['total_donuts'])

def get_achievement_count(achievements_list):
    """Wrapper dla get_unlocked_count z nowego modułu"""
    unlocked = achievements.get_unlocked_count()
    total = len(achievements.ACHIEVEMENTS)
    return unlocked, total

def save_achievements_wrapper(achievements_list):
    """Wrapper dla save_achievements z nowego modułu"""
    return achievements.save_achievements()

def load_achievements_from_save(achievements_list):
    """Wczytuje stan osiągnięć z pliku zapisu (compat wrapper)."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                achievement_data = data.get('achievements', {})
                if achievement_data:
                    achievements.load_achievements(achievement_data)
                    print(f"Loaded {len(achievement_data)} achievements")
        except Exception as e:
            print(f"Could not load achievements: {e}")

def get_sorted_achievements(achievements_list):
    """Zwraca posortowaną listę osiągnięć"""
    return sorted(achievements.ACHIEVEMENTS, key=lambda a: (not a.unlocked, a.requirement))

load_game()

# Osiągnięcia są już zainicjalizowane w module achievements jako ACHIEVEMENTS
# Wczytaj stan osiągnięć z zapisu (jeśli był)
if 'achievements' in globals():
    for achievement in achievements.ACHIEVEMENTS:
        # Stan zostanie wczytany przez load_game()
        pass

try:
    font_pixel = pygame.font.Font("PressStart2P-Regular.ttf", 80)
    font_button = pygame.font.Font("PressStart2P-Regular.ttf", 30)
    font_tab = pygame.font.Font("PressStart2P-Regular.ttf", 20)
    font_upgrade_name = pygame.font.Font("PressStart2P-Regular.ttf", 24)
    font_upgrade_desc = pygame.font.Font("PressStart2P-Regular.ttf", 16)
    font_code = pygame.font.Font("PressStart2P-Regular.ttf", 36)
    font_dps = pygame.font.Font("PressStart2P-Regular.ttf", 28)
    font_stats = pygame.font.Font("PressStart2P-Regular.ttf", 20)
except:
    font_pixel = pygame.font.Font(None, 150)
    font_button = pygame.font.Font(None, 60)
    font_tab = pygame.font.Font(None, 32)
    font_upgrade_name = pygame.font.Font(None, 36)
    font_upgrade_desc = pygame.font.Font(None, 24)
    font_code = pygame.font.Font(None, 48)
    font_dps = pygame.font.Font(None, 40)
    font_stats = pygame.font.Font(None, 32)

# ============================================
# ŚCIEŻKA DO TEKSTURY PĄCZKA
# ============================================
donut_image_path = "donut.png"

# ============================================
# ŚCIEŻKA DO DŹWIĘKU KLIKNIĘCIA W PĄCZKA
# Format: .wav, .ogg, lub .mp3
# Przykład: click_sound_path = "click.wav"
# ============================================
click_sound_path = None  # TUTAJ: Ustaw ścieżkę do pliku dźwiękowego

# ============================================
# ŚCIEŻKA DO MUZYKI W TLE
# Format: .mp3, .ogg, .wav
# Przykład: background_music_path = "music.mp3"
# ============================================
background_music_path = None  # TUTAJ: Ustaw ścieżkę do pliku muzyki

# Słownik ustawień dźwięku - używamy dict aby uniknąć global w pętli
sound_settings = {
    'enabled': True,    # Włącz/wyłącz dźwięk kliknięcia
    'volume': 0.5,      # Głośność (0.0 - cicho, 1.0 - głośno)
    'dragging': False,  # Czy aktualnie przeciągamy suwak
    'bar_x': 0,         # Pozycja X paska (wypełniana podczas rysowania)
    'bar_w': 0          # Szerokość paska (wypełniana podczas rysowania)
}

# Ustawienia muzyki w tle
music_settings = {
    'enabled': True,     # Włącz/wyłącz muzykę w tle
    'volume': 0.3,       # Głośność muzyki (0.0 - cicho, 1.0 - głośno)
    'dragging': False,   # Czy aktualnie przeciągamy suwak muzyki
    'bar_x': 0,          # Pozycja X paska muzyki
    'bar_w': 0           # Szerokość paska muzyki
}

# ============================================
# ============================================
# ŚCIEŻKA DO TEKSTURY USTAWIEŃ (50x50px)
# ============================================
settings_icon_path = None

# ============================================
# ŚCIEŻKI DO IKON ZAKŁADEK MENU (64x64px)
# Zakładki: Upgrades, Achievements, Statistics, Inventory
# Wyświetlane: 64x64px (bez skalowania, 1:1)
# ============================================
tab_upgrades_icon_path = None     # Ikona zakładki Upgrades
tab_achievements_icon_path = None # Ikona zakładki Achievements  
tab_statistics_icon_path = None   # Ikona zakładki Statistics
tab_inventory_icon_path = None    # Ikona zakładki Inventory (ekwipunek)

try:
    donut_image = pygame.image.load(donut_image_path)
    donut_image = pygame.transform.scale(donut_image, (680, 510))
    mask_surface = pygame.Surface((680, 510), pygame.SRCALPHA)
    center_x = 680 // 2
    center_y = 510 // 2
    radius = min(center_x, center_y)
    pygame.draw.ellipse(mask_surface, (255, 255, 255, 255), (0, 0, 680, 510))
    hole_radius = 30
    pygame.draw.ellipse(mask_surface, (0, 0, 0, 0), (center_x - hole_radius, center_y - hole_radius, hole_radius * 2, hole_radius * 2))
    donut_image_temp = donut_image.copy()
    donut_image_temp.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    donut_image = donut_image_temp
except:
    donut_image = pygame.Surface((680, 510), pygame.SRCALPHA)
    donut_image.fill((0, 0, 0, 0))
    pygame.draw.ellipse(donut_image, BLACK, (0, 0, 680, 510))
    center_x = 680 // 2
    center_y = 510 // 2
    hole_radius = 30
    pygame.draw.ellipse(donut_image, PINK_BG, (center_x - hole_radius, center_y - hole_radius, hole_radius * 2, hole_radius * 2))

donut_rect = donut_image.get_rect()
donut_rect.center = (WIDTH // 2, HEIGHT // 2 + 50)
DONUT_RADIUS = 255

def load_upgrade_icon(path):
    if path is None:
        return None
    try:
        icon = pygame.image.load(path)
        icon = pygame.transform.scale(icon, (100, 100))
        return icon
    except:
        return None

def load_tab_icon(path):
    """Ładuje ikony zakładek menu - 64x64px bez skalowania"""
    if path is None:
        return None
    try:
        icon = pygame.image.load(path)
        # Skaluj do 64x64 jeśli rozmiar się różni
        if icon.get_size() != (64, 64):
            icon = pygame.transform.scale(icon, (64, 64))
        return icon
    except:
        return None

settings_icon = load_upgrade_icon(settings_icon_path)

# Załaduj tekstury budynków i ulepszeń z modułu upgrades
upgrade_textures = upgrades.load_textures(load_upgrade_icon)

# Załaduj tekstury osiągnięć z modułu achievements
achievement_textures = achievements.load_textures(load_upgrade_icon)

# Extract individual icons from upgrade_textures for easier access
eater_icon = upgrade_textures.get('eater')
eater_premium_icon = upgrade_textures.get('eater_premium')
donut_house_icon = upgrade_textures.get('donut_house')
donut_eating_hall_icon = upgrade_textures.get('donut_eating_hall')
donut_co_icon = upgrade_textures.get('donut_co')
eating_power_icon = upgrade_textures.get('eating_power')
store_icon = upgrade_textures.get('store')
gastro_pill_icon = upgrade_textures.get('gastro_pill')

# Ikony zakładek menu (64x64px)
tab_upgrades_icon = load_tab_icon(tab_upgrades_icon_path)
tab_achievements_icon = load_tab_icon(tab_achievements_icon_path)
tab_statistics_icon = load_tab_icon(tab_statistics_icon_path)
tab_inventory_icon = load_tab_icon(tab_inventory_icon_path)

# ============================================
# ŁADOWANIE DŹWIĘKU KLIKNIĘCIA
# ============================================
# TUTAJ: Ładowanie pliku dźwiękowego
try:
    if click_sound_path is not None:
        click_sound = pygame.mixer.Sound(click_sound_path)
        click_sound.set_volume(sound_settings['volume'])
        print(f"Click sound loaded: {click_sound_path}")
    else:
        click_sound = None
        print("No click sound - click_sound_path is None")
except Exception as e:
    click_sound = None
    print(f"Could not load click sound: {e}")

# ============================================
# ŁADOWANIE MUZYKI W TLE
# ============================================
# TUTAJ: Ładowanie pliku muzyki
try:
    if background_music_path is not None:
        pygame.mixer.music.load(background_music_path)
        pygame.mixer.music.set_volume(music_settings['volume'])
        pygame.mixer.music.play(-1)  # -1 = zapętlenie w nieskończoność
        print(f"Background music loaded: {background_music_path}")
    else:
        print("No background music - background_music_path is None")
except Exception as e:
    print(f"Could not load background music: {e}")

MENU_WIDTH = 800
MENU_HEIGHT = HEIGHT
menu_x = WIDTH
menu_target_x = WIDTH
menu_open = False
active_tab = 0
upgrade_subtab = 0

settings_x = -800
settings_target_x = -800
settings_window_open = False
settings_close_rect = None
settings_code_button_rect = None
settings_checkbox_rect = None  # Checkbox dźwięku kliknięcia
settings_vol_minus_rect = None
settings_vol_plus_rect = None
settings_vol_bar_rect = None
settings_music_minus_rect = None
settings_music_plus_rect = None
settings_music_bar_rect = None
settings_music_checkbox_rect = None  # Checkbox muzyki w tle

button_size = 80
button_x = WIDTH - button_size - 30
button_y = HEIGHT - button_size - 30
button_rect = pygame.Rect(button_x, button_y, button_size, button_size)

exit_button_size = 70
exit_button_x = WIDTH - exit_button_size - 30
exit_button_y = 30
exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, exit_button_size, exit_button_size)

settings_button_size = 70
settings_button_x = 30
settings_button_y = HEIGHT - settings_button_size - 30
settings_button_rect = pygame.Rect(settings_button_x, settings_button_y, settings_button_size, settings_button_size)

code_input_active = False
code_verified = False
amount_input_text = ""
code_input_text = ""

store_button_size = 70
store_button_x = 30
store_button_y = 30
store_button_rect = pygame.Rect(store_button_x, store_button_y, store_button_size, store_button_size)
store_window_open = False

class FloatingDonut:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(30, 80)
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
    
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        if self.y > HEIGHT + self.size:
            self.y = -self.size
            self.x = random.randint(0, WIDTH)
    
    def draw(self):
        width = self.size
        height = int(self.size * 510 / 680)
        scaled_donut = pygame.transform.scale(donut_image, (width, height))
        rotated_donut = pygame.transform.rotate(scaled_donut, self.rotation)
        rect = rotated_donut.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_donut, rect)

floating_donuts = [FloatingDonut() for _ in range(15)]

def draw_exit_button(x, y, size, hover=False):
    RED = (220, 50, 50)
    RED_DARK = (180, 30, 30)
    RED_LIGHT = (255, 100, 100)
    color = RED_LIGHT if hover else RED
    pygame.draw.rect(screen, color, (x, y, size, size))
    pygame.draw.rect(screen, RED_DARK, (x, y, size, size), 6)
    pygame.draw.line(screen, RED_LIGHT, (x + 6, y + 6), (x + size - 6, y + 6), 6)
    pygame.draw.line(screen, RED_LIGHT, (x + 6, y + 6), (x + 6, y + size - 6), 6)
    x_text = font_button.render("X", True, WHITE)
    x_rect = x_text.get_rect(center=(x + size // 2, y + size // 2))
    screen.blit(x_text, x_rect)

def draw_settings_button(x, y, size, hover=False):
    GRAY = (120, 120, 120)
    GRAY_DARK = (80, 80, 80)
    GRAY_LIGHT = (160, 160, 160)
    color = GRAY_LIGHT if hover else GRAY
    pygame.draw.rect(screen, color, (x, y, size, size))
    pygame.draw.rect(screen, GRAY_DARK, (x, y, size, size), 6)
    pygame.draw.line(screen, GRAY_LIGHT, (x + 6, y + 6), (x + size - 6, y + 6), 6)
    pygame.draw.line(screen, GRAY_LIGHT, (x + 6, y + 6), (x + 6, y + size - 6), 6)
    
    icon_size = 50
    icon_x = x + (size - icon_size) // 2
    icon_y = y + (size - icon_size) // 2
    
    if settings_icon:
        scaled_icon = pygame.transform.scale(settings_icon, (icon_size, icon_size))
        screen.blit(scaled_icon, (icon_x, icon_y))
    else:
        pygame.draw.circle(screen, WHITE, (x + size // 2, y + size // 2), 18, 3)
        for i in range(8):
            angle = i * 45
            rad = math.radians(angle)
            x1 = x + size // 2 + int(math.cos(rad) * 12)
            y1 = y + size // 2 + int(math.sin(rad) * 12)
            x2 = x + size // 2 + int(math.cos(rad) * 22)
            y2 = y + size // 2 + int(math.sin(rad) * 22)
            pygame.draw.line(screen, WHITE, (x1, y1), (x2, y2), 3)
        pygame.draw.circle(screen, GRAY, (x + size // 2, y + size // 2), 8)
        pygame.draw.circle(screen, WHITE, (x + size // 2, y + size // 2), 8, 2)

def draw_store_button(x, y, size, hover=False):
    GREEN = (50, 180, 100)
    GREEN_DARK = (30, 130, 70)
    GREEN_LIGHT = (100, 220, 150)
    color = GREEN_LIGHT if hover else GREEN
    pygame.draw.rect(screen, color, (x, y, size, size))
    pygame.draw.rect(screen, GREEN_DARK, (x, y, size, size), 6)
    pygame.draw.line(screen, GREEN_LIGHT, (x + 6, y + 6), (x + size - 6, y + 6), 6)
    pygame.draw.line(screen, GREEN_LIGHT, (x + 6, y + 6), (x + 6, y + size - 6), 6)
    
    icon_size = 50
    icon_x = x + (size - icon_size) // 2
    icon_y = y + (size - icon_size) // 2
    
    if store_icon:
        scaled_icon = pygame.transform.scale(store_icon, (icon_size, icon_size))
        screen.blit(scaled_icon, (icon_x, icon_y))
    else:
        pygame.draw.rect(screen, WHITE, (icon_x, icon_y, icon_size, icon_size))
        pygame.draw.rect(screen, GREEN_DARK, (icon_x, icon_y, icon_size, icon_size), 3)

def draw_button(x, y, size, hover=False):
    color = BROWN_LIGHT if hover else BROWN
    pygame.draw.rect(screen, color, (x, y, size, size))
    pygame.draw.rect(screen, BROWN_DARK, (x, y, size, size), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (x + 6, y + 6), (x + size - 6, y + 6), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (x + 6, y + 6), (x + 6, y + size - 6), 6)
    line_width = size - 30
    line_height = 7
    spacing = 16
    start_x = x + 15
    start_y = y + 18
    for i in range(3):
        pygame.draw.rect(screen, WHITE, (start_x, start_y + i * spacing, line_width, line_height))

def draw_code_input():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    box_width = 600
    box_height = 200
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2
    pygame.draw.rect(screen, BROWN, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 6)
    title_text = font_code.render("Enter Code:", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, box_y + 40))
    screen.blit(title_text, title_rect)
    input_box = pygame.Rect(box_x + 50, box_y + 80, box_width - 100, 50)
    pygame.draw.rect(screen, (200, 200, 200), input_box)
    pygame.draw.rect(screen, BLACK, input_box, 4)
    input_surface = font_code.render(code_input_text, True, BLACK)
    screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))
    hint_text = font_upgrade_desc.render("Press ENTER to submit, ESC to cancel", True, WHITE)
    hint_rect = hint_text.get_rect(center=(WIDTH // 2, box_y + 160))
    screen.blit(hint_text, hint_rect)

def draw_amount_input():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    box_width = 800
    box_height = 200
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2
    pygame.draw.rect(screen, BROWN, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 6)
    title_text = font_code.render("Enter Donut Amount:", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, box_y + 40))
    screen.blit(title_text, title_rect)
    input_box = pygame.Rect(box_x + 50, box_y + 80, box_width - 100, 50)
    pygame.draw.rect(screen, (200, 200, 200), input_box)
    pygame.draw.rect(screen, BLACK, input_box, 4)
    input_surface = font_code.render(amount_input_text, True, BLACK)
    screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))
    hint_text = font_upgrade_desc.render("Press ENTER to set, ESC to cancel", True, WHITE)
    hint_rect = hint_text.get_rect(center=(WIDTH // 2, box_y + 160))
    screen.blit(hint_text, hint_rect)

def draw_store_window():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    box_width = 600
    box_height = HEIGHT
    box_x = WIDTH // 2 - box_width // 2
    box_y = 0
    
    pygame.draw.rect(screen, BROWN, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 6)
    
    title_text = font_pixel.render("STORE", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
    screen.blit(title_text, title_rect)
    
    hint_text = font_upgrade_desc.render("Press ESC to close", True, WHITE)
    hint_rect = hint_text.get_rect(center=(WIDTH // 2, box_height - 40))
    screen.blit(hint_text, hint_rect)

def draw_achievement_notification(achievement, timer):
    """Rysuje powiadomienie o nowym osiągnięciu (wyjeżdża z góry)"""
    # Animacja wjazdu/wyjazdu
    notification_height = 150
    max_time = ACHIEVEMENT_NOTIFICATION_DURATION
    
    # Oblicz pozycję Y (animacja)
    if timer < 1000:  # Pierwsze 1s - wjazd
        progress = timer / 1000
        y_pos = -notification_height + (progress * notification_height)
    elif timer > max_time - 1000:  # Ostatnia 1s - wyjazd
        progress = (max_time - timer) / 1000
        y_pos = progress * notification_height - notification_height
    else:  # Środek - stoi na miejscu
        y_pos = 0
    
    # Rysuj box
    box_width = 600
    box_height = 150
    box_x = WIDTH // 2 - box_width // 2
    box_y = int(y_pos)
    
    # Tło boxa
    pygame.draw.rect(screen, BROWN, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (box_x + 6, box_y + 6), (box_x + box_width - 6, box_y + 6), 6)
    
    # Ikona osiągnięcia
    icon_size = 100
    icon_x = box_x + 25
    icon_y = box_y + 25
    
    # Rysuj złoty placeholder (lub załaduj ikonę jeśli dostępna)
    pygame.draw.rect(screen, (255, 215, 0), (icon_x, icon_y, icon_size, icon_size))
    pygame.draw.rect(screen, BLACK, (icon_x, icon_y, icon_size, icon_size), 3)
    
    # Tekst
    text_x = icon_x + icon_size + 20
    
    unlock_text = font_upgrade_desc.render("ACHIEVEMENT UNLOCKED!", True, (255, 215, 0))
    screen.blit(unlock_text, (text_x, box_y + 20))
    
    name_text = font_upgrade_name.render(achievement.name, True, WHITE)
    screen.blit(name_text, (text_x, box_y + 50))
    
    desc_text = font_upgrade_desc.render(achievement.description, True, WHITE)
    screen.blit(desc_text, (text_x, box_y + 80))
    
    hint_text = font_upgrade_desc.render("Click to view achievements", True, (200, 200, 200))
    screen.blit(hint_text, (text_x, box_y + 110))
    
    # Zwróć rect do kliknięcia
    return pygame.Rect(box_x, box_y, box_width, box_height)

def draw_achievement_detail_window(achievement):
    """Rysuje okno ze szczegółami osiągnięcia po kliknięciu"""
    # Tło (overlay)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Okno - poszerzone
    box_width = 1000
    box_height = 500
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2
    
    pygame.draw.rect(screen, BROWN, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (box_x + 6, box_y + 6), (box_x + box_width - 6, box_y + 6), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (box_x + 6, box_y + 6), (box_x + 6, box_y + box_height - 6), 6)
    pygame.draw.line(screen, BROWN_DARK, (box_x + 6, box_y + box_height - 10), (box_x + box_width - 6, box_y + box_height - 10), 6)
    pygame.draw.line(screen, BROWN_DARK, (box_x + box_width - 10, box_y + 6), (box_x + box_width - 10, box_y + box_height - 6), 6)
    
    # Ikona po lewej stronie
    icon_size = 150
    icon_x = box_x + 50
    icon_y = box_y + (box_height - icon_size) // 2
    
    if achievement.unlocked:
        pygame.draw.rect(screen, (255, 215, 0), (icon_x, icon_y, icon_size, icon_size))
    else:
        pygame.draw.rect(screen, (100, 100, 100), (icon_x, icon_y, icon_size, icon_size))
        question_mark = font_pixel.render("?", True, WHITE)
        q_rect = question_mark.get_rect(center=(icon_x + icon_size // 2, icon_y + icon_size // 2))
        screen.blit(question_mark, q_rect)
    pygame.draw.rect(screen, BLACK, (icon_x, icon_y, icon_size, icon_size), 4)
    
    # Linia pionowa oddzielająca ikonę od tekstu
    divider_x = icon_x + icon_size + 40
    pygame.draw.line(screen, BROWN_DARK, (divider_x, box_y + 30), (divider_x, box_y + box_height - 30), 3)
    
    # Prawa strona - teksty
    text_x = divider_x + 40
    text_center_x = text_x + (box_x + box_width - 30 - text_x) // 2
    
    # Nazwa osiągnięcia
    name_y = box_y + 60
    name_text = font_upgrade_name.render(achievement.name, True, WHITE)
    name_rect = name_text.get_rect(centerx=text_center_x, y=name_y)
    screen.blit(name_text, name_rect)
    
    # Linia pod nazwą
    pygame.draw.line(screen, BROWN_LIGHT, (text_x, name_y + 45), (box_x + box_width - 30, name_y + 45), 2)
    
    # Status (Unlocked / Locked)
    status_y = name_y + 65
    if achievement.unlocked:
        status_text = font_upgrade_desc.render("★  UNLOCKED  ★", True, (255, 215, 0))
    else:
        status_text = font_upgrade_desc.render("✖  LOCKED  ✖", True, (180, 80, 80))
    status_rect = status_text.get_rect(centerx=text_center_x, y=status_y)
    screen.blit(status_text, status_rect)
    
    # Wymaganie (np. "Earn 100 total donuts")
    req_y = status_y + 35
    req_text = font_upgrade_desc.render(f"Requirement: {achievement.description}", True, (200, 200, 200))
    req_rect = req_text.get_rect(centerx=text_center_x, y=req_y)
    screen.blit(req_text, req_rect)
    
    # Linia przed opisem
    pygame.draw.line(screen, BROWN_LIGHT, (text_x, req_y + 30), (box_x + box_width - 30, req_y + 30), 2)
    
    # Opis z pliku JSON
    achievement_data = achievement_descriptions.get(achievement.id, {})
    description_lines = achievement_data.get('description', [])
    while description_lines and description_lines[-1] == "":
        description_lines.pop()
    
    desc_y = req_y + 50
    line_height = 30
    
    if not description_lines:
        no_desc = font_upgrade_desc.render("Brak opisu.", True, (150, 150, 150))
        no_desc_rect = no_desc.get_rect(centerx=text_center_x, y=desc_y)
        screen.blit(no_desc, no_desc_rect)
    else:
        for i, line in enumerate(description_lines):
            if line:
                line_text = font_upgrade_desc.render(line, True, WHITE)
                line_rect = line_text.get_rect(centerx=text_center_x, y=desc_y + i * line_height)
                screen.blit(line_text, line_rect)
    
    # Przycisk Close (prawy dolny róg okna)
    close_button_width = 220
    close_button_height = 60
    close_button_x = box_x + box_width - close_button_width - 30
    close_button_y = box_y + box_height - close_button_height - 20
    close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_width, close_button_height)
    
    close_hover = close_button_rect.collidepoint(pygame.mouse.get_pos())
    button_color = BROWN_LIGHT if close_hover else BROWN_DARK
    
    pygame.draw.rect(screen, button_color, close_button_rect)
    pygame.draw.rect(screen, BLACK, close_button_rect, 6)
    pygame.draw.line(screen, BROWN_LIGHT, (close_button_x + 6, close_button_y + 6), (close_button_x + close_button_width - 6, close_button_y + 6), 6)
    
    close_text = font_button.render("Close", True, WHITE)
    close_text_rect = close_text.get_rect(center=close_button_rect.center)
    screen.blit(close_text, close_text_rect)
    
    # Hint (lewy dolny róg okna)
    hint_text = font_upgrade_desc.render("ESC to close", True, (150, 150, 150))
    hint_rect = hint_text.get_rect(left=box_x + 30, centery=close_button_rect.centery)
    screen.blit(hint_text, hint_rect)
    
    return close_button_rect

def draw_idle_window():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    box_width = 800  # Było 700
    box_height = 400
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2
    
    pygame.draw.rect(screen, BROWN, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 6)
    
    # Formatuj czas nieobecności
    hours = idle_time_seconds // 3600
    minutes = (idle_time_seconds % 3600) // 60
    seconds = idle_time_seconds % 60
    
    if hours > 0:
        time_str = f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        time_str = f"{minutes}m {seconds}s"
    else:
        time_str = f"{seconds}s"
    
    # Tekst "You have been idle for:"
    idle_text = font_button.render("You have been idle for:", True, WHITE)
    idle_rect = idle_text.get_rect(center=(WIDTH // 2, box_y + 80))
    screen.blit(idle_text, idle_rect)
    
    # Czas nieobecności
    time_text = font_pixel.render(time_str, True, LIGHT_YELLOW)
    time_rect = time_text.get_rect(center=(WIDTH // 2, box_y + 160))
    screen.blit(time_text, time_rect)
    
    # Ilość otrzymanych pączków
    donuts_text = font_button.render(f"You earned {format_number(idle_donuts)} donuts!", True, WHITE)
    donuts_rect = donuts_text.get_rect(center=(WIDTH // 2, box_y + 240))
    screen.blit(donuts_text, donuts_rect)
    
    # Przycisk OK
    button_width = 200
    button_height = 60
    button_x = WIDTH // 2 - button_width // 2
    button_y = box_y + box_height - 100
    ok_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    ok_hover = ok_button_rect.collidepoint(pygame.mouse.get_pos())
    button_color = BROWN_LIGHT if ok_hover else BROWN
    
    pygame.draw.rect(screen, button_color, ok_button_rect)
    pygame.draw.rect(screen, BLACK, ok_button_rect, 6)
    pygame.draw.line(screen, BROWN_LIGHTER, (button_x + 6, button_y + 6), (button_x + button_width - 6, button_y + 6), 6)
    pygame.draw.line(screen, BROWN_LIGHTER, (button_x + 6, button_y + 6), (button_x + 6, button_y + button_height - 6), 6)
    
    ok_text = font_button.render("OK", True, WHITE)
    ok_text_rect = ok_text.get_rect(center=(WIDTH // 2, button_y + button_height // 2))
    screen.blit(ok_text, ok_text_rect)
    
    return ok_button_rect

def draw_settings_window(x):
    settings_width = 800
    settings_height = HEIGHT
    
    pygame.draw.rect(screen, BROWN, (x, 0, settings_width, settings_height))
    pygame.draw.rect(screen, BROWN_DARK, (x, 0, settings_width, settings_height), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (x + 6, 6), (x + settings_width - 6, 6), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (x + 6, 6), (x + 6, settings_height - 6), 6)
    pygame.draw.line(screen, BROWN_DARK, (x + 6, settings_height - 10), (x + settings_width - 6, settings_height - 10), 6)
    pygame.draw.line(screen, BROWN_DARK, (x + settings_width - 10, 6), (x + settings_width - 10, settings_height - 6), 6)
    
    # Przycisk zamknięcia
    close_size = 50
    close_x = x + settings_width - close_size - 20
    close_y = 20
    close_rect = pygame.Rect(close_x, close_y, close_size, close_size)
    close_hover = close_rect.collidepoint(pygame.mouse.get_pos())
    color = BROWN_LIGHT if close_hover else BROWN_DARK
    pygame.draw.rect(screen, color, close_rect)
    pygame.draw.rect(screen, BLACK, close_rect, 6)
    line_thickness = 7
    margin = 10
    pygame.draw.line(screen, WHITE, (close_x + margin, close_y + margin), (close_x + close_size - margin, close_y + close_size - margin), line_thickness)
    pygame.draw.line(screen, WHITE, (close_x + close_size - margin, close_y + margin), (close_x + margin, close_y + close_size - margin), line_thickness)
    
    # Tytuł
    title_text = font_pixel.render("Settings", True, WHITE)
    title_rect = title_text.get_rect(center=(x + settings_width // 2, 100))
    screen.blit(title_text, title_rect)
    
    # --- PRZYCISK ENTER CODE ---
    code_button_width = settings_width - 80
    code_button_height = 80
    code_button_x = x + 40
    code_button_y = 200
    code_button_rect_settings = pygame.Rect(code_button_x, code_button_y, code_button_width, code_button_height)
    code_hover = code_button_rect_settings.collidepoint(pygame.mouse.get_pos())
    BLUE = (50, 100, 220)
    BLUE_DARK = (30, 60, 180)
    BLUE_LIGHT = (100, 150, 255)
    code_color = BLUE_LIGHT if code_hover else BLUE
    pygame.draw.rect(screen, code_color, code_button_rect_settings)
    pygame.draw.rect(screen, BLUE_DARK, code_button_rect_settings, 6)
    pygame.draw.line(screen, BLUE_LIGHT, (code_button_x + 6, code_button_y + 6), (code_button_x + code_button_width - 6, code_button_y + 6), 6)
    pygame.draw.line(screen, BLUE_LIGHT, (code_button_x + 6, code_button_y + 6), (code_button_x + 6, code_button_y + code_button_height - 6), 6)
    code_text = font_button.render("Enter Code", True, WHITE)
    code_text_rect = code_text.get_rect(center=(code_button_x + code_button_width // 2, code_button_y + code_button_height // 2))
    screen.blit(code_text, code_text_rect)
    
    # --- CHECKBOX DŹWIĘKU KLIKNIĘCIA ---
    checkbox_size = 20
    checkbox_x = x + 40
    checkbox_y = 320
    
    # Box 20x20 - ciemniejszy brąz
    checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
    checkbox_color = (80, 50, 30)  # Ciemniejszy od tła
    pygame.draw.rect(screen, checkbox_color, checkbox_rect)
    pygame.draw.rect(screen, BLACK, checkbox_rect, 2)
    
    # X z czcionki jeśli włączony
    if sound_settings['enabled']:
        x_text = font_upgrade_name.render("X", True, WHITE)
        x_rect = x_text.get_rect(center=checkbox_rect.center)
        screen.blit(x_text, x_rect)
    
    # Opis obok checkboxa
    label_x = checkbox_x + checkbox_size + 10
    label_text = font_upgrade_name.render("Click Sound", True, WHITE)
    screen.blit(label_text, (label_x, checkbox_y - 3))
    
    # --- PASEK GŁOŚNOŚCI ---
    vol_label_y = 400
    vol_label = font_upgrade_name.render("Volume:", True, WHITE)
    screen.blit(vol_label, (x + 40, vol_label_y))
    
    # Procent głośności po prawej
    vol_pct_text = font_upgrade_name.render(f"{int(sound_settings['volume'] * 100)}%", True, WHITE)
    vol_pct_rect = vol_pct_text.get_rect(right=x + settings_width - 40, y=vol_label_y)
    screen.blit(vol_pct_text, vol_pct_rect)
    
    # Przycisk -
    vol_btn_size = 60
    vol_minus_x = x + 40
    vol_bar_y = 490
    vol_minus_rect = pygame.Rect(vol_minus_x, vol_bar_y, vol_btn_size, vol_btn_size)
    minus_hover = vol_minus_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, BROWN_LIGHT if minus_hover else BROWN_DARK, vol_minus_rect)
    pygame.draw.rect(screen, BLACK, vol_minus_rect, 5)
    minus_text = font_pixel.render("-", True, WHITE)
    minus_text = pygame.transform.scale(minus_text, (int(minus_text.get_width() * scale_minus_factor), int(minus_text.get_height() * scale_minus_factor)))
    minus_rect = minus_text.get_rect(center=vol_minus_rect.center)
    screen.blit(minus_text, minus_rect)
    
    # Przycisk +
    vol_plus_x = x + settings_width - 40 - vol_btn_size
    vol_plus_rect = pygame.Rect(vol_plus_x, vol_bar_y, vol_btn_size, vol_btn_size)
    plus_hover = vol_plus_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, BROWN_LIGHT if plus_hover else BROWN_DARK, vol_plus_rect)
    pygame.draw.rect(screen, BLACK, vol_plus_rect, 5)
    plus_text = font_pixel.render("+", True, WHITE)
    plus_text = pygame.transform.scale(plus_text, (int(plus_text.get_width() * scale_plus_factor), int(plus_text.get_height() * scale_plus_factor)))
    plus_rect = plus_text.get_rect(center=vol_plus_rect.center)
    screen.blit(plus_text, plus_rect)
    
    # Pasek suwaka (między - i +)
    bar_margin = 15
    bar_x = vol_minus_x + vol_btn_size + bar_margin
    bar_w = vol_plus_x - bar_x - bar_margin
    bar_h = 20
    bar_y = vol_bar_y + (vol_btn_size - bar_h) // 2
    
    # Tło paska (szare)
    pygame.draw.rect(screen, (80, 50, 30), (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_w, bar_h), 3)
    
    # Wypełnienie paska (złote, proporcjonalne do głośności)
    fill_w = int(bar_w * sound_settings['volume'])
    if fill_w > 0:
        pygame.draw.rect(screen, (255, 200, 0), (bar_x, bar_y, fill_w, bar_h))
    
    # Uchwyt suwaka (kółko)
    handle_x = bar_x + fill_w
    handle_y = bar_y + bar_h // 2
    pygame.draw.circle(screen, WHITE, (handle_x, handle_y), 14)
    pygame.draw.circle(screen, BLACK, (handle_x, handle_y), 14, 3)
    
    # Klikalny obszar paska (do przeciągania)
    vol_bar_rect = pygame.Rect(bar_x, bar_y - 15, bar_w, bar_h + 30)
    
    # Przekazujemy pozycję paska do sound_settings (by obsługa zdarzeń mogła z niej korzystać)
    sound_settings['bar_x'] = bar_x
    sound_settings['bar_w'] = bar_w
    
    # --- SEKCJA MUZYKI W TLE ---
    music_label_y = 600
    music_label = font_upgrade_name.render("Background Music:", True, WHITE)
    screen.blit(music_label, (x + 40, music_label_y))
    
    # Procent głośności muzyki
    music_pct_text = font_upgrade_name.render(f"{int(music_settings['volume'] * 100)}%", True, WHITE)
    music_pct_rect = music_pct_text.get_rect(right=x + settings_width - 40, y=music_label_y)
    screen.blit(music_pct_text, music_pct_rect)
    
    # Przycisk − (minus) dla muzyki
    music_minus_x = x + 40
    music_bar_y = 670
    music_minus_rect = pygame.Rect(music_minus_x, music_bar_y, vol_btn_size, vol_btn_size)
    music_minus_hover = music_minus_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, BROWN_LIGHT if music_minus_hover else BROWN_DARK, music_minus_rect)
    pygame.draw.rect(screen, BLACK, music_minus_rect, 5)
    music_minus_text = font_pixel.render("-", True, WHITE)
    music_minus_text = pygame.transform.scale(music_minus_text, (int(music_minus_text.get_width() * scale_minus_factor), int(music_minus_text.get_height() * scale_minus_factor)))
    music_minus_rect_center = music_minus_text.get_rect(center=music_minus_rect.center)
    screen.blit(music_minus_text, music_minus_rect_center)
    
    # Przycisk + dla muzyki
    music_plus_x = x + settings_width - 40 - vol_btn_size
    music_plus_rect = pygame.Rect(music_plus_x, music_bar_y, vol_btn_size, vol_btn_size)
    music_plus_hover = music_plus_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, BROWN_LIGHT if music_plus_hover else BROWN_DARK, music_plus_rect)
    pygame.draw.rect(screen, BLACK, music_plus_rect, 5)
    music_plus_text = font_pixel.render("+", True, WHITE)
    music_plus_text = pygame.transform.scale(music_plus_text, (int(music_plus_text.get_width() * scale_minus_factor), int(music_plus_text.get_height() * scale_minus_factor)))  
    music_plus_rect_center = music_plus_text.get_rect(center=music_plus_rect.center)
    screen.blit(music_plus_text, music_plus_rect_center)
    
    # Pasek muzyki
    music_bar_x = music_minus_x + vol_btn_size + bar_margin
    music_bar_w = music_plus_x - music_bar_x - bar_margin
    music_bar_h = 20
    music_bar_y_center = music_bar_y + (vol_btn_size - music_bar_h) // 2
    
    # Tło paska muzyki
    pygame.draw.rect(screen, (80, 50, 30), (music_bar_x, music_bar_y_center, music_bar_w, music_bar_h))
    pygame.draw.rect(screen, BLACK, (music_bar_x, music_bar_y_center, music_bar_w, music_bar_h), 3)
    
    # Wypełnienie paska muzyki (niebieskie zamiast złotego)
    music_fill_w = int(music_bar_w * music_settings['volume'])
    if music_fill_w > 0:
        pygame.draw.rect(screen, (100, 150, 255), (music_bar_x, music_bar_y_center, music_fill_w, music_bar_h))
    
    # Uchwyt suwaka muzyki
    music_handle_x = music_bar_x + music_fill_w
    music_handle_y = music_bar_y_center + music_bar_h // 2
    pygame.draw.circle(screen, WHITE, (music_handle_x, music_handle_y), 14)
    pygame.draw.circle(screen, BLACK, (music_handle_x, music_handle_y), 14, 3)
    
    # Klikalny obszar paska muzyki
    music_bar_rect = pygame.Rect(music_bar_x, music_bar_y_center - 15, music_bar_w, music_bar_h + 30)
    
    # Przekazujemy pozycję paska muzyki
    music_settings['bar_x'] = music_bar_x
    music_settings['bar_w'] = music_bar_w
    
    # --- CHECKBOX MUZYKI ---
    music_checkbox_size = 20
    music_checkbox_x = x + 40
    music_checkbox_y = 360
    
    # Box 20x20 - ciemniejszy brąz
    music_checkbox_rect = pygame.Rect(music_checkbox_x, music_checkbox_y, music_checkbox_size, music_checkbox_size)
    music_checkbox_color = (80, 50, 30)  # Ciemniejszy od tła
    pygame.draw.rect(screen, music_checkbox_color, music_checkbox_rect)
    pygame.draw.rect(screen, BLACK, music_checkbox_rect, 2)
    
    # X z czcionki jeśli włączony
    if music_settings['enabled']:
        music_x_text = font_upgrade_name.render("X", True, WHITE)
        music_x_rect = music_x_text.get_rect(center=music_checkbox_rect.center)
        screen.blit(music_x_text, music_x_rect)
    
    # Opis obok checkboxa
    music_label_x = music_checkbox_x + music_checkbox_size + 10
    music_label_text = font_upgrade_name.render("Background Music", True, WHITE)
    screen.blit(music_label_text, (music_label_x, music_checkbox_y - 3))
    
    return close_rect, code_button_rect_settings, checkbox_rect, vol_minus_rect, vol_plus_rect, vol_bar_rect, music_minus_rect, music_plus_rect, music_bar_rect, music_checkbox_rect

def check_code(code):
    global points, eater_count, eater_premium_count, donut_house_count, donut_eating_hall_count, donut_co_count, max_donuts, max_dps, time_played, game_start_time, total_donuts_earned, total_time_played, store_unlocked, eating_power_level, idle_donuts, idle_time_seconds, idle_window_open, gastro_pill_unlocked
    if code == "1234":
        print("Code verified!")
        return True
    elif code == "idle":
        # Symuluj 24h nieobecności
        current_dps = get_total_dps()
        idle_time_seconds = 24 * 3600  # 24 godziny w sekundach
        # NOWA FORMUŁA: Za każde 10 minut (600s) = 1 sekunda DPS
        idle_donuts = int((idle_time_seconds / 600) * current_dps)
        if idle_donuts > 0:
            idle_window_open = True
            print(f"Simulated 24h idle: {idle_donuts} donuts")
        else:
            print("Idle simulation: 0 donuts (DPS is 0)")
        return False
    elif code == "reset":
        points = 0
        eater_count = 0
        eater_premium_count = 0
        donut_house_count = 0
        donut_eating_hall_count = 0
        donut_co_count = 0
        max_donuts = 0
        max_dps = 0
        time_played = 0
        total_donuts_earned = 0
        total_time_played = 0
        store_unlocked = False
        eating_power_level = 0
        gastro_pill_unlocked = False
        # Reset osiągnięć
        for achievement in achievements.ACHIEVEMENTS:
            achievement.unlocked = False
            if hasattr(achievement, 'just_unlocked'):
                achievement.just_unlocked = False
        game_start_time = pygame.time.get_ticks()
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        print("Game reset! All progress deleted.")
        return False
    print("Wrong code!")
    return False

def draw_menu(x):
    pygame.draw.rect(screen, BROWN, (x, 0, MENU_WIDTH, MENU_HEIGHT))
    pygame.draw.rect(screen, BROWN_DARK, (x, 0, MENU_WIDTH, MENU_HEIGHT), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (x + 6, 6), (x + MENU_WIDTH - 6, 6), 6)
    pygame.draw.line(screen, BROWN_LIGHT, (x + 6, 6), (x + 6, MENU_HEIGHT - 6), 6)
    pygame.draw.line(screen, BROWN_DARK, (x + 6, MENU_HEIGHT - 10), (x + MENU_WIDTH - 6, MENU_HEIGHT - 10), 6)
    pygame.draw.line(screen, BROWN_DARK, (x + MENU_WIDTH - 10, 6), (x + MENU_WIDTH - 10, MENU_HEIGHT - 6), 6)
    close_size = 50
    close_x = x + 20
    close_y = 20
    close_rect = pygame.Rect(close_x, close_y, close_size, close_size)
    close_hover = close_rect.collidepoint(pygame.mouse.get_pos())
    color = BROWN_LIGHT if close_hover else BROWN_DARK
    pygame.draw.rect(screen, color, close_rect)
    pygame.draw.rect(screen, BLACK, close_rect, 6)
    line_thickness = 7
    margin = 10
    pygame.draw.line(screen, WHITE, (close_x + margin, close_y + margin), (close_x + close_size - margin, close_y + close_size - margin), line_thickness)
    pygame.draw.line(screen, WHITE, (close_x + close_size - margin, close_y + margin), (close_x + margin, close_y + close_size - margin), line_thickness)
    if active_tab == 0:
        upgrade_rects = draw_upgrades_tab(x)
        achievement_rects = []
    elif active_tab == 1:
        achievement_rects = draw_achievements_tab(x)
    elif active_tab == 2:
        draw_statistics_tab(x)
        achievement_rects = []
    elif active_tab == 3:
        # Zakładka Inventory (nowa)
        draw_inventory_tab(x)
        achievement_rects = []
    else:
        achievement_rects = []
    
    # ============================================
    # PASEK ZAKŁADEK - ODDZIELONY NA DOLE
    # ============================================
    # Linia oddzielająca pasek zakładek
    separator_y = MENU_HEIGHT - 110  # 80 (tab_height) + 20 (margin) + 10 (spacing)
    pygame.draw.line(screen, BROWN_DARK, (x + 20, separator_y), (x + MENU_WIDTH - 20, separator_y), 4)
    pygame.draw.line(screen, BROWN_LIGHT, (x + 20, separator_y + 2), (x + MENU_WIDTH - 20, separator_y + 2), 2)
    
    # Parametry zakładek - dostosowane do ikon 64x64
    tab_height = 80  # 64 (ikona) + 8px padding góra/dół
    tab_y = MENU_HEIGHT - tab_height - 10
    tab_width = (MENU_WIDTH - 70) // 4  # 4 zakładki + odstępy
    tab_spacing = 10
    
    # Ikony i nazwy zakładek
    tabs_data = [
        ("Upgrades", tab_upgrades_icon),
        ("Achievements", tab_achievements_icon),
        ("Statistics", tab_statistics_icon),
        ("Inventory", tab_inventory_icon)
    ]
    
    tab_rects = []
    for i, (tab_name, tab_icon) in enumerate(tabs_data):
        tab_x = x + 20 + i * (tab_width + tab_spacing)
        tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
        tab_rects.append(tab_rect)
        
        tab_hover = tab_rect.collidepoint(pygame.mouse.get_pos())
        
        # Kolor zakładki
        if active_tab == i:
            tab_color = BROWN_LIGHT
            border_color = (255, 215, 0)  # Złoty border dla aktywnej
        elif tab_hover:
            tab_color = (160, 110, 70)
            border_color = BROWN_LIGHTER
        else:
            tab_color = BROWN_DARK
            border_color = BLACK
        
        # Rysowanie zakładki
        pygame.draw.rect(screen, tab_color, tab_rect)
        pygame.draw.rect(screen, border_color, tab_rect, 5)
        
        # Podświetlenie aktywnej zakładki
        if active_tab == i:
            pygame.draw.line(screen, BROWN_LIGHTER, (tab_x + 6, tab_y + 6), (tab_x + tab_width - 6, tab_y + 6), 4)
            pygame.draw.line(screen, BROWN_LIGHTER, (tab_x + 6, tab_y + 6), (tab_x + 6, tab_y + tab_height - 6), 4)
        
        # Ikona zakładki (64x64 - standardowy rozmiar dla ikon menu)
        icon_size = 64
        icon_y = tab_y + (tab_height - icon_size) // 2  # Wyśrodkowana w pionie
        
        if tab_icon:
            scaled_icon = pygame.transform.scale(tab_icon, (icon_size, icon_size))
            icon_rect = scaled_icon.get_rect(centerx=tab_rect.centerx, y=icon_y)
            screen.blit(scaled_icon, icon_rect)
        else:
            # Placeholder jeśli brak ikony
            placeholder_rect = pygame.Rect(tab_rect.centerx - icon_size//2, icon_y, icon_size, icon_size)
            pygame.draw.rect(screen, (100, 100, 100), placeholder_rect)
            pygame.draw.rect(screen, BLACK, placeholder_rect, 3)
            # Inicjał zakładki
            initial = font_upgrade_name.render(tab_name[0], True, WHITE)
            initial_rect = initial.get_rect(center=placeholder_rect.center)
            screen.blit(initial, initial_rect)
        
        # Nazwa zakładki pod ikoną - USUNIĘTE (tylko ikony)
        # name_text = font_upgrade_desc.render(tab_name, True, WHITE)
        # name_rect = name_text.get_rect(centerx=tab_rect.centerx, bottom=tab_y + tab_height - 8)
        # screen.blit(name_text, name_rect)
    
    return close_rect, tab_rects, achievement_rects

def draw_upgrades_tab(menu_x):
    global eater_count, eater_premium_count, donut_house_count, donut_eating_hall_count, donut_co_count, points, upgrade_subtab, subtab_rects
    
    # DONUT UPGRADES - budynki i ulepszenia
    upgrade_rects, subtab_rects = draw_donut_upgrades_content(menu_x)
    return upgrade_rects


def draw_donut_upgrades_content(menu_x):
    """Zawartość zakładki Donut Upgrades - budynki i ulepszenia"""
    global upgrade_subtab, subtab_rects
    
    # Podzakładki Buildings / Upgrades
    subtab_height = 60
    subtab_y = 75  # Poniżej zakładek sklepów
    subtab_width = (MENU_WIDTH - 80) // 2
    subtab_spacing = 20
    subtabs = ["Buildings", "Upgrades"]
    subtab_rects = []
    
    for i, subtab_name in enumerate(subtabs):
        subtab_x = menu_x + 30 + i * (subtab_width + subtab_spacing)
        subtab_rect = pygame.Rect(subtab_x, subtab_y, subtab_width, subtab_height)
        subtab_rects.append(subtab_rect)
        subtab_hover = subtab_rect.collidepoint(pygame.mouse.get_pos())
        if upgrade_subtab == i:
            subtab_color = BROWN_LIGHT
        elif subtab_hover:
            subtab_color = (160, 110, 70)
        else:
            subtab_color = BROWN_DARK
        pygame.draw.rect(screen, subtab_color, subtab_rect)
        pygame.draw.rect(screen, BLACK, subtab_rect, 6)
        if upgrade_subtab == i:
            pygame.draw.line(screen, BROWN_LIGHTER, (subtab_x + 6, subtab_y + 6), (subtab_x + subtab_width - 6, subtab_y + 6), 6)
        text = font_tab.render(subtab_name, True, WHITE)
        text_rect = text.get_rect(center=subtab_rect.center)
        screen.blit(text, text_rect)
    
    if upgrade_subtab == 0:
        upgrade_rects = draw_buildings_upgrades(menu_x)
    else:
        upgrade_rects = draw_upgrades_upgrades(menu_x)
    
    return upgrade_rects, subtab_rects

def draw_buildings_upgrades(menu_x):
    global eater_count, eater_premium_count, donut_house_count, donut_eating_hall_count, donut_co_count, points
    upgrade_rects = []
    upgrade_y = 155
    upgrade_height = 120
    upgrade_margin = 20
    upgrade_spacing = 10
    upgrade_width = MENU_WIDTH - 2 * upgrade_margin
    upgrade_x = menu_x + upgrade_margin
    
    upgrade_rect = pygame.Rect(upgrade_x, upgrade_y, upgrade_width, upgrade_height)
    eater_cost = get_eater_cost()
    can_afford = points >= eater_cost and eater_count < EATER_MAX
    hover = upgrade_rect.collidepoint(pygame.mouse.get_pos())
    if eater_count >= EATER_MAX:
        bg_color = (100, 100, 100)
    elif can_afford:
        bg_color = BROWN_LIGHT if hover else (120, 90, 60)
    else:
        bg_color = BROWN_DARK
    pygame.draw.rect(screen, bg_color, upgrade_rect)
    pygame.draw.rect(screen, BLACK, upgrade_rect, 6)
    
    icon_size = 100
    icon_x = upgrade_x + 10
    icon_y = upgrade_y + 10
    if eater_icon:
        screen.blit(eater_icon, (icon_x, icon_y))
    else:
        pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y, icon_size, icon_size))
    pygame.draw.rect(screen, BLACK, (icon_x, icon_y, icon_size, icon_size), 3)
    
    text_x = upgrade_x + 120
    name_text = font_upgrade_name.render("Donut Eater", True, WHITE)
    screen.blit(name_text, (text_x, upgrade_y + 10))
    desc_text = font_upgrade_desc.render(f"+{EATER_DPS} donuts/sec", True, WHITE)
    screen.blit(desc_text, (text_x, upgrade_y + 45))
    count_text = font_upgrade_desc.render(f"Owned: {eater_count}/{EATER_MAX}", True, WHITE)
    screen.blit(count_text, (text_x, upgrade_y + 70))
    if eater_count < EATER_MAX:
        cost_text = font_upgrade_name.render(f"Cost: {format_number(eater_cost)}", True, WHITE if can_afford else (255, 100, 100))
        screen.blit(cost_text, (text_x, upgrade_y + 90))
    else:
        maxed_text = font_upgrade_name.render("MAX", True, (255, 215, 0))
        screen.blit(maxed_text, (text_x, upgrade_y + 90))
    upgrade_rects.append(('eater', upgrade_rect))
    
    upgrade_y2 = upgrade_y + upgrade_height + upgrade_spacing
    upgrade_rect2 = pygame.Rect(upgrade_x, upgrade_y2, upgrade_width, upgrade_height)
    eater_premium_cost = get_eater_premium_cost()
    can_afford2 = points >= eater_premium_cost and eater_premium_count < EATER_PREMIUM_MAX
    hover2 = upgrade_rect2.collidepoint(pygame.mouse.get_pos())
    if eater_premium_count >= EATER_PREMIUM_MAX:
        bg_color2 = (100, 100, 100)
    elif can_afford2:
        bg_color2 = BROWN_LIGHT if hover2 else (120, 90, 60)
    else:
        bg_color2 = BROWN_DARK
    pygame.draw.rect(screen, bg_color2, upgrade_rect2)
    pygame.draw.rect(screen, BLACK, upgrade_rect2, 6)
    
    icon_y2 = upgrade_y2 + 10
    if eater_premium_icon:
        screen.blit(eater_premium_icon, (icon_x, icon_y2))
    else:
        pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y2, icon_size, icon_size))
    pygame.draw.rect(screen, BLACK, (icon_x, icon_y2, icon_size, icon_size), 3)
    
    name_text2 = font_upgrade_name.render("Donut Eater Premium", True, WHITE)
    screen.blit(name_text2, (text_x, upgrade_y2 + 10))
    desc_text2 = font_upgrade_desc.render(f"+{EATER_PREMIUM_DPS} donuts/sec", True, WHITE)
    screen.blit(desc_text2, (text_x, upgrade_y2 + 45))
    count_text2 = font_upgrade_desc.render(f"Owned: {eater_premium_count}/{EATER_PREMIUM_MAX}", True, WHITE)
    screen.blit(count_text2, (text_x, upgrade_y2 + 70))
    if eater_premium_count < EATER_PREMIUM_MAX:
        cost_text2 = font_upgrade_name.render(f"Cost: {format_number(eater_premium_cost)}", True, WHITE if can_afford2 else (255, 100, 100))
        screen.blit(cost_text2, (text_x, upgrade_y2 + 90))
    else:
        maxed_text2 = font_upgrade_name.render("MAX", True, (255, 215, 0))
        screen.blit(maxed_text2, (text_x, upgrade_y2 + 90))
    upgrade_rects.append(('eater_premium', upgrade_rect2))
    
    if max_donuts >= 5000:
        upgrade_y3 = upgrade_y2 + upgrade_height + upgrade_spacing
        upgrade_rect3 = pygame.Rect(upgrade_x, upgrade_y3, upgrade_width, upgrade_height)
        donut_house_cost = get_donut_house_cost()
        can_afford3 = points >= donut_house_cost and donut_house_count < DONUT_HOUSE_MAX
        hover3 = upgrade_rect3.collidepoint(pygame.mouse.get_pos())
        if donut_house_count >= DONUT_HOUSE_MAX:
            bg_color3 = (100, 100, 100)
        elif can_afford3:
            bg_color3 = BROWN_LIGHT if hover3 else (120, 90, 60)
        else:
            bg_color3 = BROWN_DARK
        pygame.draw.rect(screen, bg_color3, upgrade_rect3)
        pygame.draw.rect(screen, BLACK, upgrade_rect3, 6)
        
        icon_y3 = upgrade_y3 + 10
        if donut_house_icon:
            screen.blit(donut_house_icon, (icon_x, icon_y3))
        else:
            pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y3, icon_size, icon_size))
        pygame.draw.rect(screen, BLACK, (icon_x, icon_y3, icon_size, icon_size), 3)
        
        name_text3 = font_upgrade_name.render("Donut House", True, WHITE)
        screen.blit(name_text3, (text_x, upgrade_y3 + 10))
        desc_text3 = font_upgrade_desc.render(f"+{DONUT_HOUSE_DPS} donuts/sec", True, WHITE)
        screen.blit(desc_text3, (text_x, upgrade_y3 + 45))
        count_text3 = font_upgrade_desc.render(f"Owned: {donut_house_count}/{DONUT_HOUSE_MAX}", True, WHITE)
        screen.blit(count_text3, (text_x, upgrade_y3 + 70))
        if donut_house_count < DONUT_HOUSE_MAX:
            cost_text3 = font_upgrade_name.render(f"Cost: {format_number(donut_house_cost)}", True, WHITE if can_afford3 else (255, 100, 100))
            screen.blit(cost_text3, (text_x, upgrade_y3 + 90))
        else:
            maxed_text3 = font_upgrade_name.render("MAX", True, (255, 215, 0))
            screen.blit(maxed_text3, (text_x, upgrade_y3 + 90))
        upgrade_rects.append(('donut_house', upgrade_rect3))
    
    # DONUT EATING HALL - czwarty box
    if max_donuts >= 50000:
        upgrade_y4 = upgrade_y3 + upgrade_height + upgrade_spacing if max_donuts >= 5000 else upgrade_y2 + upgrade_height + upgrade_spacing
        upgrade_rect4 = pygame.Rect(upgrade_x, upgrade_y4, upgrade_width, upgrade_height)
        donut_eating_hall_cost = get_donut_eating_hall_cost()
        can_afford4 = points >= donut_eating_hall_cost and donut_eating_hall_count < DONUT_EATING_HALL_MAX
        hover4 = upgrade_rect4.collidepoint(pygame.mouse.get_pos())
        if donut_eating_hall_count >= DONUT_EATING_HALL_MAX:
            bg_color4 = (100, 100, 100)
        elif can_afford4:
            bg_color4 = BROWN_LIGHT if hover4 else (120, 90, 60)
        else:
            bg_color4 = BROWN_DARK
        pygame.draw.rect(screen, bg_color4, upgrade_rect4)
        pygame.draw.rect(screen, BLACK, upgrade_rect4, 6)
        
        icon_y4 = upgrade_y4 + 10
        if donut_eating_hall_icon:
            screen.blit(donut_eating_hall_icon, (icon_x, icon_y4))
        else:
            pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y4, icon_size, icon_size))
        pygame.draw.rect(screen, BLACK, (icon_x, icon_y4, icon_size, icon_size), 3)
        
        name_text4 = font_upgrade_name.render("Donut Eating Hall", True, WHITE)
        screen.blit(name_text4, (text_x, upgrade_y4 + 10))
        desc_text4 = font_upgrade_desc.render(f"+{DONUT_EATING_HALL_DPS} donuts/sec", True, WHITE)
        screen.blit(desc_text4, (text_x, upgrade_y4 + 45))
        count_text4 = font_upgrade_desc.render(f"Owned: {donut_eating_hall_count}/{DONUT_EATING_HALL_MAX}", True, WHITE)
        screen.blit(count_text4, (text_x, upgrade_y4 + 70))
        if donut_eating_hall_count < DONUT_EATING_HALL_MAX:
            cost_text4 = font_upgrade_name.render(f"Cost: {format_number(donut_eating_hall_cost)}", True, WHITE if can_afford4 else (255, 100, 100))
            screen.blit(cost_text4, (text_x, upgrade_y4 + 90))
        else:
            maxed_text4 = font_upgrade_name.render("MAX", True, (255, 215, 0))
            screen.blit(maxed_text4, (text_x, upgrade_y4 + 90))
        upgrade_rects.append(('donut_eating_hall', upgrade_rect4))
    
    # DONUT CORPORATION - piąty box
    if max_donuts >= 500000:
        upgrade_y5 = upgrade_y4 + upgrade_height + upgrade_spacing if max_donuts >= 50000 else upgrade_y3 + upgrade_height + upgrade_spacing if max_donuts >= 5000 else upgrade_y2 + upgrade_height + upgrade_spacing
        upgrade_rect5 = pygame.Rect(upgrade_x, upgrade_y5, upgrade_width, upgrade_height)
        donut_co_cost = get_donut_co_cost()
        can_afford5 = points >= donut_co_cost and donut_co_count < DONUT_CO_MAX
        hover5 = upgrade_rect5.collidepoint(pygame.mouse.get_pos())
        if donut_co_count >= DONUT_CO_MAX:
            bg_color5 = (100, 100, 100)
        elif can_afford5:
            bg_color5 = BROWN_LIGHT if hover5 else (120, 90, 60)
        else:
            bg_color5 = BROWN_DARK
        pygame.draw.rect(screen, bg_color5, upgrade_rect5)
        pygame.draw.rect(screen, BLACK, upgrade_rect5, 6)
        
        icon_y5 = upgrade_y5 + 10
        if donut_co_icon:
            screen.blit(donut_co_icon, (icon_x, icon_y5))
        else:
            pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y5, icon_size, icon_size))
        pygame.draw.rect(screen, BLACK, (icon_x, icon_y5, icon_size, icon_size), 3)
        
        name_text5 = font_upgrade_name.render("Donut Corporation", True, WHITE)
        screen.blit(name_text5, (text_x, upgrade_y5 + 10))
        desc_text5 = font_upgrade_desc.render(f"+{DONUT_CO_DPS} donuts/sec", True, WHITE)
        screen.blit(desc_text5, (text_x, upgrade_y5 + 45))
        count_text5 = font_upgrade_desc.render(f"Owned: {donut_co_count}/{DONUT_CO_MAX}", True, WHITE)
        screen.blit(count_text5, (text_x, upgrade_y5 + 70))
        if donut_co_count < DONUT_CO_MAX:
            cost_text5 = font_upgrade_name.render(f"Cost: {format_number(donut_co_cost)}", True, WHITE if can_afford5 else (255, 100, 100))
            screen.blit(cost_text5, (text_x, upgrade_y5 + 90))
        else:
            maxed_text5 = font_upgrade_name.render("MAX", True, (255, 215, 0))
            screen.blit(maxed_text5, (text_x, upgrade_y5 + 90))
        upgrade_rects.append(('donut_co', upgrade_rect5))
    
    return upgrade_rects

def draw_upgrades_upgrades(menu_x):
    global points, store_unlocked, eating_power_level
    upgrade_rects = []
    upgrade_y = 155
    upgrade_height = 120
    upgrade_margin = 20
    upgrade_spacing = 10
    upgrade_width = MENU_WIDTH - 2 * upgrade_margin
    upgrade_x = menu_x + upgrade_margin
    
    # EATING POWER - można kupować w nieskończoność
    upgrade_rect = pygame.Rect(upgrade_x, upgrade_y, upgrade_width, upgrade_height)
    eating_power_cost = get_eating_power_cost()
    can_afford = points >= eating_power_cost
    hover = upgrade_rect.collidepoint(pygame.mouse.get_pos())
    
    if can_afford:
        bg_color = BROWN_LIGHT if hover else (120, 90, 60)
    else:
        bg_color = BROWN_DARK
    
    pygame.draw.rect(screen, bg_color, upgrade_rect)
    pygame.draw.rect(screen, BLACK, upgrade_rect, 6)
    
    icon_size = 100
    icon_x = upgrade_x + 10
    icon_y = upgrade_y + 10
    if eating_power_icon:
        screen.blit(eating_power_icon, (icon_x, icon_y))
    else:
        pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y, icon_size, icon_size))
    pygame.draw.rect(screen, BLACK, (icon_x, icon_y, icon_size, icon_size), 3)
    
    text_x = upgrade_x + 120
    name_text = font_upgrade_name.render("Eating Power", True, WHITE)
    screen.blit(name_text, (text_x, upgrade_y + 10))
    desc_text = font_upgrade_desc.render(f"+1 donut per click", True, WHITE)
    screen.blit(desc_text, (text_x, upgrade_y + 45))
    level_text = font_upgrade_desc.render(f"Level: {eating_power_level}", True, WHITE)
    screen.blit(level_text, (text_x, upgrade_y + 70))
    cost_text = font_upgrade_name.render(f"Cost: {format_number(eating_power_cost)}", True, WHITE if can_afford else (255, 100, 100))
    screen.blit(cost_text, (text_x, upgrade_y + 90))
    
    upgrade_rects.append(('eating_power', upgrade_rect))
    upgrade_y += upgrade_height + upgrade_spacing
    
    # STORE - pokazuj tylko gdy nie jest odblokowany
    if not store_unlocked:
        upgrade_rect2 = pygame.Rect(upgrade_x, upgrade_y, upgrade_width, upgrade_height)
        can_afford2 = points >= STORE_COST
        hover2 = upgrade_rect2.collidepoint(pygame.mouse.get_pos())
        
        icon_size = 100
        icon_x = upgrade_x + 10
        
        if can_afford2:
            bg_color2 = BROWN_LIGHT if hover2 else (120, 90, 60)
        else:
            bg_color2 = BROWN_DARK
        
        pygame.draw.rect(screen, bg_color2, upgrade_rect2)
        pygame.draw.rect(screen, BLACK, upgrade_rect2, 6)
        
        icon_y2 = upgrade_y + 10
        if store_icon:
            screen.blit(store_icon, (icon_x, icon_y2))
        else:
            pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y2, icon_size, icon_size))
        pygame.draw.rect(screen, BLACK, (icon_x, icon_y2, icon_size, icon_size), 3)
        
        text_x = upgrade_x + 120
        name_text2 = font_upgrade_name.render("Store", True, WHITE)
        screen.blit(name_text2, (text_x, upgrade_y + 10))
        desc_text2 = font_upgrade_desc.render("Unlock the store!", True, WHITE)
        screen.blit(desc_text2, (text_x, upgrade_y + 45))
        
        cost_text2 = font_upgrade_name.render(f"Cost: {format_number(STORE_COST)}", True, WHITE if can_afford2 else (255, 100, 100))
        screen.blit(cost_text2, (text_x, upgrade_y + 90))
        
        upgrade_rects.append(('store', upgrade_rect2))
        upgrade_y += upgrade_height + upgrade_spacing
    
    # GASTRO PILL - pokazuj tylko gdy nie jest odblokowany
    if not gastro_pill_unlocked:
        upgrade_rect3 = pygame.Rect(upgrade_x, upgrade_y, upgrade_width, upgrade_height)
        can_afford3 = points >= GASTRO_PILL_COST
        hover3 = upgrade_rect3.collidepoint(pygame.mouse.get_pos())
        
        icon_size = 100
        icon_x = upgrade_x + 10
        
        if can_afford3:
            bg_color3 = BROWN_LIGHT if hover3 else (120, 90, 60)
        else:
            bg_color3 = BROWN_DARK
        
        pygame.draw.rect(screen, bg_color3, upgrade_rect3)
        pygame.draw.rect(screen, BLACK, upgrade_rect3, 6)
        
        icon_y3 = upgrade_y + 10
        if gastro_pill_icon:
            screen.blit(gastro_pill_icon, (icon_x, icon_y3))
        else:
            pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y3, icon_size, icon_size))
        pygame.draw.rect(screen, BLACK, (icon_x, icon_y3, icon_size, icon_size), 3)
        
        text_x = upgrade_x + 120
        name_text3 = font_upgrade_name.render("Gastro Pill", True, WHITE)
        screen.blit(name_text3, (text_x, upgrade_y + 10))
        desc_text3 = font_upgrade_desc.render("+30% donuts from clicks", True, WHITE)
        screen.blit(desc_text3, (text_x, upgrade_y + 45))
        
        cost_text3 = font_upgrade_name.render(f"Cost: {format_number(GASTRO_PILL_COST)}", True, WHITE if can_afford3 else (255, 100, 100))
        screen.blit(cost_text3, (text_x, upgrade_y + 90))
        
        upgrade_rects.append(('gastro_pill', upgrade_rect3))
    
    return upgrade_rects

def draw_premium_shop_content(menu_x):
    """Zawartość zakładki Premium Shop - sklep za prawdziwe pieniądze (placeholder)"""
    # Tytuł
    title_y = 150
    title_text = font_pixel.render("Premium Shop", True, WHITE)
    title_rect = title_text.get_rect(centerx=menu_x + MENU_WIDTH // 2, y=title_y)
    screen.blit(title_text, title_rect)
    
    # Placeholder
    placeholder_y = 250
    placeholder_text = font_upgrade_name.render("Coming Soon!", True, (200, 200, 200))
    placeholder_rect = placeholder_text.get_rect(centerx=menu_x + MENU_WIDTH // 2, y=placeholder_y)
    screen.blit(placeholder_text, placeholder_rect)
    
    desc_text = font_upgrade_desc.render("This shop will contain premium items", True, (150, 150, 150))
    desc_rect = desc_text.get_rect(centerx=menu_x + MENU_WIDTH // 2, y=placeholder_y + 40)
    screen.blit(desc_text, desc_rect)
    
    desc_text2 = font_upgrade_desc.render("purchasable with real money.", True, (150, 150, 150))
    desc_rect2 = desc_text2.get_rect(centerx=menu_x + MENU_WIDTH // 2, y=placeholder_y + 70)
    screen.blit(desc_text2, desc_rect2)


def draw_achievements_tab(menu_x):
    """Rysuje zakładkę z osiągnięciami"""
    # Licznik osiągnięć na górze
    unlocked, total = get_achievement_count(None)  # Wrapper używa globalnej listy ACHIEVEMENTS
    counter_text = font_upgrade_name.render(f"Achievements: {unlocked}/{total}", True, WHITE)
    screen.blit(counter_text, (menu_x + 30, 100))
    
    # Grid z osiągnięciami (3 kolumny)
    start_y = 160
    box_size = 120
    spacing = 10
    boxes_per_row = 3
    
    sorted_achievements_list = get_sorted_achievements(None)  # Wrapper używa ACHIEVEMENTS
    
    # Lista rect'ów do zwrócenia (dla obsługi kliknięć)
    achievement_rects = []
    
    for i, achievement in enumerate(sorted_achievements_list):
        row = i // boxes_per_row
        col = i % boxes_per_row
        
        box_x = menu_x + 30 + col * (box_size + spacing)
        box_y = start_y + row * (box_size + spacing)
        
        box_rect = pygame.Rect(box_x, box_y, box_size, box_size)
        achievement_rects.append((achievement, box_rect))
        
        # Rysuj box
        if achievement.unlocked:
            color = BROWN_LIGHT
        else:
            color = BROWN_DARK
        
        pygame.draw.rect(screen, color, box_rect)
        pygame.draw.rect(screen, BLACK, box_rect, 4)
        
        # Ikona (100x100 aby lepiej wypełniała box 120x120)
        icon_size = 100
        icon_x = box_x + (box_size - icon_size) // 2
        icon_y = box_y + 10
        
        if achievement.unlocked:
            # Złoty placeholder dla odblokowanych
            pygame.draw.rect(screen, (255, 215, 0), (icon_x, icon_y, icon_size, icon_size))
        else:
            # Szary box ze znakiem zapytania dla zablokowanych
            pygame.draw.rect(screen, (100, 100, 100), (icon_x, icon_y, icon_size, icon_size))
            question_mark = font_button.render("?", True, WHITE)
            q_rect = question_mark.get_rect(center=(icon_x + icon_size // 2, icon_y + icon_size // 2))
            screen.blit(question_mark, q_rect)
        
        pygame.draw.rect(screen, BLACK, (icon_x, icon_y, icon_size, icon_size), 3)
        
        # NIE wyświetlamy nazwy pod osiągnięciem
        # Nazwa i opis pojawią się dopiero po kliknięciu
    
    return achievement_rects

def draw_statistics_tab(menu_x):
    stat_y = 100
    line_height = 50
    stat_x = menu_x + 30
    hours = int(time_played // 3600)
    minutes = int((time_played % 3600) // 60)
    seconds = int(time_played % 60)
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    total_hours = int(total_time_played // 3600)
    total_minutes = int((total_time_played % 3600) // 60)
    total_seconds = int(total_time_played % 60)
    total_time_str = f"{total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"
    
    stats = [
        f"Time Played: {time_str}",
        f"Total Time: {total_time_str}",
        f"Max Donuts: {format_number(max_donuts)}",
        f"Max DPS: {max_dps:.1f}",
        f"Current DPS: {get_total_dps():.1f}",
        f"Total Donuts: {format_number(total_donuts_earned)}",
        f"Click Power: {get_clicks_per_click()}",
    ]
    for i, stat_text in enumerate(stats):
        text = font_upgrade_desc.render(stat_text, True, WHITE)
        screen.blit(text, (stat_x, stat_y + i * line_height))

def draw_inventory_tab(menu_x):
    """Zakładka Inventory - ekwipunek (placeholder na przyszłość)"""
    # Tytuł
    title_text = font_pixel.render("Inventory", True, WHITE)
    title_rect = title_text.get_rect(centerx=menu_x + MENU_WIDTH // 2, y=100)
    screen.blit(title_text, title_rect)
    
    # Placeholder - pusta zakładka
    placeholder_y = 200
    placeholder_text = font_upgrade_name.render("Coming Soon!", True, (200, 200, 200))
    placeholder_rect = placeholder_text.get_rect(centerx=menu_x + MENU_WIDTH // 2, y=placeholder_y)
    screen.blit(placeholder_text, placeholder_rect)
    
    desc_text = font_upgrade_desc.render("This tab will contain your inventory", True, (150, 150, 150))
    desc_rect = desc_text.get_rect(centerx=menu_x + MENU_WIDTH // 2, y=placeholder_y + 40)
    screen.blit(desc_text, desc_rect)
    
    desc_text2 = font_upgrade_desc.render("and collected items.", True, (150, 150, 150))
    desc_rect2 = desc_text2.get_rect(centerx=menu_x + MENU_WIDTH // 2, y=placeholder_y + 70)
    screen.blit(desc_text2, desc_rect2)

running = True
donut_scale = 1.0
target_scale = 1.0
original_size = donut_image.get_size()
menu_close_rect = None
tab_rects = []
shop_tab_rects = []
upgrade_rects = []
subtab_rects = []
achievement_rects = []
last_time = pygame.time.get_ticks()
last_save_time = pygame.time.get_ticks()
SAVE_INTERVAL = 10000  # 10 sekund

while running:
    screen.fill(PINK_BG)
    
    for donut in floating_donuts:
        donut.update()
        donut.draw()
    
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0
    last_time = current_time
    time_played = (current_time - game_start_time) / 1000.0
    total_time_played += delta_time
    total_dps = get_total_dps()
    if total_dps > 0:
        earned_this_frame = total_dps * delta_time
        points += earned_this_frame
        total_donuts_earned += earned_this_frame
    if points > max_donuts:
        max_donuts = points
    current_dps = get_total_dps()
    if current_dps > max_dps:
        max_dps = current_dps
    
    # Sprawdź osiągnięcia
    stats = {
        'total_donuts': total_donuts_earned,
        'max_donuts': max_donuts,
        'current_dps': current_dps
    }
    newly_unlocked = check_all_achievements(None, stats)  # Wrapper używa check_achievements()
    
    # Jeśli coś zostało odblokowane, pokaż powiadomienie
    if newly_unlocked and not show_achievement_notification:
        show_achievement_notification = True
        achievement_to_show = newly_unlocked[0]  # Pokaż pierwsze osiągnięcie
        achievement_notification_timer = 0
    
    # Timer powiadomienia osiągnięcia
    if show_achievement_notification:
        achievement_notification_timer += delta_time * 1000  # Konwersja na milisekundy
        if achievement_notification_timer >= ACHIEVEMENT_NOTIFICATION_DURATION:
            show_achievement_notification = False
            achievement_to_show = None
            achievement_notification_timer = 0
    
    if current_time - last_save_time > SAVE_INTERVAL:
        save_game()
        last_save_time = current_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            sound_settings['dragging'] = False
            music_settings['dragging'] = False
        
        if event.type == pygame.MOUSEMOTION and sound_settings['dragging']:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if sound_settings['bar_w'] > 0:
                rel_x = mouse_x - sound_settings['bar_x']
                sound_settings['volume'] = max(0.0, min(1.0, rel_x / sound_settings['bar_w']))
                sound_settings['volume'] = round(sound_settings['volume'], 2)
                if click_sound:
                    click_sound.set_volume(sound_settings['volume'])
        
        if event.type == pygame.MOUSEMOTION and music_settings['dragging']:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if music_settings['bar_w'] > 0:
                rel_x = mouse_x - music_settings['bar_x']
                music_settings['volume'] = max(0.0, min(1.0, rel_x / music_settings['bar_w']))
                music_settings['volume'] = round(music_settings['volume'], 2)
                pygame.mixer.music.set_volume(music_settings['volume'])
        
        if event.type == pygame.KEYDOWN:
            if achievement_detail_window_open:
                if event.key == pygame.K_ESCAPE:
                    achievement_detail_window_open = False
                    achievement_detail_to_show = None
            elif idle_window_open:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    points += idle_donuts
                    total_donuts_earned += idle_donuts
                    idle_window_open = False
                    idle_donuts = 0
                    idle_time_seconds = 0
            elif settings_window_open:
                if event.key == pygame.K_ESCAPE:
                    settings_window_open = False
                    settings_target_x = -800
            elif store_window_open:
                if event.key == pygame.K_ESCAPE:
                    store_window_open = False
            elif code_verified:
                if event.key == pygame.K_RETURN:
                    try:
                        amount = int(amount_input_text)
                        points = amount
                        total_donuts_earned += amount
                        print(f"Donuts set to: {amount}")
                    except:
                        print("Invalid number!")
                    amount_input_text = ""
                    code_verified = False
                    code_input_active = False
                elif event.key == pygame.K_ESCAPE:
                    amount_input_text = ""
                    code_verified = False
                    code_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    amount_input_text = amount_input_text[:-1]
                else:
                    if event.unicode.isdigit() and len(amount_input_text) < 15:
                        amount_input_text += event.unicode
            elif code_input_active:
                if event.key == pygame.K_RETURN:
                    result = check_code(code_input_text)
                    if result:
                        # Kod "1234" - otwórz okno do wpisywania liczby
                        code_verified = True
                        amount_input_text = ""
                        code_input_active = False
                    else:
                        # Inne kody (idle, reset) - po prostu zamknij okno
                        code_input_active = False
                    code_input_text = ""
                elif event.key == pygame.K_ESCAPE:
                    code_input_text = ""
                    code_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    code_input_text = code_input_text[:-1]
                else:
                    if len(code_input_text) < 20:
                        code_input_text += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Obsługa kliknięcia w powiadomienie osiągnięcia (najwyższy priorytet)
            if show_achievement_notification:
                # achievement_notification_rect będzie dostępny po narysowaniu
                pass
            
            # Obsługa okna idle
            if idle_window_open:
                # ok_button_rect jest zwracany przez draw_idle_window
                # Sprawdzimy to później w sekcji rysowania
                continue
            
            if code_input_active or code_verified or store_window_open:
                continue
            
            if settings_window_open:
                if settings_close_rect and settings_close_rect.collidepoint(mouse_x, mouse_y):
                    settings_window_open = False
                    settings_target_x = -800
                elif settings_code_button_rect and settings_code_button_rect.collidepoint(mouse_x, mouse_y):
                    code_input_active = True
                    code_input_text = ""
                    settings_window_open = False
                    settings_target_x = -800
                elif settings_checkbox_rect and settings_checkbox_rect.collidepoint(mouse_x, mouse_y):
                    # Toggle dźwięku
                    sound_settings['enabled'] = not sound_settings['enabled']
                    print(f"Click sound: {'ON' if sound_settings['enabled'] else 'OFF'}")
                elif settings_vol_minus_rect and settings_vol_minus_rect.collidepoint(mouse_x, mouse_y):
                    sound_settings['volume'] = max(0.0, round(sound_settings['volume'] - 0.1, 1))
                    if click_sound:
                        click_sound.set_volume(sound_settings['volume'])
                    print(f"Volume: {int(sound_settings['volume'] * 100)}%")
                elif settings_vol_plus_rect and settings_vol_plus_rect.collidepoint(mouse_x, mouse_y):
                    sound_settings['volume'] = min(1.0, round(sound_settings['volume'] + 0.1, 1))
                    if click_sound:
                        click_sound.set_volume(sound_settings['volume'])
                    print(f"Volume: {int(sound_settings['volume'] * 100)}%")
                elif settings_vol_bar_rect and settings_vol_bar_rect.collidepoint(mouse_x, mouse_y):
                    # Kliknięcie bezpośrednio w pasek
                    rel_x = mouse_x - sound_settings['bar_x']
                    sound_settings['volume'] = max(0.0, min(1.0, rel_x / sound_settings['bar_w']))
                    sound_settings['volume'] = round(sound_settings['volume'], 2)
                    if click_sound:
                        click_sound.set_volume(sound_settings['volume'])
                    sound_settings['dragging'] = True
                # Przyciski muzyki
                elif settings_music_minus_rect and settings_music_minus_rect.collidepoint(mouse_x, mouse_y):
                    music_settings['volume'] = max(0.0, round(music_settings['volume'] - 0.1, 1))
                    pygame.mixer.music.set_volume(music_settings['volume'])
                    print(f"Music volume: {int(music_settings['volume'] * 100)}%")
                elif settings_music_plus_rect and settings_music_plus_rect.collidepoint(mouse_x, mouse_y):
                    music_settings['volume'] = min(1.0, round(music_settings['volume'] + 0.1, 1))
                    pygame.mixer.music.set_volume(music_settings['volume'])
                    print(f"Music volume: {int(music_settings['volume'] * 100)}%")
                elif settings_music_bar_rect and settings_music_bar_rect.collidepoint(mouse_x, mouse_y):
                    # Kliknięcie w pasek muzyki
                    rel_x = mouse_x - music_settings['bar_x']
                    music_settings['volume'] = max(0.0, min(1.0, rel_x / music_settings['bar_w']))
                    music_settings['volume'] = round(music_settings['volume'], 2)
                    pygame.mixer.music.set_volume(music_settings['volume'])
                    music_settings['dragging'] = True
                elif settings_music_checkbox_rect and settings_music_checkbox_rect.collidepoint(mouse_x, mouse_y):
                    # Toggle muzyki ON/OFF
                    music_settings['enabled'] = not music_settings['enabled']
                    if music_settings['enabled']:
                        pygame.mixer.music.unpause()
                        if not pygame.mixer.music.get_busy():
                            if background_music_path:
                                pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.pause()
                    print(f"Background music: {'ON' if music_settings['enabled'] else 'OFF'}")
                continue
            
            if settings_button_rect.collidepoint(mouse_x, mouse_y):
                settings_window_open = not settings_window_open
                settings_target_x = 0 if settings_window_open else -800
                continue
            
            if store_unlocked and store_button_rect.collidepoint(mouse_x, mouse_y):
                store_window_open = True
                continue
            if menu_open and menu_close_rect and menu_close_rect.collidepoint(mouse_x, mouse_y):
                menu_open = False
                menu_target_x = WIDTH
            elif menu_open and tab_rects:
                clicked_tab = False
                for i, tab_rect in enumerate(tab_rects):
                    if tab_rect.collidepoint(mouse_x, mouse_y):
                        active_tab = i
                        clicked_tab = True
                        break
                
                # Obsługa kliknięć w osiągnięcia (gdy jesteśmy w zakładce Achievements)
                if not clicked_tab and active_tab == 1 and achievement_rects:
                    for achievement, achievement_rect in achievement_rects:
                        if achievement_rect.collidepoint(mouse_x, mouse_y):
                            # Otwórz okno szczegółów osiągnięcia
                            achievement_detail_window_open = True
                            achievement_detail_to_show = achievement
                            break
                
                
                if not clicked_tab and active_tab == 0:
                    clicked_subtab = False
                    for i, subtab_rect in enumerate(subtab_rects):
                        if subtab_rect.collidepoint(mouse_x, mouse_y):
                            upgrade_subtab = i
                            clicked_subtab = True
                            break
                    if not clicked_subtab and upgrade_rects:
                        for upgrade_type, upgrade_rect in upgrade_rects:
                            if upgrade_rect.collidepoint(mouse_x, mouse_y):
                                if upgrade_type == 'eater':
                                    eater_cost = get_eater_cost()
                                    if points >= eater_cost and eater_count < EATER_MAX:
                                        points -= eater_cost
                                        eater_count += 1
                                elif upgrade_type == 'eater_premium':
                                    eater_premium_cost = get_eater_premium_cost()
                                    if points >= eater_premium_cost and eater_premium_count < EATER_PREMIUM_MAX:
                                        points -= eater_premium_cost
                                        eater_premium_count += 1
                                elif upgrade_type == 'donut_house':
                                    donut_house_cost = get_donut_house_cost()
                                    if points >= donut_house_cost and donut_house_count < DONUT_HOUSE_MAX:
                                        points -= donut_house_cost
                                        donut_house_count += 1
                                elif upgrade_type == 'donut_eating_hall':
                                    donut_eating_hall_cost = get_donut_eating_hall_cost()
                                    if points >= donut_eating_hall_cost and donut_eating_hall_count < DONUT_EATING_HALL_MAX:
                                        points -= donut_eating_hall_cost
                                        donut_eating_hall_count += 1
                                elif upgrade_type == 'donut_co':
                                    donut_co_cost = get_donut_co_cost()
                                    if points >= donut_co_cost and donut_co_count < DONUT_CO_MAX:
                                        points -= donut_co_cost
                                        donut_co_count += 1
                                elif upgrade_type == 'eating_power':
                                    eating_power_cost = get_eating_power_cost()
                                    if points >= eating_power_cost:
                                        points -= eating_power_cost
                                        eating_power_level += 1
                                        print(f"Eating Power upgraded to level {eating_power_level}!")
                                elif upgrade_type == 'store':
                                    if points >= STORE_COST and not store_unlocked:
                                        points -= STORE_COST
                                        store_unlocked = True
                                        print("Store unlocked!")
                                elif upgrade_type == 'gastro_pill':
                                    if points >= GASTRO_PILL_COST and not gastro_pill_unlocked:
                                        points -= GASTRO_PILL_COST
                                        gastro_pill_unlocked = True
                                        print("Gastro Pill unlocked! +30% clicks bonus!")
                                break
            elif button_rect.collidepoint(mouse_x, mouse_y):
                menu_open = not menu_open
                menu_target_x = WIDTH - MENU_WIDTH if menu_open else WIDTH
            elif exit_button_rect.collidepoint(mouse_x, mouse_y):
                save_game()
                running = False
            else:
                center_x = WIDTH // 2
                center_y = HEIGHT // 2 + 50
                distance = ((mouse_x - center_x) ** 2 + (mouse_y - center_y) ** 2) ** 0.5
                if distance < DONUT_RADIUS * donut_scale and mouse_x < menu_x and mouse_x > settings_x + 800:
                    clicks_to_add = get_clicks_per_click()
                    points += clicks_to_add
                    total_donuts_earned += clicks_to_add
                    target_scale = 0.90
                    
                    # TUTAJ: Odtwórz dźwięk kliknięcia (tylko jeśli włączony)
                    if click_sound and sound_settings['enabled']:
                        click_sound.play()
    
    if menu_x < menu_target_x:
        menu_x += 30
        if menu_x > menu_target_x:
            menu_x = menu_target_x
    elif menu_x > menu_target_x:
        menu_x -= 30
        if menu_x < menu_target_x:
            menu_x = menu_target_x
    
    if settings_x < settings_target_x:
        settings_x += 30
        if settings_x > settings_target_x:
            settings_x = settings_target_x
    elif settings_x > settings_target_x:
        settings_x -= 30
        if settings_x < settings_target_x:
            settings_x = settings_target_x
    
    if donut_scale < target_scale:
        donut_scale += 0.02
    elif donut_scale > 1.0:
        donut_scale -= 0.02
        if donut_scale < 1.0:
            donut_scale = 1.0
    else:
        donut_scale = 1.0
        target_scale = 1.0
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    center_x = WIDTH // 2
    center_y = HEIGHT // 2 + 50
    distance = ((mouse_x - center_x) ** 2 + (mouse_y - center_y) ** 2) ** 0.5
    tab_hover = False
    upgrade_hover = False
    if menu_open and tab_rects:
        for tab_rect in tab_rects:
            if tab_rect.collidepoint(mouse_x, mouse_y):
                tab_hover = True
                break
    if menu_open and active_tab == 0 and upgrade_rects:
        for upgrade_type, upgrade_rect in upgrade_rects:
            if upgrade_rect.collidepoint(mouse_x, mouse_y):
                if upgrade_type == 'eater':
                    eater_cost = get_eater_cost()
                    if points >= eater_cost and eater_count < EATER_MAX:
                        upgrade_hover = True
                elif upgrade_type == 'eater_premium':
                    eater_premium_cost = get_eater_premium_cost()
                    if points >= eater_premium_cost and eater_premium_count < EATER_PREMIUM_MAX:
                        upgrade_hover = True
                elif upgrade_type == 'donut_house':
                    donut_house_cost = get_donut_house_cost()
                    if points >= donut_house_cost and donut_house_count < DONUT_HOUSE_MAX:
                        upgrade_hover = True
                break
    if button_rect.collidepoint(mouse_x, mouse_y) or exit_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif settings_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif store_unlocked and store_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif distance < DONUT_RADIUS * donut_scale and mouse_x < menu_x and mouse_x > settings_x + 800:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif menu_open and menu_close_rect and menu_close_rect.collidepoint(mouse_x, mouse_y):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif tab_hover or upgrade_hover:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    new_width = int(original_size[0] * donut_scale)
    new_height = int(original_size[1] * donut_scale)
    scaled_donut = pygame.transform.scale(donut_image, (new_width, new_height))
    scaled_rect = scaled_donut.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    donut_rect = scaled_rect
    
    points_formatted = format_number(points)
    text_surface = font_pixel.render(points_formatted, True, LIGHT_YELLOW)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, 120))
    screen.blit(text_surface, text_rect)
    
    current_dps = eater_count * EATER_DPS + eater_premium_count * EATER_PREMIUM_DPS + donut_house_count * DONUT_HOUSE_DPS + donut_eating_hall_count * DONUT_EATING_HALL_DPS + donut_co_count * DONUT_CO_DPS
    dps_text = f"DPS: {current_dps:.1f}"
    dps_render = font_dps.render(dps_text, True, LIGHT_YELLOW)
    dps_position = dps_render.get_rect(center=(WIDTH // 2, 200))
    screen.blit(dps_render, dps_position)
    
    screen.blit(scaled_donut, scaled_rect)
    
    button_hover = button_rect.collidepoint(pygame.mouse.get_pos())
    draw_button(button_x, button_y, button_size, button_hover)
    
    exit_hover = exit_button_rect.collidepoint(pygame.mouse.get_pos())
    draw_exit_button(exit_button_x, exit_button_y, exit_button_size, exit_hover)
    
    settings_hover = settings_button_rect.collidepoint(pygame.mouse.get_pos())
    draw_settings_button(settings_button_x, settings_button_y, settings_button_size, settings_hover)
    
    if store_unlocked:
        store_hover = store_button_rect.collidepoint(pygame.mouse.get_pos())
        draw_store_button(store_button_x, store_button_y, store_button_size, store_hover)
    
    if menu_x < WIDTH:
        menu_close_rect, tab_rects, achievement_rects = draw_menu(menu_x)
        if active_tab == 0:
            upgrade_rects = draw_upgrades_tab(menu_x)
    
    if settings_x > -800:
        settings_close_rect, settings_code_button_rect, settings_checkbox_rect, settings_vol_minus_rect, settings_vol_plus_rect, settings_vol_bar_rect, settings_music_minus_rect, settings_music_plus_rect, settings_music_bar_rect, settings_music_checkbox_rect = draw_settings_window(settings_x)
    
    if store_window_open:
        draw_store_window()
    
    # Okno idle - rysowane na samym wierzchu
    idle_ok_button = None
    if idle_window_open:
        idle_ok_button = draw_idle_window()
        # Sprawdź czy kliknięto przycisk OK
        if pygame.mouse.get_pressed()[0] and idle_ok_button:
            mouse_pos = pygame.mouse.get_pos()
            if idle_ok_button.collidepoint(mouse_pos):
                points += idle_donuts
                total_donuts_earned += idle_donuts
                idle_window_open = False
                idle_donuts = 0
                idle_time_seconds = 0
                pygame.time.wait(200)  # Małe opóźnienie aby nie kliknąć czegoś pod spodem
    
    if code_verified:
        draw_amount_input()
    elif code_input_active:
        draw_code_input()
    
    # Rysuj powiadomienie osiągnięcia (na samym wierzchu wszystkiego)
    achievement_notification_rect = None
    if show_achievement_notification and achievement_to_show:
        achievement_notification_rect = draw_achievement_notification(
            achievement_to_show, 
            achievement_notification_timer
        )
        # Sprawdź czy kliknięto w powiadomienie
        if pygame.mouse.get_pressed()[0] and achievement_notification_rect:
            mouse_pos = pygame.mouse.get_pos()
            if achievement_notification_rect.collidepoint(mouse_pos):
                # Otwórz menu osiągnięć
                menu_open = True
                menu_target_x = WIDTH - MENU_WIDTH
                active_tab = 1  # Tab Achievements (indeks 1)
                show_achievement_notification = False
                achievement_to_show = None
                achievement_notification_timer = 0
                pygame.time.wait(200)  # Małe opóźnienie
    
    # Rysuj okno szczegółów osiągnięcia (na samym wierzchu - nad wszystkim)
    achievement_detail_close_button = None
    if achievement_detail_window_open and achievement_detail_to_show:
        achievement_detail_close_button = draw_achievement_detail_window(achievement_detail_to_show)
        # Sprawdź czy kliknięto przycisk Close
        if pygame.mouse.get_pressed()[0] and achievement_detail_close_button:
            mouse_pos = pygame.mouse.get_pos()
            if achievement_detail_close_button.collidepoint(mouse_pos):
                achievement_detail_window_open = False
                achievement_detail_to_show = None
                pygame.time.wait(200)  # Małe opóźnienie
    
    pygame.display.flip()
    clock.tick(60)

save_game()
pygame.quit()
sys.exit()