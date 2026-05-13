"""
fighter.py - Classe do lutador (jogador).
Gerencia física, estados, animações e combate de cada personagem.
"""

import pygame
from typing import Dict, List, Tuple
from asset_loader import load_all_animations


# ─────────────────────────────────────────────────────────────
# Constantes de física e combate
# ─────────────────────────────────────────────────────────────
GRAVITY = 1800          # pixels/s²
JUMP_SPEED = -620       # pixels/s (negativo = para cima)
WALK_SPEED = 280        # pixels/s
MAX_HP = 100
ATTACK_DAMAGE = 10
ATTACK_RANGE = 90       # distância máxima para conectar ataque
ATTACK_DURATION = 0.35  # segundos que o estado de ataque dura
DEFEND_REDUCE = 0.4     # % de dano bloqueado ao defender (60% redução)
ANIMATION_FPS = 10      # frames por segundo das animações


class FighterState:
    """Estados possíveis do lutador."""
    IDLE = "idle"
    WALK = "walk"
    JUMP = "jump"
    CROUCH = "crouch"
    ATTACK = "attack"
    DEFEND = "defend"
    HURT = "hurt"
    DEAD = "dead"


class Fighter:
    """
    Representa um lutador no jogo.
    Gerencia física, animação, hitbox e combate.
    """

    def __init__(
        self,
        character_name: str,
        player_num: int,
        start_x: int,
        start_y: int,
        screen_width: int,
        screen_height: int,
        facing_right: bool = True,
        sprite_scale: float = 0.18,
        sprite_y_offset: int = 0,
    ):
        self.character_name = character_name
        self.player_num = player_num
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.facing_right = facing_right
        self.sprite_y_offset = sprite_y_offset

        # ── Física ──────────────────────────────────
        self.x = float(start_x)
        self.y = float(start_y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.floor_y = screen_height - 10  # Y do chão (ajustável)

        # ── HP ──────────────────────────────────────
        self.hp = MAX_HP
        self.max_hp = MAX_HP
        self.alive = True

        # ── Estado / Animação ────────────────────────
        self.state = FighterState.IDLE
        self.prev_state = FighterState.IDLE
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.frame_duration = 1.0 / ANIMATION_FPS

        # ── Timers de ação ───────────────────────────
        self.attack_timer = 0.0
        self.hurt_timer = 0.0
        self.has_hit = False   # evita múltiplos hits por ataque

        # ── Carregamento de animações ─────────────────
        self.animations: Dict[str, List[pygame.Surface]] = load_all_animations(
            character_name, scale=sprite_scale
        )

        # Garante que temos animação de hurt (usa idle como fallback)
        if FighterState.HURT not in self.animations:
            self.animations[FighterState.HURT] = self.animations[FighterState.IDLE]
        if FighterState.DEAD not in self.animations:
            self.animations[FighterState.DEAD] = self.animations[FighterState.IDLE]

        # Dimensões do sprite atual
        self._update_rect()

    # ─────────────────────────────────────────────
    # Propriedades
    # ─────────────────────────────────────────────

    @property
    def rect(self) -> pygame.Rect:
        frame = self._current_frame()
        w, h = frame.get_size()
        return pygame.Rect(int(self.x) - w // 2, int(self.y) - h + self.sprite_y_offset, w, h)

    @property
    def center_x(self) -> float:
        return self.x

    @property
    def feet_y(self) -> float:
        return self.y

    # ─────────────────────────────────────────────
    # Update principal
    # ─────────────────────────────────────────────

    def update(self, keys, opponent: "Fighter", dt: float):
        """
        Atualiza o lutador: lê input, aplica física, atualiza estado e animação.
        """
        if not self.alive:
            self._update_animation(dt)
            return

        # Atualiza direção (sempre olha para o oponente)
        self._update_facing(opponent)

        # Processa input (somente se não estiver em estado bloqueado)
        if self.state not in (FighterState.ATTACK, FighterState.HURT, FighterState.DEAD):
            self._process_input(keys, opponent, dt)

        # Timers de ação
        self._update_timers(dt)

        # Física
        self._apply_physics(dt)

        # Animação
        self._update_animation(dt)

    def _process_input(self, keys, opponent: "Fighter", dt: float):
        """Lê teclas e aplica movimentos/ações."""
        controls = self._get_controls()

        moving = False
        self.vel_x = 0.0

        # Agachar (prioridade sobre andar)
        if keys[controls["crouch"]]:
            self._set_state(FighterState.CROUCH)
            return

        # Andar
        if keys[controls["left"]]:
            self.vel_x = -WALK_SPEED
            moving = True
        if keys[controls["right"]]:
            self.vel_x = WALK_SPEED
            moving = True

        # Pular
        if keys[controls["jump"]] and self.on_ground:
            self.vel_y = JUMP_SPEED
            self.on_ground = False
            self._set_state(FighterState.JUMP)
            return

        # Defender
        if keys[controls["defend"]]:
            self._set_state(FighterState.DEFEND)
            return

        # Atacar
        if keys[controls["attack"]]:
            self._start_attack(opponent)
            return

        # Estado de idle/walk/jump
        if not self.on_ground:
            self._set_state(FighterState.JUMP)
        elif moving:
            self._set_state(FighterState.WALK)
        else:
            self._set_state(FighterState.IDLE)

    def _update_timers(self, dt: float):
        """Atualiza timers de ataque e hurt."""
        # Timer de ataque
        if self.state == FighterState.ATTACK:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self._set_state(FighterState.IDLE)
                self.has_hit = False

        # Timer de hurt
        if self.state == FighterState.HURT:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                if self.hp <= 0:
                    self._set_state(FighterState.DEAD)
                    self.alive = False
                else:
                    self._set_state(FighterState.IDLE)

    def _apply_physics(self, dt: float):
        """Aplica gravidade, movimento e colisão com o chão."""
        # Gravidade
        if not self.on_ground:
            self.vel_y += GRAVITY * dt

        # Posição
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        # Colisão com chão
        if self.y >= self.floor_y:
            self.y = self.floor_y
            self.vel_y = 0.0
            self.on_ground = True
            if self.state == FighterState.JUMP:
                self._set_state(FighterState.IDLE)

        # Limites da tela
        frame = self._current_frame()
        half_w = frame.get_width() // 2
        self.x = max(half_w, min(self.screen_width - half_w, self.x))

    def _update_animation(self, dt: float):
        """Avança o frame da animação atual."""
        self.anim_timer += dt
        frames = self._get_frames()

        if self.anim_timer >= self.frame_duration:
            self.anim_timer = 0.0
            if self.state in (FighterState.DEAD, FighterState.ATTACK, FighterState.HURT):
                # Fica no último frame, evitando loop visual antes de voltar para idle
                self.anim_frame = min(self.anim_frame + 1, len(frames) - 1)
            else:
                self.anim_frame = (self.anim_frame + 1) % len(frames)

    # ─────────────────────────────────────────────
    # Combate
    # ─────────────────────────────────────────────

    def _start_attack(self, opponent: "Fighter"):
        """Inicia um ataque."""
        self._set_state(FighterState.ATTACK)
        
        # A duração do ataque se adapta à quantidade de frames
        frames = self._get_frames()
        if len(frames) > 0:
            self.attack_timer = len(frames) * self.frame_duration
        else:
            self.attack_timer = ATTACK_DURATION
            
        self.has_hit = False

    def check_attack_hit(self, opponent: "Fighter"):
        """
        Verifica se o ataque atual acerta o oponente.
        Chamado externamente pela FightScene.
        """
        if self.state != FighterState.ATTACK or self.has_hit or not self.alive:
            return

        dist = abs(self.x - opponent.x)
        if dist <= ATTACK_RANGE and opponent.alive:
            self.has_hit = True
            damage = ATTACK_DAMAGE
            if opponent.state == FighterState.DEFEND:
                damage = int(damage * DEFEND_REDUCE)
            opponent.take_damage(damage)

    def take_damage(self, amount: int):
        """Recebe dano."""
        if not self.alive:
            return
        self.hp = max(0, self.hp - amount)
        self._set_state(FighterState.HURT)
        
        # A duração do stun de dano se adapta à quantidade de frames
        frames = self._get_frames()
        if len(frames) > 0:
            self.hurt_timer = len(frames) * self.frame_duration
        else:
            self.hurt_timer = 0.3

        if self.hp <= 0:
            self.alive = False
            self._set_state(FighterState.DEAD)

    # ─────────────────────────────────────────────
    # Desenho
    # ─────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        """Desenha o sprite do lutador na surface."""
        frame = self._current_frame()

        # Espelha o sprite se estiver olhando para a esquerda
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        w, h = frame.get_size()
        draw_x = int(self.x) - w // 2
        draw_y = int(self.y) - h + self.sprite_y_offset

        surface.blit(frame, (draw_x, draw_y))

        # Debug: hitbox (descomente para depurar)
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

    def draw_hud(self, surface: pygame.Surface):
        """
        Desenha a HUD do personagem (barra de vida + nome).
        Posicionada externamente pela FightScene.
        """
        pass  # HUD é desenhada pela FightScene

    # ─────────────────────────────────────────────
    # Utilitários internos
    # ─────────────────────────────────────────────

    def _set_state(self, new_state: str):
        """Muda o estado do lutador e reinicia a animação se mudou."""
        if new_state != self.state:
            self.prev_state = self.state
            self.state = new_state
            self.anim_frame = 0
            self.anim_timer = 0.0

    def _update_facing(self, opponent: "Fighter"):
        """Atualiza a direção de encarar o oponente."""
        self.facing_right = opponent.x > self.x

    def _get_frames(self) -> List[pygame.Surface]:
        """Retorna os frames da animação do estado atual."""
        state = self.state
        if state not in self.animations:
            state = FighterState.IDLE
        return self.animations[state]

    def _current_frame(self) -> pygame.Surface:
        """Retorna o frame atual da animação."""
        frames = self._get_frames()
        idx = self.anim_frame % len(frames)
        return frames[idx]

    def _update_rect(self):
        """Atualiza dimensões internas (chamado na inicialização)."""
        pass  # rect é calculado dinamicamente via property

    def _get_controls(self) -> Dict[str, int]:
        """
        Retorna o mapeamento de teclas para este jogador.
        P1: WASD + E (ataque) + R (defesa)
        P2: Setas + Numpad 1 (ataque) + Numpad 2 (defesa)
        """
        if self.player_num == 1:
            return {
                "left":   pygame.K_a,
                "right":  pygame.K_d,
                "jump":   pygame.K_w,
                "crouch": pygame.K_s,
                "attack": pygame.K_e,
                "defend": pygame.K_r,
            }
        else:
            return {
                "left":   pygame.K_LEFT,
                "right":  pygame.K_RIGHT,
                "jump":   pygame.K_UP,
                "crouch": pygame.K_DOWN,
                "attack": pygame.K_KP1,
                "defend": pygame.K_KP2,
            }
