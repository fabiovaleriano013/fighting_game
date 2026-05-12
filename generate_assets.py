"""
generate_assets.py - Script auxiliar para gerar assets placeholder para testes.
Execute este script UMA VEZ para criar personagens e mapas de exemplo.

Uso:
    python generate_assets.py

Isso cria dois personagens (guerreiro, ninja) e dois mapas de exemplo.
Substitua as imagens por sprites reais quando quiser.
"""

import os
import math
import pygame
import random

pygame.init()


# ─────────────────────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR  = os.path.join(BASE_DIR, "assets")
CHARS_DIR   = os.path.join(ASSETS_DIR, "personagens")
MAPS_DIR    = os.path.join(ASSETS_DIR, "mapas")

FRAME_W, FRAME_H = 80, 100   # Tamanho dos frames dos personagens
FRAMES_PER_ACTION = 4         # Quantos frames por ação

CHARACTERS = [
    {
        "name": "guerreiro",
        "body_color": (70, 120, 200),
        "skin_color": (220, 180, 140),
        "accent_color": (200, 60, 60),
    },
    {
        "name": "ninja",
        "body_color": (40, 40, 40),
        "skin_color": (180, 140, 100),
        "accent_color": (60, 200, 80),
    },
]

ACTIONS = ["idle", "walk", "attack", "jump", "crouch", "defend"]


# ─────────────────────────────────────────────────────────────
# Geração de personagens
# ─────────────────────────────────────────────────────────────

def draw_character(
    surface: pygame.Surface,
    action: str,
    frame: int,
    body_color: tuple,
    skin_color: tuple,
    accent_color: tuple
):
    """Desenha um personagem placeholder em estilo stick-figure estilizado."""
    w, h = surface.get_size()
    cx = w // 2
    t = frame / FRAMES_PER_ACTION  # 0.0 → 1.0

    # Animação simples baseada na ação
    bob = int(math.sin(t * math.pi * 2) * 3)
    lean = int(math.sin(t * math.pi) * 4)

    if action == "idle":
        bob = int(math.sin(t * math.pi * 2) * 2)
        lean = 0
    elif action == "walk":
        bob = int(math.sin(t * math.pi * 4) * 4)
        lean = int(math.cos(t * math.pi * 2) * 5)
    elif action == "attack":
        lean = int(t * 20) if t < 0.5 else int((1 - t) * 20)
        bob = 0
    elif action == "jump":
        bob = -int(t * 15) if t < 0.5 else -int((1 - t) * 15)
        lean = 0
    elif action == "crouch":
        bob = int(t * 8)
        lean = 0
    elif action == "defend":
        lean = -5
        bob = 0

    body_top    = 30 + bob
    head_r      = 13
    head_cx     = cx + lean
    head_cy     = body_top - 5

    # Sombra
    shadow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 60),
                        (cx - 20, h - 18, 40, 10))
    surface.blit(shadow, (0, 0))

    # Corpo
    body_rect = pygame.Rect(
        cx - 14 + lean, body_top,
        28, 30 + (8 if action == "crouch" else 0)
    )
    pygame.draw.rect(surface, body_color, body_rect, border_radius=6)

    # Detalhe no peito
    pygame.draw.rect(surface, accent_color,
                     (cx - 6 + lean, body_top + 4, 12, 14), border_radius=3)

    # Cabeça
    pygame.draw.circle(surface, skin_color, (head_cx, head_cy), head_r)
    # Olhos
    eye_y = head_cy - 2
    pygame.draw.circle(surface, (30, 30, 30), (head_cx - 4, eye_y), 2)
    pygame.draw.circle(surface, (30, 30, 30), (head_cx + 4, eye_y), 2)

    # Capacete / acessório baseado no personagem
    helmet_rect = pygame.Rect(head_cx - 14, head_cy - head_r - 4, 28, 14)
    pygame.draw.rect(surface, accent_color, helmet_rect, border_radius=4)

    # Pernas
    leg_y = body_top + (28 if action != "crouch" else 20)
    leg_w = 10
    leg_h = 30 if action != "crouch" else 16

    left_leg_x  = cx - 13 + lean
    right_leg_x = cx + 3 + lean

    leg_swing = int(math.sin(t * math.pi * 4) * 8) if action == "walk" else 0

    pygame.draw.rect(surface, body_color,
                     (left_leg_x, leg_y, leg_w, leg_h + leg_swing), border_radius=4)
    pygame.draw.rect(surface, body_color,
                     (right_leg_x, leg_y, leg_w, leg_h - leg_swing), border_radius=4)

    # Botas
    pygame.draw.rect(surface, accent_color,
                     (left_leg_x - 2, leg_y + leg_h + leg_swing - 6, leg_w + 4, 10),
                     border_radius=3)
    pygame.draw.rect(surface, accent_color,
                     (right_leg_x - 2, leg_y + leg_h - leg_swing - 6, leg_w + 4, 10),
                     border_radius=3)

    # Braços
    arm_y = body_top + 4
    arm_swing = int(math.sin(t * math.pi * 4) * 10) if action == "walk" else 0

    if action == "attack":
        # Braço estendido atacando
        arm_end_x = cx + 30 + lean + int(lean * 2)
        pygame.draw.line(surface, skin_color,
                         (cx + 12 + lean, arm_y + 8),
                         (arm_end_x, arm_y + arm_swing), 6)
        # Punho
        pygame.draw.circle(surface, accent_color,
                           (arm_end_x, arm_y + arm_swing), 7)
    elif action == "defend":
        # Braço cruzado na frente
        pygame.draw.line(surface, body_color,
                         (cx - 14 + lean, arm_y + 6),
                         (cx + 14 + lean, arm_y + 20), 7)
        pygame.draw.line(surface, accent_color,
                         (cx - 10 + lean, arm_y + 8),
                         (cx + 10 + lean, arm_y + 18), 4)
    else:
        pygame.draw.line(surface, skin_color,
                         (cx - 14 + lean, arm_y + 6),
                         (cx - 22 + lean, arm_y + 22 + arm_swing), 6)
        pygame.draw.line(surface, skin_color,
                         (cx + 14 + lean, arm_y + 6),
                         (cx + 22 + lean, arm_y + 22 - arm_swing), 6)


