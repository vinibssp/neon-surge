from __future__ import annotations

import json
from pathlib import Path

LanguageCode = str
SUPPORTED_LANGUAGES: tuple[LanguageCode, ...] = ("pt_BR", "en_US")
DEFAULT_LANGUAGE: LanguageCode = "pt_BR"


TRANSLATIONS: dict[LanguageCode, dict[str, str]] = {
    "pt_BR": {
        "settings.title": "CONFIGURACOES DE SISTEMA",
        "settings.audio_header": "CONTROLE DE AUDIO",
        "settings.music": "MUSICA",
        "settings.sfx": "EFEITOS",
        "settings.preferences_header": "PREFERENCIAS DO OPERADOR",
        "settings.language": "IDIOMA",
        "settings.language.current": "ATUAL: {language}",
        "settings.language.pt": "PORTUGUES",
        "settings.language.en": "ENGLISH",
        "settings.change_name": "ALTERAR NOME DO PILOTO",
        "settings.controls": "AJUSTAR CONTROLES",
        "settings.identity": "IDENTIDADE OPERACIONAL",
        "settings.input": "CONFIGURACAO DE INPUT",
        "settings.back": "VOLTAR AO MENU PRINCIPAL",
        "main.title": "NEON SURGE",
        "main.info.select": "SELECIONE UMA OPERACAO",
        "main.info.default_desc": "Navegue pelos modulos acima para ver os detalhes tecnicos da simulacao.",
        "main.info.default_meta": "Selecione um modulo para iniciar.",
        "main.info.ui_title": "SISTEMA DE INTERFACE",
        "main.info.ui_desc": "Pronto para iniciar. Selecione um modulo de simulacao para prosseguir.",
        "main.info.ui_meta": "Use mouse, teclado ou gamepad para navegar.",
        "main.ranking": "RANKING",
        "main.unknown_player": "Desconhecido",
        "mode.race": "CORRIDA",
        "mode.race_infinite": "INFINITA",
        "mode.survival": "SOBREVIVENCIA",
        "mode.hardcore": "HARDCORE",
        "mode.labyrinth": "LABIRINTO",
        "mode.training": "TREINO",
        "mode.race.desc": "Progressao por niveis com foco em rota eficiente e execucao rapida.",
        "mode.race.meta": "Objetivo: coletar nucleos, abrir o portal e avancar no menor tempo possivel.",
        "mode.race_infinite.desc": "Variante sem limite de niveis, com pressao crescente ao longo da run.",
        "mode.race_infinite.meta": "Objetivo: sobreviver e manter consistencia por mais tempo, acumulando pontuacao.",
        "mode.survival.desc": "Combate intenso contra ondas e eventos ambientais.",
        "mode.survival.meta": "Objetivo: manter-se vivo enquanto a arena se torna mais hostil.",
        "mode.hardcore.desc": "Sobrevivencia com tuning mais punitivo e menor margem para erro.",
        "mode.hardcore.meta": "Objetivo: sustentar a run sob alta pressao e buscar a maior pontuacao.",
        "mode.labyrinth.desc": "Niveis procedurais em grade com navegacao tatica e controle de espaco.",
        "mode.labyrinth.meta": "Objetivo: achar a chave, desbloquear a saida e concluir as fases de boss.",
        "mode.training.desc": "Simulacao configuravel para praticar matchups e execucao mecanica.",
        "mode.training.meta": "Objetivo: definir spawns/eventos e repetir cenarios especificos de treino.",
        "pause.title": "PAUSADO",
        "pause.resume": "Continuar",
        "pause.settings": "Configuracoes",
        "pause.main_menu": "Menu Principal",
        "player_name.welcome": "BEM-VINDO AO SURGE",
        "player_name.change": "ALTERAR NOME DE JOGADOR",
        "player_name.prompt": "Insira seu nome (Max 12 letras):",
        "player_name.confirm": "CONFIRMAR",
        "player_name.cancel": "CANCELAR",
        "controls.title": "CONFIGURACOES DE CONTROLES",
        "controls.tab.keyboard": "TECLADO",
        "controls.tab.joystick": "JOYSTICK",
        "controls.back": "VOLTAR",
        "controls.keyboard.header": "CONTROLES DO TECLADO",
        "controls.joystick.header": "CONTROLES DO JOYSTICK",
        "controls.remap": "REMAPEAR",
        "controls.reset": "RESTAURAR PADROES",
        "controls.waiting": "PRESSIONE INPUT...",
        "controls.action.up": "MOVER PARA CIMA",
        "controls.action.down": "MOVER PARA BAIXO",
        "controls.action.left": "MOVER PARA ESQUERDA",
        "controls.action.right": "MOVER PARA DIREITA",
        "controls.action.dash": "DASH / IMPULSO",
        "controls.action.parry": "PARRY / DEFESA",
        "controls.action.bomb": "BOMBA NUCLEAR",
        "controls.action.joy_dash": "DASH / IMPULSO",
        "controls.action.joy_parry": "PARRY / DEFESA",
        "controls.action.joy_bomb": "BOMBA NUCLEAR",
        "controls.action.joy_pause": "PAUSAR JOGO",
        "controls.button_prefix": "BOTAO",
        "leaderboard.title": "CLASSIFICACAO",
        "leaderboard.back": "Voltar",
        "leaderboard.loading.local": "Carregando ranking local...",
        "leaderboard.loading.global": "Carregando ranking global...",
        "leaderboard.empty.local": "Nenhum registro local.",
        "leaderboard.empty.global": "Nenhum registro global.",
        "leaderboard.metric.time": "Tempo",
        "leaderboard.metric.score": "Score",
        "guide.title": "MANUAL DO OPERADOR",
        "guide.prev": "ANTERIOR (Q)",
        "guide.next": "PROXIMO (E)",
        "guide.back": "VOLTAR AO MENU",
        "guide.module_counter": "MODULO {index} / {total}",
        "guide.section.1.title": "SISTEMA DE MOVIMENTACAO",
        "guide.section.1.line.1": "WASD ou SETAS: Navegar pelo espaco.",
        "guide.section.1.line.2": "SHIFT ESQUERDO: Dash tatico (invulnerabilidade curta).",
        "guide.section.1.line.3": "ESPACO: Ativar campo de PARRY.",
        "guide.section.1.line.4": "DICA: Dash consome energia, use com sabedoria.",
        "guide.section.2.title": "MECANICAS DE COMBATE",
        "guide.section.2.line.1": "PARRY: Reflete projeteis e atordoa (stagger) inimigos.",
        "guide.section.2.line.2": "STAGGER: Inimigos atordoados nao causam dano por contato.",
        "guide.section.2.line.3": "COMBO: Eliminar inimigos em sequencia aumenta o multiplicador.",
        "guide.section.2.line.4": "DICA: O parry e sua principal ferramenta de defesa.",
        "guide.section.3.title": "MODOS DE SIMULACAO",
        "guide.section.3.line.1": "CORRIDA: Atravesse portais para avancar de nivel.",
        "guide.section.3.line.2": "SOBREVIVENCIA: Resista a hordas infinitas e eventos.",
        "guide.section.3.line.3": "TREINO: Configure hordas personalizadas para praticar.",
        "guide.section.3.line.4": "DICA: Use o treino para aprender padroes de chefes.",
        "guide.section.4.title": "INTERFACE E ATALHOS",
        "guide.section.4.line.1": "ESC: Abrir menu de pausa ou voltar.",
        "guide.section.4.line.2": "1 / 2 / 3 / 4: Trocar abas em menus complexos.",
        "guide.section.4.line.3": "Q / E: Alternar entre secoes adjacentes.",
        "guide.section.4.line.4": "MOUSE WHEEL: Rolar listas e trocar paginas.",
        "game_over.score_detail": "DETALHE DA PONTUACAO",
        "game_over.retry": "Tentar Novamente",
        "game_over.main_menu": "Menu Principal",
        "game_over.local": "LOCAL",
        "game_over.global": "GLOBAL",
        "game_over.loading.local": "Carregando ranking local...",
        "game_over.loading.global": "Sincronizando com a rede...",
        "game_over.sync.running": "Status: sincronizando...",
        "game_over.rank_position": "Posicao no ranking: Local {local} | Global {global}",
        "game_over.no_local": "Nenhum dado local.",
        "game_over.no_global": "Sem sincronizacao global.",
        "game_over.no_local_entries": "Nenhum registro local.",
        "game_over.sync_failed": "Falha na sincronizacao global.",
        "game_over.sync.running_table": "Sincronizando com a rede...",
        "game_over.sync.done": "Status: sincronizado ({count} item(ns) enviados)",
        "game_over.sync.degraded": "Status: pendencias locais aguardando proxima sincronizacao",
        "game_over.sync.progress": "Status: sincronizando ranking global...",
        "game_over.defeated_by": "Derrotado por {enemy}",
        "game_over.item": "ITEM",
        "game_over.value": "VALOR",
        "hud.key.mode": "Modo",
        "hud.key.time": "Tempo",
        "hud.key.level": "Nivel",
        "hud.key.survival_time": "Tempo vivo",
        "hud.key.coins": "Moedas",
        "hud.key.bomb": "Bomba [I]",
        "hud.key.defeated": "Derrotados",
        "hud.value.mode.race": "Corrida",
        "hud.value.mode.race_infinite": "Corrida Infinita",
        "hud.value.mode.survival": "Survival",
        "hud.value.mode.survival_hardcore": "Survival Hardcore",
        "hud.value.mode.labyrinth": "Labirinto",
        "hud.value.mode.training": "Treino",
        "hud.value.mode.one_vs_one": "1v1",
        "score.total": "Total",
        "score.level": "Nivel",
        "score.collectibles": "Coletaveis",
        "score.portals": "Portais",
        "score.parry": "Parry",
        "score.time": "Tempo",
        "score.enemies": "Inimigos",
        "runtime.game_over": "GAME OVER",
        "runtime.time": "Tempo: {value}",
        "runtime.level_reached": "Nivel alcancado: {value}",
        "runtime.survived": "Sobreviveu: {value}",
        "runtime.defeated": "Derrotados: {value}",
        "runtime.rounds_complete": "Rounds completos: {value}",
    },
    "en_US": {
        "settings.title": "SYSTEM SETTINGS",
        "settings.audio_header": "AUDIO CONTROL",
        "settings.music": "MUSIC",
        "settings.sfx": "SFX",
        "settings.preferences_header": "OPERATOR PREFERENCES",
        "settings.language": "LANGUAGE",
        "settings.language.current": "CURRENT: {language}",
        "settings.language.pt": "PORTUGUESE",
        "settings.language.en": "ENGLISH",
        "settings.change_name": "CHANGE PILOT NAME",
        "settings.controls": "ADJUST CONTROLS",
        "settings.identity": "OPERATIONAL IDENTITY",
        "settings.input": "INPUT CONFIGURATION",
        "settings.back": "BACK TO MAIN MENU",
        "main.title": "NEON SURGE",
        "main.info.select": "SELECT AN OPERATION",
        "main.info.default_desc": "Browse the modules above to inspect simulation details.",
        "main.info.default_meta": "Select a module to start.",
        "main.info.ui_title": "INTERFACE SYSTEM",
        "main.info.ui_desc": "Ready to begin. Select a simulation module to continue.",
        "main.info.ui_meta": "Use mouse, keyboard, or gamepad to navigate.",
        "main.ranking": "LEADERBOARD",
        "main.unknown_player": "Unknown",
        "mode.race": "RACE",
        "mode.race_infinite": "INFINITE",
        "mode.survival": "SURVIVAL",
        "mode.hardcore": "HARDCORE",
        "mode.labyrinth": "LABYRINTH",
        "mode.training": "TRAINING",
        "mode.race.desc": "Level progression focused on efficient routes and fast execution.",
        "mode.race.meta": "Goal: collect cores, open the portal, and advance in the shortest time.",
        "mode.race_infinite.desc": "Unlimited level variant with increasing pressure as the run continues.",
        "mode.race_infinite.meta": "Goal: survive longer with consistency while building score.",
        "mode.survival.desc": "Intense combat against waves and environmental hazards.",
        "mode.survival.meta": "Goal: stay alive while the arena becomes increasingly hostile.",
        "mode.hardcore.desc": "Survival tuned to be harsher with less room for mistakes.",
        "mode.hardcore.meta": "Goal: sustain the run under heavy pressure and chase high score.",
        "mode.labyrinth.desc": "Procedural grid levels with tactical navigation and space control.",
        "mode.labyrinth.meta": "Goal: find the key, unlock the exit, and clear boss stages.",
        "mode.training.desc": "Configurable simulation to practice matchups and mechanics.",
        "mode.training.meta": "Goal: define spawns/events and replay specific training scenarios.",
        "pause.title": "PAUSED",
        "pause.resume": "Resume",
        "pause.settings": "Settings",
        "pause.main_menu": "Main Menu",
        "player_name.welcome": "WELCOME TO SURGE",
        "player_name.change": "CHANGE PLAYER NAME",
        "player_name.prompt": "Enter your name (Max 12 chars):",
        "player_name.confirm": "CONFIRM",
        "player_name.cancel": "CANCEL",
        "controls.title": "CONTROL SETTINGS",
        "controls.tab.keyboard": "KEYBOARD",
        "controls.tab.joystick": "JOYSTICK",
        "controls.back": "BACK",
        "controls.keyboard.header": "KEYBOARD CONTROLS",
        "controls.joystick.header": "JOYSTICK CONTROLS",
        "controls.remap": "REMAP",
        "controls.reset": "RESTORE DEFAULTS",
        "controls.waiting": "PRESS INPUT...",
        "controls.action.up": "MOVE UP",
        "controls.action.down": "MOVE DOWN",
        "controls.action.left": "MOVE LEFT",
        "controls.action.right": "MOVE RIGHT",
        "controls.action.dash": "DASH / BURST",
        "controls.action.parry": "PARRY / DEFENSE",
        "controls.action.bomb": "NUCLEAR BOMB",
        "controls.action.joy_dash": "DASH / BURST",
        "controls.action.joy_parry": "PARRY / DEFENSE",
        "controls.action.joy_bomb": "NUCLEAR BOMB",
        "controls.action.joy_pause": "PAUSE GAME",
        "controls.button_prefix": "BUTTON",
        "leaderboard.title": "LEADERBOARD",
        "leaderboard.back": "Back",
        "leaderboard.loading.local": "Loading local leaderboard...",
        "leaderboard.loading.global": "Loading global leaderboard...",
        "leaderboard.empty.local": "No local records.",
        "leaderboard.empty.global": "No global records.",
        "leaderboard.metric.time": "Time",
        "leaderboard.metric.score": "Score",
        "guide.title": "OPERATOR MANUAL",
        "guide.prev": "PREV (Q)",
        "guide.next": "NEXT (E)",
        "guide.back": "BACK TO MENU",
        "guide.module_counter": "MODULE {index} / {total}",
        "guide.section.1.title": "MOVEMENT SYSTEM",
        "guide.section.1.line.1": "WASD or ARROWS: Navigate through space.",
        "guide.section.1.line.2": "LEFT SHIFT: Tactical dash (short invulnerability).",
        "guide.section.1.line.3": "SPACE: Activate PARRY field.",
        "guide.section.1.line.4": "TIP: Dash consumes energy, use it wisely.",
        "guide.section.2.title": "COMBAT MECHANICS",
        "guide.section.2.line.1": "PARRY: Reflects projectiles and staggers enemies.",
        "guide.section.2.line.2": "STAGGER: Staggered enemies do not deal contact damage.",
        "guide.section.2.line.3": "COMBO: Defeating enemies in sequence increases multiplier.",
        "guide.section.2.line.4": "TIP: Parry is your main defensive tool.",
        "guide.section.3.title": "SIMULATION MODES",
        "guide.section.3.line.1": "RACE: Cross portals to advance levels.",
        "guide.section.3.line.2": "SURVIVAL: Endure endless hordes and events.",
        "guide.section.3.line.3": "TRAINING: Configure custom hordes for practice.",
        "guide.section.3.line.4": "TIP: Use training to learn boss patterns.",
        "guide.section.4.title": "INTERFACE AND SHORTCUTS",
        "guide.section.4.line.1": "ESC: Open pause menu or go back.",
        "guide.section.4.line.2": "1 / 2 / 3 / 4: Switch tabs in complex menus.",
        "guide.section.4.line.3": "Q / E: Switch between adjacent sections.",
        "guide.section.4.line.4": "MOUSE WHEEL: Scroll lists and change pages.",
        "game_over.score_detail": "SCORE BREAKDOWN",
        "game_over.retry": "Retry",
        "game_over.main_menu": "Main Menu",
        "game_over.local": "LOCAL",
        "game_over.global": "GLOBAL",
        "game_over.loading.local": "Loading local leaderboard...",
        "game_over.loading.global": "Syncing with network...",
        "game_over.sync.running": "Status: syncing...",
        "game_over.rank_position": "Rank position: Local {local} | Global {global}",
        "game_over.no_local": "No local data.",
        "game_over.no_global": "No global sync.",
        "game_over.no_local_entries": "No local records.",
        "game_over.sync_failed": "Global sync failed.",
        "game_over.sync.running_table": "Syncing with network...",
        "game_over.sync.done": "Status: synced ({count} item(s) sent)",
        "game_over.sync.degraded": "Status: local pending items waiting next sync",
        "game_over.sync.progress": "Status: syncing global leaderboard...",
        "game_over.defeated_by": "Defeated by {enemy}",
        "game_over.item": "ITEM",
        "game_over.value": "VALUE",
        "hud.key.mode": "Mode",
        "hud.key.time": "Time",
        "hud.key.level": "Level",
        "hud.key.survival_time": "Survival Time",
        "hud.key.coins": "Coins",
        "hud.key.bomb": "Bomb [I]",
        "hud.key.defeated": "Defeated",
        "hud.value.mode.race": "Race",
        "hud.value.mode.race_infinite": "Infinite Race",
        "hud.value.mode.survival": "Survival",
        "hud.value.mode.survival_hardcore": "Survival Hardcore",
        "hud.value.mode.labyrinth": "Labyrinth",
        "hud.value.mode.training": "Training",
        "hud.value.mode.one_vs_one": "1v1",
        "score.total": "Total",
        "score.level": "Level",
        "score.collectibles": "Collectibles",
        "score.portals": "Portals",
        "score.parry": "Parry",
        "score.time": "Time",
        "score.enemies": "Enemies",
        "runtime.game_over": "GAME OVER",
        "runtime.time": "Time: {value}",
        "runtime.level_reached": "Level reached: {value}",
        "runtime.survived": "Survived: {value}",
        "runtime.defeated": "Defeated: {value}",
        "runtime.rounds_complete": "Completed rounds: {value}",
    },
}


