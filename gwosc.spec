%define name    gwosc
%define version 0.4.2
%define release 2

Name:      %{name}
Version:   %{version}
Release:   %{release}%{?dist}
Summary:   A python interface to the Gravitational-Wave Open Science Center data archive

License:   GPLv3
Url:       https://pypi.org/project/%{name}/
Source0:   https://pypi.io/packages/source/g/%{name}/%{name}-%{version}.tar.gz

Vendor:    Duncan Macleod <duncan.macleod@ligo.org>

BuildArch: noarch

# rpmbuild dependencies
BuildRequires: rpm-build
BuildRequires: python-srpm-macros
BuildRequires: python-rpm-macros
BuildRequires: python3-rpm-macros

# build dependencies
BuildRequires: python-setuptools
BuildRequires: python%{python3_pkgversion}-setuptools

# runtime dependencies (required for %check)
# NONE

# testing dependencies (required for %check)
BuildRequires: python%{python3_pkgversion}-pytest

%description
The `gwosc` package provides an interface to querying the open data
releases hosted on <https://losc.ligo.org> from the LIGO and Virgo
gravitational-wave observatories.

# -- python-3X-gwosc

%package -n python%{python3_pkgversion}-%{name}
Summary:  %{summary}
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}
%description -n python%{python3_pkgversion}-%{name}
The `gwosc` package provides an interface to querying the open data
releases hosted on <https://losc.ligo.org> from the LIGO and Virgo
gravitational-wave observatories.

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
