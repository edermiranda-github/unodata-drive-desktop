#!/usr/bin/env python3
"""Aplica a marca UNODATA Drive sobre o código oficial do app de desktop da Nextcloud (GPL-2.0).

Uso (na raiz do código do nextcloud/desktop, numa tag de versão):
    python3 ../unodata/aplicar-marca.py
Idempotente. Para uma versão nova: checkout da tag nova, rodar de novo, conferir o diff, compilar.

O que muda (e por quê):
- NEXTCLOUD.cmake: nome "UNODATA Drive", executável unodatadrive, fabricante UNODATA, cor #2074BA.
  "Nextcloud" é marca registrada: o app com marca não pode usar o nome.
- Atualização automática DESLIGADA (BUILD_UPDATER OFF, URL vazia): a padrão buscaria o instalador
  da Nextcloud em updates.nextcloud.org e trocaria o nosso app pelo deles.
- GUIDs próprios das extensões do Windows (ícones de status, menu de contexto, arquivos sob demanda)
  e do MSI: com os da Nextcloud, os dois apps no mesmo computador brigariam pelas mesmas chaves do registro.
- Assistente sem "Criar conta" e "Hospedar você mesmo" (levam ao site da Nextcloud) e sem importar a
  configuração de outro app de sincronização instalado.
- Ícones, logo do assistente e imagens do instalador com a arte da UNODATA.
"""
import base64
import io
import re
import uuid
from pathlib import Path

from PIL import Image, ImageDraw

ARTE = Path('/home/unodata/projetos/nextcloud/branding/logoheader.png')  # wordmark "unodata" de origem
COR = (0x20, 0x74, 0xBA)
COR_HEX = '#2074BA'
NOME, CURTO, EXE = 'UNODATA Drive', 'UNODATADrive', 'unodatadrive'
REV = 'drive'  # br.com.unodata.drive, unodata.com.br/drive/atualizacoes
ANTIGOS = ('UNODATANuvem', 'unodatanuvem')  # nome anterior (2026-11-09): arquivos dele saem da árvore
NS = uuid.UUID('6f1c1d1e-2b3a-4c5d-8e9f-0a1b2c3d4e5f')  # base fixa: os GUIDs não mudam entre compilações


def guid(nome):
    return str(uuid.uuid5(NS, nome)).upper()


def troca(caminho, pares):
    p = Path(caminho)
    s = p.read_text(encoding='utf-8')
    for padrao, novo in pares:
        # sem casamento = já aplicado (rodar de novo) ou o código oficial mudou: a conferência no fim decide
        s = re.sub(padrao, novo, s, flags=re.M)
    p.write_text(s, encoding='utf-8')


def confere(caminho, *trechos):
    s = Path(caminho).read_text(encoding='utf-8')
    faltando = [t for t in trechos if t not in s]
    if faltando:
        raise SystemExit(f'{caminho}: marca incompleta, falta {faltando} (o código oficial mudou? ajustar os padrões)')


