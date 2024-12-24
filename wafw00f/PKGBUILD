# Maintainer: Hao Long <aur@esd.cc>

pkgname=wafw00f
pkgver=2.3.0
pkgrel=1
pkgdesc="The Web Application Firewall Fingerprinting Tool"
arch=("any")
url="https://github.com/EnableSecurity/wafw00f"
license=('BSD-3-Clause')
depends=("python-pluginbase"
         "python-requests")
makedepends=('python-setuptools')
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
b2sums=('8f887bc3713893ea8af446d5b9f3aa8965568dc442c7eb7f8dd7657dd185bc9fd5f0571084da1af22edf84070f753d85587a15472d34d533ec929032a430c672')

build() {
  cd $pkgname-$pkgver
  python setup.py build
}

package() {
  cd $pkgname-$pkgver
  python setup.py install --root="$pkgdir" --optimize=1 --skip-build
  install -Dm644 LICENSE "${pkgdir}"/usr/share/licenses/${pkgname}/LICENSE
}
