#!/usr/bin/env bash
# Gera dist/mintskin_<versao>_all.deb
#   ./build-deb.sh
set -euo pipefail
cd "$(dirname "$0")"

VERSAO=$(python3 -c 'import mintskin; print(mintskin.__version__)')
MANTENEDOR=${MANTENEDOR:-"MintSkin <PablUoo@users.noreply.github.com>"}
RAIZ=$(mktemp -d)
trap 'rm -rf "$RAIZ"' EXIT
chmod 755 "$RAIZ"

echo "== MintSkin $VERSAO =="
python3 -m unittest discover -s tests -q || { echo "testes falharam: pacote nao gerado"; exit 1; }
install -d "$RAIZ/DEBIAN" "$RAIZ/usr/bin" "$RAIZ/usr/lib/mintskin/mintskin" \
  "$RAIZ/usr/share/mintskin/skins" "$RAIZ/usr/share/applications" \
  "$RAIZ/usr/share/icons/hicolor/scalable/apps" "$RAIZ/usr/share/polkit-1/actions" \
  "$RAIZ/usr/share/mime/packages" "$RAIZ/usr/share/doc/mintskin"

# pacote Python inteiro (dominio, aplicacao, infra, ui), sem caches
(cd mintskin && find . -type f \( -name '*.py' -o -name '*.css' -o -name '*.svg' \) -not -path '*/__pycache__/*' \
  -exec install -D -m 644 {} "$RAIZ/usr/lib/mintskin/mintskin/{}" \;)
install -m 755 helpers/mintskin-login-helper "$RAIZ/usr/lib/mintskin/"
install -m 755 bin/mintskin "$RAIZ/usr/bin/mintskin"
install -m 644 data/io.github.pabluoo.MintSkin.desktop "$RAIZ/usr/share/applications/"
install -m 644 data/icons/mintskin.svg "$RAIZ/usr/share/icons/hicolor/scalable/apps/mintskin.svg"
install -m 644 data/polkit/io.github.pabluoo.mintskin.policy "$RAIZ/usr/share/polkit-1/actions/"
install -m 644 data/mintskin-mime.xml "$RAIZ/usr/share/mime/packages/mintskin.xml"
install -m 644 README.md "$RAIZ/usr/share/doc/mintskin/"
cat > "$RAIZ/usr/share/doc/mintskin/copyright" <<FIM
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: MintSkin
Upstream-Contact: https://github.com/PablUoo/MintSkin

Files: *
Copyright: 2026 MintSkin
Comment: O nome MintSkin e o logotipo "m" sao marcas do projeto MintSkin.
 As skins incluidas trazem temas, icones e fontes de terceiros, cada um com
 a licenca do seu autor.
FIM
cp -a skins/. "$RAIZ/usr/share/mintskin/skins/"
# arquivos de dados: legiveis por todos, sem bit de execucao estranho
find "$RAIZ/usr/share/mintskin" -type d -exec chmod 755 {} +
find "$RAIZ/usr/share/mintskin" -type f -exec chmod 644 {} +

TAMANHO=$(du -sk --exclude=DEBIAN "$RAIZ" | cut -f1)
cat > "$RAIZ/DEBIAN/control" <<FIM
Package: mintskin
Version: $VERSAO
Section: x11
Priority: optional
Architecture: all
Installed-Size: $TAMANHO
Depends: python3 (>= 3.10), python3-gi, python3-gi-cairo, gir1.2-gtk-3.0, libglib2.0-bin, fontconfig, pkexec | policykit-1
Recommends: plank, cinnamon
Maintainer: $MANTENEDOR
Homepage: https://github.com/PablUoo/MintSkin
Description: troque o visual do Linux Mint Cinnamon com um clique
 MintSkin guarda o visual do desktop (temas, icones, fontes, painel,
 applets, dock e papel de parede) como "skins" com nome e data, e aplica
 qualquer uma delas com um clique. Vem com uma skin macOS.
 Ferramenta nao oficial de terceiros.
FIM
cat > "$RAIZ/DEBIAN/postinst" <<'FIM'
#!/bin/sh
set -e
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q -f /usr/share/icons/hicolor || true
command -v update-desktop-database >/dev/null && update-desktop-database -q /usr/share/applications || true
command -v update-mime-database >/dev/null && update-mime-database /usr/share/mime || true
exit 0
FIM
cp "$RAIZ/DEBIAN/postinst" "$RAIZ/DEBIAN/postrm"
chmod 755 "$RAIZ/DEBIAN/postinst" "$RAIZ/DEBIAN/postrm"

mkdir -p dist
SAIDA="dist/mintskin_${VERSAO}_all.deb"
dpkg-deb --root-owner-group -Zxz --build "$RAIZ" "$SAIDA" >/dev/null
echo "pronto: $SAIDA ($(du -h "$SAIDA" | cut -f1))"
echo "instalar: sudo apt install ./$SAIDA"