# ---------- configuração ----------
troca('NEXTCLOUD.cmake', [
    (r'(else\(\)\n\s*set\( APPLICATION_NAME\s+)"(?:Nextcloud|UNODATA [^"]+)"', rf'\1"{NOME}"'),
    (r'(else\(\)\n(?:.*\n)*?\s*set\( APPLICATION_SHORTNAME\s+)"(?:Nextcloud|UNODATA\w+)"', rf'\1"{CURTO}"'),
    (r'(else\(\)\n(?:.*\n)*?\s*set\( APPLICATION_EXECUTABLE\s+)"(?:nextcloud|unodata\w+)"', rf'\1"{EXE}"'),
    (r'set\( APPLICATION_DOMAIN\s+"nextcloud.com" \)', 'set( APPLICATION_DOMAIN     "unodata.com.br" )'),
    (r'set\( APPLICATION_VENDOR\s+"Nextcloud GmbH" \)', 'set( APPLICATION_VENDOR     "UNODATA" )'),
    (r'set\( APPLICATION_UPDATE_URL\s+"https://(?:updates.nextcloud.org/client|www.unodata.com.br/\w+/atualizacoes)/"', f'set( APPLICATION_UPDATE_URL "https://www.unodata.com.br/{REV}/atualizacoes/"'),
    (r'set\( APPLICATION_HELP_URL\s+""', 'set( APPLICATION_HELP_URL   "https://www.unodata.com.br"'),
    (r'set\( APPLICATION_REV_DOMAIN "(?:com.nextcloud.desktopclient|br.com.unodata.\w+)" \)', f'set( APPLICATION_REV_DOMAIN "br.com.unodata.{REV}" )'),
    (r'set\( APPLICATION_REV_DOMAIN_DBUS "(?:desktopclient.nextcloud.com|\w+.unodata.com.br)" \)', f'set( APPLICATION_REV_DOMAIN_DBUS "{REV}.unodata.com.br" )'),
    (r'set\( APPLICATION_VIRTUALFILE_SUFFIX "nextcloud"', 'set( APPLICATION_VIRTUALFILE_SUFFIX "unodata"'),
    (r'set\( LINUX_PACKAGE_SHORTNAME "(?:nextcloud|unodata\w+)" \)', f'set( LINUX_PACKAGE_SHORTNAME "{EXE}" )'),
    (r'option\( BUILD_UPDATER "Build updater" ON \)', 'option( BUILD_UPDATER "Build updater" OFF )'),
    (r'option\( WITH_PROVIDERS "Build with providers list" ON \)', 'option( WITH_PROVIDERS "Build with providers list" OFF )'),
    (r'set\(NEXTCLOUD_BACKGROUND_COLOR "#0082c9"', f'set(NEXTCLOUD_BACKGROUND_COLOR "{COR_HEX}"'),
] + [(rf'(set\( {k}\s+)"\{{?[0-9A-F-]+\}}?" \)', rf'\1"{{{guid(k)}}}" )') for k in (
    'WIN_SHELLEXT_CONTEXT_MENU_GUID', 'WIN_SHELLEXT_OVERLAY_GUID_ERROR', 'WIN_SHELLEXT_OVERLAY_GUID_OK',
    'WIN_SHELLEXT_OVERLAY_GUID_OK_SHARED', 'WIN_SHELLEXT_OVERLAY_GUID_SYNC', 'WIN_SHELLEXT_OVERLAY_GUID_WARNING')]
  + [(r'(set\( WIN_MSI_UPGRADE_CODE\s+)"[0-9A-F-]+" \)', rf'\1"{guid("WIN_MSI_UPGRADE_CODE")}" )')])

troca('CMakeLists.txt', [
    (r'set\( CFAPI_SHELLEXT_APPID_REG "\{[0-9A-F-]+\}"\)', f'set( CFAPI_SHELLEXT_APPID_REG "{{{guid("CFAPI_APPID")}}}")'),
    (r'set\( CFAPI_SHELLEXT_CUSTOM_STATE_HANDLER_CLASS_ID "[0-9A-F-]+" \)',
     f'set( CFAPI_SHELLEXT_CUSTOM_STATE_HANDLER_CLASS_ID "{guid("CFAPI_STATE")}" )'),
    (r'set\( CFAPI_SHELLEXT_THUMBNAIL_HANDLER_CLASS_ID "[0-9A-F-]+" \)',
     f'set( CFAPI_SHELLEXT_THUMBNAIL_HANDLER_CLASS_ID "{guid("CFAPI_THUMB")}" )'),
    (r'(option\( APPLICATION_DISPLAY_LEGACY_IMPORT_DIALOG "[^"]*" )ON \)', r'\1OFF )'),
    (r'(option\( DISABLE_ACCOUNT_MIGRATION "[^"]*" )OFF \)', r'\1ON )'),
    (r'(option\( WIZARD_HIDE_SELF_HOST_BUTTON "[^"]*" )OFF \)', r'\1ON )'),
    (r'(option\( WIZARD_HIDE_SIGNUP_BUTTON "[^"]*" )OFF \)', r'\1ON )'),
])

confere('NEXTCLOUD.cmake', f'"{NOME}"', f'"{CURTO}"', f'"{EXE}"', '"UNODATA"', f'unodata.com.br/{REV}/atualizacoes', f'br.com.unodata.{REV}',
        'BUILD_UPDATER "Build updater" OFF', COR_HEX, guid('WIN_SHELLEXT_CONTEXT_MENU_GUID'), guid('WIN_MSI_UPGRADE_CODE'))
confere('CMakeLists.txt', guid('CFAPI_APPID'), guid('CFAPI_STATE'), guid('CFAPI_THUMB'), 'WIZARD_HIDE_SIGNUP_BUTTON "Hide the Sign up button in the account setup wizard" ON')

