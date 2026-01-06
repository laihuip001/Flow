"""
AI Clipboard Pro - Flet GUI Application (Alpha)

A unified GUI for AI-powered clipboard text processing.
Phase 4.2 Alpha - Full feature integration.
"""
import flet as ft
import asyncio
from datetime import datetime
from api_client import process_text_stream

# Available styles with icons and descriptions
STYLES = [
    {"key": "business", "icon": ft.Icons.BUSINESS_CENTER, "label": "Business", "desc": "ビジネスメール向け"},
    {"key": "casual", "icon": ft.Icons.CHAT_BUBBLE, "label": "Casual", "desc": "カジュアルな口調"},
    {"key": "summary", "icon": ft.Icons.SUMMARIZE, "label": "Summary", "desc": "箇条書き要約"},
    {"key": "english", "icon": ft.Icons.TRANSLATE, "label": "English", "desc": "英語に翻訳"},
    {"key": "proofread", "icon": ft.Icons.SPELLCHECK, "label": "Proofread", "desc": "校正のみ"},
]

# Default backend URL
DEFAULT_BACKEND_URL = "http://localhost:8000"


class ClipboardHistory:
    """In-memory clipboard history manager."""
    
    def __init__(self, max_items: int = 20):
        self.items = []
        self.max_items = max_items
    
    def add(self, original: str, result: str, style: str):
        """Add a new history item."""
        item = {
            "timestamp": datetime.now().strftime("%H:%M"),
            "original": original[:50] + "..." if len(original) > 50 else original,
            "result": result,
            "style": style,
        }
        self.items.insert(0, item)
        if len(self.items) > self.max_items:
            self.items.pop()
    
    def get_all(self):
        """Get all history items."""
        return self.items
    
    def clear(self):
        """Clear all history."""
        self.items = []


# Global history instance
history = ClipboardHistory()


