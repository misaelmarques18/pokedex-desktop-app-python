import tkinter as tk
from tkinter import messagebox
import requests
import random
from PIL import Image, ImageTk
from io import BytesIO
import os
 
# ---------------- CONFIGURAÇÕES ----------------
MAX_POKEMON = 1010
pokedex = set()
pokedex_data = {}
 
# TOP 10 POKÉMON MAIS FORTES + RARIDADE
TOP_10 = {
    "Mewtwo": 0.5,
    "Rayquaza": 0.4,
    "Arceus": 0.2,
    "Giratina": 0.4,
    "Dialga": 0.6,
    "Palkia": 0.6,
    "Kyogre": 0.8,
    "Groudon": 0.8,
    "Lugia": 1,
    "Ho-oh": 1
}
 
# ---------------- FUNDO ANIMADO ----------------
def carregar_fundo():
    gif_nome = "nature.gif"
    if not os.path.exists(gif_nome):
        try:
            print("🌿 Baixando wallpaper animado de natureza...")
            url = "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif"
            resposta = requests.get(url)
            with open(gif_nome, "wb") as f:
                f.write(resposta.content)
            print("✅ nature.gif baixado com sucesso!")
        except:
            print("⚠️ Não foi possível baixar o GIF.")
            return []
 
    gif = Image.open(gif_nome)
    frames = []
    try:
        while True:
            frame = gif.copy().resize((520, 750))
            frames.append(ImageTk.PhotoImage(frame))
            gif.seek(len(frames))
    except EOFError:
        pass
 
    return frames
 
def animar_fundo():
    global frame_fundo
    fundo_label.config(image=fundo_frames[frame_fundo])
    frame_fundo = (frame_fundo + 1) % len(fundo_frames)
    janela.after(100, animar_fundo)
 
# ---------------- POKÉBOLA ANIMADA ----------------
POKEBOLA_FRAMES_URLS = [
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png",
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/great-ball.png",
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/ultra-ball.png",
]
 
frames_img = []
frame_atual = 0
animacao_ativa = False
 
def carregar_frames_pokebola():
    global frames_img
    for url in POKEBOLA_FRAMES_URLS:
        img = Image.open(BytesIO(requests.get(url).content))
        img = img.resize((80, 80))
        frames_img.append(ImageTk.PhotoImage(img))
 
def animar_pokebola():
    global frame_atual, animacao_ativa
    if animacao_ativa:
        pokebola_label.config(image=frames_img[frame_atual])
        frame_atual = (frame_atual + 1) % len(frames_img)
        janela.after(200, animar_pokebola)
 
# ---------------- RARIDADE ----------------
def definir_cor_raridade(percent):
    """Retorna o texto e a cor da raridade com base na %"""
    if percent >= 35:
        return f"Incomum ({percent}%)", "yellow"
    elif percent >= 25:
        return f"Comum ({percent}%)", "green"
    elif percent >= 20:
        return f"Mediano ({percent}%)", "pink"
    elif percent >= 10:
        return f"Raro ({percent}%)", "orange"
    elif percent >= 5:
        return f"Épico ({percent}%)", "purple"
    elif percent >= 3:
        return f"Lendário ({percent}%)", "brown"
    else:
        return f"GOD ({percent}%)", "white"
 
# ---------------- CAPTURA ----------------
def girar_pokebola():
    global animacao_ativa
    animacao_ativa = True
    status_label.config(text="⚪ Jogando a Pokébola...", fg="white")
    animar_pokebola()
    janela.after(2000, capturar_pokemon)
 
def capturar_pokemon():
    global animacao_ativa
    animacao_ativa = False
    pokebola_label.config(image="")
 
    pokemon_id = random.randint(1, MAX_POKEMON)
    try:
        data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}").json()
        mostrar_pokemon(data)
        nome = data["name"].capitalize()
 
        # Raridade
        if nome in TOP_10:
            percent = TOP_10[nome]
        else:
            percent = round(random.uniform(1, 50), 1)
 
        raridade_text, cor = definir_cor_raridade(percent)
        raridade_label.config(text=raridade_text, fg=cor)
 
        # Se for TOP 10
        if nome in TOP_10:
            messagebox.showinfo(
                "🎉 PARABÉNS!",
                f"Você capturou um Pokémon LENDÁRIO!\n\n{nome}\nRaridade: {raridade_text}"
            )
 
        # Adiciona na Pokédex e na coleção
        if nome not in pokedex:
            pokedex.add(nome)
        pokedex_data[nome] = {"data": data, "raridade": percent}
 
        # Atualiza lista principal
        if nome not in lista_pokedex.get(0, tk.END):
            lista_pokedex.insert(tk.END, nome)
       
        atualizar_colecao()
 
    except:
        messagebox.showerror("Erro", "Erro ao acessar a PokéAPI")
 
# ---------------- VISUALIZAÇÃO ----------------
def mostrar_pokemon(data):
    nome = data["name"].capitalize()
    tipos = ", ".join(t["type"]["name"] for t in data["types"])
    altura = data["height"]
    peso = data["weight"]
    sprite_url = data["sprites"]["front_default"]
 
    nome_label.config(text=f"🧬 {nome}", fg="white")
    tipo_label.config(text=f"🔥 Tipo: {tipos}", fg="white")
    info_label.config(text=f"📏 Altura: {altura} | ⚖️ Peso: {peso}", fg="white")
 
    if nome in pokedex_data:
        percent = pokedex_data[nome]["raridade"]
    else:
        percent = round(random.uniform(1, 50), 1)
 
    raridade_text, cor = definir_cor_raridade(percent)
    raridade_label.config(text=raridade_text, fg=cor)
 
    if sprite_url:
        img = Image.open(BytesIO(requests.get(sprite_url).content))
        img = img.resize((140, 140))
        photo = ImageTk.PhotoImage(img)
        pokemon_img.config(image=photo)
        pokemon_img.image = photo
 
