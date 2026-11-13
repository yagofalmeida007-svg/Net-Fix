"""Teste de DNS.

As consultas aos servidores públicos são feitas direto por UDP (porta 53),
sem depender do nslookup. O nslookup muda a saída conforme o idioma do Windows
("Name:" / "Nome:"), o que fazia o teste falhar em Windows em português.
"""
import random
import socket
import struct
import time

DOMINIO = "google.com"

SERVIDORES = {
    "Cloudflare": "1.1.1.1",
    "Google": "8.8.8.8",
}


def _montar_consulta(dominio):
    id_consulta = random.randint(0, 0xFFFF)
    cabecalho = struct.pack(">HHHHHH", id_consulta, 0x0100, 1, 0, 0, 0)
    nome = b"".join(bytes([len(p)]) + p.encode() for p in dominio.split(".")) + b"\x00"
    pergunta = nome + struct.pack(">HH", 1, 1)  # tipo A, classe IN
    return id_consulta, cabecalho + pergunta


def _pular_nome(dados, pos):
    while True:
        tamanho = dados[pos]
        if tamanho == 0:
            return pos + 1
        if tamanho & 0xC0 == 0xC0:  # ponteiro de compressão
            return pos + 2
        pos += tamanho + 1


def _interpretar(dados, id_esperado):
    """Retorna (ip, codigo_de_erro). ip é None se não houver registro A."""
    if len(dados) < 12:
        raise ValueError("Resposta curta demais")

    id_resp, flags, qd, an, _, _ = struct.unpack(">HHHHHH", dados[:12])
    if id_resp != id_esperado:
        raise ValueError("ID da resposta não confere")

    codigo = flags & 0xF
    if codigo != 0:
        return None, codigo

    pos = 12
    for _ in range(qd):
        pos = _pular_nome(dados, pos) + 4

    for _ in range(an):
        pos = _pular_nome(dados, pos)
        tipo, _, _, tamanho = struct.unpack(">HHIH", dados[pos:pos + 10])
        pos += 10
        if tipo == 1 and tamanho == 4:
            return socket.inet_ntoa(dados[pos:pos + 4]), 0
        pos += tamanho

    return None, 0


def _consultar(servidor, dominio=DOMINIO, timeout=3):
    id_consulta, pacote = _montar_consulta(dominio)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        inicio = time.perf_counter()
        s.sendto(pacote, (servidor, 53))
        dados, _ = s.recvfrom(512)
        tempo_ms = (time.perf_counter() - inicio) * 1000

    ip, codigo = _interpretar(dados, id_consulta)
    return ip, codigo, tempo_ms


def testar_dns():
    resultados = {}

    # DNS configurado no sistema (o que os programas realmente usam)
    try:
        inicio = time.perf_counter()
        endereco = socket.gethostbyname(DOMINIO)
        tempo_ms = (time.perf_counter() - inicio) * 1000
        resultados["Sistema"] = {
            "status": "Funcionando",
            "endereco": endereco,
            "tempo": tempo_ms,
        }
    except socket.gaierror:
        resultados["Sistema"] = {"status": "Falha na resolução"}

    # Servidores públicos
    for nome, servidor in SERVIDORES.items():
        dados = {"servidor": servidor}
        try:
            ip, codigo, tempo_ms = _consultar(servidor)
            if ip:
                dados.update(status="Funcionando", endereco=ip, tempo=tempo_ms)
            else:
                dados["status"] = "Sem resposta válida"
        except socket.timeout:
            dados["status"] = "Tempo esgotado"
        except (OSError, ValueError, struct.error, IndexError):
            dados["status"] = "Erro no teste"
        resultados[nome] = dados

    return resultados
