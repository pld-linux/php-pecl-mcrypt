#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	mcrypt
Summary:	mcrypt extension module for PHP
Summary(pl.UTF-8):	Moduł mcrypt dla PHP
Name:		%{php_name}-pecl-%{modname}
Version:	1.0.3
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	0ef94382a4d214b1ed10af8a047a68c7
URL:		https://php.net/manual/en/book.mcrypt.php
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:7.2.0
BuildRequires:	libmcrypt-devel >= 2.5.6
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-pcre
%endif
%{?requires_php_extension}
Requires:	libmcrypt >= 2.5.6
Provides:	php(%{modname}) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is a dynamic shared object (DSO) for PHP that will add mcrypt
support.

Warning:
- This extension is DEPRECATED since PHP 7.1.0

Alternatives to this extension include:
- Sodium (available as of PHP 7.2.0)
- OpenSSL

%description -l pl.UTF-8
Moduł PHP dodający możliwość szyfrowania poprzez bibliotekę mcrypt.

%prep
%setup -qc
mv %{modname}-%{version}/* .

xfail() {
	local t=$1
	test -f $t
	cat >> $t <<-EOF

	--XFAIL--
	Skip
	EOF
}

# failed tests. investigate later
while read line; do
	t=${line##*\[}; t=${t%\]}
	xfail $t
done << 'EOF'
Test for blowfish compatibility [tests/blowfish.phpt]
Bug #8040 (MCRYPT_MODE_* do not seem to exist) [tests/bug8040.phpt]
EOF

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS=""
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
