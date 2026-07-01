"""
asset_loader.py - Carregamento dinâmico de assets do jogo.
Lê pastas de personagens e mapas automaticamente, sem código fixo.
"""

import os
import pygame
from typing import Dict, List, Optional


# ─────────────────────────────────────────────────────────────
# Caminhos base
# ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CHARACTERS_DIR = os.path.join(ASSETS_DIR, "personagens")
MAPS_DIR = os.path.join(ASSETS_DIR, "mapas")
MUSIC_DIR = os.path.join(ASSETS_DIR, "musicas")

# Ações esperadas para cada personagem (pastas dentro da pasta do personagem)
CHARACTER_ACTIONS = ["idle", "walk", "attack", "jump", "crouch", "defend"]

# Extensões de imagem suportadas
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}

# Extensões de áudio suportadas para música de fundo
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac"}

# Tamanho padrão normalizado para todos os sprites de personagens (em pixels)
# Isso garante que todos os personagens fiquem com o mesmo tamanho no jogo
NORMALIZED_SPRITE_SIZE = (130, 230)


# ─────────────────────────────────────────────────────────────
# Funções de descoberta de assets
# ─────────────────────────────────────────────────────────────

def get_character_names() -> List[str]:
    """
    Lista todos os personagens disponíveis na pasta assets/personagens/.
    Retorna uma lista com os nomes das pastas.
    """
    if not os.path.isdir(CHARACTERS_DIR):
        os.makedirs(CHARACTERS_DIR, exist_ok=True)
        return []

    names = []
    for entry in sorted(os.listdir(CHARACTERS_DIR)):
        full_path = os.path.join(CHARACTERS_DIR, entry)
        if os.path.isdir(full_path):
            names.append(entry)
    return names


def get_map_paths() -> List[str]:
    """
    Lista todos os mapas disponíveis na pasta assets/mapas/.
    Retorna uma lista com os caminhos completos das imagens.
    """
    if not os.path.isdir(MAPS_DIR):
        os.makedirs(MAPS_DIR, exist_ok=True)
        return []

    paths = []
    for entry in sorted(os.listdir(MAPS_DIR)):
        ext = os.path.splitext(entry)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            paths.append(os.path.join(MAPS_DIR, entry))
    return paths


def get_music_paths() -> List[str]:
    """
    Lista todas as trilhas disponíveis na pasta assets/musicas/.
    Retorna uma lista com os caminhos completos dos arquivos de áudio.
    """
    if not os.path.isdir(MUSIC_DIR):
        os.makedirs(MUSIC_DIR, exist_ok=True)
        return []

    paths = []
    for entry in sorted(os.listdir(MUSIC_DIR)):
        ext = os.path.splitext(entry)[1].lower()
        if ext in AUDIO_EXTENSIONS:
            paths.append(os.path.join(MUSIC_DIR, entry))
    return paths

def get_menu_image_paths() -> List[str]:
    """
    Lista todas as imagens disponíveis na pasta assets/imagens/.
    Retorna uma lista com os caminhos completos das imagens.
    """
    if not os.path.isdir(MENU_IMAGES_DIR):
        os.makedirs(MENU_IMAGES_DIR, exist_ok=True)
        return []

    paths = []
    for entry in sorted(os.listdir(MENU_IMAGES_DIR)):
        ext = os.path.splitext(entry)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            paths.append(os.path.join(MENU_IMAGES_DIR, entry))
    return paths

# ─────────────────────────────────────────────────────────────
# Carregamento de frames de animação
# ─────────────────────────────────────────────────────────────

def load_animation_frames(
    character_name: str,
    action: str,
    scale: float = 1.0
) -> List[pygame.Surface]:
    """
    Carrega todos os frames de uma ação de um personagem.
    Normaliza todos os sprites para o tamanho padrão NORMALIZED_SPRITE_SIZE,
    garantindo que todos os personagens fiquem com o mesmo tamanho no jogo.

    Args:
        character_name: Nome da pasta do personagem.
        action: Nome da ação (idle, walk, attack, etc.).
        scale: Fator de escala adicional para redimensionar após normalização.

    Returns:
        Lista de Surfaces com os frames da animação (todos com tamanho normalizado).
        Se a pasta não existir, retorna uma lista com um frame placeholder.
    """
    action_dir = os.path.join(CHARACTERS_DIR, character_name, action)

    if not os.path.isdir(action_dir):
        # Retorna frame placeholder caso a pasta não exista
        return [_create_placeholder_frame(character_name, action, scale)]

    frames = []
    files = sorted([
        f for f in os.listdir(action_dir)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    ])

    if not files:
        return [_create_placeholder_frame(character_name, action, scale)]

    for filename in files:
        filepath = os.path.join(action_dir, filename)
        try:
            img = pygame.image.load(filepath).convert_alpha()
            
            # Normaliza para o tamanho padrão (mantendo aspect ratio)
            img = pygame.transform.scale(img, NORMALIZED_SPRITE_SIZE)
            
            # Aplica escala adicional se fornecida
            if scale != 1.0:
                new_w = int(img.get_width() * scale)
                new_h = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (new_w, new_h))
            
            frames.append(img)
        except pygame.error as e:
            print(f"[AssetLoader] Erro ao carregar {filepath}: {e}")

    return frames if frames else [_create_placeholder_frame(character_name, action, scale)]


