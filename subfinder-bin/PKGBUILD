# Maintainer: Hao Long <aur@esd.cc>

pkgname=subfinder-bin
pkgver=2.6.6
pkgrel=1
pkgdesc="A subdomain discovery tool that discovers valid subdomains for websites"
arch=("x86_64")
url="https://github.com/projectdiscovery/subfinder"
license=("MIT")
provides=('subfinder')
conflicts=('subfinder')
depends=('glibc')
source=("${pkgname}-${pkgver}.zip::${url}/releases/download/v${pkgver}/subfinder_${pkgver}_linux_amd64.zip"
        "https://raw.githubusercontent.com/projectdiscovery/subfinder/v${pkgver}/LICENSE.md")
b2sums=('2e549c77649f8ead33438110f9dd1db7edd40f0c0469a6ebdc20b8574ac0009597c8495a8b54a182a95b17dc9cce36316f3372588cf72e735612071c0ab408fe'
        'c699be7ccfc40564b59bfa217e254c9553678f343466becebad5017d81310d7b7519837a9a25df2e09e16b6e1bd5a209d7aeb039662a206dd8966b9697c02ede')

package() {
        install -Dm644 LICENSE.md "$pkgdir"/usr/share/licenses/$pkgname/LICENSE.md
        install -Dm755 subfinder ${pkgdir}/usr/bin/subfinder
}
