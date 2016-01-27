Name:           perl
Summary:        The Perl interpreter
License:        Artistic-1.0 or GPL-2.0+
Group:          Platform Development/Perl
Version:        5.20.0
Release:        0
Url:            http://www.perl.org/
Source:         perl-%{version}.tar.bz2
Source1:        %name-rpmlintrc
Source2:        macros.perl
Source3:        README.macros
Source4:        baselibs.conf
Source1001:     perl.manifest
BuildRequires:  db4-devel
BuildRequires:  gdbm-devel
BuildRequires:  bzip2-devel
BuildRequires:  ncurses-devel
BuildRequires:  zlib-devel
#
Provides:       /bin/perl
Provides:       perl-500
Provides:       perl-macros
Provides:       perl(:MODULE_COMPAT_%{version})
Obsoletes:      perl-macros
Provides:       perl-base
Obsoletes:      perl-base
Provides:       perl-Filter-Simple
Provides:       perl-I18N-LangTags
Provides:       perl-MIME-Base64
Provides:       perl-Storable
Provides:       perl-Test-Simple = 0.98-%{release}
Obsoletes:      perl-Filter-Simple
Obsoletes:      perl-I18N-LangTags
Obsoletes:      perl-MIME-Base64
Obsoletes:      perl-Storable
Obsoletes:      perl-Test-Simple < 0.98
Provides:       perl-Text-Balanced
Provides:       perl-Time-HiRes
Provides:       perl-libnet
Obsoletes:      perl-Text-Balanced
Obsoletes:      perl-Time-HiRes
Obsoletes:      perl-libnet
Provides:       perl-Compress-Raw-Zlib
Provides:       perl-Compress-Zlib
Obsoletes:      perl-Compress-Raw-Zlib
Obsoletes:      perl-Compress-Zlib
Provides:       perl-IO-Compress-Base
Provides:       perl-IO-Compress-Zlib
Provides:       perl-IO-Zlib
Obsoletes:      perl-IO-Compress-Base
Obsoletes:      perl-IO-Compress-Zlib
Obsoletes:      perl-IO-Zlib
Provides:       perl-Archive-Tar
Provides:       perl-Module-Build
# 0.39 is smaller than 0.3601, but this is what spec files require
Provides:       perl(Module::Build) = 0.3900
Obsoletes:      perl-Archive-Tar
Obsoletes:      perl-Module-Build
Provides:       perl-Locale-Maketext-Simple
Provides:       perl-Module-Pluggable
Obsoletes:      perl-Locale-Maketext-Simple
Obsoletes:      perl-Module-Pluggable
Provides:       perl-Pod-Escapes
Provides:       perl-Pod-Simple
Obsoletes:      perl-Pod-Escapes
Obsoletes:      perl-Pod-Simple
Provides:       perl-ExtUtils-ParseXS
Provides:       perl-version
Obsoletes:      perl-ExtUtils-ParseXS
Obsoletes:      perl-version

%description
perl - Practical Extraction and Report Language

Perl is optimized for scanning arbitrary text files, extracting
information from those text files, and printing reports based on that
information.  It is also good for many system management tasks. Perl is
intended to be practical (easy to use, efficient, and complete) rather
than beautiful (tiny, elegant, and minimal).

Some of the modules available on CPAN can be found in the "perl"
series.


%package doc
Summary:        Perl Documentation
Group:          Platform Development/Perl
Requires:       perl = %{version}
Provides:       perl:%{_mandir}/man3/CORE.3pm.gz
BuildArch:      noarch

%description doc
Perl man pages and pod files.

%prep
%setup -q -n perl-%{version}
cp %{SOURCE1001} .
cp -p %{S:3} .

%build
RPM_OPT_FLAGS=$(echo $RPM_OPT_FLAGS | sed -e "s/--param=ssp-buffer-size=4//g" )
export RPM_OPT_FLAGS
cp -a lib savelib
export LD_AS_NEEDED=0
export BZIP2_LIB=%{_libdir}
export BZIP2_INCLUDE=%{_includedir}
export BUILD_BZIP2=0
export ldflags="$ldflags -lpthread"
options="-Doptimize='$RPM_OPT_FLAGS -Wall -pipe'"
# always use glibc's setenv
options="$options -Accflags='-DPERL_USE_SAFE_PUTENV'"
options="$options -Dotherlibdirs=/usr/lib/perl5/site_perl"
chmod 755 ./configure.gnu
./configure.gnu --prefix=/usr -Dvendorprefix=/usr -Dinstallusrbinperl -Dusethreads  -Duseshrplib=\'true\' $options
%__make %{?_smp_mflags}
cp -p libperl.so savelibperl.so
cp -p lib/Config.pm saveConfig.pm
cp -p lib/Config_heavy.pl saveConfig_heavy.pl
%__make clean > /dev/null
%__make clobber
rm -rf lib
mv savelib lib
./configure.gnu --prefix=/usr -Dvendorprefix=/usr -Dinstallusrbinperl -Dusethreads  $options
%__make %{?_smp_mflags}


