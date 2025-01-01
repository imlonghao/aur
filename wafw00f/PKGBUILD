# Maintainer: Hao Long <aur@esd.cc>

pkgname=wafw00f
pkgver=2.3.1
pkgrel=1
pkgdesc="The Web Application Firewall Fingerprinting Tool"
arch=("any")
url="https://github.com/EnableSecurity/wafw00f"
license=('BSD-3-Clause')
depends=("python-pluginbase"
         "python-requests")
makedepends=('python-setuptools')
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
b2sums=('feab0c31cf068ff32019a486b13c0adfeea49464d3618479a417bb04f728f6cdc9e6bb1a28ad769d59f5de4c73addb5c4f0785c578fc2680cc3ab86b21b0cae3')

build() {
  cd $pkgname-$pkgver
  python setup.py build
}

package() {
  cd $pkgname-$pkgver
  python setup.py install --root="$pkgdir" --optimize=1 --skip-build
  install -Dm644 LICENSE "${pkgdir}"/usr/share/licenses/${pkgname}/LICENSE
}
