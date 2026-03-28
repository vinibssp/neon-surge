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
            "name": "noto_sans",
            "size": "14",
            "bold": "0"
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

    "button.tab_enemy": {
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
            "selected_border": "#b4f7bf"
        },
        "font": { "name": "noto_sans", "size": "16", "bold": "1" }
    },

    "button.tab_miniboss": {
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
            "selected_border": "#ffc3ec"
        },
        "font": { "name": "noto_sans", "size": "16", "bold": "1" }
    },

    "button.tab_boss": {
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
            "selected_border": "#ffc89b"
        },
        "font": { "name": "noto_sans", "size": "16", "bold": "1" }
    },

    "button.tab_event": {
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
            "selected_border": "#bbf5fb"
        },
        "font": { "name": "noto_sans", "size": "16", "bold": "1" }
    },

    "button.race": {
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
            "selected_border": "#99d1ff"
        }
    },

    "button.race_infinite": {
        "colours": {
            "normal_bg": "#201044",
            "hovered_bg": "#2f1964",
            "selected_bg": "#3d2382",
            "active_bg": "#4b2da0",
            "normal_text": "#c9a8ff",
            "hovered_text": "#f0e6ff",
            "selected_text": "#f0e6ff",
            "normal_border": "#9f6bff",
            "hovered_border": "#bb96ff",
            "selected_border": "#d5c0ff"
        }
    },

    "button.survival": {
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
            "selected_border": "#ffc3ec"
        }
    },

    "button.hardcore": {
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
            "selected_border": "#ffc89b"
        }
    },

    "button.labyrinth": {
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
            "selected_border": "#b4f7bf"
        }
    },

    "button.training": {
        "colours": {
            "normal_bg": "#0b3140",
            "hovered_bg": "#11495d",
            "selected_bg": "#17627a",
            "active_bg": "#1d7a96",
            "normal_text": "#91ebff",
            "hovered_text": "#ddf8ff",
            "selected_text": "#ddf8ff",
            "normal_border": "#49d4ff",
            "hovered_border": "#86e5ff",
            "selected_border": "#b6efff"
        }
    },

    "label": {
        "colours": {
            "normal_text": TEXT_MAIN,
            "normal_bg": "#00000000"
        },
        "font": {
            "name": "noto_sans",
            "size": "14",
            "bold": "0"
        }
    },

    "label.title": {
        "colours": {
            "normal_text": ACCENT_PINK
        },
        "font": {
            "name": "noto_sans",
            "size": "48",
            "bold": "1"
        }
    },

    "label.game_over_title": {
        "colours": {
            "normal_text": ACCENT_PINK
        },
        "font": {
            "name": "noto_sans",
            "size": "36",
            "bold": "1"
        }
    },

    "label.game_over_subtitle": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "noto_sans",
            "size": "16",
            "bold": "1"
        }
    },

    "label.game_over_item": {
        "colours": {
            "normal_text": "#8fc7e6"
        },
        "font": {
            "name": "noto_sans",
            "size": "14",
            "bold": "0"
        }
    },

    "label.game_over_value": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "noto_sans",
            "size": "14",
            "bold": "1"
        }
    },

    "label.game_over_breakdown": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "noto_sans",
            "size": "12",
            "bold": "1"
        }
    },

    "label.game_over_muted": {
        "colours": {
            "normal_text": "#6a4a7e"
        },
        "font": {
            "name": "noto_sans",
            "size": "12",
            "bold": "0"
        }
    },

    "label.subtitle": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "noto_sans",
            "size": "20",
            "bold": "0"
        }
    },

    "label.muted": {
        "colours": {
            "normal_text": "#6a4a7e"
        },
        "font": {
            "name": "noto_sans",
            "size": "12",
            "bold": "0"
        }
    },

    "label.value": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "noto_sans",
            "size": "16",
            "bold": "1"
        }
    },

    "label.highlight": {
        "colours": {
            "normal_text": "#00ff00"
        },
        "font": {
            "name": "noto_sans",
            "size": "14",
            "bold": "0"
        }
    },

    "label.header": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "noto_sans",
            "size": "16",
            "bold": "1"
        }
    },

    "label.guide_section": {
        "colours": {
            "normal_text": "#f6de75"
        },
        "font": {
            "name": "noto_sans",
            "size": "24",
            "bold": "1"
        }
    },

    "label.guide_body": {
        "colours": {
            "normal_text": "#ffe4a6"
        },
        "font": {
            "name": "noto_sans",
            "size": "18",
            "bold": "0"
        }
    },

    "label.guide_accent": {
        "colours": {
            "normal_text": "#8defff"
        },
        "font": {
            "name": "noto_sans",
            "size": "14",
            "bold": "0"
        }
    },

    "label.settings_header": {
        "colours": {
            "normal_text": ACCENT_BLUE
        },
        "font": {
            "name": "noto_sans",
            "size": "24",
            "bold": "1"
        }
    },

    "label.settings_label": {
        "colours": {
            "normal_text": TEXT_MAIN
        },
        "font": {
            "name": "noto_sans",
            "size": "18",
            "bold": "0"
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
            "name": "noto_sans",
            "size": "14",
            "bold": "0"
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
            "name": "noto_sans",
            "size": "14",
            "bold": "0",
            "italic": 0
        },
        "misc": {
            "border_width": 1,
            "shadow_width": 0,
            "shape": "rectangle"
        }
    }
}