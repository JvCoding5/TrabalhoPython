import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from datetime import datetime

class SistemaNotas:
    def __init__(self):
        self.conn = sqlite3.connect('sistema_notas.db')
        self.cursor = self.conn.cursor()
        self.criar_tabelas()
        self.criar_usuarios_padrao()
        self.usuario_logado = None
        self.tipo_usuario = None
        
    def criar_tabelas(self):
        # Tabela de usuários
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL,
                nome TEXT NOT NULL
            )
        ''')
        
        # Tabela de alunos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                turma TEXT NOT NULL,
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Tabela de professores
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS professores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                disciplina TEXT NOT NULL,
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Tabela de notas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                disciplina TEXT NOT NULL,
                nota REAL NOT NULL,
                professor_id INTEGER NOT NULL,
                FOREIGN KEY (aluno_id) REFERENCES alunos(id),
                FOREIGN KEY (professor_id) REFERENCES professores(id)
            )
        ''')
        
        self.conn.commit()
    
    def gerar_matricula(self):
        """Gera matrícula automática no formato: ANO + SEQUENCIAL (ex: 2025001)"""
        ano = datetime.now().year
        
        # Buscar última matrícula do ano
        self.cursor.execute('''
            SELECT matricula FROM alunos 
            WHERE matricula LIKE ? 
            ORDER BY matricula DESC LIMIT 1
        ''', (f'{ano}%',))
        
        resultado = self.cursor.fetchone()
        
        if resultado:
            ultima_matricula = resultado[0]
            sequencial = int(ultima_matricula[4:]) + 1
        else:
            sequencial = 1
        
        return f"{ano}{sequencial:03d}"
    
    def gerar_codigo_professor(self):
        """Gera código de professor no formato: PROF + SEQUENCIAL (ex: PROF001)"""
        self.cursor.execute('''
            SELECT codigo FROM professores 
            ORDER BY codigo DESC LIMIT 1
        ''')
        
        resultado = self.cursor.fetchone()
        
        if resultado:
            ultimo_codigo = resultado[0]
            sequencial = int(ultimo_codigo[4:]) + 1
        else:
            sequencial = 1
        
        return f"PROF{sequencial:03d}"
    
    def criar_usuarios_padrao(self):
        # Criar usuário secretaria padrão
        try:
            senha_hash = hashlib.md5('secretaria123'.encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO usuarios (usuario, senha, tipo, nome)
                VALUES (?, ?, ?, ?)
            ''', ('secretaria', senha_hash, 'secretaria', 'Secretaria'))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
    
    def autenticar(self, usuario, senha):
        senha_hash = hashlib.md5(senha.encode()).hexdigest()
        self.cursor.execute('''
            SELECT id, tipo, nome FROM usuarios
            WHERE usuario = ? AND senha = ?
        ''', (usuario, senha_hash))
        resultado = self.cursor.fetchone()
        
        if resultado:
            self.usuario_logado = resultado[0]
            self.tipo_usuario = resultado[1]
            return True
        return False

class InterfaceLogin:
    def __init__(self, sistema):
        self.sistema = sistema
        self.janela = tk.Tk()
        self.janela.title("Login - Sistema de Gerenciamento de Notas")
        self.janela.geometry("400x300")
        self.janela.configure(bg='#2c3e50')
        
        # Frame central
        frame = tk.Frame(self.janela, bg='#2c3e50')
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Título
        tk.Label(frame, text="Sistema de Notas", font=('Arial', 20, 'bold'),
                bg='#2c3e50', fg='white').pack(pady=20)
        
        # Usuário
        tk.Label(frame, text="Usuário:", font=('Arial', 12),
                bg='#2c3e50', fg='white').pack(pady=5)
        self.entry_usuario = tk.Entry(frame, font=('Arial', 12), width=25)
        self.entry_usuario.pack(pady=5)
        
        # Senha
        tk.Label(frame, text="Senha:", font=('Arial', 12),
                bg='#2c3e50', fg='white').pack(pady=5)
        self.entry_senha = tk.Entry(frame, font=('Arial', 12), width=25, show='*')
        self.entry_senha.pack(pady=5)
        
        # Botão login
        tk.Button(frame, text="Entrar", font=('Arial', 12, 'bold'),
                 bg='#27ae60', fg='white', width=20,
                 command=self.fazer_login).pack(pady=20)
        
        # Info
        tk.Label(frame, text="Usuário padrão: secretaria / secretaria123",
                font=('Arial', 9), bg='#2c3e50', fg='#bdc3c7').pack()
        
        self.janela.mainloop()
    
    def fazer_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()
        
        if self.sistema.autenticar(usuario, senha):
            self.janela.destroy()
            InterfacePrincipal(self.sistema)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")

class InterfacePrincipal:
    def __init__(self, sistema):
        self.sistema = sistema
        self.janela = tk.Tk()
        self.janela.title("Sistema de Gerenciamento de Notas")
        self.janela.geometry("900x600")
        self.janela.configure(bg='#ecf0f1')
        
        # Menu superior
        frame_menu = tk.Frame(self.janela, bg='#34495e', height=60)
        frame_menu.pack(fill='x')
        
        tipo_texto = self.sistema.tipo_usuario.upper()
        tk.Label(frame_menu, text=f"Bem-vindo - {tipo_texto}",
                font=('Arial', 16, 'bold'), bg='#34495e', fg='white').pack(side='left', padx=20, pady=15)
        
        tk.Button(frame_menu, text="Sair", font=('Arial', 10),
                 bg='#e74c3c', fg='white', command=self.sair).pack(side='right', padx=20, pady=15)
        
        # Área de conteúdo
        self.frame_conteudo = tk.Frame(self.janela, bg='#ecf0f1')
        self.frame_conteudo.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.carregar_interface()
        
        self.janela.mainloop()
    
    def limpar_conteudo(self):
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()
    
    def carregar_interface(self):
        if self.sistema.tipo_usuario == 'secretaria':
            self.interface_secretaria()
        elif self.sistema.tipo_usuario == 'professor':
            self.interface_professor()
        elif self.sistema.tipo_usuario == 'aluno':
            self.interface_aluno()
    
    def interface_secretaria(self):
        self.limpar_conteudo()
        
        # Notebook para abas
        notebook = ttk.Notebook(self.frame_conteudo)
        notebook.pack(fill='both', expand=True)
        
        # Aba Alunos
        frame_alunos = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(frame_alunos, text='Gerenciar Alunos')
        
        # Formulário de cadastro
        frame_form = tk.LabelFrame(frame_alunos, text="Cadastrar Aluno",
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1')
        frame_form.pack(fill='x', padx=10, pady=10)
        
        # MATRÍCULA AUTOMÁTICA - apenas exibição
        tk.Label(frame_form, text="Matrícula:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        label_matricula = tk.Label(frame_form, text="(Gerada automaticamente)", 
                                    bg='#ecf0f1', fg='#7f8c8d', font=('Arial', 10, 'italic'))
        label_matricula.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        tk.Label(frame_form, text="Nome:", bg='#ecf0f1').grid(row=0, column=2, padx=5, pady=5)
        entry_nome = tk.Entry(frame_form, width=30)
        entry_nome.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_form, text="Turma:", bg='#ecf0f1').grid(row=1, column=0, padx=5, pady=5)
        entry_turma = tk.Entry(frame_form, width=20)
        entry_turma.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_form, text="Usuário:", bg='#ecf0f1').grid(row=1, column=2, padx=5, pady=5)
        entry_user = tk.Entry(frame_form, width=20)
        entry_user.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(frame_form, text="Senha:", bg='#ecf0f1').grid(row=2, column=0, padx=5, pady=5)
        entry_pass = tk.Entry(frame_form, width=20, show='*')
        entry_pass.grid(row=2, column=1, padx=5, pady=5)
        
        def cadastrar_aluno():
            try:
                # Gerar matrícula automaticamente
                matricula = self.sistema.gerar_matricula()
                
                # Criar usuário
                senha_hash = hashlib.md5(entry_pass.get().encode()).hexdigest()
                self.sistema.cursor.execute('''
                    INSERT INTO usuarios (usuario, senha, tipo, nome)
                    VALUES (?, ?, ?, ?)
                ''', (entry_user.get(), senha_hash, 'aluno', entry_nome.get()))
                usuario_id = self.sistema.cursor.lastrowid
                
                # Criar aluno com matrícula automática
                self.sistema.cursor.execute('''
                    INSERT INTO alunos (matricula, nome, turma, usuario_id)
                    VALUES (?, ?, ?, ?)
                ''', (matricula, entry_nome.get(), entry_turma.get(), usuario_id))
                
                self.sistema.conn.commit()
                messagebox.showinfo("Sucesso", f"Aluno cadastrado!\nMatrícula: {matricula}")
                atualizar_lista()
                entry_nome.delete(0, tk.END)
                entry_turma.delete(0, tk.END)
                entry_user.delete(0, tk.END)
                entry_pass.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")
        
        tk.Button(frame_form, text="Cadastrar", bg='#27ae60', fg='white',
                 command=cadastrar_aluno).grid(row=2, column=2, columnspan=2, pady=10)
        
        # Lista de alunos
        frame_lista = tk.Frame(frame_alunos, bg='#ecf0f1')
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        
        tree_alunos = ttk.Treeview(frame_lista, columns=('ID', 'Matrícula', 'Nome', 'Turma'),
                                   show='headings', height=15)
        tree_alunos.heading('ID', text='ID')
        tree_alunos.heading('Matrícula', text='Matrícula')
        tree_alunos.heading('Nome', text='Nome')
        tree_alunos.heading('Turma', text='Turma')
        
        tree_alunos.column('ID', width=50)
        tree_alunos.column('Matrícula', width=100)
        tree_alunos.column('Nome', width=250)
        tree_alunos.column('Turma', width=100)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=tree_alunos.yview)
        tree_alunos.configure(yscrollcommand=scrollbar.set)
        
        tree_alunos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        def atualizar_lista():
            tree_alunos.delete(*tree_alunos.get_children())
            self.sistema.cursor.execute('SELECT id, matricula, nome, turma FROM alunos ORDER BY id DESC')
            for row in self.sistema.cursor.fetchall():
                tree_alunos.insert('', 'end', values=row)
        
        def excluir_aluno():
            selected = tree_alunos.selection()
            if not selected:
                messagebox.showwarning("Aviso", "Selecione um aluno!")
                return
            
            item = tree_alunos.item(selected[0])
            aluno_id = item['values'][0]
            
            if messagebox.askyesno("Confirmar", "Deseja realmente excluir este aluno?"):
                self.sistema.cursor.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
                self.sistema.conn.commit()
                messagebox.showinfo("Sucesso", "Aluno excluído!")
                atualizar_lista()
        
        tk.Button(frame_alunos, text="Excluir Selecionado", bg='#e74c3c', fg='white',
                 command=excluir_aluno).pack(pady=5)
        
        atualizar_lista()
        
        # Aba Professores
        frame_profs = tk.Frame(notebook, bg='#ecf0f1')
        notebook.add(frame_profs, text='Gerenciar Professores')
        
        frame_form_prof = tk.LabelFrame(frame_profs, text="Cadastrar Professor",
                                        font=('Arial', 12, 'bold'), bg='#ecf0f1')
        frame_form_prof.pack(fill='x', padx=10, pady=10)
        
        # CÓDIGO AUTOMÁTICO - apenas exibição
        tk.Label(frame_form_prof, text="Código:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        label_codigo = tk.Label(frame_form_prof, text="(Gerado automaticamente)", 
                               bg='#ecf0f1', fg='#7f8c8d', font=('Arial', 10, 'italic'))
        label_codigo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        tk.Label(frame_form_prof, text="Nome:", bg='#ecf0f1').grid(row=0, column=2, padx=5, pady=5)
        entry_nome_prof = tk.Entry(frame_form_prof, width=30)
        entry_nome_prof.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_form_prof, text="Disciplina:", bg='#ecf0f1').grid(row=1, column=0, padx=5, pady=5)
        entry_disc = tk.Entry(frame_form_prof, width=20)
        entry_disc.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_form_prof, text="Usuário:", bg='#ecf0f1').grid(row=1, column=2, padx=5, pady=5)
        entry_user_prof = tk.Entry(frame_form_prof, width=20)
        entry_user_prof.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(frame_form_prof, text="Senha:", bg='#ecf0f1').grid(row=2, column=0, padx=5, pady=5)
        entry_pass_prof = tk.Entry(frame_form_prof, width=20, show='*')
        entry_pass_prof.grid(row=2, column=1, padx=5, pady=5)
        
        def cadastrar_professor():
            try:
                # Gerar código automaticamente
                codigo = self.sistema.gerar_codigo_professor()
                
                senha_hash = hashlib.md5(entry_pass_prof.get().encode()).hexdigest()
                self.sistema.cursor.execute('''
                    INSERT INTO usuarios (usuario, senha, tipo, nome)
                    VALUES (?, ?, ?, ?)
                ''', (entry_user_prof.get(), senha_hash, 'professor', entry_nome_prof.get()))
                usuario_id = self.sistema.cursor.lastrowid
                
                self.sistema.cursor.execute('''
                    INSERT INTO professores (codigo, nome, disciplina, usuario_id)
                    VALUES (?, ?, ?, ?)
                ''', (codigo, entry_nome_prof.get(), entry_disc.get(), usuario_id))
                
                self.sistema.conn.commit()
                messagebox.showinfo("Sucesso", f"Professor cadastrado!\nCódigo: {codigo}")
                atualizar_lista_prof()
                entry_nome_prof.delete(0, tk.END)
                entry_disc.delete(0, tk.END)
                entry_user_prof.delete(0, tk.END)
                entry_pass_prof.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")
        
        tk.Button(frame_form_prof, text="Cadastrar", bg='#27ae60', fg='white',
                 command=cadastrar_professor).grid(row=2, column=2, columnspan=2, pady=10)
        
        frame_lista_prof = tk.Frame(frame_profs, bg='#ecf0f1')
        frame_lista_prof.pack(fill='both', expand=True, padx=10, pady=10)
        
        tree_profs = ttk.Treeview(frame_lista_prof, columns=('ID', 'Código', 'Nome', 'Disciplina'),
                                  show='headings', height=15)
        tree_profs.heading('ID', text='ID')
        tree_profs.heading('Código', text='Código')
        tree_profs.heading('Nome', text='Nome')
        tree_profs.heading('Disciplina', text='Disciplina')
        
        tree_profs.column('ID', width=50)
        tree_profs.column('Código', width=100)
        tree_profs.column('Nome', width=250)
        tree_profs.column('Disciplina', width=150)
        
        scrollbar_prof = ttk.Scrollbar(frame_lista_prof, orient='vertical', command=tree_profs.yview)
        tree_profs.configure(yscrollcommand=scrollbar_prof.set)
        
        tree_profs.pack(side='left', fill='both', expand=True)
        scrollbar_prof.pack(side='right', fill='y')
        
        def atualizar_lista_prof():
            tree_profs.delete(*tree_profs.get_children())
            self.sistema.cursor.execute('SELECT id, codigo, nome, disciplina FROM professores ORDER BY id DESC')
            for row in self.sistema.cursor.fetchall():
                tree_profs.insert('', 'end', values=row)
        
        def excluir_professor():
            selected = tree_profs.selection()
            if not selected:
                messagebox.showwarning("Aviso", "Selecione um professor!")
                return
            
            item = tree_profs.item(selected[0])
            prof_id = item['values'][0]
            
            if messagebox.askyesno("Confirmar", "Deseja realmente excluir este professor?"):
                self.sistema.cursor.execute('DELETE FROM professores WHERE id = ?', (prof_id,))
                self.sistema.conn.commit()
                messagebox.showinfo("Sucesso", "Professor excluído!")
                atualizar_lista_prof()
        
        tk.Button(frame_profs, text="Excluir Selecionado", bg='#e74c3c', fg='white',
                 command=excluir_professor).pack(pady=5)
        
        atualizar_lista_prof()
    
    def interface_professor(self):
        self.limpar_conteudo()
        
        # Buscar dados do professor
        self.sistema.cursor.execute('''
            SELECT id, nome, disciplina FROM professores
            WHERE usuario_id = ?
        ''', (self.sistema.usuario_logado,))
        prof_data = self.sistema.cursor.fetchone()
        
        if not prof_data:
            messagebox.showerror("Erro", "Dados do professor não encontrados!")
            return
        
        prof_id, prof_nome, disciplina = prof_data
        
        tk.Label(self.frame_conteudo, text=f"Professor: {prof_nome} - Disciplina: {disciplina}",
                font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(pady=10)
        
        # Frame para lançamento de notas
        frame_notas = tk.LabelFrame(self.frame_conteudo, text="Lançar/Alterar Nota",
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1')
        frame_notas.pack(fill='x', padx=20, pady=10)
        
        tk.Label(frame_notas, text="Aluno:", bg='#ecf0f1').grid(row=0, column=0, padx=5, pady=5)
        
        # Combo com alunos
        self.sistema.cursor.execute('SELECT id, nome, matricula FROM alunos')
        alunos = self.sistema.cursor.fetchall()
        alunos_dict = {f"{a[2]} - {a[1]}": a[0] for a in alunos}
        
        combo_alunos = ttk.Combobox(frame_notas, values=list(alunos_dict.keys()), width=40)
        combo_alunos.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_notas, text="Nota:", bg='#ecf0f1').grid(row=0, column=2, padx=5, pady=5)
        entry_nota = tk.Entry(frame_notas, width=10)
        entry_nota.grid(row=0, column=3, padx=5, pady=5)
        
        def lancar_nota():
            try:
                aluno_selecionado = combo_alunos.get()
                if not aluno_selecionado:
                    messagebox.showwarning("Aviso", "Selecione um aluno!")
                    return
                
                aluno_id = alunos_dict[aluno_selecionado]
                nota = float(entry_nota.get())
                
                if nota < 0 or nota > 10:
                    messagebox.showwarning("Aviso", "Nota deve estar entre 0 e 10!")
                    return
                
                # Verificar se já existe nota
                self.sistema.cursor.execute('''
                    SELECT id FROM notas
                    WHERE aluno_id = ? AND disciplina = ? AND professor_id = ?
                ''', (aluno_id, disciplina, prof_id))
                
                existe = self.sistema.cursor.fetchone()
                
                if existe:
                    self.sistema.cursor.execute('''
                        UPDATE notas SET nota = ?
                        WHERE aluno_id = ? AND disciplina = ? AND professor_id = ?
                    ''', (nota, aluno_id, disciplina, prof_id))
                    messagebox.showinfo("Sucesso", "Nota atualizada com sucesso!")
                else:
                    self.sistema.cursor.execute('''
                        INSERT INTO notas (aluno_id, disciplina, nota, professor_id)
                        VALUES (?, ?, ?, ?)
                    ''', (aluno_id, disciplina, nota, prof_id))
                    messagebox.showinfo("Sucesso", "Nota lançada com sucesso!")
                
                self.sistema.conn.commit()
                atualizar_lista_notas()
                entry_nota.delete(0, tk.END)
                
            except ValueError:
                messagebox.showerror("Erro", "Nota inválida!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao lançar nota: {str(e)}")
        
        tk.Button(frame_notas, text="Lançar/Alterar Nota", bg='#3498db', fg='white',
                 command=lancar_nota).grid(row=0, column=4, padx=10, pady=5)
        
        # Lista de notas
        frame_lista = tk.Frame(self.frame_conteudo, bg='#ecf0f1')
        frame_lista.pack(fill='both', expand=True, padx=20, pady=10)
        
        tree_notas = ttk.Treeview(frame_lista, columns=('Matrícula', 'Aluno', 'Turma', 'Nota'),
                                  show='headings', height=20)
        tree_notas.heading('Matrícula', text='Matrícula')
        tree_notas.heading('Aluno', text='Aluno')
        tree_notas.heading('Turma', text='Turma')
        tree_notas.heading('Nota', text='Nota')
        
        tree_notas.column('Matrícula', width=100)
        tree_notas.column('Aluno', width=300)
        tree_notas.column('Turma', width=100)
        tree_notas.column('Nota', width=80)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=tree_notas.yview)
        tree_notas.configure(yscrollcommand=scrollbar.set)
        
        tree_notas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        def atualizar_lista_notas():
            tree_notas.delete(*tree_notas.get_children())
            self.sistema.cursor.execute('''
                SELECT a.matricula, a.nome, a.turma, COALESCE(n.nota, '-') as nota
                FROM alunos a
                LEFT JOIN notas n ON a.id = n.aluno_id 
                    AND n.disciplina = ? AND n.professor_id = ?
                ORDER BY a.nome
            ''', (disciplina, prof_id))
            
            for row in self.sistema.cursor.fetchall():
                tree_notas.insert('', 'end', values=row)
        
        atualizar_lista_notas()
    
    def interface_aluno(self):
        self.limpar_conteudo()
        
        # Buscar dados do aluno
        self.sistema.cursor.execute('''
            SELECT id, nome, matricula, turma FROM alunos
            WHERE usuario_id = ?
        ''', (self.sistema.usuario_logado,))
        aluno_data = self.sistema.cursor.fetchone()
        
        if not aluno_data:
            messagebox.showerror("Erro", "Dados do aluno não encontrados!")
            return
        
        aluno_id, nome, matricula, turma = aluno_data
        
        # Informações do aluno
        frame_info = tk.LabelFrame(self.frame_conteudo, text="Informações",
                                   font=('Arial', 12, 'bold'), bg='#ecf0f1')
        frame_info.pack(fill='x', padx=20, pady=20)
        
        tk.Label(frame_info, text=f"Nome: {nome}", font=('Arial', 12),
                bg='#ecf0f1').grid(row=0, column=0, padx=20, pady=10, sticky='w')
        tk.Label(frame_info, text=f"Matrícula: {matricula}", font=('Arial', 12),
                bg='#ecf0f1').grid(row=0, column=1, padx=20, pady=10, sticky='w')
        tk.Label(frame_info, text=f"Turma: {turma}", font=('Arial', 12),
                bg='#ecf0f1').grid(row=0, column=2, padx=20, pady=10, sticky='w')
        
        # Notas
        frame_notas = tk.LabelFrame(self.frame_conteudo, text="Minhas Notas",
                                    font=('Arial', 12, 'bold'), bg='#ecf0f1')
        frame_notas.pack(fill='both', expand=True, padx=20, pady=10)
        
        tree_notas = ttk.Treeview(frame_notas, columns=('Disciplina', 'Nota', 'Professor'),
                                  show='headings', height=15)
        tree_notas.heading('Disciplina', text='Disciplina')
        tree_notas.heading('Nota', text='Nota')
        tree_notas.heading('Professor', text='Professor')
        
        tree_notas.column('Disciplina', width=200)
        tree_notas.column('Nota', width=100)
        tree_notas.column('Professor', width=250)
        
        tree_notas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buscar notas
        self.sistema.cursor.execute('''
            SELECT n.disciplina, n.nota, p.nome
            FROM notas n
            JOIN professores p ON n.professor_id = p.id
            WHERE n.aluno_id = ?
            ORDER BY n.disciplina
        ''', (aluno_id,))
        
        total_notas = 0
        count = 0
        
        for row in self.sistema.cursor.fetchall():
            tree_notas.insert('', 'end', values=row)
            total_notas += row[1]
            count += 1
        
        # Média
        if count > 0:
            media = total_notas / count
            tk.Label(frame_notas, text=f"Média Geral: {media:.2f}",
                    font=('Arial', 14, 'bold'), bg='#ecf0f1', fg='#27ae60').pack(pady=10)
    
    def sair(self):
        self.janela.destroy()
        InterfaceLogin(self.sistema)

# Iniciar aplicação
if __name__ == "__main__":
    sistema = SistemaNotas()
    InterfaceLogin(sistema)
