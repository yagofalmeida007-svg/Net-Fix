import queue
import threading
from tkinter import messagebox

import customtkinter as ctk

from services.diagnostico import testar_conexao
from services.dns import testar_dns
from services import reparo
from utils.recursos import caminho_recurso, carregar_icone

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

COR_REPARO = ("#d97706", "#b45309")

PERFIS_DNS = {
    "Cloudflare (1.1.1.1)": ("1.1.1.1", "1.0.0.1"),
    "Google (8.8.8.8)": ("8.8.8.8", "8.8.4.4"),
    "Automático (DHCP)": None,
}


class NetFix:
    def __init__(self):
        self.janela = ctk.CTk()
        self.janela.title("NetFix - Diagnóstico e Reparo de Rede")
        self.janela.geometry("1000x760")
        self.janela.minsize(850, 740)

        self._definir_icone_janela()

        self.fila = queue.Queue()
        self.ocupado = False
        self.botoes = []

        self.criar_interface()
        self._escrever(
            "Bem-vindo ao NetFix.\n\n"
            "Use os botões à esquerda para testar a conexão ou aplicar reparos."
        )
        self.janela.after(100, self._processar_fila)

    # ---------- Interface ----------

    def _definir_icone_janela(self):
        caminho = caminho_recurso("assets", "icons", "app.ico")
        # O CustomTkinter redefine o ícone ao abrir; por isso o after().
        self.janela.after(200, lambda: self._aplicar_icone(caminho))

    def _aplicar_icone(self, caminho):
        try:
            self.janela.iconbitmap(caminho)
        except Exception:
            pass  # sem ícone (ou fora do Windows), o app segue normalmente

    def criar_interface(self):
        self.janela.grid_columnconfigure(1, weight=1)
        self.janela.grid_rowconfigure(0, weight=1)

        lateral = ctk.CTkFrame(self.janela, width=290, corner_radius=0)
        lateral.grid(row=0, column=0, sticky="nsew")
        lateral.pack_propagate(False)

        cabecalho = ctk.CTkFrame(lateral, fg_color="transparent")
        cabecalho.pack(pady=(22, 18))
        self.img_logo = carregar_icone("images", "logo.png", 52)
        if self.img_logo:
            ctk.CTkLabel(cabecalho, image=self.img_logo, text="").grid(
                row=0, column=0, rowspan=2, padx=(0, 12)
            )
        ctk.CTkLabel(cabecalho, text="NetFix", font=("Arial", 28, "bold")).grid(
            row=0, column=1, sticky="w"
        )
        ctk.CTkLabel(
            cabecalho, text="Diagnóstico e reparo", font=("Arial", 12)
        ).grid(row=1, column=1, sticky="w")

        ctk.CTkLabel(lateral, text="Testes", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=22
        )
        self._botao(lateral, "Testar conexão", self.iniciar_diagnostico, icone="conexao.png")
        self._botao(lateral, "Testar DNS", self.iniciar_teste_dns, icone="dns.png")

        ctk.CTkLabel(lateral, text="Reparo", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=22, pady=(20, 0)
        )
        self._botao(lateral, "Limpar cache DNS", self.limpar_dns, COR_REPARO, "limpar.png")
        self._botao(lateral, "Renovar IP", self.renovar_ip, COR_REPARO, "renovar.png")
        self._botao(lateral, "Resetar pilha de rede", self.resetar_pilha, COR_REPARO, "resetar.png")

        ctk.CTkLabel(
            lateral, text="DNS do adaptador", font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=22, pady=(20, 0))
        self.menu_dns = ctk.CTkOptionMenu(
            lateral, values=list(PERFIS_DNS), height=36
        )
        self.menu_dns.pack(padx=20, pady=4, fill="x")
        self.botoes.append(self.menu_dns)
        self._botao(lateral, "Aplicar DNS", self.aplicar_dns, COR_REPARO, "aplicar.png")

        if reparo.WINDOWS and not reparo.eh_administrador():
            ctk.CTkLabel(
                lateral,
                text="Os reparos precisam de\npermissão de administrador.",
                font=("Arial", 12),
                text_color="#f59e0b",
            ).pack(side="bottom", pady=(0, 20))
            admin = ctk.CTkButton(
                lateral,
                text="Reabrir como administrador",
                height=36,
                fg_color="transparent",
                border_width=1,
                command=self.reabrir_admin,
            )
            admin.pack(side="bottom", padx=20, pady=(0, 8), fill="x")
            self.botoes.append(admin)

        self.log = ctk.CTkTextbox(
            self.janela, font=("Consolas", 14), wrap="word", state="disabled"
        )
        self.log.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def _botao(self, pai, texto, comando, cor=None, icone=None):
        opcoes = {"fg_color": cor[0], "hover_color": cor[1]} if cor else {}
        imagem = carregar_icone("icons", icone, 20) if icone else None
        if imagem:
            opcoes.update(image=imagem, compound="left")
        botao = ctk.CTkButton(pai, text=texto, height=36, command=comando, **opcoes)
        botao.pack(padx=20, pady=4, fill="x")
        self.botoes.append(botao)
        return botao

    def _escrever(self, texto):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("1.0", texto)
        self.log.configure(state="disabled")

    def _travar(self, travar):
        estado = "disabled" if travar else "normal"
        for botao in self.botoes:
            botao.configure(state=estado)

    # ---------- Execução em segundo plano ----------

    def _rodar(self, titulo, funcao, formatar):
        """Executa funcao(progresso) em thread e mostra formatar(resultado)."""
        if self.ocupado:
            return
        self.ocupado = True
        self._travar(True)
        self._escrever(f"{titulo}...")

        def progresso(atual, total):
            self.fila.put(("progresso", f"{titulo}... {atual}/{total}"))

        def tarefa():
            try:
                texto = formatar(funcao(progresso))
            except Exception as erro:
                texto = f"Erro inesperado: {erro}"
            self.fila.put(("fim", texto))

        threading.Thread(target=tarefa, daemon=True).start()

    def _processar_fila(self):
        try:
            while True:
                tipo, texto = self.fila.get_nowait()
                self._escrever(texto)
                if tipo == "fim":
                    self.ocupado = False
                    self._travar(False)
        except queue.Empty:
            pass
        self.janela.after(100, self._processar_fila)

    # ---------- Ações ----------

    def iniciar_diagnostico(self):
        self._rodar(
            "Testando conexão",
            lambda cb: testar_conexao(progresso=cb),
            self._formatar_diagnostico,
        )

    def iniciar_teste_dns(self):
        self._rodar("Testando DNS", lambda cb: testar_dns(), self._formatar_dns)

    def limpar_dns(self):
        self._rodar(
            "Limpando cache DNS",
            lambda cb: reparo.limpar_cache_dns(),
            self._formatar_reparo,
        )

    def renovar_ip(self):
        self._rodar(
            "Renovando IP", lambda cb: reparo.renovar_ip(), self._formatar_reparo
        )

    def resetar_pilha(self):
        if not messagebox.askyesno(
            "Resetar pilha de rede",
            "Isso reinicia o Winsock e o TCP/IP.\n"
            "Você precisará reiniciar o computador depois.\n\nContinuar?",
        ):
            return
        self._rodar(
            "Resetando pilha de rede",
            lambda cb: reparo.resetar_pilha(),
            self._formatar_reparo,
        )

    def aplicar_dns(self):
        escolha = self.menu_dns.get()
        self._rodar(
            f"Aplicando DNS: {escolha}",
            lambda cb: reparo.definir_dns(PERFIS_DNS[escolha]),
            self._formatar_reparo,
        )

    def reabrir_admin(self):
        if reparo.reabrir_como_administrador():
            self.janela.destroy()
        else:
            messagebox.showwarning(
                "NetFix", "Não foi possível abrir como administrador."
            )

    # ---------- Formatação dos resultados ----------

    @staticmethod
    def _formatar_diagnostico(r):
        if r["recebidos"] == 0:
            return (
                f"DIAGNÓSTICO DE CONEXÃO ({r['host']})\n\n"
                "Nenhum pacote respondeu.\n\n"
                "Sem conexão com a internet, ou o ping está bloqueado.\n"
                "Verifique o cabo/Wi-Fi e o roteador, depois tente 'Renovar IP'."
            )

        problemas = []
        if r["perda"] >= 5:
            problemas.append("perda de pacotes")
        if r["ping"] > 100:
            problemas.append("latência alta")
        if r["jitter"] > 30:
            problemas.append("jitter alto (conexão instável)")
        veredito = (
            "Conexão boa."
            if not problemas
            else "Atenção: " + ", ".join(problemas) + "."
        )

        return (
            f"DIAGNÓSTICO DE CONEXÃO ({r['host']})\n\n"
            f"Ping médio:  {r['ping']:.1f} ms "
            f"(mín {r['minimo']:.0f} / máx {r['maximo']:.0f})\n"
            f"Jitter:      {r['jitter']:.1f} ms\n"
            f"Perda:       {r['perda']:.1f}%\n\n"
            f"Enviados: {r['enviados']}   Recebidos: {r['recebidos']}   "
            f"Perdidos: {r['perdidos']}\n\n"
            f"{veredito}"
        )

    @staticmethod
    def _formatar_dns(resultados):
        linhas = ["TESTE DE DNS\n"]
        for nome, d in resultados.items():
            linha = f"{nome}"
            if "servidor" in d:
                linha += f" ({d['servidor']})"
            linha += f": {d['status']}"
            if "tempo" in d:
                linha += f" em {d['tempo']:.0f} ms"
            linhas.append(linha)
            if "endereco" in d:
                linhas.append(f"    IP encontrado: {d['endereco']}")

        sistema_ok = resultados.get("Sistema", {}).get("status") == "Funcionando"
        publicos_ok = any(
            d["status"] == "Funcionando"
            for nome, d in resultados.items()
            if nome != "Sistema"
        )

        linhas.append("")
        if sistema_ok:
            linhas.append("DNS do sistema funcionando.")
        elif publicos_ok:
            linhas.append(
                "O DNS do sistema falhou, mas os públicos respondem.\n"
                "Tente 'Limpar cache DNS' ou troque o DNS do adaptador\n"
                "para 1.1.1.1 ou 8.8.8.8."
            )
        else:
            linhas.append(
                "Nenhum DNS respondeu. Pode ser falta de internet\n"
                "ou bloqueio da porta 53 pelo firewall."
            )
        return "\n".join(linhas)

    @staticmethod
    def _formatar_reparo(passos):
        linhas = ["REPARO\n"]
        falhou = False
        for descricao, ok, saida in passos:
            linhas.append(f"{'[OK]' if ok else '[FALHOU]'} {descricao}")
            if saida:
                linhas.append("    " + saida.replace("\n", "\n    "))
            if not ok:
                falhou = True
        linhas.append("")
        if falhou and reparo.WINDOWS and not reparo.eh_administrador():
            linhas.append(
                "Falhou por falta de permissão. Use 'Reabrir como administrador'."
            )
        elif falhou:
            linhas.append("Alguma etapa falhou. Veja os detalhes acima.")
        else:
            linhas.append("Concluído. Rode 'Testar conexão' para conferir.")
        return "\n".join(linhas)

    def executar(self):
        self.janela.mainloop()

