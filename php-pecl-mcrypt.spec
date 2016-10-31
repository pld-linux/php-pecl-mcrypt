#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	mcrypt
Summary:	mcrypt extension module for PHP
Summary(pl.UTF-8):	Moduł mcrypt dla PHP
Name:		%{php_name}-pecl-%{modname}
# version taken from package.xml, .c source has NO_VERSION_YET macro
Version:	0.0.0
Release:	0.1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://git.php.net/?p=pecl/.../mcrypt.git;a=snapshot;h=...;sf=tgz;/php-pecl-%{modname}-%{version}.tar.gz
# Source0-md5:	-
URL:		http://php.net/manual/en/book.mcrypt.php
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:7.1.0
BuildRequires:	libmcrypt-devel >= 2.5.6
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-pcre
%endif
%{?requires_php_extension}
Provides:	php(%{modname}) = %{version}
Requires:	libmcrypt >= 2.5.6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is a dynamic shared object (DSO) for PHP that will add mcrypt
support.

%description -l pl.UTF-8
Moduł PHP dodający możliwość szyfrowania poprzez bibliotekę mcrypt.

%prep
%setup -qc
mv %{modname}-%{version}/* .

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{php_extensiondir}/spl.so \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="spl" \
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

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

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
%doc CREDITS TODO
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
%{_examplesdir}/%{name}-%{version}
