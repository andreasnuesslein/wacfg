# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3

inherit distutils git

DESCRIPTION="WaCfg is a replacement for webapp-config"
HOMEPAGE=""
EGIT_REPO_URI="git://github.com/nutztherookie/wacfg.git"
EGIT_BRANCH="master"

LICENSE="CDDL"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND=""
RDEPEND="${DEPEND}"


src_unpack() {
	git_src_unpack

}

src_install() {
	distutils_src_install
	dobin bin/wacfg
}
