"""Ações de reparo de rede (Windows). A maioria exige administrador."""
import ctypes
import platform
import subprocess
import sys

WINDOWS = platform.system() == "Windows"
_SEM_JANELA = subprocess.CREATE_NO_WINDOW if WINDOWS else 0


def eh_administrador():
    if not WINDOWS:
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def reabrir_como_administrador():
    """Abre uma nova instância com UAC. Retorna True se o pedido foi enviado."""
    if not WINDOWS:
        return False
    # No .exe (PyInstaller) o próprio executável já é o programa;
    # no script, o primeiro argumento é o caminho do main.py.
    argumentos = sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv
    parametros = " ".join(f'"{a}"' for a in argumentos)
    resultado = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, parametros, None, 1
    )
    return resultado > 32


def _decodificar(dados):
    for codificacao in ("oem", "utf-8", "cp1252"):
        try:
            return dados.decode(codificacao)
        except (LookupError, UnicodeDecodeError):
            continue
    return dados.decode("utf-8", errors="replace")


def _passo(descricao, comando, timeout=60, utf8=False):
    """Roda um comando. Retorna (descricao, ok, saida)."""
    if not WINDOWS:
        return (descricao, False, "Disponível apenas no Windows.")
    try:
        r = subprocess.run(
            comando,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            creationflags=_SEM_JANELA,
        )
        if utf8:
            saida = (r.stdout + r.stderr).decode("utf-8", errors="replace").strip()
        else:
            saida = (_decodificar(r.stdout) + _decodificar(r.stderr)).strip()
        return (descricao, r.returncode == 0, saida)
    except subprocess.TimeoutExpired:
        return (descricao, False, "Tempo esgotado.")
    except FileNotFoundError:
        return (descricao, False, "Comando não encontrado.")


def limpar_cache_dns():
    return [_passo("Limpando cache DNS", ["ipconfig", "/flushdns"])]


def renovar_ip():
    return [
        _passo("Liberando endereço IP", ["ipconfig", "/release"]),
        _passo("Obtendo novo endereço IP", ["ipconfig", "/renew"], timeout=90),
    ]


def resetar_pilha():
    return [
        _passo("Resetando Winsock", ["netsh", "winsock", "reset"]),
        _passo("Resetando pilha TCP/IP", ["netsh", "int", "ip", "reset"]),
    ]


# ---------- Troca de DNS do adaptador ----------

_UTF8 = "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "


def _powershell(descricao, script, timeout=60):
    return _passo(
        descricao,
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", _UTF8 + script],
        timeout=timeout,
        utf8=True,
    )


def listar_adaptadores():
    """Nomes dos adaptadores físicos (Wi-Fi/Ethernet) conectados."""
    descricao, ok, saida = _powershell(
        "Procurando adaptador de rede ativo",
        "Get-NetAdapter -Physical | Where-Object Status -eq 'Up' "
        "| ForEach-Object { $_.Name }",
    )
    if not ok:
        return [], (descricao, False, saida or "Não foi possível listar os adaptadores.")
    nomes = [linha.strip() for linha in saida.splitlines() if linha.strip()]
    return nomes, (descricao, bool(nomes), ", ".join(nomes) or "Nenhum adaptador conectado.")


def definir_dns(servidores=None):
    """Define o DNS dos adaptadores ativos. servidores=None volta ao automático (DHCP)."""
    if not WINDOWS:
        return [("Troca de DNS", False, "Disponível apenas no Windows.")]

    adaptadores, passo_busca = listar_adaptadores()
    if not adaptadores:
        return [passo_busca]

    passos = [passo_busca]
    for nome in adaptadores:
        alias = nome.replace("'", "''")
        if servidores:
            lista = ",".join(f"'{s}'" for s in servidores)
            script = (
                f"Set-DnsClientServerAddress -InterfaceAlias '{alias}' "
                f"-ServerAddresses ({lista}) -ErrorAction Stop"
            )
            descricao = f"Definindo DNS {', '.join(servidores)} em {nome}"
        else:
            script = (
                f"Set-DnsClientServerAddress -InterfaceAlias '{alias}' "
                "-ResetServerAddresses -ErrorAction Stop"
            )
            descricao = f"Restaurando DNS automático em {nome}"
        passos.append(_powershell(descricao, script))

    passos.append(_passo("Limpando cache DNS", ["ipconfig", "/flushdns"]))
    return passos
