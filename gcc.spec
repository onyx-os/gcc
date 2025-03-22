Summary: GNU Compiler Collection (C, C++, ...)
Name: gcc
Version: 14.2.0
Release: 1%{?dist}
License: GPL-3.0-or-later
Source0: https://ftp.gnu.org/gnu/%{name}/%{name}-%{version}/%{name}-%{version}.tar.xz
Patch0: https://raw.githubusercontent.com/heatd/toolchains/master/%{name}-%{version}.patch

BuildRequires: make
BuildRequires: mpfr-devel, libmpc-devel, gmp-devel
BuildRequires: binutils

Requires: mpfr, libmpc, gmp
Requires: binutils
# lto-wrapper needs make
Requires: make
Requires: gcc-libs

%description
The gcc package contains the GNU Compiler Collection. You'll need this
package in order to compile C and C++ code (and others).

%package libs
Summary: GCC runtime libraries
Autoreq: true

%description libs
This package contains various GCC runtime libraries, such as libgcc and libstdc++.

You'll almost assuredly want to have this installed in order to run programs.

%prep
%autosetup -p1

%build
%define _configure ../configure
mkdir -p build
cd build
export CFLAGS=$(echo $CFLAGS | sed -e 's/-Werror=format-security/-Wformat-security/g')
export CXXFLAGS=$(echo $CXXFLAGS | sed -e 's/-Werror=format-security/-Wformat-security/g')
%configure --with-sysroot= --enable-languages=c,c++ --disable-nls \
--enable-threads=posix --enable-libstdcxx-threads --enable-shared \
--enable-symvers=gnu --enable-default-pie --enable-lto --enable-default-ssp \
--enable-checking=release --with-bugurl=https://github.com/heatd/toolchains/issues \
--enable-initfini-array --disable-werror

# For some reason you can't do all-gcc and all-target-libgcc at the same time, or the build system
# tries to build all-target-libgcc with an xgcc that doesn't exist (because it wasn't built), weird...
make all-gcc -j4
make all-target-libgcc -j4
make all-target-libstdc++-v3 all-target-libsanitizer -j4

%install
cd build
make DESTDIR="%{?buildroot}" install-gcc install-target-libgcc install-target-libstdc++-v3 install-target-libsanitizer -j4
ln -sf gcc %{buildroot}%{_prefix}/bin/cc
#ln -sf cpp %{buildroot}%{_prefix}/bin/cpp
#ln -sf g++ %{buildroot}%{_prefix}/bin/c++

%files libs
%{_libdir}/libgcc_s.so*
%{_libdir}/libstdc++.so*

%files
%{_libdir}/gcc/
%{_libexecdir}/gcc/
%{_includedir}/c++/%{version}
%{_bindir}/*
%{_infodir}/*.info
%{_mandir}/man1/*
%{_mandir}/man7/*
%{_datadir}/gcc-%{version}/
# TODO: Separate this into gcc-libs-static maybe?
%{_libdir}/*.a
%{_libdir}/lib*san*.*o*
%{_libdir}/libsanitizer.spec
# TODO: libstdc++.so-[...]gdb.py should be owned by this package
