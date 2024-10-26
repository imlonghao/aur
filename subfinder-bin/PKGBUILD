# Maintainer: Hao Long <aur@esd.cc>
# Co-Maintainer: Misaka13514 <Misaka13514 at gmail dot com>

pkgname=subfinder-bin
_pkgname=${pkgname%-bin}
pkgver=2.6.7
pkgrel=2
pkgdesc="A subdomain discovery tool that discovers valid subdomains for websites"
arch=('i686' 'x86_64' 'armv7h' 'aarch64')
url="https://github.com/projectdiscovery/subfinder"
license=("MIT")
provides=("${_pkgname}")
conflicts=("${_pkgname}")
depends=('glibc')
source=("LICENSE.md::https://github.com/projectdiscovery/subfinder/raw/v${pkgver}/LICENSE.md")
source_i686=("${_pkgname}-${pkgver}-i686.zip::${url}/releases/download/v${pkgver}/${_pkgname}_${pkgver}_linux_386.zip")
source_x86_64=("${_pkgname}-${pkgver}-x86_64.zip::${url}/releases/download/v${pkgver}/${_pkgname}_${pkgver}_linux_amd64.zip")
source_armv7h=("${_pkgname}-${pkgver}-armv7h.zip::${url}/releases/download/v${pkgver}/${_pkgname}_${pkgver}_linux_arm.zip")
source_aarch64=("${_pkgname}-${pkgver}-aarch64.zip::${url}/releases/download/v${pkgver}/${_pkgname}_${pkgver}_linux_arm64.zip")
b2sums=('c699be7ccfc40564b59bfa217e254c9553678f343466becebad5017d81310d7b7519837a9a25df2e09e16b6e1bd5a209d7aeb039662a206dd8966b9697c02ede')
b2sums_i686=('cb7f24d44711b31a08b6dcfbdb9e6ffc60011e17e2e31c4951d21e6481e9ed667581863133e79355d1e827f3ce31bc5d4fb2ae04847e0a62806119b96aaf9cdd')
b2sums_x86_64=('23365fa0ffb62c33533205dcf91b4f416be19cad230042f128610ec9c257bb5774f1285f2a882d0fa86d8c3284bd431e9f90f54d6cb81cf6b37c3b12f598784b')
b2sums_armv7h=('3c1656b563d6d07884be8eca94f8ce15513fe44526ba89fc0de4cb60cee230c56dd794d331be1634186cd160a689ab5f57a75c1cdfb06dee9dfd4c41295e1304')
b2sums_aarch64=('de05601f67edc892806668bb670072afed195644434217d0b27171bf6b8a84bf73e4ccf46c7991805d369fefb115b8521d3404ea81d205a4969c1eff507b1f88')

package() {
  install -Dm644 LICENSE.md "$pkgdir"/usr/share/licenses/$pkgname/LICENSE.md
  install -Dm755 subfinder ${pkgdir}/usr/bin/subfinder
}

# vim: ts=2 sw=2 et:
