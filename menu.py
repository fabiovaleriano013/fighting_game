"""
menu.py - Telas de menu do jogo.
Contém: Menu Principal, Tela de Controles, Tela de Vitória.
"""

import os
import pygame
import math
from typing import Optional, List
from asset_loader import get_menu_image_paths, get_music_paths, load_map_thumbnail


# ─────────────────────────────────────────────────────────────
# Paleta de cores do jogo
# ─────────────────────────────────────────────────────────────
COLOR_BG_TOP    = (10, 10, 30)
COLOR_BG_BOT    = (30, 10, 50)
COLOR_ACCENT    = (220, 60, 60)
COLOR_GOLD      = (255, 200, 50)
COLOR_WHITE     = (240, 240, 240)
COLOR_GRAY      = (150, 150, 160)
COLOR_DARK      = (20, 20, 35)
COLOR_PANEL     = (25, 25, 45, 200)
COLOR_SELECT    = (220, 60, 60)
COLOR_P1        = (80, 140, 255)
COLOR_P2        = (255, 100, 80)


def draw_gradient_bg(surface: pygame.Surface, top: tuple, bottom: tuple):
    """Desenha um fundo com gradiente vertical."""
    h = surface.get_height()
    w = surface.get_width()
    for y in range(h):
        ratio = y / h
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))


