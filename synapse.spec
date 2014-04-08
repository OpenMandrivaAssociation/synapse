Summary:	A semantic launcher written in Vala
Name:		synapse
Version:	0.2.10
Release:	1
Group:		System/Libraries
License:	GPLv3+
URL:		http://synapse.zeitgeist-project.com/wiki/index.php?title=Main_Page
Source0:	http://launchpad.net/%{name}-project/0.2/%{version}/+download/%{name}-%{version}.tar.gz
# the generated synapse-main.c imports gtkhotkey-1.0/gtkhotkey.h,
# which imports glib-2.0/glib/gquark.h, and this is no longer allowed
# pass -DGLIB_COMPILATION to override (h/t: Mamoru Tasaka)
# https://bugs.launchpad.net/synapse-project/+bug/995354
Patch0:		%{name}-0.2.10-glib.patch
# libsynapsecore.a uses powf (defined in the libm DSO),
# it should be linked with -lm
# https://bugs.launchpad.net/synapse-project/+bug/995356
Patch1:		%{name}-0.2.10-libm-dso-for-powf.patch
Patch2:		concrete-gtk-timeout.patch
BuildRequires:	gettext
BuildRequires:	intltool
BuildRequires:	vala
BuildRequires:	pkgconfig(gee-1.0)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(gtkhotkey-1.0)
BuildRequires:	pkgconfig(json-glib-1.0)
BuildRequires:	pkgconfig(libnotify)
BuildRequires:	pkgconfig(rest-0.7)
BuildRequires:	pkgconfig(unique-1.0)
BuildRequires:	pkgconfig(zeitgeist-1.0)

%description
Synapse is a semantic launcher written in Vala that you can use to start
applications as well as find and access relevant documents and files by making
use of the Zeitgeist engine.

%files -f %{name}.lang
%doc COPYING README
%{_bindir}/synapse
%{_mandir}/man1/synapse.1*
%{_datadir}/applications/synapse.desktop
%{_datadir}/icons/hicolor/scalable/apps/synapse.svg

#----------------------------------------------------------------------------

%package devel
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%files devel
%doc AUTHORS
%{_datadir}/vala/vapi

#----------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p1 -b .glib
%patch1 -p1 -b .libm-dso-for-powf
%patch2 -p1

%build
%configure2_5x \
	--disable-static \
	--enable-zeitgeist=yes
%make V=1

%install
%makeinstall_std
install -d -p -m 755 %{buildroot}%{_datadir}/vala/vapi
install -D -p -m 644 vapi/*.vapi %{buildroot}%{_datadir}/vala/vapi

# language files
%find_lang %{name}

