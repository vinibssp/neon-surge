from __future__ import annotations

import math
from typing import Literal

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.factories.enemy_factory import EnemyFactory
from game.modes.mode_config import TrainingConfig
from game.modes.training_mode import TrainingMode
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel
from game.ui.gui_theme import register_custom_element_themes

EnemyCategory = Literal["enemy", "miniboss", "boss"]
TrainingTab = Literal["enemy", "miniboss", "boss", "event"]


ENEMY_CATEGORY_LABELS: dict[EnemyCategory, str] = {
    "enemy": "Inimigos",
    "miniboss": "Minibosses",
    "boss": "Bosses",
}


EVENT_LABELS: dict[str, str] = {
    "random": "Aleatorio",
    "lava": "Lava",
    "snow_drift": "Neve",
    "water_region": "Agua",
    "bullet_cloud": "Nuvem de Balas",
    "black_hole": "Buraco Negro",
}


EVENT_DESCRIPTIONS: dict[str, str] = {
    "random": "Sorteia qualquer evento ambiental disponivel.",
    "lava": "Hazard de lava com aviso e fase ativa.",
    "snow_drift": "Reduz controle e velocidade em area de neve.",
    "water_region": "Invoca piratas em uma regiao de agua.",
    "bullet_cloud": "Chuva de projeteis em area delimitada.",
    "black_hole": "Puxa entidades e pode consumir o player.",
}


ENEMY_DESCRIPTIONS: dict[str, str] = {
    "follower": "Persegue o player sem parar.",
    "shooter": "Atira de longe com mira lenta.",
    "quique": "Se move ricocheteando com pressao.",
    "investida": "Telegrafa e avanca em investida.",
    "explosivo": "Persegue e explode ao encostar.",
    "metralhadora": "Torre de rajadas curtas.",
    "morteiro": "Disparos em area com atraso.",
    "estrafador_arcano": "Strafe lateral com tiro preciso.",
    "emboscador_escopeta": "Burst forte em curta distancia.",
    "orbitador_hex": "Orbita e pressiona por angulos.",
    "sombra_investida": "Emboscada com salto rapido.",
    "bombardeiro_runa": "Bombardeia com projeteis runicos.",
    "atirador_laser": "Laser rapido em linha reta.",
    "kamehameha": "Canaliza feixe continuo.",
    "lanca_chamas": "Cone de dano em curto alcance.",
    "fantasma": "Alterna fases e reposiciona.",
    "buffer": "Fortalece inimigos proximos.",
    "sapo": "Rajadas de acido em arco.",
    "bandido_arcano": "Pressao agil com strafes.",
    "mago_hobbit": "Caster de tiro pesado.",
    "escorpiao_rainha": "Movimento rapido e agressivo.",
    "gazer_vazio": "Sniper laser de alto risco.",
    "abominacao_limo": "Explosivo com ritmo acelerado.",
    "assassino_crepuscular": "Emboscador muito movel.",
    "sentinela_estelar": "Feixes ritmicos em cadencia.",
    "necrolorde_orbital": "Controle espacial por orbita.",
    "horror_igneo": "Pressao constante de fogo.",
    "espectro_lancante": "Investidas espectrais repetidas.",
    "aracnideo_venenoso": "Ataques rapidos com veneno.",
    "bombardeiro_abyssal": "Area denial com bombas pesadas.",
    "olho_orbitante": "Orbita e solta tiros triplos.",
    "vigia_supressor": "Supressao a media distancia.",
    "xama_mineiro": "Planta minas em zonas de rota.",
    "algoz_faseado": "Ataque apos fase/teleporte.",
    "guardiao_cosmico": "Orbita ampla e presenca pesada.",
    "caotico_estilha": "Padrao caotico de estilhacos.",
    "fuzileiro_runico": "Rifle de supressao continuo.",
    "cavaleiro_voraz": "Investidor resistente e agressivo.",
    "necromante_torre": "Caster estatico de controle.",
    "aranha_laser": "Mobilidade com feixes laser.",
    "miniboss_espiral": "Espiral densa de projeteis.",
    "miniboss_cacador": "Caca o player com agressividade.",
    "miniboss_escudo": "Fase defensiva com escudo orbital.",
    "miniboss_sniper": "Disparos precisos de longo alcance.",
    "miniboss_laser_matrix": "Grade de lasers em sequencia.",
    "miniboss_oraculo_kame": "Feixe prolongado em area.",
    "miniboss_piro_hidra": "Fogo multiponto e saturacao.",
    "miniboss_fantasma_senhor": "Stealth tatico com emboscadas.",
    "miniboss_alquimista": "Rajadas alquimicas especiais.",
    "boss": "Chefe balanceado de referencia.",
    "boss_artilharia": "Boss focado em artilharia radial.",
    "boss_caotico": "Padroes imprevisiveis e pressao.",
    "boss_colosso_laser": "Varredura laser de alta ameaca.",
    "boss_druida_toxico": "Invocacoes e campo toxico.",
    "boss_soberano_espectral": "Rajadas espectrais avancadas.",
}


