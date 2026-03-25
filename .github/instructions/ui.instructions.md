---
applyTo: 'game/ui/**'
---
# Diretrizes para UI (pygame_gui)

Sempre que criar ou editar arquivos na pasta de interface de usuário (UI), siga estas regras estritas:

1. **Uso Exclusivo de `pygame_gui`**: Toda a interface deve ser renderizada através dos elementos do `pygame_gui` (`UIButton`, `UILabel`, `UIPanel`, etc). Não desenhe primitivas diretas do pygame (`pygame.draw`) a menos que seja um componente customizado que exija isso.
2. **Posicionamento Relativo (Anchors)**:
   - NUNCA use matemática manual para centralizar ou posicionar elementos (ex: `(screen_width - width) // 2`).
   - Use sempre as `anchors` fornecidas pelo `pygame_gui` (ex: `{'center': 'center'}`, `{'centerx': 'centerx', 'top': 'top'}`).
   - Isso garante que a UI será responsiva a mudanças de resolução de tela.
3. **Estilização Desacoplada**:
   - As cores, fontes e estilos devem residir no arquivo de tema JSON (`retrowave_theme.json`). 
   - Evite passar propriedades de estilo diretamente na instanciação dos objetos de UI no código Python.
4. **Componentes Declarativos**:
   - Utilize funções factory ou builders (como os existentes em `base_widgets.py` ou `overlay_builder.py`) passando dicionários ou dataclasses de configuração (`ButtonConfig`, `PanelConfig`).
