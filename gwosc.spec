%define name    gwosc
%define version 0.5.3
%define release 1

Name:      %{name}
Version:   %{version}
Release:   %{release}%{?dist}
Summary:   A python interface to the Gravitational-Wave Open Science Center data archive

License:   MIT
Url:       https://gwosc.readthedocs.io
Source0:   %pypi_source

Packager:  Duncan Macleod <duncan.macleod@ligo.org>
Vendor:    Duncan Macleod <duncan.macleod@ligo.org>

BuildArch: noarch
Prefix:    %{_prefix}

# rpmbuild dependencies
BuildRequires: python-srpm-macros
BuildRequires: python-rpm-macros
BuildRequires: python3-rpm-macros

# build dependencies
BuildRequires: python%{python3_pkgversion}-setuptools

# runtime dependencies (required for %check)
# NONE

# testing dependencies (required for %check)
BuildRequires: python%{python3_pkgversion}-pytest

%description
The `gwosc` package provides an interface to querying the open data
releases hosted on <https://gw-openscience.org> from the GEO, LIGO,
and Virgo gravitational-wave observatories.

# -- python-3X-gwosc

%package -n python%{python3_pkgversion}-%{name}
Summary:  %{summary}
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}
%description -n python%{python3_pkgversion}-%{name}
The `gwosc` package provides an interface to querying the open data
releases hosted on <https://gw-openscience.org> from the GEO, LIGO,
and Virgo gravitational-wave observatories.

# -- build steps

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%check
%{__python3} -m pytest --pyargs %{name} -m "not remote"

%install
%py3_install

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python%{python3_pkgversion}-%{name}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

# -- changelog

%changelog
* Wed Apr 22 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.5.3-1
- update to 0.5.3

* Wed Mar 18 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.5.2-1
- update to 0.5.2

* Tue Mar 17 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.5.1-1
- update to 0.5.1

* Tue Mar 17 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.5.0-1
- drop support for python2

* Tue Mar 12 2019 Duncan Macleod <duncan.macleod@ligo.org> - 0.4.3-1
- bug fix release, see github releases for details

* Mon Mar 11 2019 Duncan Macleod <duncan.macleod@ligo.org> - 0.4.2-1
- bug fix release, see github releases for details

* Thu Feb 28 2019 Duncan Macleod <duncan.macleod@ligo.org> - 0.4.1-1
- development release to include catalogue parsing

* Mon Oct 1 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.3.4 testing bug-fix release

* Mon Jul 9 2018 Duncan Macleod <duncan.macleod@ligo.org>
- 0.3.3 packaging bug-fix release
