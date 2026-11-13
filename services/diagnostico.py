import platform
import re
import statistics
import subprocess

WINDOWS = platform.system() == "Windows"
_SEM_JANELA = subprocess.CREATE_NO_WINDOW if WINDOWS else 0

# Pega o tempo em qualquer idioma: "tempo=15ms", "tempo<1ms", "time=15.2 ms"
_REGEX_TEMPO = re.compile(r"[=<]\s*(\d+(?:[.,]\d+)?)\s*ms", re.IGNORECASE)


def _ping_unico(host):
    """Envia 1 ping. Retorna o tempo em ms, ou None se não houve resposta."""
    if WINDOWS:
        comando = ["ping", "-n", "1", "-w", "2000", host]
    else:
        comando = ["ping", "-c", "1", "-W", "2", host]

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            text=True,
            errors="replace",
            timeout=5,
            creationflags=_SEM_JANELA,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    resposta = _REGEX_TEMPO.search(resultado.stdout)
    if not resposta:
        return None

    return float(resposta.group(1).replace(",", "."))


def testar_conexao(host="1.1.1.1", quantidade=10, progresso=None):
    """Mede ping médio, jitter e perda de pacotes.

    progresso: função opcional chamada como progresso(atual, total).
    """
    tempos = []

    for i in range(quantidade):
        tempo = _ping_unico(host)
        if tempo is not None:
            tempos.append(tempo)
        if progresso:
            progresso(i + 1, quantidade)

    ping_medio = statistics.mean(tempos) if tempos else 0

    jitter = 0
    if len(tempos) > 1:
        diferencas = [abs(tempos[i] - tempos[i - 1]) for i in range(1, len(tempos))]
        jitter = statistics.mean(diferencas)

    perdidos = quantidade - len(tempos)

    return {
        "host": host,
        "ping": ping_medio,
        "minimo": min(tempos) if tempos else 0,
        "maximo": max(tempos) if tempos else 0,
        "jitter": jitter,
        "perda": (perdidos / quantidade) * 100,
        "enviados": quantidade,
        "recebidos": len(tempos),
        "perdidos": perdidos,
    }
