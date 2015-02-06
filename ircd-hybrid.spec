%define name ircd-hybrid
%define version 7.2.3
%define release 10
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
Patch5:		ircd-hybrid-7.2.3-fix-str-fmt.patch
Requires(post,postun):		rpm-helper update-alternatives
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	pkgconfig(openssl)	>= 0.9.7
BuildRequires:	pkgconfig(zlib)
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
%patch5 -p0

# Clear all before start
#rm -rf `find -type d -name autom4te.cache`
#mv -f autoconf/{configure.in,acconfig.h} .

%build
# change dir for other automake
#cp -f %{_datadir}/automake-1.7/config.* autoconf
#%{__aclocal}
#%{__autoconf}

%configure2_5x \
	--enable-zlib \
	--enable-small-net \
	--enable-openssl \
	--disable-assert \
	--with-nicklen=12 \
	--with-maxclients=512 \
	%{?_with_ipv6:--enable-ipv6} \
	%{?_with_efnet:--enable-efnet}
%make

%install
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



%changelog
* Mon Dec 06 2010 Oden Eriksson <oeriksson@mandriva.com> 7.2.3-8mdv2011.0
+ Revision: 612408
- the mass rebuild of 2010.1 packages

* Wed Apr 28 2010 Funda Wang <fwang@mandriva.org> 7.2.3-7mdv2010.1
+ Revision: 539921
- fix str fmt

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

  + Thomas Backlund <tmb@mandriva.org>
    - fix typo in initscript

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 7.2.3-6mdv2009.0
+ Revision: 267127
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

  + Funda Wang <fwang@mandriva.org>
    - fix bug#40445: ircd-hybrid cannot find core modules
    - fix bug#40446: there is no need creating hardlink

* Wed Jan 02 2008 Olivier Blin <oblin@mandriva.com> 7.2.3-4mdv2008.1
+ Revision: 140792
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Aug 27 2007 Funda Wang <fwang@mandriva.org> 7.2.3-4mdv2008.0
+ Revision: 71708
- SILNET: bump release
- add fedora patch to build on x86_64
- Do not need bison and flex
- disable patch2
- Add patch from debian to build using flex and bison
- New version

  + Thierry Vignaud <tv@mandriva.org>
    - kill file require on update-alternatives

* Sun Jun 03 2007 Funda Wang <fwang@mandriva.org> 7.2.2-3mdv2008.0
+ Revision: 34855
- Shoulodn't conflict with itself

* Sat Jun 02 2007 Adam Williamson <awilliamson@mandriva.org> 7.2.2-2mdv2008.0
+ Revision: 34727
- rename manpage to avoid conflict with ircd (makes more sense this way anyway)

* Sun May 27 2007 Funda Wang <fwang@mandriva.org> 7.2.2-1mdv2008.0
+ Revision: 31790
- Add languages
- fix file list
- Don't use autotools
- Rediff patch0
- New version


* Wed Mar 09 2005 Lenny Cartier <lenny@mandrakesoft.com> 7.0.3-2mdk
- from Nenad Markovic <yapi@verat.net> : 
	- correct patch0 (UID and GID stuff)
	- remove/resort unneeded patches
	- fix init script
	- fix dir names

* Fri Feb 25 2005 Nenad Markovic <yapi@verat.net> 7.0.3-1mdk
- initial specfile based on RPM from PLD Team <feedback@pld.org.pl>
- bz2 sources
- build with automake-1.7
- modify init script
- devel package
- EFnet and IPv6 support (optional)

