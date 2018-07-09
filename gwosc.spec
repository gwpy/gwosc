%define name    gwosc
%define version 0.3.1
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
BuildRequires: rpm-build
BuildRequires: python-rpm-macros
BuildRequires: python3-rpm-macros
BuildRequires: python-setuptools
BuildRequires: python%{python3_pkgversion}-setuptools

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

%package -n python%{python3_pkgversion}-%{name}
Summary:  %{summary}
Requires: python%{python3_pkgversion}-six
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}
%description -n python%{python3_pkgversion}-%{name}
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
%{__python2} -m pytest --pyargs %{name}
%{__python3} -m pytest --pyargs %{name}

%install
%py2_install
%py3_install

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python2-%{name}
%license LICENSE
%doc README.md
%{python2_sitelib}/*

%files -n python%{python3_pkgversion}-%{name}
%license LICENSE
%doc README.md
%{python3_sitelib}/*
