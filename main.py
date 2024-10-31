import tkinter as tk
from tkinter import messagebox, ttk
from yt_dlp import YoutubeDL
from PIL import Image, ImageTk
import io
import requests
import os

# Funktion zur YouTube-Suche
def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch3',  # Sucht die Top-3-Ergebnisse auf YouTube
    }
    with YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(query, download=False)['entries']
    return results


# Funktion zum Herunterladen von Audio
def download_audio(url, output_path=os.path.expanduser("~/Downloads")):
    # Überprüfen, ob eine URL eingegeben wurde
    if not url.strip():
        messagebox.showwarning("Fehler", "Bitte gib eine YouTube-URL ein.")
        return  # Funktion verlassen, wenn keine URL eingegeben wurde

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        # Bestätigungsmeldung nach Abschluss des Downloads
        messagebox.showinfo("Download abgeschlossen", "Der Download wurde erfolgreich abgeschlossen!")




# Funktion zum Setzen der URL in die readonly-Textbox
def set_url(url):
    url_entry.config(state="normal")  # Schreibmodus aktivieren
    url_entry.delete(0, tk.END)       # Aktuellen Text löschen
    url_entry.insert(0, url)          # Neue URL einfügen
    url_entry.config(state="readonly")  # Wieder auf readonly setzen

# Funktion zur Anzeige der Suchergebnisse
def show_search_results():
    query = search_entry.get()
    if not query:
        messagebox.showwarning("Leeres Feld", "Bitte gib einen Songnamen ein.")
        return

    results = search_youtube(query)
    for widget in results_frame.winfo_children():  # Alte Ergebnisse löschen
        widget.destroy()

    for i, result in enumerate(results):
        title = result.get("title", "Kein Titel")
        url = result.get("webpage_url", "")
        thumbnail_url = result.get("thumbnail")

        # Thumbnail herunterladen und anzeigen
        response = requests.get(thumbnail_url)
        img_data = response.content
        img = Image.open(io.BytesIO(img_data)).resize((80, 60))  # Thumbnail-Größe anpassen
        img = ImageTk.PhotoImage(img)

        # Frame für jeden Eintrag erstellen
        entry_frame = tk.Frame(results_frame, pady=5)
        entry_frame.pack(fill='x', padx=5)

        # Thumbnail und Titel/URL in einer Linie anzeigen
        thumbnail_label = tk.Label(entry_frame, image=img)
        thumbnail_label.image = img  # Referenz speichern
        thumbnail_label.pack(side='left', padx=5)

        # Titel und URL-Text
        text_frame = tk.Frame(entry_frame)
        text_frame.pack(side='left', fill='both', expand=True)

        title_label = tk.Label(text_frame, text=title, font=('Arial', 14, 'bold'), wraplength=300, anchor='w')
        title_label.pack(anchor='w')

        url_label = tk.Label(text_frame, text=url, font=('Arial', 15), fg="blue", cursor="hand2", anchor='w')
        url_label.pack(anchor='w')
        # Verwende `set_url`, um die URL einzufügen
        url_label.bind("<Button-1>", lambda e, url=url: set_url(url))

# Scrollen mit dem Mausrad aktivieren
def on_mousewheel(event):
    if event.num == 4 or event.delta > 0:
        canvas.yview_scroll(-1, "units")
    elif event.num == 5 or event.delta < 0:
        canvas.yview_scroll(1, "units")


# GUI erstellen
root = tk.Tk()
root.title("YouTube Audio Downloader")
root.geometry("800x600")  # Festgelegte Breite und Höhe

tk.Label(root, text="Bitte gib den Namen des gewünschten Songs an:", font=('Arial', 14)).pack(pady=10)
search_entry = tk.Entry(root, width=40, font=('Arial', 14))
search_entry.pack(pady=5)

search_button = tk.Button(root, text="Suchen", command=show_search_results)
search_button.pack(pady=5)

# Canvas für Scroll-View mit fester Breite
canvas = tk.Canvas(root, bg="#333333", width=400)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Binden der Mausrad-Ereignisse für Scrollen
canvas.bind_all("<MouseWheel>", on_mousewheel)  # Für Windows und Linux
canvas.bind_all("<Button-4>", on_mousewheel)  # Für macOS nach oben
canvas.bind_all("<Button-5>", on_mousewheel)  # Für macOS nach unten

# Platzieren des Canvas und der Scrollbar
canvas.pack(side="left", fill="y", expand=False, padx=10, pady=10)
scrollbar.pack(side="left", fill="y")

results_frame = scrollable_frame

tk.Label(root, text="YouTube-URL, um den Download zu starten:", font=('Arial', 14)).pack(pady=10)
url_entry = tk.Entry(root, width=40, font=('Arial', 14), state="readonly")
url_entry.pack(pady=5)
download_button = tk.Button(root, text="Download starten", command=lambda: download_audio(url_entry.get()))
download_button.pack(ipady=5)

root.mainloop()