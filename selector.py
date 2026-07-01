"""
selector.py - Telas de seleção de personagem e mapa.
Carrega personagens e mapas dinamicamente das pastas de assets.
"""

import pygame
import os
from typing import List, Optional, Tuple
from asset_loader import (
    get_character_names, get_map_paths, get_music_paths,
    load_character_thumbnail, load_map_thumbnail
)
from menu import (
    draw_gradient_bg, draw_panel,
    COLOR_BG_TOP, COLOR_BG_BOT, COLOR_ACCENT,
    COLOR_WHITE, COLOR_GRAY, COLOR_GOLD,
    COLOR_P1, COLOR_P2, COLOR_DARK
)


# ─────────────────────────────────────────────────────────────
# Seletor de Personagens
# ─────────────────────────────────────────────────────────────

class CharacterSelector:
    """
    Tela de seleção de personagem para dois jogadores.
    P1 usa A/D para navegar e E para confirmar.
    P2 usa ←/→ para navegar e NUM1 para confirmar.
    ESC volta ao menu.
    """

    THUMB_SIZE = (120, 130)
    CARD_W = 140
    CARD_H = 170
    COLS = 5  # máximo de personagens por linha

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()

        # Fontes
        self.font_title  = pygame.font.SysFont("Impact", 50)
        self.font_sub    = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_name   = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_hint   = pygame.font.SysFont("Arial", 16)

        # Carrega personagens
        self.characters: List[str] = get_character_names()
        if not self.characters:
            self.characters = ["(Nenhum personagem encontrado)"]

        # Carrega thumbnails
        self.thumbnails = {}
        for name in self.characters:
            if name.startswith("("):
                surf = pygame.Surface(self.THUMB_SIZE)
                surf.fill((60, 60, 80))
            else:
                surf = load_character_thumbnail(name, self.THUMB_SIZE)
            self.thumbnails[name] = surf

        # Estado de seleção
        # cursor: índice no grid para cada jogador
        self.cursor = [0, min(1, len(self.characters) - 1)]
        # confirmed[i] = True se o jogador i já confirmou
        self.confirmed = [False, False]

    def update(self, events) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Voltar
                if event.key == pygame.K_ESCAPE:
                    return "back"

                # P1 navega (só se não confirmou)
                if not self.confirmed[0]:
                    if event.key == pygame.K_a:
                        self.cursor[0] = (self.cursor[0] - 1) % len(self.characters)
                    elif event.key == pygame.K_d:
                        self.cursor[0] = (self.cursor[0] + 1) % len(self.characters)
                    elif event.key == pygame.K_e:
                        if not self.characters[self.cursor[0]].startswith("("):
                            self.confirmed[0] = True
                else:
                    # P1 já confirmou, permite desconfirmar
                    if event.key == pygame.K_e:
                        self.confirmed[0] = False

                # P2 navega (só se não confirmou)
                if not self.confirmed[1]:
                    if event.key == pygame.K_LEFT:
                        self.cursor[1] = (self.cursor[1] - 1) % len(self.characters)
                    elif event.key == pygame.K_RIGHT:
                        self.cursor[1] = (self.cursor[1] + 1) % len(self.characters)
                    elif event.key in (pygame.K_KP1, pygame.K_1):
                        if not self.characters[self.cursor[1]].startswith("("):
                            self.confirmed[1] = True
                else:
                    # P2 já confirmou, permite desconfirmar
                    if event.key in (pygame.K_KP1, pygame.K_1):
                        self.confirmed[1] = False

        # Se ambos confirmaram → avança
        if self.confirmed[0] and self.confirmed[1]:
            return "confirm"

        return None

    def get_selected(self) -> List[str]:
        """Retorna [nome_p1, nome_p2]."""
        return [
            self.characters[self.cursor[0]],
            self.characters[self.cursor[1]],
        ]

    def draw(self):
        draw_gradient_bg(self.screen, COLOR_BG_TOP, COLOR_BG_BOT)

        # Título
        title = self.font_title.render("SELECIONE OS PERSONAGENS", True, COLOR_ACCENT)
        self.screen.blit(title, (self.w // 2 - title.get_width() // 2, 18))
        pygame.draw.line(self.screen, COLOR_ACCENT,
                         (self.w // 2 - 280, 74), (self.w // 2 + 280, 74), 2)

        # Grid de personagens
        n = len(self.characters)
        cols = min(self.COLS, n)
        rows = (n + cols - 1) // cols
        grid_w = cols * (self.CARD_W + 12)
        grid_x = self.w // 2 - grid_w // 2
        grid_y = 90

        for i, name in enumerate(self.characters):
            col = i % cols
            row = i // cols
            x = grid_x + col * (self.CARD_W + 12)
            y = grid_y + row * (self.CARD_H + 12)

            # Borda de seleção
            sel_p1 = (self.cursor[0] == i)
            sel_p2 = (self.cursor[1] == i)
            border_color = None
            if sel_p1 and sel_p2:
                border_color = COLOR_GOLD
            elif sel_p1:
                border_color = COLOR_P1
            elif sel_p2:
                border_color = COLOR_P2

            card_rect = pygame.Rect(x, y, self.CARD_W, self.CARD_H)
            draw_panel(self.screen, card_rect, alpha=180)

            if border_color:
                pygame.draw.rect(self.screen, border_color, card_rect, 3, border_radius=8)

            # Thumbnail
            thumb = self.thumbnails.get(name)
            if thumb:
                tw, th = thumb.get_size()
                tx = x + self.CARD_W // 2 - tw // 2
                ty = y + 10
                self.screen.blit(thumb, (tx, ty))

            # Nome do personagem
            display_name = name.replace("_", " ").title()
            name_surf = self.font_name.render(display_name, True, COLOR_WHITE)
            nx = x + self.CARD_W // 2 - name_surf.get_width() // 2
            self.screen.blit(name_surf, (nx, y + self.CARD_H - 22))

            # Badges P1/P2
            if sel_p1:
                badge = self.font_name.render("P1", True, COLOR_P1)
                self.screen.blit(badge, (x + 6, y + 6))
                if self.confirmed[0]:
                    ok = self.font_name.render("", True, COLOR_P1)
                    self.screen.blit(ok, (x + self.CARD_W - 22, y + 6))
            if sel_p2:
                badge = self.font_name.render("P2", True, COLOR_P2)
                self.screen.blit(badge, (x + self.CARD_W - 28, y + 6 + (16 if sel_p1 else 0)))
                if self.confirmed[1]:
                    ok = self.font_name.render("", True, COLOR_P2)
                    self.screen.blit(ok, (x + self.CARD_W - 22, y + 22))

        # Painel de instrução dos jogadores
        self._draw_player_status(grid_y + rows * (self.CARD_H + 12) + 20)

        # Dica
        hint = self.font_hint.render("ESC — Voltar", True, COLOR_GRAY)
        self.screen.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 30))

    def _draw_player_status(self, y):
        # P1
        p1_conf = self.confirmed[0]
        p1_name = self.characters[self.cursor[0]].replace("_", " ").title()
        p1_text = f"P1: {p1_name}  {'✔ Confirmado' if p1_conf else '— A/D navegar | E confirmar'}"
        p1_surf = self.font_hint.render(p1_text, True, COLOR_P1)
        self.screen.blit(p1_surf, (self.w // 2 - p1_surf.get_width() // 2, y))

        # P2
        p2_conf = self.confirmed[1]
        p2_name = self.characters[self.cursor[1]].replace("_", " ").title()
        p2_text = f"P2: {p2_name}  {'✔ Confirmado' if p2_conf else '— ←/→ navegar | NUM1 / 1 confirmar'}"
        p2_surf = self.font_hint.render(p2_text, True, COLOR_P2)
        self.screen.blit(p2_surf, (self.w // 2 - p2_surf.get_width() // 2, y + 24))


# ─────────────────────────────────────────────────────────────
# Seletor de Mapa
# ─────────────────────────────────────────────────────────────

class MapSelector:
    """
    Tela de seleção de mapa.
    ←/→ para navegar, ENTER para confirmar, ESC para voltar.
    """

    THUMB_SIZE = (280, 160)

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()

        self.font_title = pygame.font.SysFont("Impact", 50)
        self.font_name  = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_hint  = pygame.font.SysFont("Arial", 16)
        self.font_arrow = pygame.font.SysFont("Arial", 40, bold=True)

        # Carrega mapas
        self.map_paths: List[str] = get_map_paths()
        if not self.map_paths:
            self.map_paths = ["__placeholder__"]

        self.cursor = 0

        # Carrega thumbnails
        self.thumbnails = {}
        for path in self.map_paths:
            if path == "__placeholder__":
                from asset_loader import _create_placeholder_map
                self.thumbnails[path] = _create_placeholder_map(self.THUMB_SIZE)
            else:
                self.thumbnails[path] = load_map_thumbnail(path, self.THUMB_SIZE)

    def update(self, events) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.cursor = (self.cursor - 1) % len(self.map_paths)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.cursor = (self.cursor + 1) % len(self.map_paths)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "confirm"
        return None

    def get_selected(self) -> str:
        """Retorna o caminho do mapa selecionado."""
        return self.map_paths[self.cursor]

    def draw(self):
        draw_gradient_bg(self.screen, COLOR_BG_TOP, COLOR_BG_BOT)

        # Título
        title = self.font_title.render("SELECIONE O MAPA", True, COLOR_ACCENT)
        self.screen.blit(title, (self.w // 2 - title.get_width() // 2, 18))
        pygame.draw.line(self.screen, COLOR_ACCENT,
                         (self.w // 2 - 220, 74), (self.w // 2 + 220, 74), 2)

        # Thumbnail do mapa atual
        path = self.map_paths[self.cursor]
        thumb = self.thumbnails.get(path)
        if thumb:
            tw, th = thumb.get_size()
            tx = self.w // 2 - tw // 2
            ty = self.h // 2 - th // 2 - 20

            # Borda ao redor do mapa
            border = pygame.Rect(tx - 4, ty - 4, tw + 8, th + 8)
            pygame.draw.rect(self.screen, COLOR_ACCENT, border, 3, border_radius=10)
            self.screen.blit(thumb, (tx, ty))

            # Nome do mapa
            if path == "__placeholder__":
                map_name = "Mapa Padrão"
            else:
                map_name = os.path.splitext(os.path.basename(path))[0].replace("_", " ").title()
            name_surf = self.font_name.render(map_name, True, COLOR_WHITE)
            self.screen.blit(name_surf, (self.w // 2 - name_surf.get_width() // 2, ty + th + 14))

        # Setas de navegação
        if len(self.map_paths) > 1:
            left_arrow = self.font_arrow.render("", True, COLOR_ACCENT)
            right_arrow = self.font_arrow.render("", True, COLOR_ACCENT)
            self.screen.blit(left_arrow, (self.w // 2 - self.THUMB_SIZE[0] // 2 - 50,
                                          self.h // 2 - 20))
            self.screen.blit(right_arrow, (self.w // 2 + self.THUMB_SIZE[0] // 2 + 14,
                                           self.h // 2 - 20))

        # Contador
        counter = self.font_hint.render(
            f"{self.cursor + 1} / {len(self.map_paths)}", True, COLOR_GRAY
        )
        self.screen.blit(counter, (self.w // 2 - counter.get_width() // 2, self.h - 58))

        # Dica
        hint = self.font_hint.render("← → Navegar   ENTER Confirmar   ESC Voltar", True, COLOR_GRAY)
        self.screen.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 30))


class MusicSelector:
    """
    Tela de seleção de música de fundo.
    ←/→ para navegar, ENTER para confirmar, ESC para voltar.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()

        self.font_title = pygame.font.SysFont("Impact", 50)
        self.font_name = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_hint = pygame.font.SysFont("Arial", 16)
        self.font_info = pygame.font.SysFont("Arial", 18)

        self.music_paths: List[str] = get_music_paths()
        if not self.music_paths:
            self.music_paths = ["__placeholder__"]

        self.cursor = 0

    def update(self, events) -> Optional[str]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.cursor = (self.cursor - 1) % len(self.music_paths)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.cursor = (self.cursor + 1) % len(self.music_paths)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "confirm"
        return None

    def get_selected(self) -> Optional[str]:
        if self.music_paths[self.cursor] == "__placeholder__":
            return None
        return self.music_paths[self.cursor]

    def draw(self):
        draw_gradient_bg(self.screen, COLOR_BG_TOP, COLOR_BG_BOT)

        title = self.font_title.render("SELECIONE A MÚSICA", True, COLOR_ACCENT)
        self.screen.blit(title, (self.w // 2 - title.get_width() // 2, 18))
        pygame.draw.line(self.screen, COLOR_ACCENT,
                         (self.w // 2 - 260, 74), (self.w // 2 + 260, 74), 2)

        if self.music_paths[self.cursor] == "__placeholder__":
            info = self.font_info.render(
                "Nenhuma música encontrada em assets/musicas/", True, COLOR_WHITE)
            hint = self.font_info.render(
                "Coloque arquivos .mp3, .wav, .ogg ou .flac na pasta e reinicie.", True, COLOR_GRAY)
            self.screen.blit(info, (self.w // 2 - info.get_width() // 2, self.h // 2 - 20))
            self.screen.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h // 2 + 12))
        else:
            music_name = os.path.splitext(os.path.basename(self.music_paths[self.cursor]))[0]
            music_name = music_name.replace("_", " ").title()
            music_surf = self.font_name.render(music_name, True, COLOR_WHITE)
            self.screen.blit(music_surf, (self.w // 2 - music_surf.get_width() // 2, self.h // 2 - 24))

            detail = self.font_info.render(
                f"Arquivo: {os.path.basename(self.music_paths[self.cursor])}", True, COLOR_GRAY)
            self.screen.blit(detail, (self.w // 2 - detail.get_width() // 2, self.h // 2 + 24))

        prompt = self.font_hint.render(
            "← → Navegar   ENTER Confirmar   ESC Voltar", True, COLOR_GRAY)
        self.screen.blit(prompt, (self.w // 2 - prompt.get_width() // 2, self.h - 40))
