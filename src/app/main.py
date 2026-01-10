import flet as ft
import sys
import os
import asyncio
import threading
import keyboard
import pyperclip
import time
from datetime import datetime

# Path setup to import from root
# Assumes running from project root via `python -m src.app.main`
import sys
# sys.path hack removed as we use package imports

from .ui import (
    TitaniumTheme, 
    SyncJobItem, 
    MagicButton, 
    SeasoningBadge, 
    SeasoningSlider, 
    COLOR_BG, 
    COLOR_SURFACE, 
    COLOR_TEXT_DIM, 
    COLOR_PRIMARY
)
from src.core.processor import CoreProcessor
from src.core.models import TextRequest, SyncJob
from src.infra.database import SessionLocal


# Initialize Core
core_processor = CoreProcessor()
HOTKEY = "ctrl+alt+x"

async def main(page: ft.Page):
    page.title = "Flow AI v1.0"
    page.theme = TitaniumTheme.theme
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    page.bgcolor = COLOR_BG
    page.padding = 0
    # Enable window visibility toggling
    page.window_visible = True
    page.window_prevent_close = True # Minimize instead of close

    def on_window_event(e):
        if e.data == "close":
            page.window_visible = False
            page.update()
    
    page.on_window_event = on_window_event

    # --- Global Hotkey Handler ---
    def on_hotkey_triggered():
        print("🚀 Hotkey Triggered!")
        
        # 1. Simulate Copy (Ctrl+C)
        keyboard.send("ctrl+c")
        time.sleep(0.1) # Wait for OS clipboard update

        # 2. Get Clipboard
        try:
            text = pyperclip.paste()
        except:
            text = ""
        
        if text:
            txt_input.value = text
            txt_input.update()
            
            # Show Window
            page.window_visible = True
            page.window_to_front()
            page.window_focused = True
            page.update()
        else:
            print("Clipboard empty or access failed")

    # Run keyboard listener in separate thread
    threading.Thread(target=lambda: keyboard.add_hotkey(HOTKEY, on_hotkey_triggered), daemon=True).start()

    # --- State ---
    state = {
        "seasoning": 30, # Default: Salt
        "jobs": [] 
    }
    
    # --- UI Components ---

    def on_text_change(e):
        # Auto-growing text field logic handled by Flet usually
        pass

    txt_input = ft.TextField(
        multiline=True,
        min_lines=6,
        max_lines=12,
        hint_text="ここにテキストを流し込むだけで、Flowが始まります...",
        border_radius=12,
        bgcolor=COLOR_SURFACE,
        border_color="transparent",
        filled=True,
        on_change=on_text_change
    )

    # Seasoning Controls
    slider = SeasoningSlider(on_change=lambda val: update_seasoning(val))
    slider.visible = False # Hidden by default (Advanced Mode)

    def update_seasoning(val: int):
        state["seasoning"] = val
        # Update preset buttons visual state? (Optional)
        pass

    def on_preset_click(val: int):
        state["seasoning"] = val
        slider.set_value(val) # Cleaner update
        # Compatible fix for Flet < 0.21.0
        page.snack_bar = ft.SnackBar(ft.Text(f"Seasoning set to {val}%"), duration=1000)
        page.snack_bar.open = True
        page.update()

    btn_salt = ft.ElevatedButton("Salt (10)", on_click=lambda e: on_preset_click(10), bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE)
    btn_sauce = ft.ElevatedButton("Sauce (50)", on_click=lambda e: on_preset_click(50), bgcolor=ft.Colors.ORANGE_900, color=ft.Colors.WHITE)
    btn_spice = ft.ElevatedButton("Spice (90)", on_click=lambda e: on_preset_click(90), bgcolor=ft.Colors.RED_900, color=ft.Colors.WHITE)

    presets_row = ft.Row(
        [btn_salt, btn_sauce, btn_spice],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    def on_advanced_toggle(e):
        slider.visible = e.control.value
        page.update()

    switch_advanced = ft.Switch(
        label="Advanced Mode (Fine Tuning)", 
        value=False, 
        on_change=on_advanced_toggle,
        active_color=COLOR_PRIMARY
    )

    async def btn_process_click(e):
        if not txt_input.value:
            # Compatible fix
            page.snack_bar = ft.SnackBar(ft.Text("テキストを入力してください"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        # Visual Feedback
        btn_magic.error = False # Reset
        
        # 1. Create SyncJob (Immediate)
        db = SessionLocal()
        try:
            req = TextRequest(text=txt_input.value, seasoning=state["seasoning"])
            job_id = await asyncio.to_thread(core_processor.create_sync_job, req, db)
        except Exception as ex:
            # Compatible fix
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()
            db.close()
            return
        finally:
            db.close()

        # 2. Add to Local State & Switch Tab
        new_job = {
            "id": job_id, 
            "text": txt_input.value, 
            "seasoning": state["seasoning"], 
            "status": "pending",
            "created_at_fmt": datetime.now().strftime("%H:%M"),
            "result": ""
        }
        state["jobs"].insert(0, new_job)
        update_history_list()
        
        txt_input.value = "" # Clear input
        
        # Switch to History View
        switch_view(1)
        
        page.update()

        # 3. Trigger Background Processing
        asyncio.create_task(run_worker_task(job_id))

    btn_magic = MagicButton(on_click=btn_process_click)

    input_view = ft.Container(
        content=ft.Column([
            ft.Container(height=10),
            ft.Text("Flow Input (Seasoning Mode)", weight=ft.FontWeight.BOLD, size=20),
            ft.Container(height=10),
            txt_input,
            ft.Container(height=20),
            ft.Text("Seasoning Presets", size=12, color=COLOR_TEXT_DIM),
            presets_row,
            ft.Container(height=10),
            switch_advanced,
            slider, # Hidden by default
            ft.Container(height=20),
            btn_magic
        ]),
        padding=20
    )

    # --- History View Components ---
    history_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def update_history_list():
        history_list.controls = [
            SyncJobItem(job, on_click=lambda e: print(f"Clicked {job['id']}")) for job in state["jobs"]
        ]

    async def run_worker_task(job_id):
        """Simulate Background Worker picking up the job"""
        db = SessionLocal()
        try:
            # Polling wait for visual effect? No, just run it.
            await core_processor.process_sync_job(job_id, db)
            
            # Fetch updated job
            job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
            if job:
                # Update local state
                for j in state["jobs"]:
                    if j["id"] == job_id:
                        j["status"] = job.status
                        j["result"] = job.result
                        break
                update_history_list()
                page.update()
        except Exception as e:
            print(f"Worker Error: {e}")
        finally:
            db.close()

    history_view = ft.Container(
        content=history_list,
        padding=16,
        expand=True
    )

    # --- Main Layout (View Switcher) ---
    content_area = ft.Container(content=input_view, expand=True)

    def switch_view(index):
        if index == 0:
            content_area.content = input_view
            btn_view_input.style.bgcolor = COLOR_PRIMARY
            btn_view_history.style.bgcolor = ft.Colors.TRANSPARENT
        else:
            content_area.content = history_view
            btn_view_input.style.bgcolor = ft.Colors.TRANSPARENT
            btn_view_history.style.bgcolor = COLOR_PRIMARY
        page.update()

    btn_view_input = ft.ElevatedButton(
        "Input", 
        icon=ft.Icons.EDIT, 
        on_click=lambda e: switch_view(0),
        style=ft.ButtonStyle(
            bgcolor=COLOR_PRIMARY, 
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation=0
        )
    )

    btn_view_history = ft.ElevatedButton(
        "History", 
        icon=ft.Icons.HISTORY, 
        on_click=lambda e: switch_view(1),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.TRANSPARENT,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation=0
        )
    )

    nav_bar = ft.Container(
        content=ft.Row(
            [btn_view_input, btn_view_history],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        padding=10,
        bgcolor=COLOR_SURFACE,
        border_radius=ft.border_radius.only(top_left=16, top_right=16)
    )

    page.add(
        ft.Column(
            [
                content_area,
                nav_bar
            ],
            expand=True,
            spacing=0
        )
    )

if __name__ == "__main__":
    ft.run(target=main)
