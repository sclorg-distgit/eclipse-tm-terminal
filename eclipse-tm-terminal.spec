%{?scl:%scl_package eclipse-tm-terminal}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

# Set to 1 to build for the first time.  There is a cyclical
# dependency between eclipse-remote and eclipse-tm-terminal.
%global _bootstrap 1
%global git_tag 4.1_neon

Name:           %{?scl_prefix}eclipse-tm-terminal
Version:        4.1.0
Release:        1.%{baserelease}%{?dist}
Summary:        Terminal plugin for Eclipse

License:        EPL
URL:            https://www.eclipse.org/tm/
Source0:        http://git.eclipse.org/c/tm/org.eclipse.tm.terminal.git/snapshot/org.eclipse.tm.terminal-%{git_tag}.tar.xz
BuildArch:      noarch

BuildRequires:  %{?scl_prefix_maven}maven-local
BuildRequires:  %{?scl_prefix}tycho-extras
BuildRequires:  %{?scl_prefix}eclipse-license
BuildRequires:  %{?scl_prefix}eclipse-cdt
BuildRequires: 	%{?scl_prefix}eclipse-egit
%if ! %{_bootstrap}
BuildRequires:  %{?scl_prefix}eclipse-rse
BuildRequires:  %{?scl_prefix}eclipse-remote
%endif

%description
An integrated Eclipse View for the local command prompt (console) or 
remote hosts (SSH, Telnet, Serial).

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n org.eclipse.tm.terminal-%{git_tag}

# When bootstrapping, remote terminal.connector.remote plugins and features
# which require eclipse-remote and create cyclical dependency
%if %{_bootstrap}
%pom_disable_module plugins/org.eclipse.tm.terminal.connector.remote
%pom_disable_module features/org.eclipse.tm.terminal.connector.remote.feature
%pom_disable_module features/org.eclipse.tm.terminal.connector.remote.sdk.feature
%pom_disable_module plugins/org.eclipse.tm.terminal.view.ui.rse
%pom_disable_module features/org.eclipse.tm.terminal.view.rse.feature
%pom_disable_module features/org.eclipse.tm.terminal.view.rse.sdk.feature
%endif

#drop due to gnu.io dep not available
%pom_disable_module plugins/org.eclipse.tm.terminal.connector.serial
%pom_disable_module features/org.eclipse.tm.terminal.connector.serial.feature
%pom_disable_module features/org.eclipse.tm.terminal.connector.serial.sdk.feature
sed -i -e 's|<import feature="org.eclipse.tm.terminal.connector.serial.feature" version="4.1.0" match="greaterOrEqual"/>||g' features/org.eclipse.tm.terminal.feature/feature.xml
sed -i -e 's|<import feature="org.eclipse.tm.terminal.connector.serial.sdk.feature" version="4.1.0" match="greaterOrEqual"/>||g' features/org.eclipse.tm.terminal.sdk.feature/feature.xml
%pom_disable_module repos/org.eclipse.tm.terminal.repo

%pom_xpath_remove "pom:plugin[pom:artifactId[text()='tycho-packaging-plugin']]/pom:configuration" admin/pom-config.xml

sed -i -e "s|feature.properties,\\\|feature.properties|g" features/org.eclipse.tm.terminal.view.feature/build.properties
sed -i -e "s|p2.inf||g" features/org.eclipse.tm.terminal.view.feature/build.properties
timestamp=`date +%Y%m%d%H%M`
for b in `find -name MANIFEST.MF`; do
	sed -i -e "s|qualifier|$timestamp|g" $b
done
for b in `find -name feature.xml`; do
	sed -i -e "s|4.1.0.qualifier|4.1.0.$timestamp|g" $b
done
for b in `find -name pom.xml` admin/pom-build.xml admin/pom-config.xml; do
	sed -i -e "s|qualifier|$timestamp|g" $b
    sed -i -e "s|-SNAPSHOT|.$timestamp|g" $b
done

# No need to install poms
%mvn_package "::pom::" __noinstall
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_build -j
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install
%{?scl:EOF}


%files -f .mfiles

%changelog
* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 4.1.0-1.2
- Perform a bootstrap build

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 4.1.0-1.1
- Auto SCL-ise package for rh-eclipse46 collection

* Fri Jul 01 2016 Mat Booth <mat.booth@redhat.com> - 4.1.0-1
- Update to Neon release

* Thu Mar 03 2016 Sopot Cela <scela@redhat.com> - 4.0.0-6.gitcf7ef3f
- Update for Mars.2 release

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Sep 14 2015 Roland Grunberg <rgrunber@redhat.com> - 4.0.0-4
- Rebuild as an Eclipse p2 Droplet.

* Thu Aug 27 2015 Mat Booth <mat.booth@redhat.com> - 4.0.0-3
- Add bootstrap mode to allow breaking of cyclic dependencies

* Thu Jun 25 2015 Roland Grunberg <rgrunber@redhat.com> - 4.0.0-2
- Rebuild to correct auto-generated requires.

* Wed Jun 24 2015 Alexander Kurtakov <akurtako@redhat.com> 4.0.0-1
- Update to 4.0 final.

* Wed Jun 17 2015 Alexander Kurtakov <akurtako@redhat.com> 4.0.0-0.5.gite58c5d3
- Fix FTBFS - pom/manifest/feature qualifier misalignments.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.0-0.4.gite58c5d3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun 3 2015 Alexander Kurtakov <akurtako@redhat.com> 4.0.0-0.3.gite58c5d3
- New git snapshot.

* Tue Jun 2 2015 Alexander Kurtakov <akurtako@redhat.com> 4.0.0-0.2.git4ea71eb
- Fix review comments.

* Tue Jun 2 2015 Alexander Kurtakov <akurtako@redhat.com> 4.0.0-0.1.git4ea71eb
- Initial packaging