def generate_character(char_info: dict):
    """Gera todos os frames de animação de um personagem."""
    name = char_info["name"]
    char_dir = os.path.join(CHARS_DIR, name)

    print(f"  Gerando personagem: {name}")
    for action in ACTIONS:
        action_dir = os.path.join(char_dir, action)
        os.makedirs(action_dir, exist_ok=True)

        for i in range(FRAMES_PER_ACTION):
            surf = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
            draw_character(
                surf, action, i,
                char_info["body_color"],
                char_info["skin_color"],
                char_info["accent_color"]
            )
            filepath = os.path.join(action_dir, f"{action}_{i:02d}.png")
            pygame.image.save(surf, filepath)

        print(f"    ✓ {action} ({FRAMES_PER_ACTION} frames)")


# ─────────────────────────────────────────────────────────────
# Geração de mapas
# ─────────────────────────────────────────────────────────────

def generate_maps():
    """Gera dois mapas placeholder."""
    os.makedirs(MAPS_DIR, exist_ok=True)
    maps = [
        ("arena_volcano",  _draw_volcano_map),
        ("templo_antigo",  _draw_temple_map),
    ]
    for name, draw_fn in maps:
        surf = pygame.Surface((1024, 576))
        draw_fn(surf)
        path = os.path.join(MAPS_DIR, f"{name}.png")
        pygame.image.save(surf, path)
        print(f"  ✓ Mapa: {name}.png")


def _draw_volcano_map(surf: pygame.Surface):
    w, h = surf.get_size()
    # Céu laranja/vermelho
    for y in range(h):
        r = int(180 + 50 * y / h)
        g = int(60 - 40 * y / h)
        b = 20
        pygame.draw.line(surf, (min(255,r), max(0,g), b), (0, y), (w, y))

    # Montanhas de fundo
    rng = random.Random(1)
    for _ in range(5):
        mx = rng.randint(50, w - 50)
        mh = rng.randint(120, 250)
        pts = [
            (mx - rng.randint(60, 100), h * 2 // 3),
            (mx, h * 2 // 3 - mh),
            (mx + rng.randint(60, 100), h * 2 // 3),
        ]
        pygame.draw.polygon(surf, (80, 30, 20), pts)
        # Cratera no topo
        pygame.draw.circle(surf, (200, 50, 10), (mx, h * 2 // 3 - mh), 14)

    # Lava (chão)
    for y in range(h * 2 // 3, h):
        ratio = (y - h * 2 // 3) / (h // 3)
        r = int(220 - ratio * 50)
        g = int(80 - ratio * 60)
        pygame.draw.line(surf, (r, max(0, g), 0), (0, y), (w, y))

    # Pedras no chão
    pygame.draw.rect(surf, (60, 30, 20), (0, h - 90, w, 90))
    pygame.draw.rect(surf, (100, 50, 30), (0, h - 90, w, 10))


def _draw_temple_map(surf: pygame.Surface):
    w, h = surf.get_size()
    # Céu noturno azul-roxo
    for y in range(h):
        r = int(10 + 20 * y / h)
        g = int(5 + 15 * y / h)
        b = int(60 + 40 * y / h)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

    # Estrelas
    rng = random.Random(7)
    for _ in range(80):
        sx = rng.randint(0, w)
        sy = rng.randint(0, h // 2)
        sz = rng.randint(1, 3)
        pygame.draw.circle(surf, (220, 220, 255), (sx, sy), sz)

    # Lua
    pygame.draw.circle(surf, (240, 240, 200), (w - 120, 80), 50)
    pygame.draw.circle(surf, (10, 10, 60), (w - 100, 70), 44)

    # Colunas do templo
    col_color = (100, 80, 60)
    for cx in range(80, w, 120):
        pygame.draw.rect(surf, col_color, (cx - 15, h // 3, 30, h * 2 // 3))
        pygame.draw.rect(surf, (120, 100, 80), (cx - 20, h // 3 - 20, 40, 20))  # capitel

    # Teto do templo
    pygame.draw.rect(surf, (80, 60, 40), (0, h // 3 - 30, w, 15))

    # Chão de pedra
    pygame.draw.rect(surf, (60, 50, 40), (0, h - 90, w, 90))
    for x in range(0, w, 80):
        pygame.draw.line(surf, (50, 40, 30), (x, h - 90), (x, h), 2)
    for y in range(h - 90, h, 30):
        pygame.draw.line(surf, (50, 40, 30), (0, y), (w, y), 2)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  PyFighter - Gerador de Assets Placeholder")
    print("=" * 50)

    os.makedirs(CHARS_DIR, exist_ok=True)
    os.makedirs(MAPS_DIR, exist_ok=True)

    print("\n📦 Gerando personagens...")
    for char in CHARACTERS:
        generate_character(char)

    print("\n🗺  Gerando mapas...")
    generate_maps()

    print("\n✅ Assets gerados com sucesso!")
    print(f"   Pasta: {ASSETS_DIR}")
    print("\nAgora execute: python main.py")
    print("=" * 50)

    pygame.quit()


if __name__ == "__main__":
    main()
