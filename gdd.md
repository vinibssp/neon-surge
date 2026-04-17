# Game Design Document: Neon Surge (Godot Rebirth)

## 1. Visão Geral
**Neon Surge** é um jogo de ação arcade 2D em ritmo acelerado, inspirado em bullet-hells modernos e roguelites minimalistas. O jogador controla uma entidade de energia em arenas abstratas, enfrentando ondas de inimigos geométricos com padrões de ataque complexos. O foco está na precisão do movimento, no uso estratégico de *Dash* e *Parry*, e na sobrevivência contra eventos ambientais dinâmicos.

### Pilares de Design
- **Minimalismo de Alto Contraste:** Visual baseado em formas geométricas e cores neon pulsantes.
- **Dificuldade Escalável:** Inimigos introduzidos progressivamente com padrões de "balas" cada vez mais densos.
- **Feedback Cinético:** Cada impacto e explosão deve ser sentido através de efeitos visuais (screenshake, flashes, partículas).
- **Mecânicas de Risco-Recompensa:** O Parry exige tempo perfeito, mas recompensa com energia e controle de grupo.

---

## 2. Mecânicas de Gameplay

### 2.1 Movimentação e Combate (The Player)
- **Movimento:** 8 direções com aceleração e atrito configuráveis.
- **Dash (Espaço):** Impulso rápido que concede invulnerabilidade temporária (I-frames). Consome energia fixa.
- **Parry (J):** Onda circular de curto alcance. Se atingir um projétil ou inimigo no frame ativo:
    - Projéteis são neutralizados ou refletidos.
    - Inimigos entram em estado de **Stagger** (paralisia visual e pausa em ataques).
    - Regenera uma porção da barra de energia.
- **Nuclear Bomb (I):** Limpa todos os inimigos comuns da tela. Carregada ao coletar 100 itens de energia em campo.
- **Sistema de Energia:** Uma barra única que limita o spam de Dash e Parry. Regenera passivamente ao longo do tempo.

### 2.2 Eventos Ambientais (Hazards)
Arenas podem ser afetadas por eventos periódicos e mutuamente exclusivos:
- **Lava:** Cria padrões de zonas de dano (cruzes, linhas, anéis) precedidos por um aviso visual (telegraph).
- **Snow Drift:** Reduz o atrito do jogador, causando deslizamento.
- **Water Region:** Aplica uma força de arrasto (drag) constante, desacelerando todas as entidades.
- **Bullet Cloud:** Uma zona densa de micro-projéteis que se move pela arena.
- **Black Hole:** Ponto gravitacional que suga o jogador e inimigos para o centro, causando dano ao contato.

---

## 3. Arquétipos de Inimigos (Roster Completo)

O jogo possui 40 inimigos únicos, divididos em categorias de dificuldade e comportamento.

### 3.1 Inimigos Comuns (25)
| Nome | Comportamento Principal | Padrão de Tiro |
| :--- | :--- | :--- |
| **Neon Pursuer** | Perseguição direta (Seeker) | Colisão |
| **Arcshot Sentry** | Estático/Lento | Disparo único direcionado |
| **Ricochet Imp** | Movimento em ricochete nas bordas | Disparo em ângulo fixo |
| **Rift Charger** | Investida telegrafada (Charge) | Dano por contato em alta velocidade |
| **Blast Wisp** | Suicida / Explosivo | Detonação em área ao aproximar |
| **Burst Turret** | Estático | Rajadas curtas (Burst) de 3 tiros |
| **Siege Mortar** | Posicionamento à distância | Projéteis parabólicos com dano em área |
| **Arcane Strafer** | Move-se lateralmente ao player | Disparos precisos de interceptação |
| **Scatter Stalker** | Aproximação furtiva | Disparo estilo escopeta (Fan-out) |
| **Hex Orbiter** | Orbita o player em círculos | Disparo constante para o centro |
| **Shadow Pouncer** | Salto rápido para posição futura | Explosão curta pós-salto |
| **Runic Bombardier** | Bombardeio de área | Projéteis que deixam poças temporárias |
| **Laser Marksman** | Mira laser longa antes do tiro | Tiro instantâneo em linha reta |
| **Nova Channeler** | Canaliza feixe contínuo (Kamehameha) | Raio de dano persistente |
| **Flame Lancer** | Perseguição lenta | Cone de fogo em curto alcance |
| **Blink Specter** | Teleporte aleatório (Faseamento) | Disparo radial após reaparecer |
| **Aegis Buffer** | Suporte (Foge do player) | Aura que aumenta defesa/velocidade de aliados |
| **Acid Hopper** | Salto irregular | Disparos de arco que deixam rastro tóxico |
| **Orbiting Eye** | Orbita e dispara | Tiros triplos sincronizados |
| **Suppressor Watcher** | Mantém distância média | Fogo de supressão de alta cadência |
| **Mine Shaman** | Cria barreiras de minas | Minas de proximidade estáticas |
| **Phased Executioner** | Ataque físico pós-fase | Ataque de área corpo-a-corpo |
| **Runic Rifleman** | Movimento de infantaria | Rajadas de longo alcance |
| **Tower Necromancer** | Invocador estático | Cria pequenas unidades de energia |
| **Laser Arachnid** | Movimento em grid | Cria cercas de laser entre pontos |

