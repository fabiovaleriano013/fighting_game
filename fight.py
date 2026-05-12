"""
fight.py - Cena de luta principal.
Gerencia dois lutadores, HUD (barras de vida), timer e detecção de vitória.
"""

import pygame
import math
from typing import List, Optional, Tuple
from fighter import Fighter, FighterState
from asset_loader import load_map_image
from menu import (
    draw_gradient_bg,
    COLOR_BG_TOP, COLOR_BG_BOT,
    COLOR_ACCENT, COLOR_WHITE, COLOR_GRAY, COLOR_GOLD,
    COLOR_P1, COLOR_P2
)


# ─────────────────────────────────────────────────────────────
# Constantes da luta
# ─────────────────────────────────────────────────────────────
FIGHT_DURATION = 99.0    # segundos de luta
HUD_HEIGHT = 80          # altura do painel HUD no topo
ROUND_START_DELAY = 2.0  # segundos de "Lute!" antes de liberar controles
ROUND_END_DELAY = 2.5    # segundos de tela de vitória local antes de notificar


class FightScene:
    """
    Cena principal de luta entre dois jogadores.
    Gerencia: mapa, lutadores, HUD, timer e condição de vitória.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        character_names: List[str],
        map_path: str
    ):
        self.screen = screen
        self.w = screen.get_width()
        self.h = screen.get_height()

        # Fontes
        self.font_big   = pygame.font.SysFont("Impact", 72)
        self.font_med   = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_hud   = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_timer = pygame.font.SysFont("Impact", 44)

        # Carrega o mapa de fundo
        self.background = load_map_image(map_path, (self.w, self.h))

        # Posição do chão (levando em conta HUD no topo)
        floor_y = self.h - 80

        # Cria os dois lutadores
        self.p1 = Fighter(
            character_name=character_names[0],
            player_num=1,
            start_x=self.w // 4,
            start_y=floor_y,
            screen_width=self.w,
            screen_height=self.h,
            facing_right=True,
            sprite_scale=1.8,
        )
        self.p1.floor_y = floor_y

        self.p2 = Fighter(
            character_name=character_names[1],
            player_num=2,
            start_x=self.w * 3 // 4,
            start_y=floor_y,
            screen_width=self.w,
            screen_height=self.h,
            facing_right=False,
            sprite_scale=1.8,
        )
        self.p2.floor_y = floor_y

        # Timer da luta
        self.time_left = FIGHT_DURATION
        self.fight_active = False
        self.start_timer = ROUND_START_DELAY
        self.end_timer = 0.0
        self.winner = None  # None, 1, ou 2 (empate → 0)
        self.fight_ended = False

        # Efeitos visuais
        self.hit_flash = 0.0  # timer para flash de tela ao levar hit

    # ─────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────

    def update(self, events, dt: float) -> Optional[int]:
        """
        Atualiza a cena de luta.
        Retorna:
            None        → luta em andamento
            1 ou 2      → vencedor
            0           → empate (ambos sem vida / tempo esgotado)
        """
        keys = pygame.key.get_pressed()

        # Fase de início (conta regressiva "LUTE!")
        if not self.fight_active:
            self.start_timer -= dt
            if self.start_timer <= 0:
                self.fight_active = True
            return None

        # Fase de fim (exibe resultado por um tempo antes de notificar)
        if self.fight_ended:
            self.end_timer -= dt
            if self.end_timer <= 0:
                return self.winner
            # Animação continua mas sem input
            self.p1.update(pygame.key.get_pressed(), self.p2, dt)
            self.p2.update(pygame.key.get_pressed(), self.p1, dt)
            return None

        # Atualiza lutadores
        self.p1.update(keys, self.p2, dt)
        self.p2.update(keys, self.p1, dt)

        # Verifica colisões de ataque
        self.p1.check_attack_hit(self.p2)
        self.p2.check_attack_hit(self.p1)

        # Flash ao levar dano
        if (self.p1.state == FighterState.HURT or
                self.p2.state == FighterState.HURT):
            self.hit_flash = 0.1

        if self.hit_flash > 0:
            self.hit_flash -= dt

        # Timer da luta
        self.time_left -= dt

        # Verifica condição de vitória
        self._check_victory()

        return None

    def _check_victory(self):
        """Checa se alguém venceu (HP zerado ou tempo esgotado)."""
        if self.fight_ended:
            return

        p1_dead = not self.p1.alive
        p2_dead = not self.p2.alive
        time_up = self.time_left <= 0

        if p1_dead and p2_dead:
            self._end_fight(0)  # empate
        elif p2_dead:
            self._end_fight(1)
        elif p1_dead:
            self._end_fight(2)
        elif time_up:
            # Quem tem mais HP vence
            if self.p1.hp > self.p2.hp:
                self._end_fight(1)
            elif self.p2.hp > self.p1.hp:
                self._end_fight(2)
            else:
                self._end_fight(0)  # empate

    def _end_fight(self, winner: int):
        """Encerra a luta com um vencedor (ou empate)."""
        self.fight_ended = True
        self.winner = winner
        self.end_timer = ROUND_END_DELAY

    # ─────────────────────────────────────────────
    # Desenho
    # ─────────────────────────────────────────────

    def draw(self):
        """Desenha tudo: mapa, chão, lutadores, HUD."""
        # Fundo (mapa)
        self.screen.blit(self.background, (0, 0))

        # Chão decorativo
        self._draw_floor()

        # Flash de hit (overlay vermelho)
        if self.hit_flash > 0:
            alpha = int(self.hit_flash * 800)
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((255, 50, 50, min(alpha, 60)))
            self.screen.blit(overlay, (0, 0))

        # Lutadores
        self.p1.draw(self.screen)
        self.p2.draw(self.screen)

        # HUD no topo
        self._draw_hud()

        # Mensagem de início / fim
        if not self.fight_active:
            self._draw_start_message()
        elif self.fight_ended:
            self._draw_end_message()

    def _draw_floor(self):
        """Desenha uma linha de chão estilizada."""
        floor_y = self.h - 80
        # Sombra
        for i in range(8):
            alpha = 120 - i * 15
            s = pygame.Surface((self.w, 2), pygame.SRCALPHA)
            s.fill((0, 0, 0, alpha))
            self.screen.blit(s, (0, floor_y + i))

        pygame.draw.line(self.screen, (255, 255, 255, 80),
                         (0, floor_y), (self.w, floor_y), 1)

    def _draw_hud(self):
        """Desenha o HUD completo: barras de vida, nomes, timer."""
        # Painel de fundo do HUD
        hud_surf = pygame.Surface((self.w, HUD_HEIGHT), pygame.SRCALPHA)
        hud_surf.fill((10, 10, 25, 200))
        self.screen.blit(hud_surf, (0, 0))
        pygame.draw.line(self.screen, (80, 80, 120), (0, HUD_HEIGHT), (self.w, HUD_HEIGHT), 2)

        bar_w = self.w // 3
        bar_h = 22
        bar_y = 30

        # ── Barra de vida P1 ──────────────────────────────
        p1_ratio = max(0, self.p1.hp / self.p1.max_hp)
        # Fundo (cinza escuro)
        pygame.draw.rect(self.screen, (40, 40, 50),
                         (20, bar_y, bar_w, bar_h), border_radius=4)
        # Barra de HP (vermelho → verde)
        hp_color = self._hp_color(p1_ratio)
        pygame.draw.rect(self.screen, hp_color,
                         (20, bar_y, int(bar_w * p1_ratio), bar_h), border_radius=4)
        # Borda
        pygame.draw.rect(self.screen, COLOR_P1,
                         (20, bar_y, bar_w, bar_h), 2, border_radius=4)

        # Nome P1
        n1 = self.font_hud.render(
            self.p1.character_name.replace("_", " ").title(), True, COLOR_P1
        )
        self.screen.blit(n1, (20, bar_y - 22))

        # HP valor P1
        hp1_txt = self.font_hud.render(f"{self.p1.hp}/{self.p1.max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp1_txt, (20 + bar_w // 2 - hp1_txt.get_width() // 2, bar_y + 2))

        # ── Barra de vida P2 ──────────────────────────────
        p2_ratio = max(0, self.p2.hp / self.p2.max_hp)
        x2 = self.w - 20 - bar_w
        # Fundo
        pygame.draw.rect(self.screen, (40, 40, 50),
                         (x2, bar_y, bar_w, bar_h), border_radius=4)
        # Barra (cresce da direita para a esquerda)
        hp_color2 = self._hp_color(p2_ratio)
        hp2_w = int(bar_w * p2_ratio)
        pygame.draw.rect(self.screen, hp_color2,
                         (x2 + bar_w - hp2_w, bar_y, hp2_w, bar_h), border_radius=4)
        # Borda
        pygame.draw.rect(self.screen, COLOR_P2,
                         (x2, bar_y, bar_w, bar_h), 2, border_radius=4)

        # Nome P2
        n2 = self.font_hud.render(
            self.p2.character_name.replace("_", " ").title(), True, COLOR_P2
        )
        self.screen.blit(n2, (self.w - 20 - n2.get_width(), bar_y - 22))

        # HP valor P2
        hp2_txt = self.font_hud.render(f"{self.p2.hp}/{self.p2.max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp2_txt, (x2 + bar_w // 2 - hp2_txt.get_width() // 2, bar_y + 2))

        # ── Timer central ─────────────────────────────────
        secs = max(0, int(self.time_left))
        timer_color = COLOR_ACCENT if secs <= 10 else COLOR_WHITE
        timer_surf = self.font_timer.render(str(secs), True, timer_color)
        tx = self.w // 2 - timer_surf.get_width() // 2
        self.screen.blit(timer_surf, (tx, 10))

        # Labels P1 / P2
        l1 = self.font_small.render("P1", True, COLOR_P1)
        self.screen.blit(l1, (20, 5))
        l2 = self.font_small.render("P2", True, COLOR_P2)
        self.screen.blit(l2, (self.w - 20 - l2.get_width(), 5))

    def _draw_start_message(self):
        """Exibe a mensagem de contagem regressiva antes da luta."""
        secs = math.ceil(self.start_timer)
        if self.start_timer > 0.5:
            msg = str(secs)
            color = COLOR_GOLD
        else:
            msg = "LUTE!"
            color = COLOR_ACCENT

        surf = self.font_big.render(msg, True, color)
        # Sombra
        shadow = self.font_big.render(msg, True, (0, 0, 0))
        x = self.w // 2 - surf.get_width() // 2
        y = self.h // 2 - surf.get_height() // 2
        self.screen.blit(shadow, (x + 3, y + 3))
        self.screen.blit(surf, (x, y))

    def _draw_end_message(self):
        """Exibe a mensagem de vitória local."""
        if self.winner == 0:
            msg = "EMPATE!"
            color = COLOR_GOLD
        else:
            msg = f"JOGADOR {self.winner} VENCEU!"
            color = COLOR_P1 if self.winner == 1 else COLOR_P2

        # Overlay escuro
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        surf = self.font_big.render(msg, True, color)
        shadow = self.font_big.render(msg, True, (0, 0, 0))
        x = self.w // 2 - surf.get_width() // 2
        y = self.h // 2 - surf.get_height() // 2
        self.screen.blit(shadow, (x + 4, y + 4))
        self.screen.blit(surf, (x, y))

    def _hp_color(self, ratio: float) -> Tuple[int, int, int]:
        """Retorna uma cor interpolada de verde (cheio) para vermelho (vazio)."""
        r = int(255 * (1 - ratio))
        g = int(255 * ratio)
        b = 30
        return (max(0, min(255, r)), max(0, min(255, g)), b)
