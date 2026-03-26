from __future__ import annotations

import math
from typing import Callable, Literal

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.factories.enemy_factory import EnemyFactory
from game.modes.mode_config import TrainingConfig
from game.modes.training_mode import TrainingMode
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.components import ButtonConfig, LabelConfig, PanelConfig, create_button, create_label, create_panel

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

        # State initialization
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
        
        # UI references
        self._slot_kinds: list[str | None] = [None] * self._rows_per_page
        self._control_actions: dict[object, Callable[[], None]] = {}
        
        self._init_ui()
        self._refresh_view()

    def _init_ui(self) -> None:
        """Initialize all UI components."""
        # Header
        create_label(
            LabelConfig(
                text="TREINO PERSONALIZADO",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 40), (600, 60)),
                variant="title",
            ),
            manager=self.ui_manager,
        )
        create_label(
            LabelConfig(
                text="Configure as hordas e eventos para praticar suas habilidades.",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 360, 100), (720, 30)),
                variant="subtitle",
            ),
            manager=self.ui_manager,
        )

        # Tabs
        self._tab_buttons: dict[TrainingTab, object] = {
            "enemy": create_button(
                ButtonConfig(
                    text="Inimigos",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 - 440, 150), (210, 40)),
                    variant="tab_enemy",
                ),
                manager=self.ui_manager,
            ),
            "miniboss": create_button(
                ButtonConfig(
                    text="Minibosses",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 - 220, 150), (210, 40)),
                    variant="tab_miniboss",
                ),
                manager=self.ui_manager,
            ),
            "boss": create_button(
                ButtonConfig(
                    text="Bosses",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 + 10, 150), (200, 40)),
                    variant="tab_boss",
                ),
                manager=self.ui_manager,
            ),
            "event": create_button(
                ButtonConfig(
                    text="Eventos",
                    rect=pygame.Rect((SCREEN_WIDTH // 2 + 220, 150), (200, 40)),
                    variant="tab_event",
                ),
                manager=self.ui_manager,
            ),
        }

        # Main Panel
        self._content_panel = create_panel(
            PanelConfig(
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 500, 200), (1000, 360)),
                variant="card",
            ),
            manager=self.ui_manager,
        )

        # Table Headers
        self._header_name_label = create_label(
            LabelConfig(
                text="Entidade",
                rect=pygame.Rect((20, 10), (220, 30)),
                variant="header",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        self._header_desc_label = create_label(
            LabelConfig(
                text="Descricao",
                rect=pygame.Rect((250, 10), (450, 30)),
                variant="header",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )
        self._header_count_label = create_label(
            LabelConfig(
                text="Qtd",
                rect=pygame.Rect((780, 10), (100, 30)),
                variant="header",
            ),
            manager=self.ui_manager,
            container=self._content_panel,
        )

        # Rows
        self._row_name_labels: list[object] = []
        self._row_desc_labels: list[object] = []
        self._row_minus_buttons: list[object] = []
        self._row_count_labels: list[object] = []
        self._row_plus_buttons: list[object] = []

        row_y = 50
        row_h = 45
        for i in range(self._rows_per_page):
            y = row_y + i * row_h
            self._row_name_labels.append(create_label(
                LabelConfig(text="-", rect=pygame.Rect((20, y), (220, 35)), variant="value"),
                manager=self.ui_manager, container=self._content_panel
            ))
            self._row_desc_labels.append(create_label(
                LabelConfig(text="-", rect=pygame.Rect((250, y), (450, 35))),
                manager=self.ui_manager, container=self._content_panel
            ))
            minus_btn = create_button(
                ButtonConfig(text="-", rect=pygame.Rect((720, y), (45, 35)), variant="ghost"),
                manager=self.ui_manager, container=self._content_panel
            )
            self._row_minus_buttons.append(minus_btn)
            self._row_count_labels.append(create_label(
                LabelConfig(text="0", rect=pygame.Rect((775, y), (80, 35)), variant="value"),
                manager=self.ui_manager, container=self._content_panel
            ))
            plus_btn = create_button(
                ButtonConfig(text="+", rect=pygame.Rect((865, y), (45, 35)), variant="ghost"),
                manager=self.ui_manager, container=self._content_panel
            )
            self._row_plus_buttons.append(plus_btn)
            
            # Register row actions
            self._control_actions[minus_btn] = lambda idx=i: self._adjust_slot_count(idx, -1)
            self._control_actions[plus_btn] = lambda idx=i: self._adjust_slot_count(idx, 1)

        # Pagination
        self._page_label = create_label(
            LabelConfig(text="Pagina 1/1", rect=pygame.Rect((400, 320), (200, 30)), variant="muted"),
            manager=self.ui_manager, container=self._content_panel
        )
        self._page_prev_button = create_button(
            ButtonConfig(text="<", rect=pygame.Rect((340, 315), (50, 35)), variant="ghost"),
            manager=self.ui_manager, container=self._content_panel
        )
        self._page_next_button = create_button(
            ButtonConfig(text=">", rect=pygame.Rect((610, 315), (50, 35)), variant="ghost"),
            manager=self.ui_manager, container=self._content_panel
        )

        # Event Interval Controls (Special for Event tab)
        self._event_interval_panel = create_panel(
            PanelConfig(rect=pygame.Rect((250, 260), (500, 50)), variant="hud"),
            manager=self.ui_manager, container=self._content_panel
        )
        create_label(
            LabelConfig(text="Intervalo de Evento", rect=pygame.Rect((10, 10), (200, 30)), variant="header"),
            manager=self.ui_manager, container=self._event_interval_panel
        )
        self._event_interval_minus_btn = create_button(
            ButtonConfig(text="-", rect=pygame.Rect((220, 10), (40, 30)), variant="ghost"),
            manager=self.ui_manager, container=self._event_interval_panel
        )
        self._event_interval_value_label = create_label(
            LabelConfig(text="22s", rect=pygame.Rect((270, 10), (80, 30)), variant="value"),
            manager=self.ui_manager, container=self._event_interval_panel
        )
        self._event_interval_plus_btn = create_button(
            ButtonConfig(text="+", rect=pygame.Rect((360, 10), (40, 30)), variant="ghost"),
            manager=self.ui_manager, container=self._event_interval_panel
        )

        # Bottom Summary & Controls
        self._summary_label = create_label(
            LabelConfig(
                text="Total Selecionado: 0",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 570), (600, 30)),
                variant="subtitle",
            ),
            manager=self.ui_manager,
        )
        self._keyboard_hint_label = create_label(
            LabelConfig(
                text="1-4: Abas | Q/E: Alternar | PgUp/Dn: Pagina | Enter: Iniciar | +/-: Ajustar",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 500, 600), (1000, 25)),
                variant="muted",
            ),
            manager=self.ui_manager,
        )

        self._start_button = create_button(
            ButtonConfig(
                text="INICIAR TREINO",
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 260, 630), (250, 50)),
                variant="primary",
            ),
            manager=self.ui_manager,
        )
        self._back_button = create_button(
            ButtonConfig(
                text="VOLTAR",
                rect=pygame.Rect((SCREEN_WIDTH // 2 + 10, 630), (250, 50)),
                variant="danger",
            ),
            manager=self.ui_manager,
        )

        # Register Global Actions
        self._control_actions.update({
            self._tab_buttons["enemy"]: lambda: self._switch_tab("enemy"),
            self._tab_buttons["miniboss"]: lambda: self._switch_tab("miniboss"),
            self._tab_buttons["boss"]: lambda: self._switch_tab("boss"),
            self._tab_buttons["event"]: lambda: self._switch_tab("event"),
            self._page_prev_button: lambda: self._change_page(-1),
            self._page_next_button: lambda: self._change_page(1),
            self._event_interval_minus_btn: lambda: self._adjust_event_interval(-self._event_interval_step),
            self._event_interval_plus_btn: lambda: self._adjust_event_interval(self._event_interval_step),
            self._start_button: self._start_training,
            self._back_button: self._close,
        })

    def _refresh_view(self) -> None:
        """Update UI elements based on current state."""
        # Keep track of current selection to restore it later
        old_sel = self.navigator.selected_control if self.navigator else None

        # Update header labels based on tab
        if self._active_tab == "event":
            self._header_name_label.set_text("Evento")
            self._header_desc_label.set_text("Efeito")
            self._header_count_label.set_text("Status")
            self._event_interval_panel.show()
        else:
            self._header_name_label.set_text("Entidade")
            self._header_desc_label.set_text("Descricao")
            self._header_count_label.set_text("Qtd")
            self._event_interval_panel.hide()

        # Pagination logic
        kinds = list(self._event_options) if self._active_tab == "event" else self._kinds_by_tab[self._active_tab]
        max_page = max(0, math.ceil(len(kinds) / self._rows_per_page) - 1)
        current_page = min(self._page_index_by_tab[self._active_tab], max_page)
        self._page_index_by_tab[self._active_tab] = current_page

        start = current_page * self._rows_per_page
        visible_kinds = kinds[start : start + self._rows_per_page]

        # Update rows
        for i in range(self._rows_per_page):
            kind = visible_kinds[i] if i < len(visible_kinds) else None
            self._slot_kinds[i] = kind
            
            name_lbl = self._row_name_labels[i]
            desc_lbl = self._row_desc_labels[i]
            minus_btn = self._row_minus_buttons[i]
            count_lbl = self._row_count_labels[i]
            plus_btn = self._row_plus_buttons[i]

            if kind is None:
                name_lbl.set_text("-")
                desc_lbl.set_text("-")
                count_lbl.set_text("-")
                minus_btn.disable()
                plus_btn.disable()
                continue

            if self._active_tab == "event":
                name_lbl.set_text(EVENT_LABELS.get(kind, kind.title()))
                desc_lbl.set_text(EVENT_DESCRIPTIONS.get(kind, ""))
                is_active = self._selected_event == kind
                count_lbl.set_text("ATIVO" if is_active else "-")
                minus_btn.set_text("Ativar")
                if is_active:
                    minus_btn.disable()
                else:
                    minus_btn.enable()
                plus_btn.hide()
            else:
                name_lbl.set_text(kind.replace("_", " ").title())
                desc_lbl.set_text(ENEMY_DESCRIPTIONS.get(kind, ""))
                count = self._selected_counts.get(kind, 0)
                count_lbl.set_text(str(count))
                minus_btn.set_text("-")
                plus_btn.show()
                plus_btn.enable() # Always enabled for focus stability
                
                if count <= 0: minus_btn.disable()
                else: minus_btn.enable()

        # Update page label and buttons
        self._page_label.set_text(f"Pagina {current_page + 1}/{max_page + 1}")
        if current_page <= 0: self._page_prev_button.disable()
        else: self._page_prev_button.enable()
        if current_page >= max_page: self._page_next_button.disable()
        else: self._page_next_button.enable()

        # Update event interval
        self._event_interval_value_label.set_text(f"{self._selected_event_interval:.0f}s")
        self._event_interval_minus_btn.enable()
        self._event_interval_plus_btn.enable()

        self._update_tab_highlights()
        self._update_summary()
        self._rebuild_navigator(old_sel)

    def _update_tab_highlights(self) -> None:
        """Highlight the active tab."""
        for cat, btn in self._tab_buttons.items():
            marker = ">> " if cat == self._active_tab else ""
            if cat == "event":
                label = EVENT_LABELS.get(self._selected_event, "Aleatorio")
                btn.set_text(f"{marker}Eventos ({label})")
            else:
                total = sum(self._selected_counts[k] for k in self._kinds_by_tab[cat])
                btn.set_text(f"{marker}{ENEMY_CATEGORY_LABELS[cat]} ({total})")

    def _update_summary(self) -> None:
        total = sum(self._selected_counts.values())
        event = EVENT_LABELS.get(self._selected_event, "Aleatorio")
        self._summary_label.set_text(
            f"Selecionados: {total} | Evento: {event} | Intervalo: {self._selected_event_interval:.0f}s"
        )
        if total <= 0: self._start_button.disable()
        else: self._start_button.enable()

    def _switch_tab(self, tab: TrainingTab) -> None:
        self._active_tab = tab
        self._refresh_view()

    def _change_page(self, delta: int) -> None:
        kinds = list(self._event_options) if self._active_tab == "event" else self._kinds_by_tab[self._active_tab]
        max_page = max(0, math.ceil(len(kinds) / self._rows_per_page) - 1)
        current = self._page_index_by_tab[self._active_tab]
        self._page_index_by_tab[self._active_tab] = max(0, min(max_page, current + delta))
        self._refresh_view()

    def _adjust_slot_count(self, slot_idx: int, delta: int) -> None:
        kind = self._slot_kinds[slot_idx]
        if kind is None: return

        if self._active_tab == "event":
            self._selected_event = kind
        else:
            current = self._selected_counts.get(kind, 0)
            max_c = self._max_count_by_tab[self._active_tab]
            self._selected_counts[kind] = max(0, min(max_c, current + delta))
        
        self._refresh_view()

    def _adjust_event_interval(self, delta: float) -> None:
        updated = self._selected_event_interval + delta
        self._selected_event_interval = max(self._event_interval_min, min(self._event_interval_max, updated))
        self._refresh_view()

    def _rebuild_navigator(self, old_sel: object | None = None) -> None:
        """Sync UINavigator with current visible controls."""
        controls: list[object] = []
        # Tab buttons are NOT focusable via keyboard navigation (switched via Q/E)
        # but are clickable by mouse.

        if self._active_tab == "event":
            for btn in self._row_minus_buttons:
                if btn.is_enabled: controls.append(btn)
            controls.extend([self._event_interval_minus_btn, self._event_interval_plus_btn])
        else:
            controls.extend([self._page_prev_button, self._page_next_button])
            # Focus only plus_btn for rows to maintain vertical list
            for p in self._row_plus_buttons:
                if p.is_enabled: controls.append(p)

        controls.extend([self._start_button, self._back_button])
        
        actions = {c: self._control_actions[c] for c in controls if c in self._control_actions}
        self.set_navigator(controls=controls, actions=actions, on_cancel=self._close)
        
        # Restore focus
        if old_sel and self.navigator and old_sel in controls:
            self.navigator.select_index(controls.index(old_sel))
        elif self.navigator and not self.navigator.selected_control and controls:
            self.navigator.select_index(0)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        filtered_events = []
        for event in events:
            consumed = False
            if event.type == pygame.KEYDOWN:
                consumed = self._handle_shortcuts(event.key)
            if not consumed:
                filtered_events.append(event)
        super().handle_input(filtered_events)

    def _handle_shortcuts(self, key: int) -> bool:
        # Tab change shortcuts (Q/E and 1-4)
        if key == pygame.K_1: self._switch_tab("enemy"); return True
        if key == pygame.K_2: self._switch_tab("miniboss"); return True
        if key == pygame.K_3: self._switch_tab("boss"); return True
        if key == pygame.K_4: self._switch_tab("event"); return True
        if key == pygame.K_q: self._switch_tab_by_offset(-1); return True
        if key == pygame.K_e: self._switch_tab_by_offset(1); return True
        
        # Navigation shortcuts
        if key == pygame.K_PAGEUP: self._change_page(-1); return True
        if key == pygame.K_PAGEDOWN: self._change_page(1); return True
        
        # Strictly Vertical Navigation (W/S and Up/Down)
        if key in (pygame.K_w, pygame.K_UP):
            return self._navigate_vertically(-1)
        if key in (pygame.K_s, pygame.K_DOWN):
            return self._navigate_vertically(1)
            
        # Horizontal Navigation / Adjustment (A/D and Left/Right)
        if key in (pygame.K_a, pygame.K_LEFT):
            return self._navigate_horizontally(-1)
        if key in (pygame.K_d, pygame.K_RIGHT):
            return self._navigate_horizontally(1)
            
        # Plus/Minus shortcuts
        if key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
            self._adjust_selected_control(1); return True
        if key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self._adjust_selected_control(-1); return True

        return False

    def _navigate_vertically(self, delta: int) -> bool:
        if not self.navigator or not self.navigator.selected_control: return False
        ctrl = self.navigator.selected_control
        controls = list(self.navigator.controls)
        
        # Define functional blocks
        pagination = [self._page_prev_button, self._page_next_button]
        rows = [r for r in (self._row_plus_buttons if self._active_tab != "event" else self._row_minus_buttons) if r in controls]
        event_ctrls = [self._event_interval_minus_btn, self._event_interval_plus_btn]
        bottom = [self._start_button, self._back_button]

        target = None
        if ctrl in pagination:
            if delta > 0: target = rows[0] if rows else bottom[0]
            else: target = bottom[0]
        elif ctrl in rows:
            idx = rows.index(ctrl)
            if delta > 0:
                if idx < len(rows) - 1: target = rows[idx + 1]
                elif self._active_tab == "event": target = event_ctrls[0]
                else: target = bottom[0]
            else:
                if idx > 0: target = rows[idx - 1]
                elif self._active_tab != "event": target = pagination[0]
                else: target = bottom[-1]
        elif ctrl in event_ctrls:
            if delta > 0: target = bottom[0]
            else: target = rows[-1] if rows else pagination[0]
        elif ctrl in bottom:
            if delta < 0:
                if self._active_tab == "event": target = event_ctrls[0]
                elif rows: target = rows[-1]
                else: target = pagination[0]
            else:
                if self._active_tab != "event": target = pagination[0]
                elif rows: target = rows[0]
        
        if target and target in controls:
            self.navigator.select_index(controls.index(target))
            return True
        return False

    def _navigate_horizontally(self, delta: int) -> bool:
        if not self.navigator or not self.navigator.selected_control: return False
        ctrl = self.navigator.selected_control

        # In rows, A/D only adjust values
        cur_rows = self._row_plus_buttons if self._active_tab != "event" else self._row_minus_buttons
        if ctrl in cur_rows:
            self._adjust_slot_count(cur_rows.index(ctrl), delta)
            return True
        
        # In event interval, A/D adjust
        if ctrl in (self._event_interval_minus_btn, self._event_interval_plus_btn):
            self._adjust_event_interval(delta * self._event_interval_step)
            return True

        # In other blocks (pagination, bottom), A/D moves focus
        self.navigator.move_selection(delta)
        return True

    def _switch_tab_by_offset(self, offset: int) -> None:
        idx = (self._tab_order.index(self._active_tab) + offset) % len(self._tab_order)
        self._switch_tab(self._tab_order[idx])

    def _adjust_selected_control(self, delta: int) -> bool:
        if not self.navigator or not self.navigator.selected_control:
            return False
            
        ctrl = self.navigator.selected_control
        if ctrl in self._row_minus_buttons:
            self._adjust_slot_count(self._row_minus_buttons.index(ctrl), delta)
            return True
        if ctrl in self._row_plus_buttons:
            self._adjust_slot_count(self._row_plus_buttons.index(ctrl), delta)
            return True
        if ctrl in (self._event_interval_minus_btn, self._event_interval_plus_btn):
            self._adjust_event_interval(delta * self._event_interval_step)
            return True
        return False



    def _start_training(self) -> None:
        plan = {k: v for k, v in self._selected_counts.items() if v > 0}
        if not plan: return
        
        from game.scenes.game_scene import GameScene
        event = None if self._selected_event == "random" else self._selected_event
        self.stack.replace(GameScene(self.stack, TrainingMode(
            spawn_plan=plan,
            config=TrainingConfig(
                forced_environment_event=event,
                env_event_interval=self._selected_event_interval
            )
        )))

    def _close(self) -> None:
        self.stack.pop()

    def on_menu_update(self, dt: float) -> None:
        self._elapsed_time += dt

    def render_menu_background(self, screen: pygame.Surface) -> None:
        self._background_renderer.render(screen, self._elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)
