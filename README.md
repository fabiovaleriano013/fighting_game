# ⚔ PyFighter 2D

Jogo de luta 2D desenvolvido em Python com Pygame.
Totalmente orientado a objetos, modular e expansível — adicione personagens e mapas sem tocar no código.

---

## 🚀 Instalação e Execução

### 1. Instale as dependências
```bash
pip install -r requirements.txt
```

### 2. Gere os assets de teste (sprites e mapas placeholder)
```bash
python generate_assets.py
```

### 3. Execute o jogo
```bash
python main.py
```

---

## 🎮 Controles

| Ação          | Jogador 1 | Jogador 2 |
|---------------|-----------|-----------|
| Andar ←       | A         | ←         |
| Andar →       | D         | →         |
| Pular         | W         | ↑         |
| Agachar       | S         | ↓         |
| Atacar        | E         | Numpad 1  |
| Defender      | R         | Numpad 2  |

**Navegação nos menus:** ↑↓ / A/D + ENTER  
**Voltar:** ESC

---

## 📁 Estrutura do Projeto

```
fighting_game/
│
├── main.py             # Ponto de entrada — inicializa Pygame e chama Game
├── game.py             # State machine — gerencia fluxo entre telas
├── fighter.py          # Classe Fighter — física, animação, combate
├── fight.py            # Cena de luta — HUD, timer, vitória
├── menu.py             # Telas: Menu Principal, Controles, Vitória
├── selector.py         # Telas: Seleção de Personagem e Mapa
├── asset_loader.py     # Carregamento dinâmico de assets das pastas
├── generate_assets.py  # Script auxiliar para gerar sprites placeholder
├── requirements.txt
│
└── assets/
    ├── personagens/
    │   ├── guerreiro/
    │   │   ├── idle/       (idle_00.png, idle_01.png, ...)
    │   │   ├── walk/
    │   │   ├── attack/
    │   │   ├── jump/
    │   │   ├── crouch/
    │   │   └── defend/
    │   └── ninja/
    │       └── ... (mesma estrutura)
    │
    └── mapas/
        ├── arena_volcano.png
        └── templo_antigo.png
```

---

## 👤 Como Adicionar um Novo Personagem

1. Crie uma pasta com o nome do personagem em `assets/personagens/`:
   ```
   assets/personagens/meu_personagem/
   ```

2. Dentro, crie uma pasta para cada ação:
   ```
   meu_personagem/
   ├── idle/
   ├── walk/
   ├── attack/
   ├── jump/
   ├── crouch/
   └── defend/
   ```

3. Coloque os frames de cada animação dentro de cada pasta:
   - Use arquivos `.png` (recomendado, suporta transparência)
   - Nomeie em ordem: `idle_00.png`, `idle_01.png`, `idle_02.png`, ...
   - O código carrega todos os arquivos da pasta **em ordem alfabética**

4. **Pronto!** O personagem aparecerá automaticamente na tela de seleção.

> **Dica sobre tamanho dos sprites:**  
> Sprites com ~80×100 pixels ficam bem com `sprite_scale=1.8` (padrão).  
> Ajuste `sprite_scale` em `fight.py` se precisar.

> **Pastas ausentes:**  
> Se uma ação não tiver pasta (ex: `defend/`), o jogo usará um sprite placeholder automático. Nenhum erro ocorrerá.

---

## 🗺 Como Adicionar um Novo Mapa

1. Coloque uma imagem em `assets/mapas/`:
   ```
   assets/mapas/meu_mapa.png
   ```

2. Formatos suportados: `.png`, `.jpg`, `.jpeg`, `.bmp`

3. Recomendação: **1024×576 pixels** (proporção 16:9). O jogo redimensiona automaticamente, mas a proporção original preserva a qualidade.

4. **Pronto!** O mapa aparecerá no seletor de mapas.

---

## 🏗 Arquitetura

```
main.py
  └── Game (game.py)          ← State Machine central
        ├── MainMenu           ← menu.py
        ├── ControlsScreen     ← menu.py
        ├── CharacterSelector  ← selector.py
        ├── MapSelector        ← selector.py
        ├── FightScene         ← fight.py
        │     ├── Fighter P1   ← fighter.py
        │     └── Fighter P2   ← fighter.py
        └── VictoryScreen      ← menu.py

asset_loader.py  ← usado por selector.py e fighter.py
```

### Fluxo de estados:
```
MAIN_MENU → CHARACTER_SELECT → MAP_SELECT → MUSIC_SELECT → FIGHTING → VICTORY
               ↑ (ESC)            ↑ (ESC)             ↑ (ESC)        ↓ (vencedor)
                                                          FIGHTING (revanche)
                                                          MAIN_MENU (menu)
```

---

## ⚙ Configurações Ajustáveis

| Arquivo       | Constante          | Descrição                        |
|---------------|--------------------|----------------------------------|
| `fighter.py`  | `GRAVITY`          | Força da gravidade               |
| `fighter.py`  | `JUMP_SPEED`       | Velocidade de pulo               |
| `fighter.py`  | `WALK_SPEED`       | Velocidade de caminhada          |
| `fighter.py`  | `ATTACK_DAMAGE`    | Dano por ataque                  |
| `fighter.py`  | `ATTACK_RANGE`     | Alcance do ataque (pixels)       |
| `fighter.py`  | `ATTACK_DURATION`  | Duração do estado de ataque (s)  |
| `fighter.py`  | `DEFEND_REDUCE`    | Multiplicador de dano ao defender|
| `fighter.py`  | `ANIMATION_FPS`    | FPS das animações dos sprites    |
| `fight.py`    | `FIGHT_DURATION`   | Duração da luta (segundos)       |
| `main.py`     | `FPS`              | FPS do jogo                      |

---

## 🔧 Dicas de Expansão

- **Adicionar sons:** Use `pygame.mixer.Sound` no `fighter.py` nos métodos `_start_attack` e `take_damage`.
- **Música de fundo:** Coloque faixas em `assets/musicas/` e escolha a trilha no menu de configuração ou antes da luta.
- **Menu personalizado:** Use `assets/imagens/` para imagens do menu inicial e `assets/musicas/` para músicas do menu.
- **Múltiplas rodadas:** Adicione um contador de rounds em `fight.py` e `game.py`.
- **Efeitos especiais:** Crie uma classe `Particle` e gerencie-a em `fight.py`.
- **Rede local:** Substitua a leitura de `keys` no `fighter.py` por dados de socket.
- **IA simples:** Crie uma subclasse `AIFighter(Fighter)` que sobrescreve `_process_input`.

---

## 📋 Requisitos

- Python 3.8+
- Pygame 2.1+
