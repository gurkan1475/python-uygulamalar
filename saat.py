# saat_uygulamasi.py
# Python 3.x ile çalışır. (Windows / macOS / Linux)
# Çalıştırmadan önce: pip install pillow  (sadece istersen ikon/resim kullanırsın, ama zorunlu değil)

import tkinter as tk
from tkinter import ttk, messagebox
import time

class SaatUygulamasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Saat | Kronometre | Geri Sayım")
        self.resizable(False, False)
        self.configure(padx=12, pady=12)

        # --- Canlı Saat ---
        self.saat_label = ttk.Label(self, text="", font=("Consolas", 24))
        self.saat_label.grid(row=0, column=0, columnspan=3, pady=(0,10))

        # --- Kronometre (Stopwatch) ---
        self.stopwatch_frame = ttk.LabelFrame(self, text="Kronometre")
        self.stopwatch_frame.grid(row=1, column=0, padx=6, pady=6, sticky="nsew")

        self.sw_time_var = tk.StringVar(value="00:00:00.0")
        self.sw_label = ttk.Label(self.stopwatch_frame, textvariable=self.sw_time_var, font=("Consolas", 18))
        self.sw_label.grid(row=0, column=0, columnspan=3, pady=(6,8), padx=6)

        self.sw_start_btn = ttk.Button(self.stopwatch_frame, text="Başlat", command=self.sw_start)
        self.sw_stop_btn = ttk.Button(self.stopwatch_frame, text="Durdur", command=self.sw_stop)
        self.sw_reset_btn = ttk.Button(self.stopwatch_frame, text="Sıfırla", command=self.sw_reset)

        self.sw_start_btn.grid(row=1, column=0, padx=4, pady=6, sticky="ew")
        self.sw_stop_btn.grid(row=1, column=1, padx=4, pady=6, sticky="ew")
        self.sw_reset_btn.grid(row=1, column=2, padx=4, pady=6, sticky="ew")

        # kronometre state
        self.sw_running = False
        self.sw_start_time = None
        self.sw_elapsed = 0.0  # saniye cinsinden

        # --- Geri Sayım (Countdown) ---
        self.count_frame = ttk.LabelFrame(self, text="Geri Sayım")
        self.count_frame.grid(row=1, column=1, padx=6, pady=6, sticky="nsew")

        ttk.Label(self.count_frame, text="Dakika:").grid(row=0, column=0, sticky="e")
        ttk.Label(self.count_frame, text="Saniye:").grid(row=0, column=2, sticky="e")

        self.count_min_var = tk.StringVar(value="0")
        self.count_sec_var = tk.StringVar(value="30")

        self.count_min_entry = ttk.Entry(self.count_frame, width=5, textvariable=self.count_min_var, justify="center")
        self.count_sec_entry = ttk.Entry(self.count_frame, width=5, textvariable=self.count_sec_var, justify="center")

        self.count_min_entry.grid(row=0, column=1, padx=4, pady=6)
        self.count_sec_entry.grid(row=0, column=3, padx=4, pady=6)

        self.count_time_var = tk.StringVar(value="00:30")
        self.count_label = ttk.Label(self.count_frame, textvariable=self.count_time_var, font=("Consolas", 18))
        self.count_label.grid(row=1, column=0, columnspan=4, pady=(4,8))

        self.count_start_btn = ttk.Button(self.count_frame, text="Başlat", command=self.count_start)
        self.count_pause_btn = ttk.Button(self.count_frame, text="Duraklat", command=self.count_pause)
        self.count_reset_btn = ttk.Button(self.count_frame, text="Sıfırla", command=self.count_reset)

        self.count_start_btn.grid(row=2, column=0, columnspan=1, padx=4, pady=6, sticky="ew")
        self.count_pause_btn.grid(row=2, column=1, columnspan=1, padx=4, pady=6, sticky="ew")
        self.count_reset_btn.grid(row=2, column=2, columnspan=2, padx=4, pady=6, sticky="ew")

        # geri sayım state
        self.count_total_seconds = 30
        self.count_remaining = 30
        self.count_running = False

        # --- Küçük yardım / durum çubuğu ---
        self.status_var = tk.StringVar(value="Hazır")
        self.status_label = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_label.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(8,0))

        # Başlat updater
        self.update_clock()

    # --- Canlı Saat Güncelle ---
    def update_clock(self):
        now = time.localtime()
        saat_str = time.strftime("%Y-%m-%d %H:%M:%S", now)
        self.saat_label.config(text=saat_str)
        # kronometreyi de periyodik güncelle
        self.update_stopwatch_display()
        # geri sayımı da periyodik güncelle (bir saniyelik hassasiyet)
        # (geri sayım tick'i ayrı yönetiliyor)
        self.after(200, self.update_clock)  # 200 ms aralıkla güncelle (saniyede 5 kez)

    # --- Kronometre Fonksiyonları ---
    def sw_start(self):
        if not self.sw_running:
            self.sw_running = True
            self.status_var.set("Kronometre çalışıyor...")
            # başlangıç zamanı / eğer daha önce bir süre geçtiyse onu koru
            self.sw_start_time = time.time() - self.sw_elapsed
            self._sw_tick()

    def _sw_tick(self):
        if not self.sw_running:
            return
        self.sw_elapsed = time.time() - self.sw_start_time
        self.update_stopwatch_display()
        # 100 ms aralık
        self.after(100, self._sw_tick)

    def sw_stop(self):
        if self.sw_running:
            self.sw_running = False
            self.update_stopwatch_display()
            self.status_var.set("Kronometre durdu.")

    def sw_reset(self):
        self.sw_running = False
        self.sw_start_time = None
        self.sw_elapsed = 0.0
        self.update_stopwatch_display()
        self.status_var.set("Kronometre sıfırlandı.")

    def update_stopwatch_display(self):
        # sw_elapsed -> format HH:MM:SS.d
        elapsed = self.sw_elapsed
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        deci = int((elapsed - int(elapsed)) * 10)
        self.sw_time_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}.{deci}")

    # --- Geri Sayım Fonksiyonları ---
    def count_start(self):
        # inputlardan saniyeyi oku, geçersiz girdi kontrolü
        try:
            dakika = int(self.count_min_var.get())
            saniye = int(self.count_sec_var.get())
            if dakika < 0 or saniye < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Hata", "Lütfen geçerli bir sayı girin (0 veya pozitif).")
            return

        toplam = dakika * 60 + saniye
        if toplam <= 0:
            messagebox.showwarning("Hata", "Süre 0'dan büyük olmalı.")
            return

        self.count_total_seconds = toplam
        # eğer daha önce başlamış ve duraklatılmışsa, kalan süreye devam eder
        if not self.count_running:
            # yeni başlatmaysa remaining'i toplamla ayarla
            if self.count_remaining <= 0 or self.count_remaining > self.count_total_seconds:
                self.count_remaining = self.count_total_seconds
        self.count_running = True
        self.status_var.set("Geri sayım çalışıyor...")
        self._count_tick()

    def _count_tick(self):
        if not self.count_running:
            return
        # 1 saniyede bir azalır
        if self.count_remaining > 0:
            self.count_remaining -= 1
            self._update_count_display()
            self.after(1000, self._count_tick)
        else:
            self.count_running = False
            self._update_count_display()
            self.status_var.set("Geri sayım bitti!")
            # uyarı ver
            try:
                # beep (Windows)
                self.bell()
            except:
                pass
            messagebox.showinfo("Süre doldu", "Geri sayım tamamlandı!")

    def count_pause(self):
        if self.count_running:
            self.count_running = False
            self.status_var.set("Geri sayım duraklatıldı.")
        else:
            self.status_var.set("Geri sayım çalışmıyor.")

    def count_reset(self):
        self.count_running = False
        # varsayılan total'i giriş alanlarından alıp remaining'i ona eşitle
        try:
            dakika = int(self.count_min_var.get())
            saniye = int(self.count_sec_var.get())
            if dakika < 0 or saniye < 0:
                raise ValueError
            toplam = dakika * 60 + saniye
            if toplam <= 0:
                toplam = 0
        except Exception:
            toplam = 0
        self.count_total_seconds = toplam
        self.count_remaining = toplam
        self._update_count_display()
        self.status_var.set("Geri sayım sıfırlandı.")

    def _update_count_display(self):
        secs = max(0, int(self.count_remaining))
        m = secs // 60
        s = secs % 60
        self.count_time_var.set(f"{m:02d}:{s:02d}")

if __name__ == "__main__":
    app = SaatUygulamasi()
    app.mainloop()
