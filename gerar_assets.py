"""Gera o logo, o ícone do app (.ico) e os ícones dos botões do NetFix.

Uso: python gerar_assets.py   (precisa do Pillow)
Os arquivos vão para assets/images e assets/icons. Edite as cores e rode de novo.
"""
import math
import os

from PIL import Image, ImageDraw

VERDE = (44, 201, 133)      # testes (mesmo tom do tema "green")
LARANJA = (245, 158, 11)    # reparo
FUNDO = (16, 35, 27)
BRANCO = (255, 255, 255)
S = 8  # supersampling: desenha 8x maior e reduz, para bordas suaves

PASTA_IMG = os.path.join("assets", "images")
PASTA_ICO = os.path.join("assets", "icons")


def tela(tamanho):
    img = Image.new("RGBA", (tamanho * S, tamanho * S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def reduzir(img, tamanho):
    return img.resize((tamanho, tamanho), Image.LANCZOS)


def ponto_arco(cx, cy, r, graus):
    a = math.radians(graus)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def bola(d, x, y, r, cor):
    d.ellipse([x - r, y - r, x + r, y + r], fill=cor)


def arco(d, cx, cy, r, largura, a0, a1, cor):
    """Arco com pontas arredondadas (ângulos do Pillow, sentido horário)."""
    d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=cor, width=int(largura))
    for ang in (a0, a1):
        x, y = ponto_arco(cx, cy, r - largura / 2 + 0.5, ang)
        bola(d, x, y, largura / 2, cor)


# ---------- Logo: ondas verdes (teste) + ponto laranja (reparo) ----------
def desenhar_logo(d, n, escala=1.0, deslocar=0):
    """Desenha o símbolo numa grade de n x n (n em pixels já multiplicados por S)."""
    u = n / 256 * escala
    cx = n / 2
    cy = n / 2 + (66 * u) + deslocar
    larg = 20 * u
    for r in (60, 102, 144):
        arco(d, cx, cy, r * u, larg, 225, 315, VERDE)
    bola(d, cx, cy, 15 * u, LARANJA)


def logo(tamanho=256):
    img, d = tela(tamanho)
    desenhar_logo(d, tamanho * S, escala=1.0)
    return reduzir(img, tamanho)


def icone_app(tamanho=256):
    img, d = tela(tamanho)
    n = tamanho * S
    margem = n * 0.04
    d.rounded_rectangle([margem, margem, n - margem, n - margem],
                        radius=n * 0.22, fill=FUNDO)
    desenhar_logo(d, n, escala=0.88, deslocar=-n * 0.005)
    return reduzir(img, tamanho)


# ---------- Ícones de botão (64 px, brancos, fundo transparente) ----------
def icone_conexao():
    img, d = tela(64)
    k = 2 * S
    for x0, y0, x1 in ((10, 38, 20), (26, 24, 36), (42, 10, 52)):
        d.rounded_rectangle([x0 * S, y0 * S, x1 * S, 54 * S], radius=3 * S, fill=BRANCO)
    return reduzir(img, 64)


def icone_dns():
    img, d = tela(64)
    w = int(4.5 * S)
    d.ellipse([8 * S, 8 * S, 56 * S, 56 * S], outline=BRANCO, width=w)
    d.ellipse([22 * S, 8 * S, 42 * S, 56 * S], outline=BRANCO, width=w)
    d.line([8 * S, 32 * S, 56 * S, 32 * S], fill=BRANCO, width=w)
    return reduzir(img, 64)


def icone_limpar():
    img, d = tela(64)
    w = int(4.5 * S)
    d.line([12 * S, 18 * S, 52 * S, 18 * S], fill=BRANCO, width=w)
    d.rounded_rectangle([25 * S, 8 * S, 39 * S, 18 * S], radius=2 * S,
                        outline=BRANCO, width=w)
    pts = [(17 * S, 24 * S), (20 * S, 56 * S), (44 * S, 56 * S), (47 * S, 24 * S)]
    d.line(pts, fill=BRANCO, width=w, joint="curve")
    for x, y in pts:
        bola(d, x, y, w / 2, BRANCO)
    d.line([27 * S, 30 * S, 27 * S, 48 * S], fill=BRANCO, width=w)
    d.line([37 * S, 30 * S, 37 * S, 48 * S], fill=BRANCO, width=w)
    return reduzir(img, 64)


def icone_renovar():
    img, d = tela(64)
    cx = cy = 32 * S
    r = 19 * S
    w = 5 * S
    arco(d, cx, cy, r, w, 40, 300, BRANCO)
    fim = ponto_arco(cx, cy, r - w / 2, 300)
    tang = (-math.sin(math.radians(300)), math.cos(math.radians(300)))
    rad = (math.cos(math.radians(300)), math.sin(math.radians(300)))
    ponta = (fim[0] + tang[0] * 9 * S, fim[1] + tang[1] * 9 * S)
    b1 = (fim[0] + rad[0] * 8 * S, fim[1] + rad[1] * 8 * S)
    b2 = (fim[0] - rad[0] * 8 * S, fim[1] - rad[1] * 8 * S)
    d.polygon([ponta, b1, b2], fill=BRANCO)
    return reduzir(img, 64)


def icone_resetar():
    img, d = tela(64)
    cx, cy, r, w = 32 * S, 35 * S, 18 * S, 5 * S
    arco(d, cx, cy, r, w, 300, 360, BRANCO)
    arco(d, cx, cy, r, w, 0, 240, BRANCO)
    d.line([cx, 8 * S, cx, 32 * S], fill=BRANCO, width=int(w))
    bola(d, cx, 8 * S + w / 2 - 1, w / 2, BRANCO)
    return reduzir(img, 64)


def icone_aplicar():
    img, d = tela(64)
    w = int(5 * S)
    d.ellipse([7 * S, 7 * S, 57 * S, 57 * S], outline=BRANCO, width=w)
    pts = [(20 * S, 33 * S), (28 * S, 41 * S), (44 * S, 23 * S)]
    d.line(pts, fill=BRANCO, width=w, joint="curve")
    for x, y in pts:
        bola(d, x, y, w / 2, BRANCO)
    return reduzir(img, 64)


def main():
    os.makedirs(PASTA_IMG, exist_ok=True)
    os.makedirs(PASTA_ICO, exist_ok=True)

    logo(256).save(os.path.join(PASTA_IMG, "logo.png"))

    app = icone_app(256)
    app.save(os.path.join(PASTA_ICO, "app.png"))
    app.save(
        os.path.join(PASTA_ICO, "app.ico"),
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )

    botoes = {
        "conexao.png": icone_conexao, "dns.png": icone_dns,
        "limpar.png": icone_limpar, "renovar.png": icone_renovar,
        "resetar.png": icone_resetar, "aplicar.png": icone_aplicar,
    }
    for nome, fn in botoes.items():
        fn().save(os.path.join(PASTA_ICO, nome))
    print("Arquivos gerados em assets/")


if __name__ == "__main__":
    main()