%install
%make_install 
cp -a %{buildroot}/usr/lib/perl5/site_perl %{buildroot}/usr/lib/perl5/vendor_perl
cpa=`echo %{buildroot}/usr/lib/perl5/*/*/CORE | sed -e 's@/CORE$@@'`
cp=`echo "$cpa" | sed -e 's@/[^/]*$@@'`
vpa=`echo $cpa | sed -e 's@/perl5/@/perl5/vendor_perl/@'`
vp=`echo "$vpa" | sed -e 's@/[^/]*$@@'`
install -d $vp/auto
install -d $vpa/auto
install -m 555 savelibperl.so $cpa/CORE/libperl.so
install -m 444 saveConfig.pm $cpa/Config.pm
install -m 444 saveConfig_heavy.pl $cpa/Config_heavy.pl
# install macros.perl file
install -D -m 644 %{S:2} %{buildroot}%{_sysconfdir}/rpm/macros.perl
pushd %{_includedir}
(rpm -ql glibc-devel | fgrep '.h'
    find %{_includedir}/asm/ -name \*.h
    find %{_includedir}/asm-generic -name \*.h
    find %{_includedir}/linux -name \*.h
) | while read f; do
    %{buildroot}%{_bindir}/perl -I$cp -I$cpa %{buildroot}%{_bindir}/h2ph -d $vpa ${f/\/usr\/include\//} || : 
done
popd
d="`gcc -print-file-name=include`"
test -f "$d/stdarg.h" && (cd $d ; %{buildroot}%{_bindir}/perl -I$cp -I$cpa %{buildroot}%{_bindir}/h2ph -d $vpa stdarg.h stddef.h float.h)
# remove broken pm - we don't have the module
rm %{buildroot}/usr/lib/perl5/*/Pod/Perldoc/ToTk.pm
# we don't need this in here
#rm %%{buildroot}/usr/lib/perl5/*/*/CORE/libperl.a
#touch %%{buildroot}%%{_mandir}/man3/perllocal.3pm
#touch $cpa/perllocal.pod
# test CVE-2007-5116
%{buildroot}%{_bindir}/perl -e '$r=chr(128)."\\x{100}";/$r/'
# test perl-regexp-refoverflow.diff
%{buildroot}%{_bindir}/perl -e '/\6666666666/'
cat << EOF > perl-base-filelist
/usr/lib/perl5/%{version}/B/Deparse.pm
/usr/lib/perl5/%{version}/Carp.pm
/usr/lib/perl5/%{version}/Carp/
/usr/lib/perl5/%{version}/Class/
/usr/lib/perl5/%{version}/Config/
/usr/lib/perl5/%{version}/Digest.pm
/usr/lib/perl5/%{version}/Digest/
/usr/lib/perl5/%{version}/Exporter.pm
/usr/lib/perl5/%{version}/Exporter/
/usr/lib/perl5/%{version}/File/
/usr/lib/perl5/%{version}/Getopt/
/usr/lib/perl5/%{version}/IPC/
/usr/lib/perl5/%{version}/Text/
/usr/lib/perl5/%{version}/Tie/Hash.pm
/usr/lib/perl5/%{version}/XSLoader.pm
/usr/lib/perl5/%{version}/warnings.pm
/usr/lib/perl5/%{version}/warnings/
/usr/lib/perl5/%{version}/AutoLoader.pm
/usr/lib/perl5/%{version}/FileHandle.pm
/usr/lib/perl5/%{version}/SelectSaver.pm
/usr/lib/perl5/%{version}/Symbol.pm
/usr/lib/perl5/%{version}/base.pm
/usr/lib/perl5/%{version}/bytes.pm
/usr/lib/perl5/%{version}/bytes_heavy.pl
/usr/lib/perl5/%{version}/constant.pm
/usr/lib/perl5/%{version}/fields.pm
/usr/lib/perl5/%{version}/feature.pm
/usr/lib/perl5/%{version}/integer.pm
/usr/lib/perl5/%{version}/locale.pm
/usr/lib/perl5/%{version}/overload.pm
/usr/lib/perl5/%{version}/overloading.pm
/usr/lib/perl5/%{version}/strict.pm
/usr/lib/perl5/%{version}/unicore/Heavy.pl
/usr/lib/perl5/%{version}/utf8.pm
/usr/lib/perl5/%{version}/utf8_heavy.pl
/usr/lib/perl5/%{version}/vars.pm
/usr/lib/perl5/%{version}/version.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Data/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Digest/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/File/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/List/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Scalar/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/Dir.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/File.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/Handle.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/Pipe.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/Poll.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/Seekable.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/Select.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/Socket.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/IO/Socket/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/B.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Config.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Config_heavy.pl
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Cwd.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/DynaLoader.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Errno.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Fcntl.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/POSIX.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/Socket.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/attributes.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/Data/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/Digest/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/Fcntl/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/File/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/IO/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/List/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/Cwd/
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/Socket/
#/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/POSIX/POSIX.bs
/usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/POSIX/POSIX.so
/usr/lib/perl5/%{version}/*-linux-thread-multi*/lib.pm
/usr/lib/perl5/%{version}/*-linux-thread-multi*/re.pm
EOF

%files -f perl-base-filelist
%manifest %{name}.manifest
%defattr(-,root,root)
%dir /usr/lib/perl5/%{version}/B
%dir /usr/lib/perl5/%{version}/*-linux-thread-multi*/auto/POSIX
%config %{_sysconfdir}/rpm/macros.perl
/usr/lib/perl5/*
%{_bindir}/*

%files doc
%manifest %{name}.manifest
%defattr(-,root,root)
%doc README.macros
%exclude /usr/lib/perl5/*/pod/perldiag.pod
%doc /usr/lib/perl5/*/pod
%doc %{_mandir}/man?/*
