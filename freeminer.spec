Name:           freeminer
Version:        0.4.13.7
Release:        1%{?dist}
Summary:        Open source sandbox game inspired by Minecraft

License:        LGPLv2+ and CC-BY-SA and MIT
URL:            http://freeminer.org/
Source0:        https://github.com/freeminer/%{name}/archive/%{version}/%{name}-%{version}.zip
Source1:        %{name}@.service
Source2:        https://github.com/freeminer/default/archive/%{version}/%{name}_default-%{version}.tar.gz
Source3:        default.conf

#https://github.com/freeminer/freeminer/issues/103
Patch0:         cguittfont.patch
Patch1:         add_library_STATIC.patch

BuildRequires:  cmake
BuildRequires:  irrlicht-devel
BuildRequires:  bzip2-devel gettext-devel sqlite-devel
BuildRequires:  libpng-devel libjpeg-turbo-devel libXxf86vm mesa-libGL-devel
BuildRequires:  desktop-file-utils
BuildRequires:  systemd
BuildRequires:  openal-soft-devel
BuildRequires:  libvorbis-devel
BuildRequires:  libcurl-devel
BuildRequires:  luajit-devel
BuildRequires:  freetype-devel
BuildRequires:  leveldb-devel
BuildRequires:  snappy-devel

Requires:       %{name}-server = %{version}-%{release}

%description
Game of mining, crafting and building in the infinite world of cubic
blocks with optional hostile creatures, features both single and the
network multiplayer mode. There are no in-game sounds yet

%package server
Summary: freeminer multiplayer server

Requires(pre):    shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description server
freeminer multiplayer server. This package does not require X Window System

%prep
%setup -q
%patch0 -p1
%patch1 -p1

#pushd games
#  tar xf %{SOURCE2}
#  mv default-%{version}/* default/
#popd

rm -rf src/lua
# purge bundled jsoncpp
#rm -rf src/json

%build
pushd build
  %cmake ../ -DRUN_IN_PLACE=0
  make %{?_smp_mflags}
popd

%install
pushd build
  %make_install
popd

install -d -m 0755 %{buildroot}%{_sharedstatedir}/%{name}

# Systemd unit file
mkdir -p %{buildroot}%{_unitdir}
cp -p %{SOURCE1} %{buildroot}%{_unitdir}

install -d -m 0775 %{buildroot}%{_sysconfdir}/%{name}/
install    -m 0775 %{name}.conf.example %{buildroot}%{_sysconfdir}/%{name}/default.conf
install -d -m 0775 %{buildroot}%{_sharedstatedir}/%{name}/

install -d -m 0775 %{buildroot}%{_sysconfdir}/sysconfig/%{name}/
install    -m 0664 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

rm %{buildroot}%{_pkgdocdir}/*

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/appdata/%{name}.appdata.xml

%pre server
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_sharedstatedir}/%{name}/ -s /sbin/nologin \
    -c "Freeminer multiplayer server" %{name}

%post server
%systemd_post %{name}@default.service

%preun server
%systemd_preun %{name}@default.service

%postun server
%systemd_postun_with_restart %{name}@default.service

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_mandir}/man6/%{name}.6.*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%files server
%doc LICENSE.txt src/jthread/LICENSE.MIT README.md doc/lua_api.txt
%{_sysconfdir}/%{name}/
%{_bindir}/%{name}server
%{_mandir}/man6/%{name}server.6.*
%{_unitdir}/%{name}@.service

%attr(-,%{name},%{name})%{_sharedstatedir}/%{name}/
%attr(-,%{name},%{name})%{_sysconfdir}/sysconfig/%{name}/

%changelog
* Mon Jul 14 2014  Vladimir Karandin  <konstantinjch@mail.ru> - 0.4.9.3-1
- Initial package

*Mon Jan 03 2016 Vladimir Karandin  <konstantinjch@mail.ru> - 0.4.13.7
- Update 
