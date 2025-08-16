#!/usr/bin/env python3
# mini_not_defteri.py
# Küçük, güvenilir Tkinter not defteri ~200-300 satır

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import tkinter.font as tkfont
from pathlib import Path

APP_NAME = "d Not Defteri"

class MiniNotepad:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("900x600")
        self.filepath = None

        # Font
        self.font_size = 12
        self.font = tkfont.Font(family="Consolas" if root.tk.call("tk", "windowingsystem") == "win32" else "Courier", size=self.font_size)

        # Theme
        self.themes = {
            "Açık": {"bg":"#ffffff","fg":"#111111","gutter":"#f0f0f0"},
            "Koyu": {"bg":"#0f1722","fg":"#e6eef6","gutter":"#0b1220"}
        }
        self.current_theme = "Açık"

        # Menu
        self._build_menu()

        # Main layout: gutter + text
        self.main = ttk.Frame(root)
        self.main.pack(fill=tk.BOTH, expand=True)

        self.gutter = tk.Text(self.main, width=5, padx=4, takefocus=0, bd=0, state="disabled")
        self.gutter.pack(side=tk.LEFT, fill=tk.Y)

        self.text = tk.Text(self.main, undo=True, wrap=tk.WORD)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vsb = ttk.Scrollbar(self.main, orient=tk.VERTICAL, command=self._on_scroll)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=self._on_yscroll)

        # Status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(root, textvariable=self.status, anchor="w")
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bindings
        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", lambda e: self._update_gutter())
        self.text.bind("<ButtonRelease-1>", lambda e: self._update_status())
        self.text.bind("<Control-z>", lambda e: self._do("undo") or "break")
        self.text.bind("<Control-y>", lambda e: self._do("redo") or "break")
        self.text.bind("<Control-plus>", lambda e: self._zoom(1) or "break")
        self.text.bind("<Control-minus>", lambda e: self._zoom(-1) or "break")
        self.root.bind("<Control-n>", lambda e: self.new_file() or "break")
        self.root.bind("<Control-o>", lambda e: self.open_file() or "break")
        self.root.bind("<Control-s>", lambda e: self.save_file() or "break")
        self.root.bind("<Control-S>", lambda e: self.save_as() or "break")
        self.root.bind("<Control-f>", lambda e: self.find_dialog() or "break")

        # Apply initial styling
        self.text.configure(font=self.font)
        self.gutter.configure(font=self.font)
        self.apply_theme(self.current_theme)
        self._update_gutter()
        self._update_status()

    # Menu
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label="Yeni\tCtrl+N", command=self.new_file)
        filem.add_command(label="Aç... \tCtrl+O", command=self.open_file)
        filem.add_separator()
        filem.add_command(label="Kaydet\tCtrl+S", command=self.save_file)
        filem.add_command(label="Farklı Kaydet...\tCtrl+Shift+S", command=self.save_as)
        filem.add_separator()
        filem.add_command(label="Çıkış", command=self.on_exit)
        menubar.add_cascade(label="Dosya", menu=filem)

        editm = tk.Menu(menubar, tearoff=0)
        editm.add_command(label="Geri Al\tCtrl+Z", command=lambda: self._do("undo"))
        editm.add_command(label="İleri Al\tCtrl+Y", command=lambda: self._do("redo"))
        editm.add_separator()
        editm.add_command(label="Kes\tCtrl+X", command=lambda: self._do("cut"))
        editm.add_command(label="Kopyala\tCtrl+C", command=lambda: self._do("copy"))
        editm.add_command(label="Yapıştır\tCtrl+V", command=lambda: self._do("paste"))
        editm.add_separator()
        editm.add_command(label="Bul...\tCtrl+F", command=self.find_dialog)
        editm.add_command(label="Değiştir...", command=self.replace_dialog)
        menubar.add_cascade(label="Düzen", menu=editm)

        viewm = tk.Menu(menubar, tearoff=0)
        viewm.add_command(label="Kelime Kaydırma Aç/Kapa", command=self.toggle_wrap)
        viewm.add_command(label="Tema Değiştir", command=self.toggle_theme)
        viewm.add_separator()
        viewm.add_command(label="Yakınlaştır\tCtrl++", command=lambda: self._zoom(1))
        viewm.add_command(label="Uzaklaştır\tCtrl+-", command=lambda: self._zoom(-1))
        menubar.add_cascade(label="Görünüm", menu=viewm)

    # File ops
    def new_file(self):
        if self._maybe_save():
            self.text.delete("1.0", tk.END)
            self.filepath = None
            self.root.title(APP_NAME)
            self._update_gutter()
            self._update_status()

    def open_file(self):
        if not self._maybe_save():
            return
        fn = filedialog.askopenfilename(filetypes=[("Metin", "*.txt;*.md;*.py;*.json"), ("Tümü", "*.*")])
        if fn:
            try:
                s = Path(fn).read_text(encoding="utf-8")
            except Exception:
                s = Path(fn).read_text(errors="replace")
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", s)
            self.filepath = fn
            self.root.title(f"{Path(fn).name} - {APP_NAME}")
            self.text.edit_reset()
            self._update_gutter()
            self._update_status()

    def save_file(self):
        if not self.filepath:
            return self.save_as()
        try:
            Path(self.filepath).write_text(self.text.get("1.0", tk.END), encoding="utf-8")
            self.text.edit_modified(False)
            self._update_status()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def save_as(self):
        fn = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Metin", "*.txt"), ("Tümü", "*.*")])
        if fn:
            self.filepath = fn
            self.save_file()
            self.root.title(f"{Path(fn).name} - {APP_NAME}")

    def on_exit(self):
        if self._maybe_save():
            self.root.destroy()

    def _maybe_save(self):
        if self.text.edit_modified():
            ans = messagebox.askyesnocancel("Kaydet", "Değişiklikleri kaydetmek ister misin?")
            if ans is None:
                return False
            if ans:
                self.save_file()
        return True

    # Edit helpers
    def _do(self, cmd):
        try:
            if cmd == "undo":
                self.text.edit_undo()
            elif cmd == "redo":
                self.text.edit_redo()
            elif cmd == "cut":
                self.text.event_generate("<<Cut>>")
            elif cmd == "copy":
                self.text.event_generate("<<Copy>>")
            elif cmd == "paste":
                self.text.event_generate("<<Paste>>")
        except Exception:
            pass
        self._update_gutter()
        self._update_status()

    # Gutter and status
    def _update_gutter(self):
        lines = int(self.text.index("end-1c").split(".")[0])
        gutter_text = "\n".join(str(i) for i in range(1, lines+1))
        self.gutter.config(state="normal")
        self.gutter.delete("1.0", tk.END)
        self.gutter.insert("1.0", gutter_text)
        self.gutter.config(state="disabled")

    def _on_scroll(self, *args):
        self.text.yview(*args)
        self.gutter.yview_moveto(self.text.yview()[0])

    def _on_yscroll(self, first, last):
        self.vsb.set(first, last)
        self.gutter.yview_moveto(first)

    def _on_modified(self, event=None):
        self.text.edit_modified(False)
        self._update_status()

    def _update_status(self):
        idx = self.text.index("insert")
        line, col = idx.split(".")
        mod = "●" if self.text.edit_modified() else ""
        name = Path(self.filepath).name if self.filepath else "Adsız"
        wrap = "Wrap" if self.text.cget("wrap") != "none" else "NoWrap"
        self.status.set(f"{name}    Satır {line}, Sütun {int(col)+1}    {wrap}    {mod}")

    # Wrap & theme & zoom
    def toggle_wrap(self):
        current = self.text.cget("wrap")
        self.text.config(wrap=tk.NONE if current != tk.NONE else tk.WORD)
        self._update_status()

    def toggle_theme(self):
        self.current_theme = "Koyu" if self.current_theme == "Açık" else "Açık"
        self.apply_theme(self.current_theme)

    def apply_theme(self, name):
        t = self.themes[name]
        self.text.config(bg=t["bg"], fg=t["fg"], insertbackground=t["fg"])
        self.gutter.config(bg=t["gutter"], fg=t["fg"])
        self._update_gutter()

    def _zoom(self, delta):
        self.font_size = max(8, min(48, self.font_size + delta))
        self.font.configure(size=self.font_size)
        self._update_gutter()

    # Find / Replace
    def find_dialog(self):
        d = tk.Toplevel(self.root)
        d.title("Bul")
        d.transient(self.root)
        tk.Label(d, text="Ara:").grid(row=0, column=0, padx=6, pady=6)
        e = tk.Entry(d, width=30); e.grid(row=0, column=1, padx=6, pady=6); e.focus_set()
        var = tk.BooleanVar(value=False)
        tk.Checkbutton(d, text="Büyük/küçük duyarlı", variable=var).grid(row=1, column=1, sticky="w", padx=6)
        def do_find():
            needle = e.get()
            if not needle:
                return
            start = self.text.index("insert")
            idx = self.text.search(needle, start, nocase=not var.get(), stopindex=tk.END)
            if not idx:
                messagebox.showinfo("Bul", "Bulunamadı")
                return
            self.text.tag_remove("sel", "1.0", tk.END)
            end = f"{idx}+{len(needle)}c"
            self.text.tag_add("sel", idx, end)
            self.text.mark_set("insert", end)
            self.text.see(idx)
        tk.Button(d, text="Bul", command=do_find).grid(row=2, column=0, padx=6, pady=6)
        tk.Button(d, text="Kapat", command=d.destroy).grid(row=2, column=1, padx=6, pady=6)

    def replace_dialog(self):
        d = tk.Toplevel(self.root)
        d.title("Değiştir")
        d.transient(self.root)
        tk.Label(d, text="Ara:").grid(row=0,column=0,padx=6,pady=6)
        e1 = tk.Entry(d, width=30); e1.grid(row=0,column=1,padx=6,pady=6); e1.focus_set()
        tk.Label(d, text="Değiştir:").grid(row=1,column=0,padx=6,pady=6)
        e2 = tk.Entry(d, width=30); e2.grid(row=1,column=1,padx=6,pady=6)
        def replace_one():
            needle = e1.get(); repl = e2.get()
            if not needle:
                return
            idx = self.text.search(needle, "1.0", nocase=True, stopindex=tk.END)
            if idx:
                self.text.delete(idx, f"{idx}+{len(needle)}c")
                self.text.insert(idx, repl)
                self._update_gutter()
        def replace_all():
            needle = e1.get(); repl = e2.get()
            if not needle:
                return
            count = 0
            pos = "1.0"
            while True:
                idx = self.text.search(needle, pos, nocase=True, stopindex=tk.END)
                if not idx:
                    break
                self.text.delete(idx, f"{idx}+{len(needle)}c")
                self.text.insert(idx, repl)
                pos = f"{idx}+{len(repl)}c"
                count += 1
            messagebox.showinfo("Değiştir", f"{count} adet değiştirildi.")
            self._update_gutter()
        tk.Button(d, text="Değiştir", command=replace_one).grid(row=2,column=0,padx=6,pady=6)
        tk.Button(d, text="Tümünü Değiştir", command=replace_all).grid(row=2,column=1,padx=6,pady=6)

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniNotepad(root)
    root.mainloop()
