%define name ircd-hybrid
%define version 7.2.3
%define release %mkrel 7
%define _messagesdir %{_libdir}/ircd-hybrid/messages

# default: Don't build with IPv6 for production server
%define with_IPv6 0
%{?_without_ipv6:	%{expand: %%global with_IPv6 0}}
%{?_with_ipv6:		%{expand: %%global with_IPv6 1}}
# default: Don't build with EFnet support
%define with_EFnet 0
%{?_without_efnet:	%{expand: %%global with_EFnet 0}}
%{?_with_efnet:		%{expand: %%global with_EFnet 1}}

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Internet Relay Chat Server
License:	GPL
Group:		Networking/IRC
URL: 		http://www.ircd-hybrid.org/
Source0:	http://prdownloads.sf.net/ircd-hybrid/%{name}-%{version}.tar.bz2
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Patch0:		%{name}-config.patch
Patch1:		%{name}-opt.patch
Patch3:		%{name}-7.2.3-fix-x86_64-build.patch
Patch4:		%{name}-7.2.3-fix-module-path.patch
Requires(post,postun):		rpm-helper update-alternatives
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	openssl-devel	>= 0.9.7
BuildRequires:	zlib-devel
BuildRequires:	elfutils-devel
# Both have a 
Conflicts:	ircd

%package	devel
Summary:		Development headers for %{name}
Group:			Networking/IRC
Requires:		%{name} = %{version}

%description
Ircd-hybrid is an advanced IRC server which is most commonly used on
the EFNet IRC network. It is fast, reliable, and powerful.
Build time options:
    IPv6 support:	--with ipv6 %{with_IPv6}
    EFnet support:	--with efnet %{with_EFnet}

%description	devel
Development headers and libraries for %{name}

%prep
%setup -q
%patch0 -p1
#%patch1 -p1
#patch2 -p0
%patch3 -p0
%patch4 -p0

# Clear all before start
#rm -rf `find -type d -name autom4te.cache`
#mv -f autoconf/{configure.in,acconfig.h} .

%build
# change dir for other automake
#cp -f %{_datadir}/automake-1.7/config.* autoconf
#%{__aclocal}
#%{__autoconf}

%serverbuild
%configure2_5x \
	--enable-zlib \
	--enable-small-net \
	--enable-openssl \
	--disable-assert \
	--with-nicklen=12 \
	--with-maxclients=512 \
	%{?_with_ipv6:--enable-ipv6} \
	%{?_with_efnet:--enable-efnet}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/ircd-hybrid,%{_var}/{log/ircd-hybrid,run/ircd-hybrid},%{_sysconfdir}/{ircd-hybrid,rc.d/init.d,sysconfig,logrotate.d}} \
	$RPM_BUILD_ROOT{%{_libdir}/ircd-hybrid/{modules{,/autoload},tools,help},%{_sbindir},%{_mandir}/man8,%{_localstatedir}/lib/ircd-hybrid} \
	$RPM_BUILD_ROOT{%{_includedir}/%{name},%{_messagesdir},%{_messagesdir}/{ayb{,/LC_MESSAGES},custom{,/LC_MESSAGES}}}

