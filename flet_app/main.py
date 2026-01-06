"""
AI Clipboard Pro - Flet GUI Application

A unified GUI for AI-powered clipboard text processing.
Phase 4.1 Prototype.
"""
import flet as ft
import asyncio
from api_client import process_text, process_text_stream

# Available styles
STYLES = [
    ("📝 Business", "business"),
    ("💬 Casual", "casual"),
    ("📄 Summary", "summary"),
    ("🌐 English", "english"),
    ("✏️ Proofread", "proofread"),
]

# Default backend URL
DEFAULT_BACKEND_URL = "http://localhost:8000"


async def main(page: ft.Page):
    """Main Flet application entry point."""
    
    # Page setup
    page.title = "AI Clipboard Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.width = 500
    page.window.height = 700
    
    # State
    backend_url = DEFAULT_BACKEND_URL
    selected_style = "business"
    is_processing = False
    
    # --- UI Components ---
    
    # Header
    header = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CONTENT_PASTE, size=32, color=ft.Colors.BLUE_400),
                ft.Text("AI Clipboard Pro", size=24, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        margin=ft.margin.only(bottom=20),
    )
    
    # Input area
    input_field = ft.TextField(
        label="📋 Input Text",
        multiline=True,
        min_lines=5,
        max_lines=8,
        expand=True,
        hint_text="Paste or type text here...",
    )
    
    # Paste from clipboard button
    async def paste_clipboard(e):
        clipboard_text = await page.get_clipboard_async()
        if clipboard_text:
            input_field.value = clipboard_text
            await page.update_async()
    
    paste_button = ft.IconButton(
        icon=ft.Icons.CONTENT_PASTE,
        tooltip="Paste from clipboard",
        on_click=paste_clipboard,
    )
    
    input_container = ft.Column([
        ft.Row([
            ft.Text("Input", weight=ft.FontWeight.BOLD),
            paste_button,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        input_field,
    ])
    
    # Style selector
    style_dropdown = ft.Dropdown(
        label="Style",
        width=200,
        value="business",
        options=[ft.dropdown.Option(key=key, text=label) for label, key in STYLES],
    )
    
    def on_style_change(e):
        nonlocal selected_style
        selected_style = e.control.value
    
    style_dropdown.on_change = on_style_change
    
    # Output area
    output_field = ft.TextField(
        label="✨ Result",
        multiline=True,
        min_lines=5,
        max_lines=10,
        expand=True,
        read_only=True,
        value="",
    )
    
    # Copy result button
    async def copy_result(e):
        if output_field.value:
            await page.set_clipboard_async(output_field.value)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Copied to clipboard!"),
                bgcolor=ft.Colors.GREEN_700,
            )
            page.snack_bar.open = True
            await page.update_async()
    
    copy_button = ft.ElevatedButton(
        text="Copy Result",
        icon=ft.Icons.COPY,
        on_click=copy_result,
        disabled=True,
    )
    
    output_container = ft.Column([
        ft.Row([
            ft.Text("Result", weight=ft.FontWeight.BOLD),
            copy_button,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        output_field,
    ])
    
    # Progress indicator
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20)
    
    # Process button
    async def process_click(e):
        nonlocal is_processing
        
        if not input_field.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please enter some text first."),
                bgcolor=ft.Colors.ORANGE_700,
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
        
        try:
            # Use streaming for real-time display
            async for chunk in process_text_stream(
                input_field.value,
                style=selected_style,
                base_url=backend_url
            ):
                output_field.value += chunk
                await page.update_async()
            
            copy_button.disabled = False
            
        except Exception as ex:
            output_field.value = f"Error: {str(ex)}"
        
        finally:
            is_processing = False
            process_button.disabled = False
            progress_ring.visible = False
            await page.update_async()
    
    process_button = ft.ElevatedButton(
        text="Process",
        icon=ft.Icons.AUTO_AWESOME,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
        ),
        on_click=process_click,
        expand=True,
    )
    
    # Action row
    action_row = ft.Row([
        style_dropdown,
        progress_ring,
        process_button,
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Settings (collapsible)
    url_field = ft.TextField(
        label="Backend URL",
        value=DEFAULT_BACKEND_URL,
        width=300,
    )
    
    def on_url_change(e):
        nonlocal backend_url
        backend_url = e.control.value
    
    url_field.on_change = on_url_change
    
    settings_panel = ft.ExpansionTile(
        title=ft.Text("⚙️ Settings"),
        controls=[
            ft.Container(
                content=url_field,
                padding=10,
            ),
        ],
    )
    
    # --- Layout ---
    page.add(
        header,
        input_container,
        ft.Divider(height=20),
        action_row,
        ft.Divider(height=20),
        output_container,
        ft.Divider(height=20),
        settings_panel,
    )


# Entry point
if __name__ == "__main__":
    ft.run(target=main)
