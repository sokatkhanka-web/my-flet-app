import flet as ft
import sqlite3

# --- Database Setup ---
DB_NAME = 'urdu_library_pro.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS MyBook 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       topic TEXT, content TEXT, vol TEXT DEFAULT '', page TEXT DEFAULT '')''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "Urdu Library Pro"
    page.rtl = True 
    page.theme_mode = ft.ThemeMode.LIGHT
    init_db()

    # --- UI Elements ---
    search_input = ft.TextField(label="آئی ڈی یا لفظ لکھیں", expand=True)
    content_viewer = ft.TextField(multiline=True, min_lines=15, expand=True, label="تحریر", text_size=20)
    list_view = ft.ListView(expand=True, spacing=10)

    # --- FUNCTIONS (Fixed Search & Click) ---
    
    def load_content(item_id):
        """فہرست سے کسی آئٹم پر کلک کرنے کا فنکشن"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM MyBook WHERE id=?", (item_id,))
        res = cursor.fetchone()
        conn.close()
        
        if res:
            content_viewer.value = res[0]
            # دوسرے پیج (تحریر) پر لے کر جانا
            nav_bar.selected_index = 1 
            change_page(1)
            page.update()

    def run_search(e=None):
        """سرچ کرنے کا فنکشن (ID اور حروف دونوں کے لیے)"""
        list_view.controls.clear()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        val = search_input.value.strip()
        
        if not val:
            # اگر سرچ خالی ہے تو سب دکھاؤ
            cursor.execute("SELECT id, topic FROM MyBook ORDER BY id DESC")
        elif val.isdigit():
            # اگر صرف نمبر ہے تو ID سرچ کرو
            cursor.execute("SELECT id, topic FROM MyBook WHERE id = ?", (val,))
        else:
            # اگر حروف ہیں تو ٹاپک اور مواد میں سرچ کرو
            cursor.execute("SELECT id, topic FROM MyBook WHERE topic LIKE ? OR content LIKE ?", (f'%{val}%', f'%{val}%'))
        
        rows = cursor.fetchall()
        for row in rows:
            # ہر رو کے لیے لسٹ آئٹم بنانا
            list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(row[1], weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"ID: {row[0]}"),
                    # یہاں فنکشن کو صحیح طریقے سے بائنڈ کیا گیا ہے
                    on_click=lambda _, idx=row[0]: load_content(idx)
                )
            )
        
        if not rows:
            list_view.controls.append(ft.Text("کچھ نہیں ملا", color=ft.Colors.RED))
            
        conn.close()
        page.update()

    def save_data(e):
        if not content_viewer.value.strip(): return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        parts = content_viewer.value.split('###')
        for part in parts:
            if part.strip():
                lines = part.strip().splitlines()
                topic = lines[0][:100] if lines else "بغیر عنوان"
                cursor.execute("INSERT INTO MyBook (topic, content) VALUES (?, ?)", (topic, part))
        conn.commit()
        conn.close()
        
        content_viewer.value = ""
        nav_bar.selected_index = 0
        change_page(0)
        run_search() # لسٹ اپڈیٹ کریں
        page.snack_bar = ft.SnackBar(ft.Text("محفوظ کر لیا گیا!"))
        page.snack_bar.open = True
        page.update()

    # --- Pages Layout ---
    list_page = ft.Column([
        ft.Row([
            search_input, 
            ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_search)
        ], alignment=ft.MainAxisAlignment.CENTER),
        list_view
    ], expand=True, visible=True)

    edit_page = ft.Column([
        content_viewer,
        ft.Row([
            ft.ElevatedButton("محفوظ کریں", icon=ft.Icons.SAVE, on_click=save_data, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
        ], alignment=ft.MainAxisAlignment.CENTER)
    ], expand=True, visible=False)

    def change_page(index):
        list_page.visible = (index == 0)
        edit_page.visible = (index == 1)
        page.update()

    # --- Navigation ---
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.LIST, label="فہرست"),
            ft.NavigationBarDestination(icon=ft.Icons.EDIT, label="تحریر"),
        ],
        on_change=lambda e: change_page(e.control.selected_index)
    )

    page.navigation_bar = nav_bar
    page.add(list_page, edit_page)
    
    # شروع میں ڈیٹا لوڈ کریں
    run_search()

if __name__ == "__main__":
    ft.app(target=main)