class LocalizationManager:
    def __init__(self, settings_path: Path | None = None, default_language: LanguageCode = DEFAULT_LANGUAGE) -> None:
        self._settings_path = settings_path or (Path(__file__).resolve().parent.parent / "assets" / "localization_settings.json")
        self._language = default_language if default_language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        self.load()

    @property
    def language(self) -> LanguageCode:
        return self._language

    def set_language(self, language: LanguageCode) -> None:
        if language not in SUPPORTED_LANGUAGES:
            return
        if self._language == language:
            return
        self._language = language
        self.save()

    def load(self) -> None:
        if not self._settings_path.exists():
            return
        try:
            raw_data = json.loads(self._settings_path.read_text(encoding="utf-8"))
        except Exception:
            return

        language = raw_data.get("language")
        if isinstance(language, str) and language in SUPPORTED_LANGUAGES:
            self._language = language

    def save(self) -> None:
        payload = {"language": self._language}
        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            self._settings_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        except Exception:
            return

    def t(self, key: str, **kwargs: object) -> str:
        active_map = TRANSLATIONS.get(self._language, {})
        fallback_map = TRANSLATIONS.get(DEFAULT_LANGUAGE, {})
        text = active_map.get(key, fallback_map.get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

    def display_language_name(self, language: LanguageCode | None = None) -> str:
        lang = self._language if language is None else language
        return self.t("settings.language.pt") if lang == "pt_BR" else self.t("settings.language.en")

    def localize_mode_name(self, raw_name: str) -> str:
        mode_map = {
            "corrida": "hud.value.mode.race",
            "race": "hud.value.mode.race",
            "corrida infinita": "hud.value.mode.race_infinite",
            "race infinite": "hud.value.mode.race_infinite",
            "infinita": "hud.value.mode.race_infinite",
            "survival": "hud.value.mode.survival",
            "sobrevivencia": "hud.value.mode.survival",
            "survival hardcore": "hud.value.mode.survival_hardcore",
            "labirinto": "hud.value.mode.labyrinth",
            "labyrinth": "hud.value.mode.labyrinth",
            "treino": "hud.value.mode.training",
            "training": "hud.value.mode.training",
            "1v1": "hud.value.mode.one_vs_one",
        }
        key = mode_map.get(raw_name.strip().lower())
        if key is None:
            return raw_name
        return self.t(key)

    def localize_hud_line(self, line: str) -> str:
        if ":" not in line:
            return line
        raw_key, raw_value = line.split(":", 1)
        source_key = raw_key.strip().lower()
        value = raw_value.strip()
        key_map = {
            "modo": "hud.key.mode",
            "mode": "hud.key.mode",
            "tempo": "hud.key.time",
            "time": "hud.key.time",
            "nivel": "hud.key.level",
            "level": "hud.key.level",
            "tempo vivo": "hud.key.survival_time",
            "survival time": "hud.key.survival_time",
            "moedas": "hud.key.coins",
            "coins": "hud.key.coins",
            "bomba [i]": "hud.key.bomb",
            "bomb [i]": "hud.key.bomb",
            "derrotados": "hud.key.defeated",
            "defeated": "hud.key.defeated",
        }
        translated_key = self.t(key_map.get(source_key, source_key))
        if source_key in ("modo", "mode"):
            value = self.localize_mode_name(value)
        return f"{translated_key}: {value}"

    def localize_runtime_subtitle(self, subtitle: str) -> str:
        base = subtitle.strip()
        lower = base.lower()
        if lower.startswith("tempo:") or lower.startswith("time:"):
            return self.t("runtime.time", value=base.split(":", 1)[1].strip())
        if lower.startswith("nivel alcancado:") or lower.startswith("level reached:"):
            return self.t("runtime.level_reached", value=base.split(":", 1)[1].strip())
        if lower.startswith("sobreviveu:") or lower.startswith("survived:"):
            return self.t("runtime.survived", value=base.split(":", 1)[1].strip())
        if lower.startswith("resistiu:"):
            return self.t("runtime.survived", value=base.split(":", 1)[1].strip())
        if lower.startswith("derrotados:") or lower.startswith("defeated:"):
            return self.t("runtime.defeated", value=base.split(":", 1)[1].strip())
        if lower.startswith("rounds completos:") or lower.startswith("completed rounds:"):
            return self.t("runtime.rounds_complete", value=base.split(":", 1)[1].strip())
        return subtitle

    def localize_score_label(self, label: str) -> str:
        raw = label.strip()
        lower = raw.lower()
        prefix_map = {
            "nivel": "score.level",
            "coletaveis": "score.collectibles",
            "portais": "score.portals",
            "parry": "score.parry",
            "tempo": "score.time",
            "total": "score.total",
            "level": "score.level",
            "collectibles": "score.collectibles",
            "portals": "score.portals",
            "time": "score.time",
        }
        for prefix, key in prefix_map.items():
            if lower.startswith(prefix):
                suffix = raw[len(prefix):]
                return f"{self.t(key)}{suffix}"
        return label
