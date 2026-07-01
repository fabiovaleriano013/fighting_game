"""
game.py - Gerenciador principal de estados do jogo.
Controla o fluxo entre: Menu → Controles → Seleção de Personagem → Seleção de Mapa → Luta → Vitória
"""

import pygame
import sys
from asset_loader import load_map_image
from menu import MainMenu, ControlsScreen, VictoryScreen, MenuConfigScreen
from selector import CharacterSelector, MapSelector, MusicSelector
from fight import FightScene


class GameState:
    """Enum de estados do jogo."""
    MAIN_MENU = "main_menu"
    CONTROLS = "controls"
    CHARACTER_SELECT = "character_select"
    MAP_SELECT = "map_select"
    MUSIC_SELECT = "music_select"
    MENU_CONFIG = "menu_config"
    FIGHTING = "fighting"
    VICTORY = "victory"


class Game:
    """
    Classe principal que gerencia todos os estados do jogo.
    Atua como um controlador central (State Machine).
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, fps: int):
        self.screen = screen
        self.clock = clock
        self.fps = fps
        self.state = GameState.MAIN_MENU
        self.running = True

        # Dados compartilhados entre telas
        self.selected_characters = [None, None]  # [P1, P2]
        self.selected_map = None
        self.selected_music = None
        self.selected_menu_image = None
        self.selected_menu_music = None
        self.current_menu_music_path = None
        self.winner = None  # 1 ou 2

        # Inicializa telas
        self._init_screens()

    def _init_screens(self):
        """Instancia todas as telas do jogo."""
        self.main_menu = MainMenu(self.screen)
        self.controls_screen = ControlsScreen(self.screen)
        self.char_selector = CharacterSelector(self.screen)
        self.map_selector = MapSelector(self.screen)
        self.menu_config_screen = MenuConfigScreen(self.screen)
        self.music_selector = MusicSelector(self.screen)
        self.fight_scene = None   # Criado na hora de lutar
        self.victory_screen = None  # Criado após vitória

    def run(self):
        """Loop principal do jogo."""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time em segundos

            if self.state == GameState.MAIN_MENU:
                self._handle_main_menu(dt)

            elif self.state == GameState.CONTROLS:
                self._handle_controls(dt)

            elif self.state == GameState.CHARACTER_SELECT:
                self._handle_character_select(dt)

            elif self.state == GameState.MAP_SELECT:
                self._handle_map_select(dt)

            elif self.state == GameState.MUSIC_SELECT:
                self._handle_music_select(dt)

            elif self.state == GameState.MENU_CONFIG:
                self._handle_menu_config(dt)

            elif self.state == GameState.FIGHTING:
                self._handle_fighting(dt)

            elif self.state == GameState.VICTORY:
                self._handle_victory(dt)

            pygame.display.flip()

    # ─────────────────────────────────────────────
    # Handlers de cada estado
    # ─────────────────────────────────────────────

    def _handle_main_menu(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

        self._ensure_menu_music()

        result = self.main_menu.update(events)
        self.main_menu.draw()

        if result == "play":
            self.state = GameState.CHARACTER_SELECT
        elif result == "controls":
            self.state = GameState.CONTROLS
        elif result == "menu_config":
            self.menu_config_screen = MenuConfigScreen(
                self.screen,
                self.selected_menu_image,
                self.selected_menu_music
            )
            self.state = GameState.MENU_CONFIG
        elif result == "quit":
            self._quit()

    def _handle_controls(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

        result = self.controls_screen.update(events)
        self.controls_screen.draw()

        if result == "back":
            self.state = GameState.MAIN_MENU

    def _handle_character_select(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

        result = self.char_selector.update(events)
        self.char_selector.draw()

        if result == "back":
            self.state = GameState.MAIN_MENU
        elif result == "confirm":
            self.selected_characters = self.char_selector.get_selected()
            self.state = GameState.MAP_SELECT

    def _handle_map_select(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

        result = self.map_selector.update(events)
        self.map_selector.draw()

        if result == "back":
            self.state = GameState.CHARACTER_SELECT
        elif result == "confirm":
            self.selected_map = self.map_selector.get_selected()
            self.music_selector = MusicSelector(self.screen)
            self.state = GameState.MUSIC_SELECT

    def _handle_menu_config(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

        result = self.menu_config_screen.update(events)
        self.menu_config_screen.draw()

        if result == "back":
            self.selected_menu_image = self.menu_config_screen.get_selected_image()
            self.selected_menu_music = self.menu_config_screen.get_selected_music()
            self._apply_menu_settings()
            self.state = GameState.MAIN_MENU

    def _handle_music_select(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

        result = self.music_selector.update(events)
        self.music_selector.draw()

        if result == "back":
            self.state = GameState.MAP_SELECT
        elif result == "confirm":
            self.selected_music = self.music_selector.get_selected()
            self._start_fight()

    def _handle_fighting(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

        result = self.fight_scene.update(events, dt)
        self.fight_scene.draw()

        if result is not None:
            pygame.mixer.music.stop()
            self.winner = result
            self.victory_screen = VictoryScreen(
                self.screen,
                self.winner,
                self.selected_characters[self.winner - 1]
            )
            self.state = GameState.VICTORY

    def _handle_victory(self, dt):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

        result = self.victory_screen.update(events)
        self.victory_screen.draw()

        if result == "rematch":
            self._start_fight()
        elif result == "menu":
            self.selected_characters = [None, None]
            self.selected_map = None
            self.winner = None
            self.char_selector = CharacterSelector(self.screen)
            self.map_selector = MapSelector(self.screen)
            self.state = GameState.MAIN_MENU

    # ─────────────────────────────────────────────
    # Utilitários
    # ─────────────────────────────────────────────

    def _start_fight(self):
        """Cria uma nova cena de luta com os personagens, mapa e música selecionados."""
        self.fight_scene = FightScene(
            self.screen,
            self.selected_characters,
            self.selected_map
        )

        pygame.mixer.music.stop()
        if self.selected_music:
            try:
                pygame.mixer.music.load(self.selected_music)
                pygame.mixer.music.play(-1)
            except pygame.error as e:
                print(f"[Game] Erro ao carregar música {self.selected_music}: {e}")

        self.state = GameState.FIGHTING

    def _apply_menu_settings(self):
        if self.selected_menu_image:
            try:
                image = load_map_image(self.selected_menu_image, (self.screen.get_width(), self.screen.get_height()))
                self.main_menu.set_background_image(image)
            except pygame.error as e:
                print(f"[Game] Erro ao carregar imagem de menu {self.selected_menu_image}: {e}")
                self.main_menu.set_background_image(None)
        else:
            self.main_menu.set_background_image(None)

        self.current_menu_music_path = None
        self._ensure_menu_music()

    def _ensure_menu_music(self):
        if self.selected_menu_music:
            if (self.current_menu_music_path != self.selected_menu_music or
                    not pygame.mixer.music.get_busy()):
                try:
                    pygame.mixer.music.load(self.selected_menu_music)
                    pygame.mixer.music.play(-1)
                    self.current_menu_music_path = self.selected_menu_music
                except pygame.error as e:
                    print(f"[Game] Erro ao carregar música do menu {self.selected_menu_music}: {e}")
                    self.current_menu_music_path = None
        else:
            pygame.mixer.music.stop()
            self.current_menu_music_path = None

    def _quit(self):
        self.running = False
        pygame.quit()
        sys.exit()
