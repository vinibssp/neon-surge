from __future__ import annotations

import math
from typing import Callable, Literal

import pygame
import pygame_gui

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.enemy_names import format_enemy_name
from game.factories.enemy_factory import EnemyFactory
from game.modes.mode_config import TrainingConfig
from game.modes.training_mode import TrainingMode
from game.scenes.menus._base_menu_scene import BaseMenuScene
from game.scenes.services import CyberpunkMenuBackgroundRenderer
from game.ui.gui_theme import build_component_object_id
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
                rect=pygame.Rect((SCREEN_WIDTH // 2 - 320, 34), (640, 72)),
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
        tab_w, tab_h, gap = 240, 40, 10
        tab_start_x = SCREEN_WIDTH // 2 - 495
        
        self._tab_buttons: dict[TrainingTab, object] = {
            "enemy": create_button(
                ButtonConfig(text="Inimigos", rect=pygame.Rect((tab_start_x, 150), (tab_w, tab_h)), variant="tab_enemy"),
                manager=self.ui_manager,
            ),
            "miniboss": create_button(
                ButtonConfig(text="Minibosses", rect=pygame.Rect((tab_start_x + (tab_w + gap), 150), (tab_w, tab_h)), variant="tab_miniboss"),
                manager=self.ui_manager,
            ),
            "boss": create_button(
                ButtonConfig(text="Bosses", rect=pygame.Rect((tab_start_x + 2 * (tab_w + gap), 150), (tab_w, tab_h)), variant="tab_boss"),
                manager=self.ui_manager,
            ),
            "event": create_button(
                ButtonConfig(text="Eventos", rect=pygame.Rect((tab_start_x + 3 * (tab_w + gap), 150), (tab_w, tab_h)), variant="tab_event"),
                manager=self.ui_manager,
            ),
        }

        # Main Panel
        self._content_panel = create_panel(
            PanelConfig(rect=pygame.Rect((SCREEN_WIDTH // 2 - 500, 200), (1000, 400)), variant="card"),
            manager=self.ui_manager,
        )

        # Table Headers
        self._header_name_label = create_label(
            LabelConfig(text="Entidade", rect=pygame.Rect((20, 10), (220, 30)), variant="header"),
            manager=self.ui_manager, container=self._content_panel,
        )
        self._header_desc_label = create_label(
            LabelConfig(text="Descricao", rect=pygame.Rect((250, 10), (450, 30)), variant="header"),
            manager=self.ui_manager, container=self._content_panel,
        )
        self._header_count_label = create_label(
            LabelConfig(text="Qtd", rect=pygame.Rect((780, 10), (100, 30)), variant="header"),
            manager=self.ui_manager, container=self._content_panel,
        )

        # Rows
        self._row_name_labels = []
        self._row_desc_labels = []
        self._row_minus_buttons = []
        self._row_count_labels = []
        self._row_plus_buttons = []

        row_y, row_h = 50, 45
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
            m_btn = create_button(
                ButtonConfig(text="-", rect=pygame.Rect((720, y), (45, 35)), variant="ghost"),
                manager=self.ui_manager, container=self._content_panel
            )
            self._row_minus_buttons.append(m_btn)
            self._row_count_labels.append(create_label(
                LabelConfig(text="0", rect=pygame.Rect((775, y), (80, 35)), variant="value"),
                manager=self.ui_manager, container=self._content_panel
            ))
            p_btn = create_button(
                ButtonConfig(text="+", rect=pygame.Rect((865, y), (45, 35)), variant="ghost"),
                manager=self.ui_manager, container=self._content_panel
            )
            self._row_plus_buttons.append(p_btn)
            self._control_actions[m_btn] = lambda idx=i: self._adjust_slot_count(idx, -1)
            self._control_actions[p_btn] = lambda idx=i: self._adjust_slot_count(idx, 1)

        # Pagination
        self._page_label = create_label(
            LabelConfig(text="Pagina 1/1", rect=pygame.Rect((400, 325), (200, 30)), variant="muted"),
            manager=self.ui_manager, container=self._content_panel
        )
        self._page_prev_button = create_button(
            ButtonConfig(text="<", rect=pygame.Rect((340, 320), (50, 35)), variant="ghost"),
            manager=self.ui_manager, container=self._content_panel
        )
        self._page_next_button = create_button(
            ButtonConfig(text=">", rect=pygame.Rect((610, 320), (50, 35)), variant="ghost"),
            manager=self.ui_manager, container=self._content_panel
        )

        # Event Interval
        self._event_interval_panel = create_panel(
            PanelConfig(rect=pygame.Rect((150, 330), (700, 60)), variant="hud"),
            manager=self.ui_manager, container=self._content_panel
        )
        create_label(
            LabelConfig(text="INTERVALO ENTRE EVENTOS", rect=pygame.Rect((20, 15), (260, 30)), variant="header"),
            manager=self.ui_manager, container=self._event_interval_panel
        )
        self._event_interval_minus_btn = create_button(
            ButtonConfig(text="-", rect=pygame.Rect((300, 12), (50, 35)), variant="ghost"),
            manager=self.ui_manager, container=self._event_interval_panel
        )
        self._event_interval_value_label = create_label(
            LabelConfig(text="22s", rect=pygame.Rect((360, 12), (100, 35)), variant="value"),
            manager=self.ui_manager, container=self._event_interval_panel
        )
        self._event_interval_plus_btn = create_button(
            ButtonConfig(text="+", rect=pygame.Rect((470, 12), (50, 35)), variant="ghost"),
            manager=self.ui_manager, container=self._event_interval_panel
        )

        # Bottom
        self._summary_label = create_label(
            LabelConfig(text="Total: 0", rect=pygame.Rect((SCREEN_WIDTH // 2 - 300, 605), (600, 30)), variant="subtitle"),
            manager=self.ui_manager,
        )
        self._keyboard_hint_label = create_label(
            LabelConfig(text="1-4: Abas | Q/E: Alternar | PgUp/Dn: Pagina | Enter: Iniciar | +/-: Ajustar | Mouse Wheel: Pagina | Dir: Ajuste Rapido", 
                        rect=pygame.Rect((SCREEN_WIDTH // 2 - 500, 635), (1000, 25)), variant="muted"),
            manager=self.ui_manager,
        )
        self._start_button = create_button(
            ButtonConfig(text="INICIAR TREINO", rect=pygame.Rect((SCREEN_WIDTH // 2 - 260, 665), (250, 50)), variant="primary"),
            manager=self.ui_manager,
        )
        self._back_button = create_button(
            ButtonConfig(text="VOLTAR", rect=pygame.Rect((SCREEN_WIDTH // 2 + 10, 665), (250, 50)), variant="danger"),
            manager=self.ui_manager,
        )

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
        old_sel = self.navigator.selected_control if self.navigator else None

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

        kinds = list(self._event_options) if self._active_tab == "event" else self._kinds_by_tab[self._active_tab]
        max_page = max(0, math.ceil(len(kinds) / self._rows_per_page) - 1)
        current_page = min(self._page_index_by_tab[self._active_tab], max_page)
        self._page_index_by_tab[self._active_tab] = current_page

        start = current_page * self._rows_per_page
        visible_kinds = kinds[start : start + self._rows_per_page]

        for i in range(self._rows_per_page):
            kind = visible_kinds[i] if i < len(visible_kinds) else None
            self._slot_kinds[i] = kind
            
            n_lbl, d_lbl, m_btn, c_lbl, p_btn = self._row_name_labels[i], self._row_desc_labels[i], \
                self._row_minus_buttons[i], self._row_count_labels[i], self._row_plus_buttons[i]

            if kind is None:
                for ctrl in [n_lbl, d_lbl, c_lbl]: ctrl.set_text("-")
                for btn in [m_btn, p_btn]: btn.disable()
                continue

            if self._active_tab == "event":
                n_lbl.set_text(EVENT_LABELS.get(kind, kind.title()))
                is_active = self._selected_event == kind
                c_lbl.set_text("ATIVO" if is_active else "-")
                c_lbl.change_object_id(build_component_object_id("label", "highlight" if is_active else "value"))
                d_lbl.set_text(EVENT_DESCRIPTIONS.get(kind, ""))
                d_lbl.change_object_id(build_component_object_id("label", "value" if is_active else "muted"))
                m_btn.set_text("Ativar"); m_btn.enable()
                if is_active: m_btn.disable()
                p_btn.hide()
            else:
                n_lbl.set_text(format_enemy_name(kind))
                d_lbl.set_text(ENEMY_DESCRIPTIONS.get(kind, ""))
                d_lbl.change_object_id(build_component_object_id("label", None))
                count = self._selected_counts.get(kind, 0)
                c_lbl.set_text(str(count))
                c_lbl.change_object_id(build_component_object_id("label", "value"))
                m_btn.set_text("-"); p_btn.show(); p_btn.enable()
                if count <= 0: m_btn.disable()
                else: m_btn.enable()

        self._page_label.set_text(f"Pagina {current_page + 1}/{max_page + 1}")
        if self._active_tab == "event":
            for ctrl in [self._page_label, self._page_prev_button, self._page_next_button]: ctrl.hide()
        else:
            for ctrl in [self._page_label, self._page_prev_button, self._page_next_button]: ctrl.show()
            if current_page <= 0: self._page_prev_button.disable()
            else: self._page_prev_button.enable()
            if current_page >= max_page: self._page_next_button.disable()
            else: self._page_next_button.enable()

        self._event_interval_value_label.set_text(f"{self._selected_event_interval:.0f}s")
        self._update_tab_highlights(); self._update_summary(); self._rebuild_navigator(old_sel)

    def _update_tab_highlights(self) -> None:
        for cat, btn in self._tab_buttons.items():
            marker = ">> " if cat == self._active_tab else ""
            if cat == "event":
                btn.set_text(f"{marker}Eventos ({EVENT_LABELS.get(self._selected_event, 'Aleatorio')})")
            else:
                total = sum(self._selected_counts[k] for k in self._kinds_by_tab[cat])
                btn.set_text(f"{marker}{ENEMY_CATEGORY_LABELS[cat]} ({total})")

    def _update_summary(self) -> None:
        total = sum(self._selected_counts.values())
        self._summary_label.set_text(f"Selecionados: {total} | Evento: {EVENT_LABELS.get(self._selected_event, 'Aleatorio')} | Intervalo: {self._selected_event_interval:.0f}s")
        if total <= 0: self._start_button.disable()
        else: self._start_button.enable()

    def _switch_tab(self, tab: TrainingTab) -> None:
        self._active_tab = tab; self._refresh_view()

    def _change_page(self, delta: int) -> None:
        kinds = list(self._event_options) if self._active_tab == "event" else self._kinds_by_tab[self._active_tab]
        max_page = max(0, math.ceil(len(kinds) / self._rows_per_page) - 1)
        self._page_index_by_tab[self._active_tab] = max(0, min(max_page, self._page_index_by_tab[self._active_tab] + delta))
        self._refresh_view()

    def _adjust_slot_count(self, slot_idx: int, delta: int) -> None:
        kind = self._slot_kinds[slot_idx]
        if kind:
            if self._active_tab == "event": self._selected_event = kind
            else:
                self._selected_counts[kind] = max(0, min(self._max_count_by_tab[self._active_tab], self._selected_counts.get(kind, 0) + delta))
            self._refresh_view()

    def _adjust_event_interval(self, delta: float) -> None:
        self._selected_event_interval = max(self._event_interval_min, min(self._event_interval_max, self._selected_event_interval + delta))
        self._refresh_view()

    def _rebuild_navigator(self, old_sel: object | None = None) -> None:
        controls = [self._tab_buttons[t] for t in self._tab_order]
        if self._active_tab != "event": controls.extend([self._page_prev_button, self._page_next_button])
        for i in range(self._rows_per_page):
            if self._slot_kinds[i]:
                controls.append(self._row_minus_buttons[i])
                if self._active_tab != "event": controls.append(self._row_plus_buttons[i])
        if self._active_tab == "event": controls.extend([self._event_interval_minus_btn, self._event_interval_plus_btn])
        controls.extend([self._start_button, self._back_button])
        
        self.set_navigator(controls=controls, actions={c: self._control_actions[c] for c in controls if c in self._control_actions}, on_cancel=self._close)
        if old_sel in controls: self.navigator.select_index(controls.index(old_sel))
        elif not self.navigator.selected_control and controls: self.navigator.select_index(min(len(controls)-1, 4 + (0 if self._active_tab == "event" else 2)))

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        filtered = []
        for e in events:
            if e.type == pygame.MOUSEWHEEL: self._change_page(-e.y); continue
            if e.type == pygame.USEREVENT and e.user_type == pygame_gui.UI_BUTTON_ON_HOVERED:
                if self.navigator and e.ui_element in self.navigator.controls: self.navigator.select_index(self.navigator.controls.index(e.ui_element))
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3: self._handle_right_click(e.pos); continue
            if e.type == pygame.KEYDOWN and self._handle_shortcuts(e.key): continue
            filtered.append(e)
        super().handle_input(filtered)

    def _handle_right_click(self, pos: tuple[int, int]) -> bool:
        for btn in self._row_plus_buttons:
            if btn.rect.collidepoint(pos): self._adjust_slot_count(self._row_plus_buttons.index(btn), 5); return True
        for btn in self._row_minus_buttons:
            if btn.rect.collidepoint(pos):
                k = self._slot_kinds[self._row_minus_buttons.index(btn)]
                if k and self._active_tab != "event": self._selected_counts[k] = 0; self._refresh_view()
                return True
        for b, v in [(self._event_interval_plus_btn, 10), (self._event_interval_minus_btn, -10)]:
            if b.rect.collidepoint(pos): self._adjust_event_interval(v); return True
        return False

    def _handle_shortcuts(self, k: int) -> bool:
        if k in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]: self._switch_tab(self._tab_order[k - pygame.K_1]); return True
        if k == pygame.K_q: self._switch_tab_by_offset(-1); return True
        if k == pygame.K_e: self._switch_tab_by_offset(1); return True
        if k == pygame.K_PAGEUP: self._change_page(-1); return True
        if k == pygame.K_PAGEDOWN: self._change_page(1); return True
        if k in [pygame.K_w, pygame.K_UP]: return self._navigate_vertically(-1)
        if k in [pygame.K_s, pygame.K_DOWN]: return self._navigate_vertically(1)
        if k in [pygame.K_a, pygame.K_LEFT]: return self._navigate_horizontally(-1)
        if k in [pygame.K_d, pygame.K_RIGHT]: return self._navigate_horizontally(1)
        if k in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]: self._adjust_selected_control(1); return True
        if k in [pygame.K_MINUS, pygame.K_KP_MINUS]: self._adjust_selected_control(-1); return True
        return False

    def _navigate_vertically(self, d: int) -> bool:
        if not self.navigator or not self.navigator.selected_control: return False
        ctrl, ctrls = self.navigator.selected_control, list(self.navigator.controls)
        rows = [[self._tab_buttons[t] for t in self._tab_order]]
        if self._active_tab != "event": rows.append([self._page_prev_button, self._page_next_button])
        for i in range(self._rows_per_page):
            r = []
            if self._row_minus_buttons[i] in ctrls: r.append(self._row_minus_buttons[i])
            if self._active_tab != "event" and self._row_plus_buttons[i] in ctrls: r.append(self._row_plus_buttons[i])
            if r: rows.append(r)
        if self._active_tab == "event": rows.append([self._event_interval_minus_btn, self._event_interval_plus_btn])
        rows.append([self._start_button, self._back_button])
        curr_r = next((i for i, r in enumerate(rows) if ctrl in r), -1)
        if curr_r == -1: return False
        t_row = rows[(curr_r + d) % len(rows)]
        self.navigator.select_index(ctrls.index(t_row[min(rows[curr_r].index(ctrl), len(t_row)-1)]))
        return True

    def _navigate_horizontally(self, d: int) -> bool:
        if not self.navigator or not self.navigator.selected_control: return False
        ctrl = self.navigator.selected_control
        rows = [[self._row_minus_buttons[i], self._row_plus_buttons[i]] for i in range(self._rows_per_page)] + [[self._event_interval_minus_btn, self._event_interval_plus_btn]]
        for r in rows:
            if ctrl in r:
                t_idx = r.index(ctrl) + d
                if 0 <= t_idx < len(r): 
                    if r[t_idx] in self.navigator.controls: self.navigator.select_index(self.navigator.controls.index(r[t_idx])); return True
                self._adjust_selected_control(d); return True
        self.navigator.move_selection(d); return True

    def _switch_tab_by_offset(self, o: int) -> None: self._switch_tab(self._tab_order[(self._tab_order.index(self._active_tab) + o) % len(self._tab_order)])

    def _adjust_selected_control(self, d: int) -> bool:
        ctrl = self.navigator.selected_control
        if ctrl in self._row_minus_buttons: self._adjust_slot_count(self._row_minus_buttons.index(ctrl), d); return True
        if ctrl in self._row_plus_buttons: self._adjust_slot_count(self._row_plus_buttons.index(ctrl), d); return True
        if ctrl in [self._event_interval_minus_btn, self._event_interval_plus_btn]: self._adjust_event_interval(d * self._event_interval_step); return True
        return False

    def _start_training(self) -> None:
        plan = {k: v for k, v in self._selected_counts.items() if v > 0}
        if plan:
            from game.scenes.game_scene import GameScene
            self.stack.replace(GameScene(self.stack, TrainingMode(spawn_plan=plan, config=TrainingConfig(forced_environment_event=None if self._selected_event == "random" else self._selected_event, env_event_interval=self._selected_event_interval))))

    def _close(self) -> None: self.stack.pop()
    def on_menu_update(self, dt: float) -> None: self._elapsed_time += dt
    def render_menu_background(self, screen: pygame.Surface) -> None: self._background_renderer.render(screen, self._elapsed_time, SCREEN_WIDTH, SCREEN_HEIGHT)