async def main(page: ft.Page):
    """Main Flet application entry point."""
    
    # Page setup
    page.title = "AI Clipboard Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 420
    page.window.height = 700
    page.bgcolor = "#1a1a2e"
    
    # State
    backend_url = DEFAULT_BACKEND_URL
    selected_style = "business"
    is_processing = False
    current_view = "main"  # "main" or "history" or "settings"
    
    # --- Style Button Grid ---
    def create_style_button(style_info):
        async def on_click(e):
            nonlocal selected_style
            selected_style = style_info["key"]
            # Update button states
            for btn in style_buttons:
                btn.bgcolor = "#3d3d5c" if btn.data != selected_style else "#6366f1"
            await page.update_async()
        
        btn = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(style_info["icon"], size=28, color=ft.Colors.WHITE),
                    ft.Text(style_info["label"], size=12, weight=ft.FontWeight.BOLD),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            width=75,
            height=70,
            bgcolor="#3d3d5c" if style_info["key"] != "business" else "#6366f1",
            border_radius=12,
            alignment=ft.alignment.center,
            on_click=on_click,
            data=style_info["key"],
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
        return btn
    
    style_buttons = [create_style_button(s) for s in STYLES]
    
    style_grid = ft.Container(
        content=ft.Row(
            style_buttons,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=8,
        ),
        padding=ft.padding.symmetric(horizontal=10),
    )
    
    # --- Input Area ---
    input_field = ft.TextField(
        hint_text="Enter or paste text here...",
        multiline=True,
        min_lines=4,
        max_lines=6,
        border_radius=12,
        filled=True,
        bgcolor="#2d2d44",
        border_color="transparent",
        focused_border_color="#6366f1",
    )
    
    async def paste_clipboard(e):
        clipboard_text = await page.get_clipboard_async()
        if clipboard_text:
            input_field.value = clipboard_text
            await page.update_async()
    
    input_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Input", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
                ft.IconButton(
                    icon=ft.Icons.CONTENT_PASTE,
                    icon_color=ft.Colors.WHITE70,
                    tooltip="Paste from clipboard",
                    on_click=paste_clipboard,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            input_field,
        ]),
        padding=ft.padding.symmetric(horizontal=16),
    )
    
    # --- Output Area ---
    output_field = ft.TextField(
        hint_text="AI result will appear here...",
        multiline=True,
        min_lines=4,
        max_lines=8,
        border_radius=12,
        filled=True,
        bgcolor="#2d2d44",
        border_color="transparent",
        read_only=True,
    )
    
    async def copy_result(e):
        if output_field.value:
            await page.set_clipboard_async(output_field.value)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Copied to clipboard!"),
                bgcolor="#22c55e",
            )
            page.snack_bar.open = True
            await page.update_async()
    
    copy_button = ft.IconButton(
        icon=ft.Icons.COPY,
        icon_color=ft.Colors.WHITE70,
        tooltip="Copy result",
        on_click=copy_result,
        disabled=True,
    )
    
    output_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Result", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70),
                copy_button,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            output_field,
        ]),
        padding=ft.padding.symmetric(horizontal=16),
    )
    
    # --- Process Button ---
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20, color=ft.Colors.WHITE)
    
    async def process_click(e):
        nonlocal is_processing
        
        if not input_field.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("⚠️ Please enter some text first."),
                bgcolor="#f59e0b",
            )
            page.snack_bar.open = True
            await page.update_async()
            return
        
        if is_processing:
            return
        
        is_processing = True
        process_button.disabled = True
        progress_ring.visible = True
        output_field.value = ""
        copy_button.disabled = True
        await page.update_async()
        
        original_text = input_field.value
        
        try:
            async for chunk in process_text_stream(
                original_text,
                style=selected_style,
                base_url=backend_url
            ):
                output_field.value += chunk
                await page.update_async()
            
            copy_button.disabled = False
            
            # Add to history
            if output_field.value and not output_field.value.startswith("Error"):
                history.add(original_text, output_field.value, selected_style)
            
        except Exception as ex:
            output_field.value = f"Error: {str(ex)}"
        
        finally:
            is_processing = False
            process_button.disabled = False
            progress_ring.visible = False
            await page.update_async()
    
    process_button = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.WHITE),
                ft.Text("Process", size=16, weight=ft.FontWeight.BOLD),
                progress_ring,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        style=ft.ButtonStyle(
            bgcolor="#6366f1",
            color=ft.Colors.WHITE,
            padding=ft.padding.symmetric(vertical=16),
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=process_click,
        width=380,
    )
    
    process_section = ft.Container(
        content=process_button,
        padding=ft.padding.symmetric(horizontal=16),
    )
    
    # --- History View ---
    def build_history_view():
        items = history.get_all()
        if not items:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY, size=48, color=ft.Colors.WHITE30),
                    ft.Text("No history yet", color=ft.Colors.WHITE30),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        history_items = []
        for item in items:
            history_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(item["timestamp"], color=ft.Colors.WHITE54, size=11),
                            ft.Container(
                                content=ft.Text(item["style"].upper(), size=10, color=ft.Colors.WHITE),
                                bgcolor="#6366f1",
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_radius=4,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(item["original"], color=ft.Colors.WHITE70, size=12),
                        ft.Text(item["result"][:100] + "..." if len(item["result"]) > 100 else item["result"], 
                               color=ft.Colors.WHITE, size=13),
                    ], spacing=4),
                    bgcolor="#2d2d44",
                    border_radius=8,
                    padding=12,
                    margin=ft.margin.only(bottom=8),
                )
            )
        
        return ft.Column(
            controls=history_items,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    history_container = ft.Container(
        content=build_history_view(),
        padding=16,
        expand=True,
    )
    
    # --- Navigation Bar ---
    async def nav_change(e):
        nonlocal current_view
        index = e.control.selected_index
        if index == 0:
            current_view = "main"
            main_view.visible = True
            history_view.visible = False
            settings_view.visible = False
        elif index == 1:
            current_view = "history"
            main_view.visible = False
            history_container.content = build_history_view()
            history_view.visible = True
            settings_view.visible = False
        elif index == 2:
            current_view = "settings"
            main_view.visible = False
            history_view.visible = False
            settings_view.visible = True
        await page.update_async()
    
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY, label="History"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        selected_index=0,
        on_change=nav_change,
        bgcolor="#1a1a2e",
        indicator_color="#6366f1",
    )
    
    # --- Settings View ---
    url_field = ft.TextField(
        label="Backend URL",
        value=DEFAULT_BACKEND_URL,
        border_radius=12,
        filled=True,
        bgcolor="#2d2d44",
    )
    
    def on_url_change(e):
        nonlocal backend_url
        backend_url = e.control.value
    
    url_field.on_change = on_url_change
    
    async def clear_history_click(e):
        history.clear()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("History cleared"),
            bgcolor="#6366f1",
        )
        page.snack_bar.open = True
        await page.update_async()
    
    settings_content = ft.Column([
        ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
        ft.Divider(height=20, color=ft.Colors.WHITE12),
        url_field,
        ft.Divider(height=20, color=ft.Colors.WHITE12),
        ft.ElevatedButton(
            text="Clear History",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=clear_history_click,
            style=ft.ButtonStyle(bgcolor="#dc2626"),
        ),
        ft.Divider(height=20, color=ft.Colors.WHITE12),
        ft.Text("AI Clipboard Pro v4.0 Alpha", color=ft.Colors.WHITE30, size=12),
    ], spacing=12)
    
    settings_view = ft.Container(
        content=settings_content,
        padding=20,
        visible=False,
        expand=True,
    )
    
    # --- Main View ---
    main_view = ft.Column([
        ft.Container(height=16),
        ft.Container(
            content=ft.Text("AI Clipboard Pro", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            alignment=ft.alignment.center,
        ),
        ft.Container(height=16),
        style_grid,
        ft.Container(height=16),
        input_section,
        ft.Container(height=12),
        process_section,
        ft.Container(height=12),
        output_section,
    ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    history_view = ft.Container(
        content=history_container,
        visible=False,
        expand=True,
    )
    
    # --- Page Layout ---
    page.add(
        ft.Container(
            content=ft.Stack([
                main_view,
                history_view,
                settings_view,
            ]),
            expand=True,
        ),
        nav_bar,
    )


# Entry point
if __name__ == "__main__":
    ft.run(target=main)
