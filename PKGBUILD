# Maintainer: Matoryuska <skibidy839@gmail.com>
pkgname=asciivideo
pkgver=0.1.0
pkgrel=1
pkgdesc="Reproductor de video ascii para la terminal"
arch=('any')
url="https://github.com/Matoryuska/asciivideo"
license=('MIT')
depends=('python' 'python-opencv' 'python-numpy')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::https://github.com/Matoryuska/asciivideo/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$pkgname-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$pkgname-$pkgver"
    python -m installer --destdir="$pkgdir" dist/*.whl
}