install src/ircd $RPM_BUILD_ROOT%{_sbindir}/ircd-hybrid
install servlink/servlink $RPM_BUILD_ROOT%{_sbindir}/servlink
install etc/*.conf $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid
# which conf file we need?
%if %{with_EFnet}
	mv $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid/example.efnet.conf $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid/ircd.conf
	rm $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid/{simple.conf,example.conf}
%else
	mv $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid/simple.conf $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid/ircd.conf
	rm $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid/example.efnet.conf
%endif
#mv $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid/convertconf-example.conf $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid/.convertconf-example.conf
#install doc/ircd.motd $RPM_BUILD_ROOT%{_sysconfdir}/ircd-hybrid
install doc/ircd.8 $RPM_BUILD_ROOT%{_mandir}/man8/ircd-hybrid.8
install include/*.h $RPM_BUILD_ROOT%{_includedir}/%{name}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ircd-hybrid
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ircd-hybrid
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/ircd-hybrid

cd modules
	install *.so $RPM_BUILD_ROOT%{_libdir}/ircd-hybrid/modules/autoload
	cd core
		install *.so $RPM_BUILD_ROOT%{_libdir}/ircd-hybrid/modules
	cd ..
cd ..

# make this to have ircservices support
cd contrib
	make ; install *.so $RPM_BUILD_ROOT%{_libdir}/ircd-hybrid/modules
cd ..

cd tools
	for i in encspeed mkkeypair mkpasswd untabify; do
		install $i $RPM_BUILD_ROOT%{_libdir}/ircd-hybrid/tools/$i
	done
cd ..

cd help

cp -rf opers users $RPM_BUILD_ROOT%{_libdir}/ircd-hybrid/help

for link in topic accept cjoin cmode admin names links away whowas \
	version kick who invite quit join list nick oper part \
	time credits motd userhost users whois ison lusers \
	user help pass error challenge knock ping pong; do \
	rm -f $RPM_BUILD_ROOT%{_libdir}/ircd-hybrid/help/users/$link; \
	ln -s %{_libdir}/ircd-hybrid/help/opers/$link $RPM_BUILD_ROOT%{_libdir}/ircd-hybrid/help/users; \
	done
cd ..

cd messages
	install *.lang $RPM_BUILD_ROOT%{_messagesdir}
cd ..

%multiarch_binaries $RPM_BUILD_ROOT%_includedir/%{name}/*.h

%pre
%_pre_useradd ircd-hybrid %{_localstatedir}/lib/ircd-hybrid /bin/false

%post
%_post_service ircd-hybrid
%create_ghostfile /var/log/ircd-hybrid/user.log ircd-hybrid ircd-hybrid 0644
%create_ghostfile /var/log/ircd-hybrid/oper.log ircd-hybrid ircd-hybrid 0644
%create_ghostfile /var/log/ircd-hybrid/foper.log ircd-hybrid ircd-hybrid 0644
update-alternatives --install %{_sbindir}/ircd ircd %{_sbindir}/ircd-hybrid 10

%preun
%_preun_service ircd-hybrid

# remove hardlinks
rm -f %{_libdir}/ircd-hybrid/tools/viklines %{_libdir}/ircd-hybrid/tools/vimotd

%postun
%_postun_userdel ircd-hybrid

update-alternatives --remove ircd %{_sbindir}/ircd-hybrid

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc doc/{*.txt,server-version-info,technical} Hybrid-team LICENSE BUGS RELNOTES TODO
%attr(755,root,root) %{_sbindir}/*
%attr(755,ircd-hybrid,ircd-hybrid) %dir %{_sysconfdir}/ircd-hybrid
#%attr(644,ircd-hybrid,ircd-hybrid) %config(noreplace) %{_sysconfdir}/ircd-hybrid/.convertconf-example.conf
%attr(644,ircd-hybrid,ircd-hybrid) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ircd-hybrid/*
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/ircd-hybrid
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/ircd-hybrid
%attr(755,root,root) /etc/rc.d/init.d/ircd-hybrid
%dir %{_libdir}/ircd-hybrid
%dir %{_libdir}/ircd-hybrid/modules
%dir %{_libdir}/ircd-hybrid/tools
%dir %{_libdir}/ircd-hybrid/help
%dir %{_messagesdir}
%{_messagesdir}/*
%attr(755,ircd-hybrid,ircd-hybrid) %dir %{_localstatedir}/lib/ircd-hybrid
%attr(755,root,root) %{_libdir}/ircd-hybrid/modules/*
%attr(755,root,root) %{_libdir}/ircd-hybrid/tools/*
%attr(755,root,root) %{_libdir}/ircd-hybrid/help/*
%attr(755,ircd-hybrid,ircd-hybrid) %dir %{_var}/log/ircd-hybrid
%attr(755,ircd-hybrid,ircd-hybrid) %dir %{_var}/run/ircd-hybrid
%{_mandir}/man*/*

# devel
%files devel
%defattr(644,root,root,755)
%{_includedir}/%{name}
%doc ChangeLog

