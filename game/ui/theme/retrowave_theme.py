# === BASE COLORS ===
BG_MAIN = "#0d0019"
BG_DARK = "#08000f"
BG_HOVER = "#1a0533"
ACCENT_PURPLE = "#c724f5"
ACCENT_PINK = "#ff2fff"
ACCENT_BLUE = "#00f5ff"
TEXT_MAIN = "#e0c0ff"
TEXT_WHITE = "#ffffff"

# === BUTTON COLORS ===
BTN_BG = "#1a0533"
BTN_BG_HOVER = "#2d0a5e"
BTN_BG_DISABLED = "#0d0019"
BTN_BG_SELECTED = "#3d0f7a"
BTN_BG_ACTIVE = "#4a1296"

BTN_TEXT = "#f0a0ff"
BTN_TEXT_DISABLED = "#5a3a6e"

BTN_BORDER = "#c724f5"
BTN_BORDER_HOVER = "#ff2fff"
BTN_BORDER_DISABLED = "#2a1040"

# === THEME DATA ===
THEME_DATA = {

    "button": {
        "colours": {
            "normal_bg": BTN_BG,
            "hovered_bg": BTN_BG_HOVER,
            "disabled_bg": BTN_BG_DISABLED,
            "selected_bg": BTN_BG_SELECTED,
            "active_bg": BTN_BG_ACTIVE,

            "normal_text": BTN_TEXT,
            "hovered_text": TEXT_WHITE,
            "disabled_text": BTN_TEXT_DISABLED,
            "selected_text": TEXT_WHITE,

            "normal_border": BTN_BORDER,
            "hovered_border": BTN_BORDER_HOVER,
            "disabled_border": BTN_BORDER_DISABLED,
            "selected_border": BTN_BORDER_HOVER
        },
        "font": {
            "name": "monospace",
            "size": 14,
            "bold": 0
        },
        "misc": {
            "shape": "rectangle",
            "border_width": 2,
            "shadow_width": 0,
            "tool_tip_delay": 1.0
        }
    },

    "button.danger": {
        "colours": {
            "normal_bg": "#330a1a",
            "hovered_bg": "#5e0a2d",
            "normal_text": "#ff6090",
            "hovered_text": TEXT_WHITE,
            "normal_border": "#f52450",
            "hovered_border": "#ff2f6f"
        }
    },

    "button.primary": {
        "colours": {
            "normal_bg": "#0a1a33",
            "hovered_bg": "#0a2d5e",
            "normal_text": ACCENT_BLUE,
            "hovered_text": TEXT_WHITE,
            "normal_border": "#00b8d4",
            "hovered_border": ACCENT_BLUE
        }
    },

    "button.ghost": {
        "colours": {
            "normal_bg": "#00000000",
            "hovered_bg": "#1a053340",
            "normal_text": ACCENT_PURPLE,
            "hovered_text": BTN_TEXT,
            "normal_border": "#c724f540",
            "hovered_border": ACCENT_PURPLE
        }
    },

    "label": {
        "colours": {
            "normal_text": TEXT_MAIN,
            "normal_bg": "#00000000"
        },
        "font": {
            "name": "monospace",
            "size": 14,
            "bold": 0
        }
    },

    "label.title": {
        "colours": {
            "normal_text": ACCENT_PINK
        },
        "font": {
            "name": "monospace",
            "size": 22,
            "bold": 1
        }
    },

    "label.subtitle": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "monospace",
            "size": 16,
            "bold": 0
        }
    },

    "label.muted": {
        "colours": {
            "normal_text": "#6a4a7e"
        },
        "font": {
            "name": "monospace",
            "size": 12,
            "bold": 0
        }
    },

    "label.value": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "monospace",
            "size": 14,
            "bold": 1
        }
    },

    "panel": {
        "colours": {
            "dark_bg": BG_MAIN,
            "normal_border": "#c724f540"
        },
        "misc": {
            "border_width": 1,
            "shadow_width": 0,
            "shape": "rectangle"
        }
    },

    "panel.card": {
        "colours": {
            "dark_bg": "#150028",
            "normal_border": ACCENT_PURPLE
        },
        "misc": {
            "border_width": 2
        }
    },

    "panel.hud": {
        "colours": {
            "dark_bg": "#0a001580",
            "normal_border": "#00f5ff40"
        },
        "misc": {
            "border_width": 1
        }
    },

    "text_entry_line": {
        "colours": {
            "normal_bg": BG_MAIN,
            "focused_bg": BG_HOVER,
            "disabled_bg": BG_DARK,

            "normal_text": TEXT_MAIN,
            "focused_text": TEXT_WHITE,
            "disabled_text": "#3a2050",
            "selected_text": TEXT_WHITE,

            "normal_border": "#c724f570",
            "focused_border": ACCENT_PURPLE,
            "disabled_border": "#1a0a2e",

            "cursor_colour": ACCENT_PINK,
            "selected_bg": "#3d0f7a"
        },
        "font": {
            "name": "monospace",
            "size": 14,
            "bold": 0
        },
        "misc": {
            "border_width": 2,
            "shape": "rectangle",
            "padding": "4,2"
        }
    },

    "status_bar": {
        "colours": {
            "normal_bg": BG_MAIN,
            "normal_border": "#c724f540",
            "bars_colour": ACCENT_PURPLE,
            "normal_text": TEXT_MAIN
        },
        "misc": {
            "border_width": 1
        }
    },

    "status_bar.health": {
        "colours": {
            "bars_colour": "#ff2f6f"
        }
    },

    "status_bar.energy": {
        "colours": {
            "bars_colour": ACCENT_BLUE
        }
    },

    "status_bar.xp": {
        "colours": {
            "bars_colour": "#ffe600"
        }
    },

    "horizontal_slider": {
        "colours": {
            "normal_bg": BG_MAIN,
            "hovered_bg": BG_HOVER,
            "disabled_bg": BG_DARK,
            "normal_text": TEXT_MAIN,

            "normal_border": "#c724f570",
            "hovered_border": ACCENT_PURPLE,
            "disabled_border": "#1a0a2e",

            "filled_bar": ACCENT_PURPLE,
            "unfilled_bar": BG_HOVER
        },
        "misc": {
            "border_width": 2
        }
    },

    "check_box": {
        "colours": {
            "normal_bg": BG_MAIN,
            "hovered_bg": BG_HOVER,
            "selected_bg": BTN_BG_HOVER,

            "normal_text": TEXT_MAIN,
            "hovered_text": TEXT_WHITE,
            "selected_text": TEXT_WHITE,

            "normal_border": "#c724f570",
            "hovered_border": ACCENT_PURPLE,
            "selected_border": ACCENT_PINK
        },
        "misc": {
            "border_width": 2
        }
    },

    "scrolling_container": {
        "colours": {
            "dark_bg": BG_MAIN,
            "normal_border": "#c724f540"
        },
        "misc": {
            "border_width": 1
        }
    },

    "vertical_scroll_bar": {
        "colours": {
            "normal_bg": BG_MAIN,
            "hovered_bg": BG_HOVER,
            "normal_border": "#c724f530",
            "hovered_border": ACCENT_PURPLE,
            "filled_bar": "#c724f580",
            "unfilled_bar": BG_MAIN
        }
    },

    "defaults": {
        "colours": {
            "normal_bg": BG_MAIN,
            "dark_bg": BG_DARK,
            "normal_text": TEXT_MAIN,
            "normal_border": "#c724f540",
            "link_text": ACCENT_BLUE,
            "link_hover": ACCENT_PINK,
            "link_selected": TEXT_WHITE,
            "text_shadow": "#00000000",
            "filled_bar": ACCENT_PURPLE,
            "unfilled_bar": BG_HOVER
        },
        "font": {
            "name": "monospace",
            "size": 14,
            "bold": 0,
            "italic": 0
        },
        "misc": {
            "border_width": 1,
            "shadow_width": 0,
            "shape": "rectangle"
        }
    }
}