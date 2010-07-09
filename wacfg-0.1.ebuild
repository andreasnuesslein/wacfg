# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3

inherit distutils git

DESCRIPTION="WaCfg is a replacement for webapp-config"
HOMEPAGE=""
SRC_URI="git://git.noova.de/wacfg.git"

LICENSE="CDDL"
SLOT="0"
KEYWORDS="~amd64 ~x86" 
IUSE="+color"

DEPEND=""
RDEPEND="${DEPEND}
	color? ( dev-python/colorama )"


src_unpack() {
	git_src_unpack

}

src_install() {
	distutils_src_install
}
