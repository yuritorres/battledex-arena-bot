import tkinter as tk
from tkinter import ttk, messagebox
from db_utils import get_connection, read_participation_bonus

class AdminGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Painel de Administração - Bot Telegram')
        self.geometry('800x500')
        self.resizable(False, False)
        self.create_tabs()
        self.refresh_all()

    def create_tabs(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        # Aba Ranking
        self.tab_ranking = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_ranking, text='Ranking')
        self.tree_ranking = ttk.Treeview(self.tab_ranking, columns=("Nome", "ELO", "Vitórias", "Derrotas"), show="headings")
        for col in ("Nome", "ELO", "Vitórias", "Derrotas"):
            self.tree_ranking.heading(col, text=col)
        self.tree_ranking.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba Moedas
        self.tab_coins = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_coins, text='Moedas')
        self.tree_coins = ttk.Treeview(self.tab_coins, columns=("Nome", "Moedas"), show="headings")
        for col in ("Nome", "Moedas"):
            self.tree_coins.heading(col, text=col)
        self.tree_coins.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba Inventário
        self.tab_inventario = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_inventario, text='Inventário')
        self.tree_inventario = ttk.Treeview(self.tab_inventario, columns=("Usuário", "ID Item", "Quantidade"), show="headings")
        for col in ("Usuário", "ID Item", "Quantidade"):
            self.tree_inventario.heading(col, text=col)
        self.tree_inventario.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba Loja
        self.tab_loja = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_loja, text='Loja')
        self.tree_loja = ttk.Treeview(self.tab_loja, columns=("ID", "ID Item", "Nome", "Preço", "Imagem"), show="headings")
        for col in ("ID", "ID Item", "Nome", "Preço", "Imagem"):
            self.tree_loja.heading(col, text=col)
        self.tree_loja.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba Participação
        self.tab_bonus = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_bonus, text='Participação')
        self.tree_bonus = ttk.Treeview(self.tab_bonus, columns=("User ID", "Última Participação"), show="headings")
        for col in ("User ID", "Última Participação"):
            self.tree_bonus.heading(col, text=col)
        self.tree_bonus.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh_all(self):
        self.refresh_ranking()
        self.refresh_coins()
        self.refresh_inventario()
        self.refresh_loja()
        self.refresh_bonus()

    def refresh_coins(self):
        for row in self.tree_coins.get_children():
            self.tree_coins.delete(row)
        try:
            conn = get_connection('coins')
            cursor = conn.cursor()
            cursor.execute("SELECT nome, moedas FROM coins")
            for nome, moedas in cursor.fetchall():
                self.tree_coins.insert('', tk.END, values=(nome, moedas))
            conn.close()
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao carregar moedas: {e}')

    def refresh_inventario(self):
        for row in self.tree_inventario.get_children():
            self.tree_inventario.delete(row)
        try:
            conn = get_connection('inventario')
            cursor = conn.cursor()
            cursor.execute("SELECT usuario, id_item, quantidade FROM inventario")
            for usuario, id_item, quantidade in cursor.fetchall():
                self.tree_inventario.insert('', tk.END, values=(usuario, id_item, quantidade))
            conn.close()
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao carregar inventário: {e}')

    def refresh_loja(self):
        for row in self.tree_loja.get_children():
            self.tree_loja.delete(row)
        try:
            conn = get_connection('shop')
            cursor = conn.cursor()
            cursor.execute("SELECT id, id_item, nome, preco, imagem FROM itens")
            for id_, id_item, nome, preco, imagem in cursor.fetchall():
                self.tree_loja.insert('', tk.END, values=(id_, id_item, nome, preco, imagem))
            conn.close()
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao carregar loja: {e}')

    def refresh_bonus(self):
        for row in self.tree_bonus.get_children():
            self.tree_bonus.delete(row)
        try:
            bonus = read_participation_bonus()
            for user_id, last in bonus.items():
                self.tree_bonus.insert('', tk.END, values=(user_id, last))
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao carregar participação: {e}')

    def refresh_ranking(self):
        for row in self.tree_ranking.get_children():
            self.tree_ranking.delete(row)
        try:
            conn = get_connection('ranking')
            cursor = conn.cursor()
            cursor.execute("SELECT nome, elo, vitorias, derrotas FROM ranking")
            for nome, elo, vitorias, derrotas in cursor.fetchall():
                self.tree_ranking.insert('', tk.END, values=(nome, elo, vitorias, derrotas))
            conn.close()
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao carregar ranking: {e}')

    def add_coins_dialog(self):
        self.coin_action_dialog('Adicionar Moedas', True)

    def remove_coins_dialog(self):
        self.coin_action_dialog('Remover Moedas', False)

    def coin_action_dialog(self, title, add):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry('300x150')
        tk.Label(dialog, text='Nome do usuário:').pack(pady=5)
        user_entry = tk.Entry(dialog)
        user_entry.pack(pady=5)
        tk.Label(dialog, text='Quantidade:').pack(pady=5)
        amount_entry = tk.Entry(dialog)
        amount_entry.pack(pady=5)
        def submit():
            nome = user_entry.get().strip()
            try:
                quant = int(amount_entry.get())
                if quant <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror('Erro', 'Quantidade inválida.')
                return
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT saldo FROM coins WHERE nome=?", (nome,))
                row = cursor.fetchone()
                saldo_atual = row[0] if row else 0
                novo_saldo = saldo_atual + quant if add else saldo_atual - quant
                if novo_saldo < 0:
                    messagebox.showerror('Erro', 'Saldo insuficiente.')
                    return
                cursor.execute("INSERT OR REPLACE INTO coins (nome, saldo) VALUES (?, ?)", (nome, novo_saldo))
                conn.commit()
                conn.close()
                messagebox.showinfo('Sucesso', f'Saldo atualizado: {novo_saldo} moedas.')
                dialog.destroy()
                self.refresh_ranking()
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao atualizar moedas: {e}')
        tk.Button(dialog, text='Confirmar', command=submit).pack(pady=10)

if __name__ == '__main__':
    app = AdminGUI()
    app.mainloop()