### 3.2 Minibosses (9)
| Nome | Especialidade |
| :--- | :--- |
| **Spiral Warden** | Padrões de projéteis em espiral densa. |
| **Hunter Vanguard** | IA de caça agressiva e velocidade superior. |
| **Aegis Bastion** | Escudo orbital que deve ser contornado. |
| **Dread Sniper** | One-shot kill telegrafado de longa distância. |
| **Matrix Overseer** | Cria grades de laser que cobrem 50% da arena. |
| **Beam Oracle** | Feixes de energia massivos que rotacionam. |
| **Pyro Hydra** | Disparos de fogo em múltiplas direções simultâneas. |
| **Phantom Overlord** | Fica invisível e ataca com projéteis ricocheteadores. |
| **Plague Alchemist** | Lança frascos que criam zonas de status negativo. |

### 3.3 Bosses (6)
| Nome | Descrição Técnica |
| :--- | :--- |
| **Overseer Prime** | Ciclos de tiro radial, perseguição e fase defensiva. |
| **War Cannon Sovereign** | Foco total em artilharia pesada e saturação de projéteis. |
| **Chaos Regent** | Padroes de tiro pseudo-aleatórios e mudança de velocidade. |
| **Laser Colossus** | Varreduras de tela inteira com lasers duplos. |
| **Toxic Druid** | Controla o campo com invocações e zonas de veneno. |
| **Spectral Overlord** | Combina teleporte com ataques espectrais persistentes. |

---

## 4. Modos de Jogo

### 4.1 Race (Corrida)
O objetivo é atravessar portais que aparecem na arena. Cada portal destruído/atravessado aumenta o nível e a dificuldade.
- **Vitória:** Alcançar o nível alvo (ex: 10 ou 20).
- **Ranking:** Baseado no tempo de conclusão.

### 4.2 Survival (Sobrevivência)
Ondas infinitas de inimigos. A dificuldade escala com o tempo decorrido. Coletáveis de energia aparecem frequentemente.
- **Hardcore:** Variante com mais eventos ambientais e dano recebido elevado.
- **Ranking:** Baseado no tempo de sobrevivência e inimigos abatidos.

### 4.3 Labyrinth (Labirinto)
Geração procedural de uma grade de salas (Recursive Backtracking).
- **Objetivo:** Encontrar a **Chave** escondida e chegar ao **Portal de Saída**.
- **Mecânica:** Arena de Boss em níveis múltiplos de 5.
- **Progresso:** Níveis infinitos com grades cada vez maiores.

### 4.4 Training (Treino)
Sandbox onde o jogador pode:
- Escolher inimigos específicos para spawnar.
- Ativar/Desativar eventos ambientais.
- Testar mecânicas sem penalidade de morte.

---

## 5. Arquitetura Técnica (Migração para Godot)

### 5.1 Estrutura de Nós (Composition over Inheritance)
- **`CharacterBody2D` (BaseEntity):** Gerencia física básica.
    - `HealthComponent` (Node): Vida e I-frames.
    - `HitboxComponent` (Area2D): Detecção de dano.
    - `BehaviorComponent` (Node): Script de IA específico (ex: `ChaserBehavior`, `SniperBehavior`).
    - `VisualComponent` (Node2D/GPUParticles2D): Desenho geométrico e efeitos neon.

### 5.2 Gerenciamento de Dados
- **Resources (`.tres`):** Configurações de inimigos (vida, velocidade, cores, tipo de behavior).
- **Autoloads (Singletons):**
    - `EventManager`: Barramento de sinais globais.
    - `AudioManager`: Controle de trilhas e efeitos com ducking.
    - `ProgressionManager`: Lógica de dificuldade por modo.

### 5.3 UI e UX
- **Theme:** Uso extensivo de `StyleBoxFlat` com bordas e sombras para o efeito "glow".
- **Navigation:** Focada em teclado/gamepad com suporte nativo a `focus`.
- **i18n:** Uso do sistema de tradução nativo do Godot (`tr()`) via arquivos `.csv` ou `.po`.

---

## 6. Feedback Visual e Áudio
- **Post-Processing:** WorldEnvironment com Bloom (Threshold < 1.0) para o efeito Neon.
- **Partículas:** GPUParticles2D para explosões e rastros (Trails).
- **Áudio:** Trilhas dinâmicas que sofrem filtro Low-Pass quando o jogo é pausado. SFX com variação de pitch aleatória para evitar fadiga auditiva.
