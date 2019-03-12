%define name    gwosc
%define version 0.4.2
%define release 1

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
BuildRequires: python-rpm-macros
BuildRequires: python2-rpm-macros
BuildRequires: python3-rpm-macros

# build dependencies
BuildRequires: python-setuptools
BuildRequires: python%{python3_version_nodots}-setuptools

# runtime dependencies (required for %check)
BuildRequires: python2-six
BuildRequires: python%{python3_version_nodots}-six

# testing dependencies (required for %check)
BuildRequires: python2-pytest
BuildRequires: python%{python3_version_nodots}-pytest
BuildRequires: python2-mock

%description
The `gwosc` package provides an interface to querying the open data
releases hosted on <https://losc.ligo.org> from the LIGO and Virgo
gravitational-wave observatories.

# -- python2-ligotimegps

%package -n python2-%{name}
Summary:  %{summary}
Requires: python-six
%{?python_provide:%python_provide python2-%{name}}
%description -n python2-%{name}
The `gwosc` package provides an interface to querying the open data
releases hosted on <https://losc.ligo.org> from the LIGO and Virgo
gravitational-wave observatories.

# -- python-3X-ligotimegps

%package -n python%{python3_version_nodots}-%{name}
Summary:  %{summary}
Requires: python%{python3_version_nodots}-six
%{?python_provide:%python_provide python%{python3_version_nodots}-%{name}}
%description -n python%{python3_version_nodots}-%{name}
The `gwosc` package provides an interface to querying the open data
releases hosted on <https://losc.ligo.org> from the LIGO and Virgo
gravitational-wave observatories.

# -- build steps

%prep
%autosetup -n %{name}-%{version}

%build
%py2_build
%py3_build

%check
%{__python2} -m pytest --pyargs %{name} -m "not remote"
%{__python3} -m pytest --pyargs %{name} -m "not remote"

%install
%py2_install
%py3_install

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python2-%{name}
%license LICENSE
%doc README.md
%{python2_sitelib}/*

%files -n python%{python3_version_nodots}-%{name}
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
