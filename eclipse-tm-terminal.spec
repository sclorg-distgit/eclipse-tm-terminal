%{?scl:%scl_package eclipse-tm-terminal}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

# Set to 1 to build for the first time.  There is a cyclical
# dependency between eclipse-remote and eclipse-tm-terminal.
%global _bootstrap 0

Name:           %{?scl_prefix}eclipse-tm-terminal
Version:        4.0.0
Release:        2.1.bs2%{?dist}
Summary:        Terminal plugin for Eclipse

License:        EPL
URL:            https://www.eclipse.org/tm/
Source0:        http://git.eclipse.org/c/tm/org.eclipse.tm.terminal.git/snapshot/org.eclipse.tm.terminal-%{version}.tar.xz
BuildArch:      noarch

BuildRequires:  %{?scl_prefix_java_common}maven-local
BuildRequires:  %{?scl_prefix}tycho-extras
BuildRequires:  %{?scl_prefix}eclipse-license
BuildRequires:  %{?scl_prefix}eclipse-cdt
BuildRequires:  %{?scl_prefix}eclipse-rse
%if %{_bootstrap} == 0
BuildRequires:  %{?scl_prefix}eclipse-remote
%endif

%description
An integrated Eclipse View for the local command prompt (console) or 
remote hosts (SSH, Telnet, Serial).

%prep

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}

%setup -q -n org.eclipse.tm.terminal-%{version}

# When bootstrapping, remote terminal.connector.remote plugins and features
# which require eclipse-remote and create cyclical dependency
%if %{_bootstrap}
%pom_disable_module plugins/org.eclipse.tm.terminal.connector.remote
%pom_disable_module features/org.eclipse.tm.terminal.connector.remote.feature
%pom_disable_module features/org.eclipse.tm.terminal.connector.remote.sdk.feature
%endif

#drop due to gnu.io dep not available
%pom_disable_module plugins/org.eclipse.tm.terminal.connector.serial
%pom_disable_module features/org.eclipse.tm.terminal.connector.serial.feature
%pom_disable_module features/org.eclipse.tm.terminal.connector.serial.sdk.feature
sed -i -e 's|<import feature="org.eclipse.tm.terminal.connector.serial.feature" version="4.0.0" match="greaterOrEqual"/>||g' features/org.eclipse.tm.terminal.feature/feature.xml
sed -i -e 's|<import feature="org.eclipse.tm.terminal.connector.serial.sdk.feature" version="4.0.0" match="greaterOrEqual"/>||g' features/org.eclipse.tm.terminal.sdk.feature/feature.xml
%pom_disable_module repos/org.eclipse.tm.terminal.repo

%pom_xpath_remove "pom:plugin[pom:artifactId[text()='tycho-packaging-plugin']]/pom:configuration" admin/pom-config.xml

sed -i -e "s|feature.properties,\\\|feature.properties|g" features/org.eclipse.tm.terminal.view.feature/build.properties
sed -i -e "s|p2.inf||g" features/org.eclipse.tm.terminal.view.feature/build.properties
timestamp=`date +%Y%m%d%H%M`
for b in `find -name MANIFEST.MF`; do
	sed -i -e "s|qualifier|$timestamp|g" $b
done
for b in `find -name feature.xml`; do
	sed -i -e "s|4.0.0.qualifier|4.0.0.$timestamp|g" $b
done
for b in `find -name pom.xml`; do
	sed -i -e "s|qualifier|$timestamp|g" $b
    sed -i -e "s|-SNAPSHOT|.$timestamp|g" $b
done
for b in `find -name pom-build.xml`; do
	sed -i -e "s|qualifier|$timestamp|g" $b
    sed -i -e "s|-SNAPSHOT|.$timestamp|g" $b
done
for b in `find -name pom-config.xml`; do
	sed -i -e "s|qualifier|$timestamp|g" $b
    sed -i -e "s|-SNAPSHOT|.$timestamp|g" $b
done

%mvn_package org.eclipse.tm.terminal:terminal-parent __noinstall
%{?scl:EOF}

%build

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}

#%mvn_install admin/pom-config.xml
#%mvn_install admin/pom-build.xml

%mvn_build -j

%{?scl:EOF}

%install

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}

%mvn_install

%{?scl:EOF}

%files -f .mfiles

%changelog
* Fri Jul 17 2015 Mat Booth <mat.booth@redhat.com> - 4.0.0-2.1
- Fix unowned directories

* Mon Jul 13 2015 Jeff Johnston <jjohnstn@redhat.com> - 4.0.0-2
- Put back rse stuff that was erroneously removed.
- Turn off bootstrap and build fully.
- Fix BRs to add eclipse-remote when not bootstrapping.

* Mon Jul 13 2015 Jeff Johnston <jjohnstn@redhat.com> - 4.0.0-1
- Import from Fedora rawhide and SCL-ize.
- Set a bootstrap build to get stuff needed to build eclipse-remote
  which then can be used to build full eclipse-tm-terminal.
