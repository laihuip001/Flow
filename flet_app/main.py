"""
AI Clipboard Pro - Flet GUI Application (Beta)

A unified GUI for AI-powered clipboard text processing.
Phase 4.3 Beta - Distribution ready with onboarding.
"""
import flet as ft
import asyncio
import json
import os
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

# Config file path
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "backend_url": "http://localhost:8000",
    "onboarding_complete": False,
}


def load_config():
    """Load configuration from file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
    except Exception:
        pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Config save error: {e}")


class ClipboardHistory:
    """In-memory clipboard history manager."""
    
    def __init__(self, max_items: int = 20):
        self.items = []
        self.max_items = max_items
    
    def add(self, original: str, result: str, style: str):
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
        return self.items
    
    def clear(self):
        self.items = []


history = ClipboardHistory()


async def main(page: ft.Page):
    """Main Flet application entry point."""
    
    # Load config
    config = load_config()
    
    # Page setup
    page.title = "AI Clipboard Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 420
    page.window.height = 700
    page.bgcolor = "#1a1a2e"
    
    # State
    backend_url = config["backend_url"]
    selected_style = "business"
    is_processing = False
    
    # ========================================
    # ONBOARDING SCREENS
    # ========================================
    
    async def complete_onboarding(e):
        config["onboarding_complete"] = True
        config["backend_url"] = backend_url
        save_config(config)
        onboarding_view.visible = False
        main_app_view.visible = True
        await page.update_async()
    
    def update_url(e):
        nonlocal backend_url
        backend_url = e.control.value
    
    # Onboarding Step 1: Welcome
    welcome_content = ft.Column([
        ft.Container(height=60),
        ft.Icon(ft.Icons.AUTO_AWESOME, size=80, color="#6366f1"),
        ft.Container(height=20),
        ft.Text("AI Clipboard Pro", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("クリップボードをAIでスマートに", size=14, color=ft.Colors.WHITE70),
        ft.Container(height=40),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CONTENT_PASTE, color="#6366f1"),
                    ft.Text("テキストをコピー", size=14),
                ], spacing=12),
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_AWESOME, color="#6366f1"),
                    ft.Text("スタイルを選んでタップ", size=14),
                ], spacing=12),
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#22c55e"),
                    ft.Text("AIが自動で整形！", size=14),
                ], spacing=12),
            ], spacing=16),
            padding=20,
            bgcolor="#2d2d44",
            border_radius=12,
        ),
        ft.Container(height=40),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Onboarding Step 2: Setup
    url_input = ft.TextField(
        label="Backend URL",
        value=backend_url,
        on_change=update_url,
        border_radius=12,
        filled=True,
        bgcolor="#2d2d44",
        width=340,
    )
    
    setup_content = ft.Column([
        ft.Container(height=40),
        ft.Icon(ft.Icons.SETTINGS, size=60, color="#6366f1"),
        ft.Container(height=20),
        ft.Text("接続設定", size=24, weight=ft.FontWeight.BOLD),
        ft.Container(height=10),
        ft.Text("バックエンドサーバーのURLを入力してください", 
               size=13, color=ft.Colors.WHITE70, text_align=ft.TextAlign.CENTER),
        ft.Container(height=30),
        url_input,
        ft.Container(height=20),
        ft.Container(
            content=ft.Column([
                ft.Text("💡 ヒント", weight=ft.FontWeight.BOLD, size=13),
                ft.Text("• ローカル: http://localhost:8000", size=12, color=ft.Colors.WHITE70),
                ft.Text("• Cloudflare Tunnel: https://xxx.trycloudflare.com", size=12, color=ft.Colors.WHITE70),
            ], spacing=6),
            padding=16,
            bgcolor="#2d2d44",
            border_radius=12,
            width=340,
        ),
        ft.Container(height=30),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Text("始める", size=16, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.ARROW_FORWARD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            style=ft.ButtonStyle(
                bgcolor="#6366f1",
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=40, vertical=16),
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            on_click=complete_onboarding,
        ),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    onboarding_view = ft.Container(
        content=ft.Column([
            welcome_content,
            ft.Divider(height=40, color=ft.Colors.WHITE12),
            setup_content,
        ], scroll=ft.ScrollMode.AUTO),
        visible=not config["onboarding_complete"],
        expand=True,
    )
    
    # ========================================
    # MAIN APP (same as Alpha)
    # ========================================
    
    def create_style_button(style_info):
        async def on_click(e):
            nonlocal selected_style
            selected_style = style_info["key"]
            for btn in style_buttons:
                btn.bgcolor = "#3d3d5c" if btn.data != selected_style else "#6366f1"
            await page.update_async()
        
        btn = ft.Container(
            content=ft.Column([
                ft.Icon(style_info["icon"], size=28, color=ft.Colors.WHITE),
                ft.Text(style_info["label"], size=12, weight=ft.FontWeight.BOLD),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            width=75,
            height=70,
            bgcolor="#3d3d5c" if style_info["key"] != "business" else "#6366f1",
            border_radius=12,
            alignment=ft.alignment.center,
            on_click=on_click,
            data=style_info["key"],
        )
        return btn
    
    style_buttons = [create_style_button(s) for s in STYLES]
    
    style_grid = ft.Container(
        content=ft.Row(style_buttons, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=8),
        padding=ft.padding.symmetric(horizontal=10),
    )
    
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
                ft.IconButton(icon=ft.Icons.CONTENT_PASTE, icon_color=ft.Colors.WHITE70, 
                             tooltip="Paste", on_click=paste_clipboard),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            input_field,
        ]),
        padding=ft.padding.symmetric(horizontal=16),
    )
    
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
            page.snack_bar = ft.SnackBar(content=ft.Text("✅ Copied!"), bgcolor="#22c55e")
            page.snack_bar.open = True
            await page.update_async()
    
    copy_button = ft.IconButton(icon=ft.Icons.COPY, icon_color=ft.Colors.WHITE70, 
                                tooltip="Copy", on_click=copy_result, disabled=True)
    
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
    
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20, color=ft.Colors.WHITE)
    
    async def process_click(e):
        nonlocal is_processing
        
        if not input_field.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("⚠️ Enter text first"), bgcolor="#f59e0b")
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
            async for chunk in process_text_stream(original_text, style=selected_style, base_url=backend_url):
                output_field.value += chunk
                await page.update_async()
            
            copy_button.disabled = False
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
        content=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.WHITE),
            ft.Text("Process", size=16, weight=ft.FontWeight.BOLD),
            progress_ring,
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        style=ft.ButtonStyle(
            bgcolor="#6366f1", color=ft.Colors.WHITE,
            padding=ft.padding.symmetric(vertical=16),
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=process_click,
        width=380,
    )
    
    process_section = ft.Container(content=process_button, padding=ft.padding.symmetric(horizontal=16))
    
    # History view builder
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
        
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(item["timestamp"], color=ft.Colors.WHITE54, size=11),
                            ft.Container(
                                content=ft.Text(item["style"].upper(), size=10, color=ft.Colors.WHITE),
                                bgcolor="#6366f1", padding=ft.padding.symmetric(horizontal=8, vertical=2), border_radius=4,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(item["original"], color=ft.Colors.WHITE70, size=12),
                        ft.Text(item["result"][:100] + "..." if len(item["result"]) > 100 else item["result"],
                               color=ft.Colors.WHITE, size=13),
                    ], spacing=4),
                    bgcolor="#2d2d44", border_radius=8, padding=12, margin=ft.margin.only(bottom=8),
                ) for item in items
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    history_container = ft.Container(content=build_history_view(), padding=16, expand=True)
    
    # Navigation
    async def nav_change(e):
        index = e.control.selected_index
        main_view.visible = index == 0
        history_view.visible = index == 1
        settings_view.visible = index == 2
        if index == 1:
            history_container.content = build_history_view()
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
    
    # Settings view
    settings_url_field = ft.TextField(
        label="Backend URL", value=backend_url, border_radius=12, filled=True, bgcolor="#2d2d44",
        on_change=lambda e: setattr(config, 'backend_url', e.control.value) or save_config(config),
    )
    
    async def clear_history_click(e):
        history.clear()
        page.snack_bar = ft.SnackBar(content=ft.Text("History cleared"), bgcolor="#6366f1")
        page.snack_bar.open = True
        await page.update_async()
    
    async def reset_onboarding(e):
        config["onboarding_complete"] = False
        save_config(config)
        onboarding_view.visible = True
        main_app_view.visible = False
        await page.update_async()
    
    settings_view = ft.Container(
        content=ft.Column([
            ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=ft.Colors.WHITE12),
            settings_url_field,
            ft.Divider(height=20, color=ft.Colors.WHITE12),
            ft.ElevatedButton(text="Clear History", icon=ft.Icons.DELETE_OUTLINE,
                            on_click=clear_history_click, style=ft.ButtonStyle(bgcolor="#dc2626")),
            ft.ElevatedButton(text="Reset Onboarding", icon=ft.Icons.RESTART_ALT,
                            on_click=reset_onboarding),
            ft.Divider(height=20, color=ft.Colors.WHITE12),
            ft.Text("AI Clipboard Pro v4.0 Beta", color=ft.Colors.WHITE30, size=12),
        ], spacing=12),
        padding=20,
        visible=False,
        expand=True,
    )
    
    # Main view
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
    ], scroll=ft.ScrollMode.AUTO, expand=True, visible=True)
    
    history_view = ft.Container(content=history_container, visible=False, expand=True)
    
    main_app_view = ft.Container(
        content=ft.Column([
            ft.Stack([main_view, history_view, settings_view], expand=True),
            nav_bar,
        ]),
        visible=config["onboarding_complete"],
        expand=True,
    )
    
    # Page layout
    page.add(
        ft.Stack([onboarding_view, main_app_view], expand=True),
    )


if __name__ == "__main__":
    ft.run(target=main)
