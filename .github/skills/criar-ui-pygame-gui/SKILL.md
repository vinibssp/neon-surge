---
name: criar-ui-pygame-gui
description: "Use esta skill quando o usuário pedir para criar, modificar ou integrar elementos de UI com pygame_gui (menus, overlays, HUD, painéis, controles interativos)."
---

# Workflow: Criação e Manutenção de UI com pygame_gui

Siga este fluxo para manter a UI alinhada à arquitetura atual do Neon Surge 2.

## 1) Escolher o contrato de cena correto

- Para menus/overlays: herdar de `BaseMenuScene`.
- Não instanciar `pygame_gui.UIManager` manualmente na cena; usar `create_ui_manager(...)` via base (`BaseMenuScene`).
- A cena orquestra fluxo e transições; não implementa motor de navegação próprio.

## 2) Construir UI por composição declarativa

- Criar widgets com factories em `game/ui/components/`:
  - `create_button(ButtonConfig)`
  - `create_label(LabelConfig)`
  - `create_panel(PanelConfig)`
  - `create_slider(SliderConfig)`
  - `create_checkbox(CheckboxConfig)`
  - `create_text_input(TextInputConfig)`
  - `create_status_bar(StatusBarConfig)`
- Evitar criação ad-hoc de elementos `pygame_gui.elements.*` dentro das cenas quando já existir factory equivalente.
- Preferir `variant` semântico para estilo; usar `object_id` apenas para identificação/override pontual.

## 3) Registrar navegação unificada

- Registrar navegação com `set_navigator(controls=..., actions=..., on_cancel=...)`.
- `controls` define a ordem oficial de foco.
- `UINavigator` opera em `FocusableControl` e unifica: `button`, `slider`, `checkbox`, `text_entry`.
- Não criar rotas paralelas de confirmação/cancelamento fora do navigator.

Exemplo:

```python
self.set_navigator(
    controls=[start_button, music_slider, fullscreen_checkbox, name_input, back_button],
    actions={
        start_button: self._start,
        back_button: self._back,
    },
    on_cancel=self._back,
)
```

## 4) Processar eventos somente na fronteira oficial

- Fluxo obrigatório: `pygame_gui event -> PygameGUIEventAdapter -> UINavigator -> action/event_bus`.
- Em `BaseMenuScene`, manter `handle_input()` delegando primeiro para `ui_event_adapter.process_event(event)` e depois para `ui_manager.process_events(event)` quando não consumido.
- Não traduzir input bruto em ações de widget diretamente na cena.

## 5) Atualizar e renderizar no ciclo padrão

- Em `update(dt)`: manter `ui_manager.update(dt)` e usar `on_menu_update(dt)` para estado visual da cena.
- Em `render(screen)`: desenhar fundo no `render_menu_background(screen)`, depois `ui_manager.draw_ui(screen)`, depois overlays no `render_menu_foreground(screen)`.
- Não acoplar regra de gameplay ao render da UI.

## 6) Tema e estilo (sem hardcode de visual em cena)

- Tema base centralizado em `game/ui/theme/retrowave_theme.py` (`THEME_DATA`).
- Criação de object/class ids via `build_component_object_id(...)`.
- Overrides pontuais com `register_custom_element_themes(...)` quando necessário.
- Evitar hardcode de cor/fonte na cena para styling recorrente; elevar para variante de tema.

## 7) Regras de qualidade para UI

- Sem números mágicos para layout recorrente; preferir constantes/specs/helpers.
- Sem lógica de domínio dentro de componentes visuais.
- Sem duplicação de fluxo de navegação entre cenas.
- Manter contratos públicos estáveis (`BaseMenuScene`, `PygameGUIEventAdapter`, `UINavigator`, factories de componente).

## Checklist de entrega

- Usa `BaseMenuScene` e factories de componentes.
- Usa `set_navigator(controls=..., actions=...)`.
- Navegação publicada via `UINavigated`/`UIConfirmed`/`UICancelled`.
- Estilo centralizado em tema (`THEME_DATA`) ou override pontual justificado.
- Cena apenas orquestra fluxo/transições.
