# Maintainer: Matoryuska <skibidy839@gmail.com>
pkgname=asciivideo
pkgver=0.1.0
pkgrel=1
pkgdesc="Reproductor de video ascii para la terminal"
arch=('any')
url="https://github.com/Matoryuska/asciivideo"
license=('MIT')
depends=('python' 'python-opencv' 'python-numpy')
source=()

package() {
    # Copiar el código fuente directamente desde tu carpeta actual al sistema
    cd "$startdir"
    
    # Crear las carpetas de destino en el sistema
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/lib/python3.14/site-packages/asciivideo"
    
    # Copiar los archivos de la librería
    install -m 644 asciivideo/__init__.py "$pkgdir/usr/lib/python3.14/site-packages/asciivideo/"
    install -m 644 asciivideo/main.py "$pkgdir/usr/lib/python3.14/site-packages/asciivideo/"
    
    # Crear el script ejecutable global de terminal
    cat << 'EOF' > "$pkgdir/usr/bin/asciivideo"
#!/usr/bin/env python
from asciivideo.main import main
if __name__ == '__main__':
    main()
EOF
    chmod +x "$pkgdir/usr/bin/asciivideo"
}