def draw_panel(surface: pygame.Surface, rect: pygame.Rect, alpha: int = 200):
    """Desenha um painel semi-transparente com borda."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((20, 20, 40, alpha))
    pygame.draw.rect(panel, (80, 80, 120, 255), (0, 0, rect.width, rect.height), 2, border_radius=10)
    surface.blit(panel, rect.topleft)


# ─────────────────────────────────────────────────────────────
# Menu Principal
# ─────────────────────────────────────────────────────────────

class MainMenu:
    """Tela de menu principal com navegação por teclado."""

    ITEMS = [
        ("JOGAR",          "play"),
        ("CONTROLES",      "controls"),
        ("CONFIGURAR MENU", "menu_config"),
        ("SAIR",           "quit"),
    ]

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()
        self.selected = 0
        self.time = 0.0

        # Fontes
        self.font_title  = pygame.font.SysFont("Impact", 80)
        self.font_sub    = pygame.font.SysFont("Arial", 18)
        self.font_item   = pygame.font.SysFont("Arial", 38, bold=True)
        self.font_item_s = pygame.font.SysFont("Arial", 44, bold=True)
        self.background = None

    def set_background_image(self, image: Optional[pygame.Surface]):
        self.background = image

    def update(self, events) -> Optional[str]:
        """Processa eventos e retorna ação ou None."""
        self.time += 1 / 60

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.ITEMS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.ITEMS[self.selected][1]
        return None

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            draw_gradient_bg(self.screen, COLOR_BG_TOP, COLOR_BG_BOT)

        # Partículas de fundo (estrelas animadas)
        self._draw_stars()

        # Linha decorativa
        pygame.draw.line(self.screen, COLOR_ACCENT,
                         (self.w // 2 - 220, self.h // 2 - 90),
                         (self.w // 2 + 220, self.h // 2 - 90), 2)

        # Título com pulso
        pulse = 1.0 + 0.03 * math.sin(self.time * 3)
        title_surf = self.font_title.render("PYFIGHTER", True, COLOR_ACCENT)
        tw = int(title_surf.get_width() * pulse)
        th = int(title_surf.get_height() * pulse)
        title_surf = pygame.transform.scale(title_surf, (tw, th))
        self.screen.blit(title_surf, (self.w // 2 - tw // 2, self.h // 4 - th // 2))

        sub = self.font_sub.render("2D FIGHTING GAME", True, COLOR_GRAY)
        self.screen.blit(sub, (self.w // 2 - sub.get_width() // 2, self.h // 4 + 55))

        # Itens do menu
        panel_rect = pygame.Rect(self.w // 2 - 200, self.h // 2 - 80, 400, 200)
        draw_panel(self.screen, panel_rect)

        for i, (label, _) in enumerate(self.ITEMS):
            is_sel = (i == self.selected)
            color = COLOR_GOLD if is_sel else COLOR_WHITE
            font  = self.font_item_s if is_sel else self.font_item
            surf  = font.render(label, True, color)

            y = self.h // 2 - 50 + i * 62
            x = self.w // 2 - surf.get_width() // 2

            if is_sel:
                # Seta indicadora
                arrow = self.font_item.render("", True, COLOR_ACCENT)
                self.screen.blit(arrow, (x - 40, y + 2))

            self.screen.blit(surf, (x, y))

        # Rodapé
        hint = self.font_sub.render("↑↓ Navegar   ENTER Confirmar", True, COLOR_GRAY)
        self.screen.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 40))

    def _draw_stars(self):
        """Desenha estrelas estáticas de fundo."""
        import random
        rng = random.Random(42)
        for _ in range(60):
            x = rng.randint(0, self.w)
            y = rng.randint(0, self.h // 2)
            size = rng.randint(1, 3)
            alpha = rng.randint(80, 200)
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (size, size), size)
            self.screen.blit(s, (x, y))


class MenuConfigScreen:
    """Tela de configuração de imagem e música do menu principal."""

    def __init__(self, screen: pygame.Surface, selected_image: Optional[str] = None, selected_music: Optional[str] = None):
        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()

        self.font_title = pygame.font.SysFont("Impact", 46)
        self.font_label = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 18)
        self.font_hint = pygame.font.SysFont("Arial", 16)

        self.image_paths: List[str] = get_menu_image_paths()
        if not self.image_paths:
            self.image_paths = ["__placeholder__"]

        self.music_paths: List[str] = get_music_paths()
        if not self.music_paths:
            self.music_paths = ["__placeholder__"]

        self.selected_image_index = 0
        self.selected_music_index = 0
        if selected_image and selected_image in self.image_paths:
            self.selected_image_index = self.image_paths.index(selected_image)
        if selected_music and selected_music in self.music_paths:
            self.selected_music_index = self.music_paths.index(selected_music)

        self.active_field = 0

    def update(self, events) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    return "back"
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.active_field = (self.active_field - 1) % 2
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.active_field = (self.active_field + 1) % 2
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.active_field == 0:
                        self.selected_image_index = (self.selected_image_index - 1) % len(self.image_paths)
                    else:
                        self.selected_music_index = (self.selected_music_index - 1) % len(self.music_paths)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.active_field == 0:
                        self.selected_image_index = (self.selected_image_index + 1) % len(self.image_paths)
                    else:
                        self.selected_music_index = (self.selected_music_index + 1) % len(self.music_paths)
        return None

    def get_selected_image(self) -> Optional[str]:
        if self.image_paths[self.selected_image_index] == "__placeholder__":
            return None
        return self.image_paths[self.selected_image_index]

    def get_selected_music(self) -> Optional[str]:
        if self.music_paths[self.selected_music_index] == "__placeholder__":
            return None
        return self.music_paths[self.selected_music_index]

    def draw(self):
        draw_gradient_bg(self.screen, COLOR_BG_TOP, COLOR_BG_BOT)

        title = self.font_title.render("CONFIGURAR MENU", True, COLOR_ACCENT)
        self.screen.blit(title, (self.w // 2 - title.get_width() // 2, 30))

        # Imagem do menu
        image_label = self.font_label.render("Imagem do Menu", True, COLOR_WHITE)
        image_y = 130
        self.screen.blit(image_label, (80, image_y))
        image_name = os.path.splitext(os.path.basename(self.image_paths[self.selected_image_index]))[0]
        if self.image_paths[self.selected_image_index] == "__placeholder__":
            image_name = "Nenhuma imagem encontrada"
        image_text = self.font_text.render(image_name.replace("_", " ").title(), True, COLOR_GRAY)
        self.screen.blit(image_text, (80, image_y + 38))

        # Música do menu
        music_label = self.font_label.render("Música do Menu", True, COLOR_WHITE)
        music_y = 220
        self.screen.blit(music_label, (80, music_y))
        if self.music_paths[self.selected_music_index] == "__placeholder__":
            music_name = "Nenhuma música encontrada"
        else:
            music_name = os.path.splitext(os.path.basename(self.music_paths[self.selected_music_index]))[0]
        music_text = self.font_text.render(music_name.replace("_", " ").title(), True, COLOR_GRAY)
        self.screen.blit(music_text, (80, music_y + 38))

        # Preview da imagem
        preview_x = self.w - 360
        preview_y = 130
        preview_w = 280
        preview_h = 180
        preview_rect = pygame.Rect(preview_x, preview_y, preview_w, preview_h)
        pygame.draw.rect(self.screen, (40, 40, 50), preview_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_ACCENT, preview_rect, 2, border_radius=10)

        if self.image_paths[self.selected_image_index] != "__placeholder__":
            preview = load_map_thumbnail(self.image_paths[self.selected_image_index], (preview_w - 12, preview_h - 12))
            self.screen.blit(preview, (preview_x + 6, preview_y + 6))
        else:
            placeholder = self.font_text.render("Preview indisponível", True, COLOR_GRAY)
            self.screen.blit(placeholder, (preview_x + 16, preview_y + preview_h // 2 - 10))

        # Seleção ativa
        for idx, label in enumerate(["Imagem", "Música"]):
            color = COLOR_GOLD if self.active_field == idx else COLOR_WHITE
            mark = "> " if self.active_field == idx else "  "
            line = self.font_text.render(f"{mark}{label}", True, color)
            self.screen.blit(line, (80, 320 + idx * 28))

        hint = self.font_hint.render(
            "↑↓ Selecionar   ←→ Alterar   ENTER/ESC Voltar", True, COLOR_GRAY)
        self.screen.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 40))


# ─────────────────────────────────────────────────────────────
# Tela de Controles
# ─────────────────────────────────────────────────────────────

class ControlsScreen:
    """Exibe os controles dos dois jogadores."""

    P1_CONTROLS = [
        ("Andar esquerda", "A"),
        ("Andar direita",  "D"),
        ("Pular",          "W"),
        ("Agachar",        "S"),
        ("Atacar",         "E"),
        ("Defender",       "R"),
    ]

    P2_CONTROLS = [
        ("Andar esquerda", "←"),
        ("Andar direita",  "→"),
        ("Pular",          "↑"),
        ("Agachar",        "↓"),
        ("Atacar",         "NUM 1"),
        ("Defender",       "NUM 2"),
    ]

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()
        self.font_title  = pygame.font.SysFont("Impact", 52)
        self.font_header = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_item   = pygame.font.SysFont("Arial", 22)
        self.font_hint   = pygame.font.SysFont("Arial", 18)

    def update(self, events) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN):
                    return "back"
        return None

    def draw(self):
        draw_gradient_bg(self.screen, COLOR_BG_TOP, COLOR_BG_BOT)

        # Título
        title = self.font_title.render("CONTROLES", True, COLOR_ACCENT)
        self.screen.blit(title, (self.w // 2 - title.get_width() // 2, 30))

        # Linha
        pygame.draw.line(self.screen, COLOR_ACCENT,
                         (self.w // 2 - 250, 100), (self.w // 2 + 250, 100), 2)

        # Painéis de controles
        self._draw_player_controls(self.P1_CONTROLS, "JOGADOR 1", self.w // 4 - 120, 130, COLOR_P1)
        self._draw_player_controls(self.P2_CONTROLS, "JOGADOR 2", self.w * 3 // 4 - 120, 130, COLOR_P2)

        # Dica
        hint = self.font_hint.render("ESC / ENTER — Voltar ao Menu", True, COLOR_GRAY)
        self.screen.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 40))

    def _draw_player_controls(self, controls, title, x, y, color):
        panel_w = 280
        panel_h = 50 + len(controls) * 42
        draw_panel(self.screen, pygame.Rect(x, y, panel_w, panel_h))

        header = self.font_header.render(title, True, color)
        self.screen.blit(header, (x + panel_w // 2 - header.get_width() // 2, y + 10))
        pygame.draw.line(self.screen, color, (x + 10, y + 42), (x + panel_w - 10, y + 42), 1)

        for i, (action, key) in enumerate(controls):
            row_y = y + 54 + i * 42
            icon_bg = pygame.Rect(x + panel_w - 90, row_y + 2, 80, 30)
            pygame.draw.rect(self.screen, (40, 40, 70), icon_bg, border_radius=6)
            pygame.draw.rect(self.screen, color, icon_bg, 1, border_radius=6)

            action_surf = self.font_item.render(action, True, COLOR_WHITE)
            self.screen.blit(action_surf, (x + 14, row_y + 6))

            key_surf = self.font_item.render(key, True, color)
            kx = icon_bg.x + icon_bg.w // 2 - key_surf.get_width() // 2
            self.screen.blit(key_surf, (kx, row_y + 6))


# ─────────────────────────────────────────────────────────────
# Tela de Vitória
# ─────────────────────────────────────────────────────────────

class VictoryScreen:
    """Exibe o vencedor e opções de revanche ou voltar ao menu."""

    def __init__(self, screen: pygame.Surface, winner: int, character_name: str):
        self.screen = screen
        self.winner = winner
        self.character_name = character_name
        self.w = screen.get_width()
        self.h = screen.get_height()
        self.time = 0.0
        self.selected = 0
        self.options = [("REVANCHE", "rematch"), ("MENU", "menu")]

        self.font_big   = pygame.font.SysFont("Impact", 72)
        self.font_med   = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_item  = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_hint  = pygame.font.SysFont("Arial", 18)
        self.color = COLOR_P1 if winner == 1 else COLOR_P2

    def update(self, events) -> Optional[str]:
        self.time += 1 / 60
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.options[self.selected][1]
        return None

    def draw(self):
        draw_gradient_bg(self.screen, (10, 5, 20), (40, 10, 30))

        # Título pulsante
        pulse = 1.0 + 0.04 * math.sin(self.time * 4)
        title_text = f"JOGADOR {self.winner} VENCEU!"
        title = self.font_big.render(title_text, True, self.color)
        tw = int(title.get_width() * pulse)
        th = int(title.get_height() * pulse)
        title = pygame.transform.scale(title, (tw, th))
        self.screen.blit(title, (self.w // 2 - tw // 2, self.h // 4 - th // 2))

        # Nome do personagem
        name_surf = self.font_med.render(
            f"  {self.character_name.replace('_', ' ').title()}  ",
            True, COLOR_GOLD
        )
        self.screen.blit(name_surf, (self.w // 2 - name_surf.get_width() // 2, self.h // 4 + 80))

        # Linha
        pygame.draw.line(self.screen, self.color,
                         (self.w // 2 - 200, self.h // 2 + 20),
                         (self.w // 2 + 200, self.h // 2 + 20), 2)

        # Opções
        total_w = 0
        surfs = []
        for i, (label, _) in enumerate(self.options):
            is_sel = (i == self.selected)
            color = COLOR_GOLD if is_sel else COLOR_WHITE
            s = self.font_item.render(label, True, color)
            surfs.append((s, is_sel))
            total_w += s.get_width() + 60

        start_x = self.w // 2 - total_w // 2
        y = self.h // 2 + 50
        for s, is_sel in surfs:
            rect = pygame.Rect(start_x - 15, y - 8, s.get_width() + 30, s.get_height() + 16)
            if is_sel:
                draw_panel(self.screen, rect)
                pygame.draw.rect(self.screen, self.color, rect, 2, border_radius=8)
            self.screen.blit(s, (start_x, y))
            start_x += s.get_width() + 60

        hint = self.font_hint.render("← → Navegar   ENTER Confirmar", True, COLOR_GRAY)
        self.screen.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 40))
