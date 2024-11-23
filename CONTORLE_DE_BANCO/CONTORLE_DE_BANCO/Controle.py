import sqlite3
import tkinter as tk
from tkinter import messagebox

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
            root.deiconify()
            janela_criar.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário já existe. Escolha outro nome.")

    def voltar_login():
        janela_criar.destroy()
        root.deiconify()

    root.withdraw()

    janela_criar = tk.Toplevel()
    janela_criar.title("Criar Usuário")
    janela_criar.state('zoomed')

    frame = tk.Frame(janela_criar)
    frame.pack(expand=True)

    tk.Label(frame, text="Nome de Usuário:", font=("Arial", 14)).pack(pady=10)
    entry_username = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_username.pack(pady=10)
    
    tk.Label(frame, text="Senha:", font=("Arial", 14)).pack(pady=10)
    entry_password = tk.Entry(frame, font=("Arial", 14), show="*", width=40)
    entry_password.pack(pady=10)

    tipo_conta_var = tk.StringVar(value="corrente")
    tk.Radiobutton(frame, text="Corrente", variable=tipo_conta_var, value="corrente", font=("Arial", 14)).pack(pady=10)
    tk.Radiobutton(frame, text="Poupança", variable=tipo_conta_var, value="poupanca", font=("Arial", 14)).pack(pady=10)

    tk.Button(frame, text="Salvar", command=salvar_usuario, font=("Arial", 14), width=20).pack(pady=20)
    tk.Button(frame, text="Voltar", command=voltar_login, font=("Arial", 14), width=20).pack(pady=10)

def login_usuario():
    username = entry_username.get()
    password = entry_password.get()

    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
    usuario = cursor.fetchone()

    if usuario:
        messagebox.showinfo("Bem-vindo", f"Bem-vindo(a), {username}!")
        root.destroy()
        abrir_menu_principal(usuario)
    else:
        messagebox.showerror("Erro", "Nome de usuário ou senha inválidos.")

def abrir_menu_principal(usuario):
    janela_menu = tk.Tk()
    janela_menu.title("Menu Principal")
    janela_menu.state('zoomed')

    frame = tk.Frame(janela_menu)
    frame.pack(expand=True)

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

    def sair():
        janela_menu.destroy()
        root.deiconify()

    tk.Label(frame, text=f"Bem-vindo(a), {usuario[1]}!", font=("Arial", 16)).pack(pady=20)
    lbl_saldo = tk.Label(frame, text=f"Saldo Atual: R${saldo:.2f}", font=("Arial", 16))
    lbl_saldo.pack(pady=10)

    tk.Label(frame, text="Valor:", font=("Arial", 14)).pack(pady=10)
    entry_valor = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_valor.pack(pady=10)

    largura_botao = 20
    
    tk.Button(frame, text="Depositar", command=realizar_deposito, font=("Arial", 14), width=largura_botao).pack(pady=10)
    tk.Button(frame, text="Sacar", command=realizar_saque, font=("Arial", 14), width=largura_botao).pack(pady=10)
    tk.Button(frame, text="Ver Extrato", command=mostrar_extrato, font=("Arial", 14), width=largura_botao).pack(pady=10)
    tk.Button(frame, text="Sair", command=sair, font=("Arial", 14), width=largura_botao).pack(pady=20)

root = tk.Tk()
root.title("Sistema Bancário")

root.geometry("1920x1080")
root.state('zoomed')

frame = tk.Frame(root)
frame.pack(expand=True)

tk.Label(frame, text="Nome de Usuário:", font=("Arial", 14)).pack(pady=10)
entry_username = tk.Entry(frame, font=("Arial", 14), width=40)
entry_username.pack(pady=10)

tk.Label(frame, text="Senha:", font=("Arial", 14)).pack(pady=10)
entry_password = tk.Entry(frame, font=("Arial", 14), show="*", width=40)
entry_password.pack(pady=10)

tk.Button(frame, text="Login", command=login_usuario, font=("Arial", 14), width=20).pack(pady=20)
tk.Button(frame, text="Criar Usuário", command=criar_usuario, font=("Arial", 14), width=20).pack(pady=20)

root.mainloop()