def selecionar_pokemon(event):
    if not lista_pokedex.curselection():
        return
    index = lista_pokedex.curselection()[0]
    nome = lista_pokedex.get(index).lower()
    try:
        data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nome}").json()
        mostrar_pokemon(data)
        status_label.config(text="📖 Visualizando Pokémon", fg="purple")
        btn_voltar.pack(pady=10)
    except:
        messagebox.showerror("Erro", "Erro ao carregar Pokémon")
 
def voltar():
    nome_label.config(text="🧬 ???")
    tipo_label.config(text="🔥 Tipo: ???")
    info_label.config(text="")
    raridade_label.config(text="")
    pokemon_img.config(image="")
    status_label.config(text="")
    btn_voltar.pack_forget()
 
# ---------------- COLEÇÃO ----------------
def abrir_colecao():
    frame_ui.pack_forget()
    frame_colecao.pack(fill="both", expand=True)
    atualizar_colecao()
 
def atualizar_colecao():
    pesquisa = entrada_pesquisa.get().lower()
    lista_colecao.delete(0, tk.END)
    for nome in sorted(pokedex):
        if pesquisa in nome.lower():
            raridade = pokedex_data[nome]["raridade"]
            texto, cor = definir_cor_raridade(raridade)
            lista_colecao.insert(tk.END, f"{nome} — {texto}")
            lista_colecao.itemconfig(tk.END, fg=cor)
 
def voltar_colecao():
    frame_colecao.pack_forget()
    frame_ui.pack(fill="both", expand=True)
 
# ---------------- INTERFACE ----------------
janela = tk.Tk()
janela.title("Pokédex Nature Edition")
janela.geometry("520x750")
janela.configure(bg="black")
 
# Fundo animado
fundo_frames = carregar_fundo()
frame_fundo = 0
fundo_label = tk.Label(janela)
fundo_label.place(x=0, y=0, relwidth=1, relheight=1)
if fundo_frames:
    animar_fundo()
 
# Frame principal
frame_ui = tk.Frame(janela, bg="#000000")
frame_ui.pack(fill="both", expand=True)
 
titulo = tk.Label(frame_ui, text="🌿 POKÉDEX NATURE", font=("Arial", 24, "bold"), bg="#000000", fg="white")
titulo.pack(pady=10)
 
pokebola_label = tk.Label(frame_ui, bg="#000000")
pokebola_label.pack(pady=5)
 
pokemon_img = tk.Label(frame_ui, bg="#000000")
pokemon_img.pack(pady=10)
 
nome_label = tk.Label(frame_ui, text="🧬 ???", font=("Arial", 18), bg="#000000", fg="white")
nome_label.pack()
 
tipo_label = tk.Label(frame_ui, text="🔥 Tipo: ???", font=("Arial", 14), bg="#000000", fg="white")
tipo_label.pack()
 
info_label = tk.Label(frame_ui, text="", font=("Arial", 12), bg="#000000", fg="white")
info_label.pack(pady=5)
 
raridade_label = tk.Label(frame_ui, text="", font=("Arial", 12, "bold"), bg="#000000")
raridade_label.pack(pady=2)
 
btn_girar = tk.Button(frame_ui, text="⚪ Jogar Pokébola", font=("Arial", 14, "bold"), bg="#ff4d4d", fg="white", command=girar_pokebola)
btn_girar.pack(pady=10)
 
btn_colecao = tk.Button(frame_ui, text="📁 Coleção", font=("Arial", 14, "bold"), bg="#3399ff", fg="white", command=abrir_colecao)
btn_colecao.pack(pady=5)
 
status_label = tk.Label(frame_ui, text="", bg="#000000", fg="white")
status_label.pack()
 
lista_pokedex = tk.Listbox(frame_ui, width=28, height=8, font=("Arial", 11))
lista_pokedex.pack(pady=5)
lista_pokedex.bind("<<ListboxSelect>>", selecionar_pokemon)
 
btn_voltar = tk.Button(frame_ui, text="⬅️ Voltar", font=("Arial", 12), command=voltar)
 
# Frame coleção
frame_colecao = tk.Frame(janela, bg="black")
 
entrada_pesquisa = tk.Entry(frame_colecao, font=("Arial", 14))
entrada_pesquisa.pack(pady=10, padx=10, fill="x")
entrada_pesquisa.bind("<KeyRelease>", lambda e: atualizar_colecao())
 
lista_colecao = tk.Listbox(frame_colecao, width=40, height=20, font=("Arial", 11))
lista_colecao.pack(padx=10, pady=10)
 
btn_voltar_colecao = tk.Button(frame_colecao, text="⬅️ Voltar", font=("Arial", 12), command=voltar_colecao)
btn_voltar_colecao.pack(pady=10)
 
# Carrega frames da Pokébola
carregar_frames_pokebola()
 
janela.mainloop()