# ---------- arte ----------
# arquivos com o nome anterior: o CMake procura só os do nome atual, os antigos viram lixo
for velho in ANTIGOS:
    for f in list(Path('theme').rglob(f'{velho}*')) + list(Path('theme').rglob(f'*-{velho}-*')):
        if f.is_file():
            f.unlink()


def bbox(im):
    return im.getbbox()


src = Image.open(ARTE).convert('RGBA')
palavra = src.crop((0, 0, src.width, 580))
palavra = palavra.crop(bbox(palavra))
branco = Image.new('RGBA', palavra.size, (255, 255, 255, 0))
branco.putalpha(palavra.getchannel('A'))
azul = Image.new('RGBA', palavra.size, COR + (0,))
azul.putalpha(palavra.getchannel('A'))

# a letra "u": primeira coluna contínua do wordmark
a = palavra.getchannel('A')
cols = [max(a.crop((x, 0, x + 1, a.height)).getdata()) > 0 for x in range(a.width)]
x1 = next(i for i, v in enumerate(cols) if not v)
u = branco.crop((0, 0, x1, palavra.height))
u = u.crop(bbox(u))


def icone(S=1024):
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, S - 1, S - 1), radius=int(0.2 * S), fill=COR + (255,))
    h = int(S * 0.5)
    w = round(u.width * h / u.height)
    us = u.resize((w, h), Image.LANCZOS)
    im.alpha_composite(us, ((S - w) // 2, (S - h) // 2 + int(S * 0.03)))
    return im


def caber(img, W, H, margem=0.0, fundo=(0, 0, 0, 0)):
    t = Image.new('RGBA', (W, H), fundo)
    esc = min(W * (1 - 2 * margem) / img.width, H * (1 - 2 * margem) / img.height)
    r = img.resize((max(1, int(img.width * esc)), max(1, int(img.height * esc))), Image.LANCZOS)
    t.alpha_composite(r, ((W - r.width) // 2, (H - r.height) // 2))
    return t


def svg_de(img, caminho):
    b = io.BytesIO()
    img.save(b, 'PNG')
    d = base64.b64encode(b.getvalue()).decode()
    Path(caminho).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{img.width}" height="{img.height}" viewBox="0 0 {img.width} {img.height}">'
        f'<image width="{img.width}" height="{img.height}" xlink:href="data:image/png;base64,{d}"/></svg>\n')


ic = icone()
svg_de(ic, f'theme/colored/{CURTO}-icon.svg')
svg_de(ic, f'theme/colored/{CURTO}-w10startmenu.svg')
# logo do assistente: wordmark branco sobre o cabeçalho na cor da marca
for nome, (W, H) in (('wizard_logo.png', (132, 63)), ('wizard_logo@2x.png', (266, 126))):
    caber(branco, W, H, 0.08).save(f'theme/colored/{nome}')
svg_de(caber(branco, 532, 252, 0.08), 'theme/colored/wizard_logo.svg')
# instalador (NSIS): imagem lateral de boas-vindas e cabeçalho das páginas
boas = Image.new('RGBA', (164, 314), COR + (255,))
boas.alpha_composite(caber(icone(256), 88, 88), (38, 70))
boas.alpha_composite(caber(branco, 132, 40), (16, 180))
boas.convert('RGB').save('admin/win/nsi/welcome.bmp')
caber(azul, 150, 57, 0.12, (255, 255, 255, 255)).convert('RGB').save('admin/win/nsi/page_header.bmp')
# bloco do menu Iniciar: o instalador procura theme/<executável>.VisualElementsManifest.xml
Path(f'theme/{EXE}.VisualElementsManifest.xml').write_text(
    "<Application xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>\n"
    f'  <VisualElements BackgroundColor="{COR_HEX}" ForegroundText="light" ShowNameOnSquare150x150Logo="on"\n'
    f'    Square150x150Logo="visualelements\\150-{CURTO}-w10startmenu.png"\n'
    f'    Square70x70Logo="visualelements\\70-{CURTO}-w10startmenu.png"/>\n'
    '</Application>\n')
ic.save('admin/win/nsi/installer.ico', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(f'marca {NOME} aplicada')
for k in ('CFAPI_APPID', 'WIN_MSI_UPGRADE_CODE'):
    print(f'  {k}: {guid(k)}')