class TrainingSetupScene(BaseMenuScene):
    def __init__(self, stack) -> None:
        super().__init__(stack)
        self._elapsed_time = 0.0
        self._background_renderer = CyberpunkMenuBackgroundRenderer()
        self._register_themes()

        self._tab_order: tuple[TrainingTab, ...] = ("enemy", "miniboss", "boss", "event")
        self._active_tab: TrainingTab = "enemy"
        self._rows_per_page = 6
        self._max_count_by_tab: dict[EnemyCategory, int] = {
            "enemy": 30,
            "miniboss": 12,
            "boss": 8,
        }
        self._page_index_by_tab: dict[TrainingTab, int] = {category: 0 for category in self._tab_order}

        self._kinds_by_tab: dict[EnemyCategory, list[str]] = {
            "enemy": EnemyFactory.registered_enemy_kinds(),
            "miniboss": EnemyFactory.registered_miniboss_kinds(),
            "boss": EnemyFactory.registered_boss_kinds(),
        }

        self._selected_counts: dict[str, int] = {
            kind: 0
            for category in self._kinds_by_tab
            for kind in self._kinds_by_tab[category]
        }
        self._event_options: tuple[str, ...] = (
            "random",
            "lava",
            "snow_drift",
            "water_region",
            "bullet_cloud",
            "black_hole",
        )
        self._selected_event = "random"
        self._event_interval_min = 6.0
        self._event_interval_max = 60.0
        self._event_interval_step = 1.0
        self._selected_event_interval = 22.0
        self._slot_kinds: list[str | None] = [None] * self._rows_per_page
        self._row_minus_index_by_control: dict[object, int] = {}
        self._row_plus_index_by_control: dict[object, int] = {}

        title = create_label(
            LabelConfig(
                text="TREINO PERSONALIZADO",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 68), (600, 68)),
                object_id="training_title_label",
            ),
            manager=self.ui_manager,
        )
        subtitle = create_label(
            LabelConfig(
                text="Escolha o que praticar: categorias de inimigos e aba de evento ambiental.",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 360, 126), (720, 36)),
                object_id="training_subtitle_label",
            ),
            manager=self.ui_manager,
        )
        del title, subtitle

        self._tab_buttons: dict[TrainingTab, object] = {
            "enemy": create_button(
                ButtonConfig(
                    text="Inimigos",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 - 315, 170), (200, 44)),
                    object_id="training_tab_enemy_button",
                ),
                manager=self.ui_manager,
            ),
            "miniboss": create_button(
                ButtonConfig(
                    text="Minibosses",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 - 100, 170), (200, 44)),
                    object_id="training_tab_miniboss_button",
                ),
                manager=self.ui_manager,
            ),
            "boss": create_button(
                ButtonConfig(
                    text="Bosses",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 + 100, 170), (170, 44)),
                    object_id="training_tab_boss_button",
                ),
                manager=self.ui_manager,
            ),
            "event": create_button(
                ButtonConfig(
                    text="Eventos",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 + 285, 170), (170, 44)),
                    object_id="training_tab_event_button",
                ),
                manager=self.ui_manager,
            ),
        }

        self._content_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 530, 224), (1060, 332)),
                variant="card",
                object_id="training_content_panel",
            ),
            manager=self.ui_manager,
        )

        create_label(
            LabelConfig(
                text="Inimigo",
                rect=pygame.Rect((24, 10), (210, 28)),
                object_id="training_header_name_label",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        create_label(
            LabelConfig(
                text="Descricao",
                rect=pygame.Rect((248, 10), (450, 28)),
                object_id="training_header_desc_label",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        create_label(
            LabelConfig(
                text="Qtd",
                rect=pygame.Rect((792, 10), (80, 28)),
                object_id="training_header_count_label",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )

        self._row_name_labels: list[object] = []
        self._row_desc_labels: list[object] = []
        self._row_minus_buttons: list[object] = []
        self._row_count_labels: list[object] = []
        self._row_plus_buttons: list[object] = []

        row_origin_y = 44
        row_height = 44
        for index in range(self._rows_per_page):
            y = row_origin_y + index * row_height
            name_label = create_label(
                LabelConfig(
                    text="-",
                    rect=pygame.Rect((24, y), (210, 32)),
                    object_id=f"training_row_name_{index}",
                ),
                manager=self.ui_manager,
                container=self._content_panel,
            )
            desc_label = create_label(
                LabelConfig(
                    text="-",
                    rect=pygame.Rect((248, y), (450, 32)),
                    object_id=f"training_row_desc_{index}",
                ),
                manager=self.ui_manager,
                container=self._content_panel,
            )
            minus_button = create_button(
                ButtonConfig(
                    text="-",
                    rect=pygame.Rect((730, y), (46, 32)),
                    object_id=f"training_row_minus_{index}",
                ),
                manager=self.ui_manager,
                container=self._content_panel,
            )
            count_label = create_label(
                LabelConfig(
                    text="0",
                    rect=pygame.Rect((790, y), (80, 32)),
                    object_id=f"training_row_count_{index}",
                ),
                manager=self.ui_manager,
                container=self._content_panel,
            )
            plus_button = create_button(
                ButtonConfig(
                    text="+",
                    rect=pygame.Rect((884, y), (46, 32)),
                    object_id=f"training_row_plus_{index}",
                ),
                manager=self.ui_manager,
                container=self._content_panel,
            )
            self._row_name_labels.append(name_label)
            self._row_desc_labels.append(desc_label)
            self._row_minus_buttons.append(minus_button)
            self._row_count_labels.append(count_label)
            self._row_plus_buttons.append(plus_button)

        self._page_label = create_label(
            LabelConfig(
                text="Pagina 1/1",
                rect=pygame.Rect((420, 308), (220, 24)),
                object_id="training_page_label",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        self._page_prev_button = create_button(
            ButtonConfig(
                text="<",
                rect=pygame.Rect((356, 302), (50, 30)),
                object_id="training_page_prev_button",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        self._page_next_button = create_button(
            ButtonConfig(
                text=">",
                rect=pygame.Rect((654, 302), (50, 30)),
                object_id="training_page_next_button",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        self._event_interval_title_label = create_label(
            LabelConfig(
                text="Intervalo do Evento",
                rect=pygame.Rect((300, 268), (230, 28)),
                object_id="training_event_interval_title_label",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        self._event_interval_minus_button = create_button(
            ButtonConfig(
                text="-",
                rect=pygame.Rect((540, 268), (42, 30)),
                object_id="training_event_interval_minus_button",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        self._event_interval_value_label = create_label(
            LabelConfig(
                text="22s",
                rect=pygame.Rect((592, 268), (96, 28)),
                object_id="training_event_interval_value_label",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        self._event_interval_plus_button = create_button(
            ButtonConfig(
                text="+",
                rect=pygame.Rect((698, 268), (42, 30)),
                object_id="training_event_interval_plus_button",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )

        self._summary_label = create_label(
            LabelConfig(
                text="Selecionados: 0",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 240, 568), (480, 30)),
                object_id="training_summary_label",
            ),
            manager=self.ui_manager,
        )
        self._keyboard_hint_label = create_label(
            LabelConfig(
                text="Atalhos: 1/2/3/4 abas | Q/E alterna abas | PgUp/PgDn pagina | <-/-> ou A/D e +/- ajustam foco",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 500, 592), (1000, 24)),
                object_id="training_keyboard_hint_label",
            ),
            manager=self.ui_manager,
        )

        self._start_button = create_button(
            ButtonConfig(
                text="Iniciar Treino",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 270, 606), (250, 56)),
                object_id="training_start_button",
            ),
            manager=self.ui_manager,
        )
        self._back_button = create_button(
            ButtonConfig(
                text="Voltar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 + 20, 606), (250, 56)),
                object_id="training_back_button",
            ),
            manager=self.ui_manager,
        )

        controls: list[object] = [
            self._tab_buttons["enemy"],
            self._tab_buttons["miniboss"],
            self._tab_buttons["boss"],
            self._tab_buttons["event"],
            self._page_prev_button,
            self._page_next_button,
            self._event_interval_minus_button,
            self._event_interval_plus_button,
        ]
        actions = {
            self._tab_buttons["enemy"]: lambda: self._switch_tab("enemy"),
            self._tab_buttons["miniboss"]: lambda: self._switch_tab("miniboss"),
            self._tab_buttons["boss"]: lambda: self._switch_tab("boss"),
            self._tab_buttons["event"]: lambda: self._switch_tab("event"),
            self._page_prev_button: lambda: self._change_page(-1),
            self._page_next_button: lambda: self._change_page(1),
            self._event_interval_minus_button: lambda: self._adjust_event_interval(-self._event_interval_step),
            self._event_interval_plus_button: lambda: self._adjust_event_interval(self._event_interval_step),
        }

        for index, (minus_button, plus_button) in enumerate(zip(self._row_minus_buttons, self._row_plus_buttons)):
            self._row_minus_index_by_control[minus_button] = index
            self._row_plus_index_by_control[plus_button] = index
            controls.append(minus_button)
            controls.append(plus_button)
            actions[minus_button] = lambda idx=index: self._adjust_slot_count(idx, -1)
            actions[plus_button] = lambda idx=index: self._adjust_slot_count(idx, 1)

        controls.extend([self._start_button, self._back_button])
        actions[self._start_button] = self._start_training
        actions[self._back_button] = self._close

        self.set_navigator(
            controls=controls,
            actions=actions,
            on_cancel=self._close,
        )

        self._refresh_tab_view()

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        forwarded_events: list[pygame.event.Event] = []
        for event in events:
            if event.type != pygame.KEYDOWN:
                forwarded_events.append(event)
                continue
            if not self._handle_keyboard_shortcut(event):
                forwarded_events.append(event)
        super().handle_input(forwarded_events)

    def _register_themes(self) -> None:
        register_custom_element_themes(
            self.ui_manager,
            {
                "training_title_label": {
                    "colours": {
                        "normal_text": "#91ebff",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "44",
                        "bold": "1",
                    },
                },
                "training_subtitle_label": {
                    "colours": {
                        "normal_text": "#ddf8ff",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "0",
                    },
                },
                "training_keyboard_hint_label": {
                    "colours": {
                        "normal_text": "#9ed8ea",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "14",
                        "bold": "0",
                    },
                },
                "training_content_panel": {
                    "colours": {
                        "dark_bg": "#0f1e26",
                        "normal_border": "#49d4ff",
                    },
                    "misc": {
                        "border_width": 2,
                        "shadow_width": 0,
                        "shape": "rectangle",
                    },
                },
                "training_header_name_label": {
                    "colours": {
                        "normal_text": "#9be8ff",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
                "training_header_desc_label": {
                    "colours": {
                        "normal_text": "#9be8ff",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
                "training_header_count_label": {
                    "colours": {
                        "normal_text": "#9be8ff",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
                "training_tab_enemy_button": {
                    "colours": {
                        "normal_bg": "#112f15",
                        "hovered_bg": "#19461f",
                        "selected_bg": "#215f2a",
                        "active_bg": "#2a7834",
                        "normal_text": "#92f5a0",
                        "hovered_text": "#ddffe3",
                        "selected_text": "#ddffe3",
                        "normal_border": "#4ee06a",
                        "hovered_border": "#7ff08e",
                        "selected_border": "#b4f7bf",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
                "training_tab_miniboss_button": {
                    "colours": {
                        "normal_bg": "#3c1030",
                        "hovered_bg": "#561848",
                        "selected_bg": "#711f60",
                        "active_bg": "#8b2878",
                        "normal_text": "#ff95dd",
                        "hovered_text": "#ffe4f8",
                        "selected_text": "#ffe4f8",
                        "normal_border": "#ff5ec8",
                        "hovered_border": "#ff95dd",
                        "selected_border": "#ffc3ec",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
                "training_tab_boss_button": {
                    "colours": {
                        "normal_bg": "#3f1b04",
                        "hovered_bg": "#5b2808",
                        "selected_bg": "#75350b",
                        "active_bg": "#8f410f",
                        "normal_text": "#ffbd85",
                        "hovered_text": "#ffeddc",
                        "selected_text": "#ffeddc",
                        "normal_border": "#ff8e3a",
                        "hovered_border": "#ffad6b",
                        "selected_border": "#ffc89b",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
                "training_tab_event_button": {
                    "colours": {
                        "normal_bg": "#0b2d33",
                        "hovered_bg": "#11424b",
                        "selected_bg": "#175761",
                        "active_bg": "#1f6c77",
                        "normal_text": "#9bf7ff",
                        "hovered_text": "#e6fdff",
                        "selected_text": "#e6fdff",
                        "normal_border": "#5de3f2",
                        "hovered_border": "#8aedf7",
                        "selected_border": "#bbf5fb",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
                "training_event_interval_title_label": {
                    "colours": {
                        "normal_text": "#8de8f2",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "15",
                        "bold": "1",
                    },
                },
                "training_event_interval_value_label": {
                    "colours": {
                        "normal_text": "#dffcff",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "16",
                        "bold": "1",
                    },
                },
                "training_event_interval_minus_button": {
                    "colours": {
                        "normal_bg": "#10323a",
                        "hovered_bg": "#184955",
                        "selected_bg": "#1f6270",
                        "active_bg": "#287886",
                        "normal_text": "#c6f8ff",
                        "hovered_text": "#ecfdff",
                        "selected_text": "#ecfdff",
                        "normal_border": "#6ee8f6",
                        "hovered_border": "#97eff8",
                        "selected_border": "#c2f6fb",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "1",
                    },
                },
                "training_event_interval_plus_button": {
                    "colours": {
                        "normal_bg": "#10323a",
                        "hovered_bg": "#184955",
                        "selected_bg": "#1f6270",
                        "active_bg": "#287886",
                        "normal_text": "#c6f8ff",
                        "hovered_text": "#ecfdff",
                        "selected_text": "#ecfdff",
                        "normal_border": "#6ee8f6",
                        "hovered_border": "#97eff8",
                        "selected_border": "#c2f6fb",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "1",
                    },
                },
                "training_page_prev_button": {
                    "colours": {
                        "normal_bg": "#1b2f3c",
                        "hovered_bg": "#264353",
                        "selected_bg": "#30586d",
                        "active_bg": "#3a6f87",
                        "normal_text": "#b9eaff",
                        "hovered_text": "#ecf9ff",
                        "selected_text": "#ecf9ff",
                        "normal_border": "#5ebce3",
                        "hovered_border": "#8fd3ef",
                        "selected_border": "#bce7f7",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "1",
                    },
                },
                "training_page_next_button": {
                    "colours": {
                        "normal_bg": "#1b2f3c",
                        "hovered_bg": "#264353",
                        "selected_bg": "#30586d",
                        "active_bg": "#3a6f87",
                        "normal_text": "#b9eaff",
                        "hovered_text": "#ecf9ff",
                        "selected_text": "#ecf9ff",
                        "normal_border": "#5ebce3",
                        "hovered_border": "#8fd3ef",
                        "selected_border": "#bce7f7",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "18",
                        "bold": "1",
                    },
                },
                "training_start_button": {
                    "colours": {
                        "normal_bg": "#0a1f3e",
                        "hovered_bg": "#0f2f5c",
                        "selected_bg": "#154078",
                        "active_bg": "#1a4f92",
                        "normal_text": "#8fd6ff",
                        "hovered_text": "#e0f5ff",
                        "selected_text": "#e0f5ff",
                        "normal_border": "#2f9dff",
                        "hovered_border": "#66b9ff",
                        "selected_border": "#99d1ff",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "17",
                        "bold": "1",
                    },
                },
                "training_back_button": {
                    "colours": {
                        "normal_bg": "#35201d",
                        "hovered_bg": "#4d2f2a",
                        "selected_bg": "#664039",
                        "active_bg": "#7f5148",
                        "normal_text": "#ffd5cb",
                        "hovered_text": "#ffefeb",
                        "selected_text": "#ffefeb",
                        "normal_border": "#ff9d85",
                        "hovered_border": "#ffb59f",
                        "selected_border": "#ffcfbf",
                    },
                    "font": {
                        "name": "noto_sans",
                        "size": "17",
                        "bold": "1",
                    },
                },
            },
            rebuild_all=True,
        )

    def _switch_tab(self, category: TrainingTab) -> None:
        self._active_tab = category
        self._refresh_tab_view()

    def _switch_tab_by_offset(self, offset: int) -> None:
        current_index = self._tab_order.index(self._active_tab)
        target_index = (current_index + offset) % len(self._tab_order)
        self._switch_tab(self._tab_order[target_index])

    def _change_page(self, delta: int) -> None:
        if self._active_tab == "event":
            kinds = list(self._event_options)
        else:
            kinds = self._kinds_by_tab[self._active_tab]
        max_page = max(0, math.ceil(len(kinds) / self._rows_per_page) - 1)
        current = self._page_index_by_tab[self._active_tab]
        self._page_index_by_tab[self._active_tab] = max(0, min(max_page, current + delta))
        self._refresh_tab_view()

    def _adjust_slot_count(self, slot_index: int, delta: int) -> None:
        if slot_index < 0 or slot_index >= self._rows_per_page:
            return
        kind = self._slot_kinds[slot_index]
        if kind is None:
            return

        if self._active_tab == "event":
            if self._selected_event == kind:
                return
            self._selected_event = kind
            self._refresh_tab_view()
            return

        category = self._category_for_kind(kind)
        max_count = self._max_count_by_tab[category]
        current = self._selected_counts.get(kind, 0)
        updated = max(0, min(max_count, current + delta))
        if updated == current:
            return

        self._selected_counts[kind] = updated
        self._refresh_tab_view()

    def _refresh_tab_view(self) -> None:
        if self._active_tab == "event":
            kinds = list(self._event_options)
        else:
            kinds = self._kinds_by_tab[self._active_tab]
        max_page = max(0, math.ceil(len(kinds) / self._rows_per_page) - 1)
        current_page = min(self._page_index_by_tab[self._active_tab], max_page)
        self._page_index_by_tab[self._active_tab] = current_page

        start = current_page * self._rows_per_page
        visible_kinds = kinds[start : start + self._rows_per_page]

        for index in range(self._rows_per_page):
            kind = visible_kinds[index] if index < len(visible_kinds) else None
            self._slot_kinds[index] = kind
            name_label = self._row_name_labels[index]
            desc_label = self._row_desc_labels[index]
            minus_button = self._row_minus_buttons[index]
            count_label = self._row_count_labels[index]
            plus_button = self._row_plus_buttons[index]

            if kind is None:
                name_label.set_text("-")
                desc_label.set_text("-")
                count_label.set_text("-")
                minus_button.disable()
                plus_button.disable()
                continue

            if self._active_tab == "event":
                name_label.set_text(EVENT_LABELS.get(kind, _display_name(kind)))
                desc_label.set_text(EVENT_DESCRIPTIONS.get(kind, "Evento ambiental para treino."))
                is_selected = self._selected_event == kind
                count_label.set_text("ATIVO" if is_selected else "-")
                minus_button.set_text("Sel")
                plus_button.set_text("Sel")
                if is_selected:
                    minus_button.disable()
                    plus_button.disable()
                else:
                    minus_button.enable()
                    plus_button.enable()
                continue

            minus_button.set_text("-")
            plus_button.set_text("+")

            count_value = self._selected_counts.get(kind, 0)
            name_label.set_text(_display_name(kind))
            desc_label.set_text(ENEMY_DESCRIPTIONS.get(kind, "Arquetipo para treino especifico."))
            count_label.set_text(str(count_value))

            if count_value <= 0:
                minus_button.disable()
            else:
                minus_button.enable()

            max_count = self._max_count_by_tab[self._active_tab]
            if count_value >= max_count:
                plus_button.disable()
            else:
                plus_button.enable()

        self._page_label.set_text(f"Pagina {current_page + 1}/{max_page + 1}")
        if current_page <= 0:
            self._page_prev_button.disable()
        else:
            self._page_prev_button.enable()

        if current_page >= max_page:
            self._page_next_button.disable()
        else:
            self._page_next_button.enable()

        self._event_interval_value_label.set_text(f"{self._selected_event_interval:.0f}s")
        if self._active_tab == "event":
            self._event_interval_title_label.show()
            self._event_interval_value_label.show()
            self._event_interval_minus_button.show()
            self._event_interval_plus_button.show()
            if self._selected_event_interval <= self._event_interval_min:
                self._event_interval_minus_button.disable()
            else:
                self._event_interval_minus_button.enable()
            if self._selected_event_interval >= self._event_interval_max:
                self._event_interval_plus_button.disable()
            else:
                self._event_interval_plus_button.enable()
        else:
            self._event_interval_title_label.hide()
            self._event_interval_value_label.hide()
            self._event_interval_minus_button.hide()
            self._event_interval_plus_button.hide()
            self._event_interval_minus_button.disable()
            self._event_interval_plus_button.disable()

        self._update_tab_titles()
        self._update_summary()

    def _handle_keyboard_shortcut(self, event: pygame.event.Event) -> bool:
        key = event.key
        if key in (pygame.K_LEFT, pygame.K_a):
            return self._adjust_selected_row_count(-1)
        if key in (pygame.K_RIGHT, pygame.K_d):
            return self._adjust_selected_row_count(1)
        if key in (pygame.K_1, pygame.K_KP1):
            self._switch_tab("enemy")
            return True
        if key in (pygame.K_2, pygame.K_KP2):
            self._switch_tab("miniboss")
            return True
        if key in (pygame.K_3, pygame.K_KP3):
            self._switch_tab("boss")
            return True
        if key in (pygame.K_4, pygame.K_KP4):
            self._switch_tab("event")
            return True
        if key == pygame.K_q:
            self._switch_tab_by_offset(-1)
            return True
        if key == pygame.K_e:
            self._switch_tab_by_offset(1)
            return True
        if key == pygame.K_PAGEUP:
            self._change_page(-1)
            return True
        if key == pygame.K_PAGEDOWN:
            self._change_page(1)
            return True
        if key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            return self._adjust_selected_row_count(-1)
        if key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            return self._adjust_selected_row_count(1)
        return False

    def _adjust_selected_row_count(self, delta: int) -> bool:
        if self.navigator is None:
            return False
        selected_control = self.navigator.selected_control
        if selected_control is None:
            return False

        slot_index: int | None = None
        if selected_control in self._row_minus_index_by_control:
            slot_index = self._row_minus_index_by_control[selected_control]
        elif selected_control in self._row_plus_index_by_control:
            slot_index = self._row_plus_index_by_control[selected_control]

        if selected_control is self._event_interval_minus_button:
            self._adjust_event_interval(-self._event_interval_step)
            return True
        if selected_control is self._event_interval_plus_button:
            self._adjust_event_interval(self._event_interval_step)
            return True

        if slot_index is None:
            return False

        self._adjust_slot_count(slot_index, delta)
        return True

    def _adjust_event_interval(self, delta: float) -> None:
        if self._active_tab != "event":
            return
        updated = self._selected_event_interval + delta
        clamped = max(self._event_interval_min, min(self._event_interval_max, updated))
        if abs(clamped - self._selected_event_interval) <= 0.001:
            return
        self._selected_event_interval = clamped
        self._refresh_tab_view()

    def _update_tab_titles(self) -> None:
        for category in self._tab_order:
            marker = "> " if category == self._active_tab else ""
            if category == "event":
                event_label = EVENT_LABELS.get(self._selected_event, "Aleatorio")
                self._tab_buttons[category].set_text(f"{marker}Eventos ({event_label})")
                continue
            total = sum(self._selected_counts[kind] for kind in self._kinds_by_tab[category])
            self._tab_buttons[category].set_text(f"{marker}{ENEMY_CATEGORY_LABELS[category]} ({total})")

    def _update_summary(self) -> None:
        total_selected = sum(self._selected_counts.values())
        event_label = EVENT_LABELS.get(self._selected_event, "Aleatorio")
        self._summary_label.set_text(
            f"Selecionados: {total_selected} | Evento: {event_label} | Intervalo: {self._selected_event_interval:.0f}s"
        )
        if total_selected <= 0:
            self._start_button.disable()
        else:
            self._start_button.enable()

    def _category_for_kind(self, kind: str) -> EnemyCategory:
        if kind in self._kinds_by_tab["enemy"]:
            return "enemy"
        if kind in self._kinds_by_tab["miniboss"]:
            return "miniboss"
        return "boss"

    def _start_training(self) -> None:
        spawn_plan = {kind: count for kind, count in self._selected_counts.items() if count > 0}
        if not spawn_plan:
            return
        from game.scenes.game_scene import GameScene

        forced_event = None if self._selected_event == "random" else self._selected_event
        self.stack.replace(
            GameScene(
                self.stack,
                TrainingMode(
                    spawn_plan=spawn_plan,
                    config=TrainingConfig(
                        forced_environment_event=forced_event,
                        env_event_interval=self._selected_event_interval,
                    ),
                ),
            )
        )

    def _close(self) -> None:
        self.stack.pop()

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(
            screen=screen,
            elapsed_time=self._elapsed_time,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
        )


def _display_name(kind: str) -> str:
    return kind.replace("_", " ").title()
