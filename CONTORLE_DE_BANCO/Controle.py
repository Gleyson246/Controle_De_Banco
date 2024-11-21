import sqlite3
import tkinter as tk
from tkinter import messagebox

# Configuração inicial do banco de dados
conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    saldo REAL NOT NULL DEFAULT 0,
    extrato TEXT DEFAULT '',
    tipo_conta TEXT NOT NULL
)
''')
conn.commit()

# Função para criar um novo usuário
def criar_usuario():
    def salvar_usuario():
        username = entry_username.get()
        password = entry_password.get()
        tipo_conta = tipo_conta_var.get()

        if not username or not password:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        try:
            cursor.execute("INSERT INTO usuarios (username, password, tipo_conta) VALUES (?, ?, ?)",
                           (username, password, tipo_conta))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
            janela_criar.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário já existe. Escolha outro nome.")

    janela_criar = tk.Toplevel()
    janela_criar.title("Criar Usuário")

    tk.Label(janela_criar, text="Nome de Usuário:").pack()
    entry_username = tk.Entry(janela_criar)
    entry_username.pack()

    tk.Label(janela_criar, text="Senha:").pack()
    entry_password = tk.Entry(janela_criar, show="*")
    entry_password.pack()

    tk.Label(janela_criar, text="Tipo de Conta:").pack()
    tipo_conta_var = tk.StringVar(value="corrente")
    tk.Radiobutton(janela_criar, text="Corrente", variable=tipo_conta_var, value="corrente").pack()
    tk.Radiobutton(janela_criar, text="Poupança", variable=tipo_conta_var, value="poupanca").pack()

    tk.Button(janela_criar, text="Salvar", command=salvar_usuario).pack()

# Função para fazer login do usuário
def login_usuario():
    username = entry_username.get()
    password = entry_password.get()

    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
    usuario = cursor.fetchone()

    if usuario:
        messagebox.showinfo("Bem-vindo", f"Bem-vindo(a), {username}!")
        abrir_menu_principal(usuario)
    else:
        messagebox.showerror("Erro", "Nome de usuário ou senha inválidos.")

# Menu principal do usuário
def abrir_menu_principal(usuario):
    janela_login.destroy()

    janela_menu = tk.Tk()
    janela_menu.title("Menu Principal")

    saldo = usuario[3]
    extrato = usuario[4]

    def atualizar_saldo():
        lbl_saldo.config(text=f"Saldo Atual: R${saldo:.2f}")

    def realizar_deposito():
        nonlocal saldo, extrato
        try:
            valor = float(entry_valor.get())
            if valor > 0:
                saldo += valor
                extrato += f"Depósito: R${valor:.2f}\n"
                cursor.execute("UPDATE usuarios SET saldo = ?, extrato = ? WHERE id = ?", 
                               (saldo, extrato, usuario[0]))
                conn.commit()
                messagebox.showinfo("Sucesso", f"Depósito de R${valor:.2f} realizado!")
                atualizar_saldo()
                entry_valor.delete(0, tk.END)
            else:
                messagebox.showerror("Erro", "O valor deve ser maior que zero!")
        except ValueError:
            messagebox.showerror("Erro", "Insira um valor válido!")

    def realizar_saque():
        nonlocal saldo, extrato
        try:
            valor = float(entry_valor.get())
            if valor > 0:
                if saldo >= valor:
                    saldo -= valor
                    extrato += f"Saque: R${valor:.2f}\n"
                    cursor.execute("UPDATE usuarios SET saldo = ?, extrato = ? WHERE id = ?", 
                                   (saldo, extrato, usuario[0]))
                    conn.commit()
                    messagebox.showinfo("Sucesso", f"Saque de R${valor:.2f} realizado!")
                    atualizar_saldo()
                    entry_valor.delete(0, tk.END)
                else:
                    messagebox.showerror("Erro", "Saldo insuficiente!")
            else:
                messagebox.showerror("Erro", "O valor deve ser maior que zero!")
        except ValueError:
            messagebox.showerror("Erro", "Insira um valor válido!")

    def mostrar_extrato():
        messagebox.showinfo("Extrato", f"Extrato da conta:\n\n{extrato}")

    tk.Label(janela_menu, text=f"Bem-vindo(a), {usuario[1]}!").pack()
    lbl_saldo = tk.Label(janela_menu, text=f"Saldo Atual: R${saldo:.2f}")
    lbl_saldo.pack()

    tk.Label(janela_menu, text="Valor:").pack()
    entry_valor = tk.Entry(janela_menu)
    entry_valor.pack()

    tk.Button(janela_menu, text="Depositar", command=realizar_deposito).pack()
    tk.Button(janela_menu, text="Sacar", command=realizar_saque).pack()
    tk.Button(janela_menu, text="Ver Extrato", command=mostrar_extrato).pack()

# Janela principal de login
janela_login = tk.Tk()
janela_login.title("Sistema Bancário")

tk.Label(janela_login, text="Nome de Usuário:").pack()
entry_username = tk.Entry(janela_login)
entry_username.pack()

tk.Label(janela_login, text="Senha:").pack()
entry_password = tk.Entry(janela_login, show="*")
entry_password.pack()

tk.Button(janela_login, text="Login", command=login_usuario).pack()
tk.Button(janela_login, text="Criar Usuário", command=criar_usuario).pack()

janela_login.mainloop()
