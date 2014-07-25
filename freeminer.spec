Name:           freeminer
Version:        0.4.9.3
Release:        2%{?dist}
Summary:        Freeminer is an open source sandbox game inspired by [Minecraft](https://minecraft.net/)

License:        LGPLv2+ and CC-BY-SA and MIT
URL:            http://freeminer.org/
Source0:        https://github.com/freeminer/%{name}/archive/%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}@.service


# https://github.com/minetest/minetest/pull/954
Patch0:         0001-FindJson.cmake-now-will-correctly-find-system-module.patch
Patch1:         cguittfont.patch

BuildRequires:  cmake 
BuildRequires:  irrlicht-devel
BuildRequires:  bzip2-devel gettext-devel sqlite-devel
BuildRequires:  libpng-devel libjpeg-turbo-devel libXxf86vm mesa-libGL-devel
BuildRequires:  desktop-file-utils
BuildRequires:  systemd
BuildRequires:  openal-soft-devel
BuildRequires:  libvorbis-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  libcurl-devel
BuildRequires:  luajit-devel  


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

# purge bundled jsoncpp and lua
rm -rf src/lua src/json

%build
pushd build
  %cmake ../ -DDEBUG:BOOL=TRUE
  make  %{?_smp_mflags}  
popd

%install
pushd build
  %make_install
popd

install -Dpm 0644 doc/%{name}.6 %{buildroot}%{_prefix}/man/man6/%{name}.6
install -d -m 0755 %{buildroot}%{_sharedstatedir}/%{name}


# Systemd unit file
mkdir -p %{buildroot}%{_unitdir}
cp -p %{SOURCE1} %{buildroot}%{_unitdir}

install -d -m 0775 %{buildroot}%{_sysconfdir}/%{name}/
install    -m 0775 %{name}.conf.example %{buildroot}%{_sysconfdir}/%{name}/default.conf
install -d -m 0775 %{buildroot}%{_sharedstatedir}/%{name}/

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_sharedstatedir}/%{name}/ -s /sbin/nologin \
    -c "Freeminer multiplayer server" %{name}
exit 0


%post server

%systemd_post %{name}@default.service

%preun server

%systemd_preun %{name}@default.service

%postun server
 
%systemd_postun_with_restart %{name}@default.service

%files 

%doc   LICENSE.txt src/jthread/LICENSE.MIT README.md doc/lua_api.txt 
#README.md doc/lua_api.txt

%{_bindir}/%{name}
%{_mandir}/man6/%{name}.6.gz
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/%{name}/



%files server
%{_sharedstatedir}/%{name}/
%{_sysconfdir}/%{name}/
%{_bindir}/%{name}server
%{_mandir}/man6/%{name}server.*
%{_unitdir}/%{name}@.service


%changelog

* Mon Jul 25 2014  Vladimir Karandin  <konstantinjch@mail.ru> - 0.4.9.3-2
- mega-update spec

* Mon Jul 14 2014  Vladimir Karandin  <konstantinjch@mail.ru> - 0.4.9.3-1
- Initial release