def load_all_animations(
    character_name: str,
    scale: float = 1.0
) -> Dict[str, List[pygame.Surface]]:
    """
    Carrega todas as animações de um personagem.

    Returns:
        Dicionário {ação: [frames]}
    """
    animations = {}
    for action in CHARACTER_ACTIONS:
        animations[action] = load_animation_frames(character_name, action, scale)
    return animations


def load_map_image(map_path: str, size: tuple) -> pygame.Surface:
    """
    Carrega e redimensiona a imagem de um mapa.

    Args:
        map_path: Caminho completo para o arquivo de imagem.
        size: Tupla (largura, altura) para redimensionar.

    Returns:
        Surface com o mapa carregado e redimensionado.
    """
    if not os.path.isfile(map_path):
        return _create_placeholder_map(size)

    try:
        img = pygame.image.load(map_path).convert()
        img = pygame.transform.scale(img, size)
        return img
    except pygame.error as e:
        print(f"[AssetLoader] Erro ao carregar mapa {map_path}: {e}")
        return _create_placeholder_map(size)


def load_map_thumbnail(map_path: str, thumb_size: tuple = (200, 120)) -> pygame.Surface:
    """Carrega uma miniatura do mapa para exibição no seletor."""
    return load_map_image(map_path, thumb_size)


def load_character_thumbnail(
    character_name: str,
    thumb_size: tuple = (120, 120)
) -> pygame.Surface:
    """
    Carrega o primeiro frame de 'idle' como thumbnail do personagem.
    """
    frames = load_animation_frames(character_name, "idle", scale=1.0)
    thumb = frames[0]
    return pygame.transform.scale(thumb, thumb_size)


# ─────────────────────────────────────────────────────────────
# Placeholders (usados quando assets reais não existem)
# ─────────────────────────────────────────────────────────────

def _create_placeholder_frame(
    character_name: str,
    action: str,
    scale: float
) -> pygame.Surface:
    """
    Cria um frame placeholder colorido para uso em desenvolvimento.
    Cada personagem recebe uma cor única baseada no nome.
    """
    w = int(80 * scale)
    h = int(100 * scale)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Cor baseada no hash do nome
    color = _name_to_color(character_name)
    pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=8)

    # Bordinha escura
    pygame.draw.rect(surf, (0, 0, 0), (0, 0, w, h), 2, border_radius=8)

    # Texto da ação
    font = pygame.font.SysFont("Arial", max(8, int(10 * scale)))
    label = font.render(action[:4], True, (255, 255, 255))
    surf.blit(label, (4, 4))

    # Silhueta humana simples
    cx = w // 2
    # Cabeça
    pygame.draw.circle(surf, (220, 180, 140), (cx, int(h * 0.2)), int(h * 0.12))
    # Corpo
    pygame.draw.rect(surf, (180, 180, 220), (cx - int(w*0.2), int(h*0.3), int(w*0.4), int(h*0.3)))
    # Pernas
    pygame.draw.rect(surf, (100, 100, 180), (cx - int(w*0.18), int(h*0.6), int(w*0.16), int(h*0.3)))
    pygame.draw.rect(surf, (100, 100, 180), (cx + int(w*0.02), int(h*0.6), int(w*0.16), int(h*0.3)))

    return surf


def _create_placeholder_map(size: tuple) -> pygame.Surface:
    """Cria um mapa placeholder com gradiente simples."""
    surf = pygame.Surface(size)
    w, h = size

    # Gradiente de céu
    for y in range(h * 2 // 3):
        ratio = y / (h * 2 // 3)
        r = int(50 + ratio * 100)
        g = int(100 + ratio * 100)
        b = int(200 - ratio * 50)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

    # Chão
    pygame.draw.rect(surf, (60, 40, 20), (0, h * 2 // 3, w, h // 3))
    pygame.draw.rect(surf, (80, 140, 60), (0, h * 2 // 3, w, h // 10))

    font = pygame.font.SysFont("Arial", 24)
    label = font.render("Mapa Padrão", True, (255, 255, 255))
    surf.blit(label, (w // 2 - label.get_width() // 2, h // 2))

    return surf


def _name_to_color(name: str) -> tuple:
    """Gera uma cor RGB a partir de um nome (determinístico)."""
    h = hash(name) % (256 ** 3)
    r = (h >> 16) & 0xFF
    g = (h >> 8) & 0xFF
    b = h & 0xFF
    # Garante que não seja muito escuro
    r = max(r, 80)
    g = max(g, 80)
    b = max(b, 80)
    return (r, g, b)
