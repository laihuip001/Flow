import flet as ft

# --- Titanium Theme Colors ---
COLOR_BG = "#1a1a2e"
COLOR_SURFACE = "#2d2d44"
COLOR_PRIMARY = "#6366f1"  # Indigo-ish
COLOR_ACCENT = "#818cf8"
COLOR_TEXT = "#FFFFFF"
COLOR_TEXT_DIM = "#FFFFFFB3" # 70%

class TitaniumTheme:
    """Titanium Theme Definition"""
    theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=COLOR_PRIMARY,
            on_primary=COLOR_TEXT,
            # background=COLOR_BG, # Removed to fix TypeError
            surface=COLOR_SURFACE,
            on_surface=COLOR_TEXT,
        ),
        font_family="Roboto",
    )

class MagicButton(ft.Container):
    """The 'Zero Friction' Main Action Button"""
    def __init__(self, on_click):
        super().__init__()
        self.on_click_fn = on_click
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[COLOR_PRIMARY, COLOR_ACCENT],
        )
        self.content = ft.Row(
            [
                ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.WHITE, size=24),
                ft.Text("AI Magic Transform", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )
        self.padding = 20
        self.border_radius = 16
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.with_opacity(0.5, COLOR_PRIMARY),
            offset=ft.Offset(0, 4),
        )
        self.on_click = self._handle_click
        # Visuals
        self.ink = True
    
    async def _handle_click(self, e):
        if self.on_click_fn:
            await self.on_click_fn(e)

class SeasoningBadge(ft.Container):
    """Seasoning Level Indicator"""
    def __init__(self, level: int):
        super().__init__()
        from src.core.seasoning import SeasoningManager
        label = SeasoningManager.get_level_label(level)
        
        # Color scale
        color = ft.Colors.BLUE_200 # Salt
        if level > 30: color = ft.Colors.ORANGE_300 # Sauce
        if level > 70: color = ft.Colors.RED_400 # Spice

        self.content = ft.Row(
            [
                ft.Icon(ft.Icons.soup_kitchen, size=14, color=color),
                ft.Text(f"{label} ({level}%)", size=12, color=ft.Colors.WHITE),
            ],
            spacing=6,
        )
        self.bgcolor = ft.Colors.with_opacity(0.1, color)
        self.padding = ft.padding.symmetric(horizontal=12, vertical=6)
        self.border_radius = 20
        self.border = ft.border.all(1, ft.Colors.with_opacity(0.5, color))

class SyncJobItem(ft.Container):
    """List Item for History View"""
    def __init__(self, job, on_click=None):
        super().__init__()
        self.job = job # Dict or Object
        result_preview = job.get("result", "") or ""
        if len(result_preview) > 500: # Limit only very long text
            result_preview = result_preview[:500] + "..."
        
        status_color = {
            "pending": ft.Colors.ORANGE,
            "processing": ft.Colors.BLUE,
            "completed": ft.Colors.GREEN,
            "failed": ft.Colors.RED
        }.get(job.get("status", "pending"), ft.Colors.GREY)

        seasoning_val = job.get("seasoning", 30)
        from src.core.seasoning import SeasoningManager
        seasoning_label = SeasoningManager.get_level_label(seasoning_val)

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(job.get("created_at_fmt", ""), color=ft.Colors.WHITE54, size=11),
                        ft.Container(
                            content=ft.Text(
                                f"{seasoning_label} ({seasoning_val}%)", 
                                size=10, 
                                color=ft.Colors.WHITE, 
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=COLOR_PRIMARY,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=4,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CIRCLE, size=10, color=status_color),
                        ft.Text(job.get("status", "pending").upper(), size=10, color=status_color),
                    ],
                    spacing=4
                ),
                ft.Divider(height=1, color=ft.Colors.WHITE10),
                # Show full input text (truncated slightly less)
                ft.Text(job.get("text", ""), color=ft.Colors.WHITE70, size=12, no_wrap=False, max_lines=3, overflow=ft.TextOverflow.ELLIPSIS),
                # Show result prominently
                ft.Container(
                    content=ft.Text(result_preview, color=ft.Colors.WHITE, size=14, selectable=True), # Selectable!
                    bgcolor=ft.Colors.BLACK12,
                    padding=8,
                    border_radius=4,
                )
            ],
            spacing=4,
        )
        self.bgcolor = COLOR_SURFACE
        self.border_radius = 8
        self.padding = 12
        self.margin = ft.margin.only(bottom=8)
        self.on_click = on_click

class SeasoningSlider(ft.Column):
    def __init__(self, on_change=None):
        super().__init__()
        self.on_change_fn = on_change
        self.slider = ft.Slider(
            min=0, max=100, divisions=10, value=30, 
            label="{value}%", 
            on_change=self._handle_change,
            active_color=COLOR_ACCENT
        )
        self.label = ft.Text("Seasoning Level: Salt (30%)", color=COLOR_TEXT_DIM, size=12)
        
        self.controls = [
            ft.Text("Seasoning (味付け)", size=14, weight=ft.FontWeight.BOLD),
            self.slider,
            ft.Container(content=self.label, alignment=ft.Alignment(0, 0))
        ]
        self.spacing = 0

    def set_value(self, val: int):
        self.slider.value = val
        self._update_label(val)
        if self.on_change_fn:
            self.on_change_fn(val)

    def _handle_change(self, e):
        val = int(e.control.value)
        self._update_label(val)
        if self.on_change_fn:
            self.on_change_fn(val)

    def _update_label(self, val: int):
        from src.core.seasoning import SeasoningManager
        lbl = SeasoningManager.get_level_label(val)
        self.label.value = f"Seasoning Level: {lbl} ({val}%)"
        self.label.update()
    
    @property
    def value(self):
        return int(self.slider.value)
