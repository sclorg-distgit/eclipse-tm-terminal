%{?scl:%scl_package eclipse-tm-terminal}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 1

# Set to 1 to build for the first time.  There is a cyclical
# dependency between eclipse-remote and eclipse-tm-terminal.
%global _bootstrap 0

%global git_tag 4.1_neon

Name:           %{?scl_prefix}eclipse-tm-terminal
Version:        4.1.0
Release:        3.%{baserelease}%{?dist}
Summary:        Terminal plug-in for Eclipse

License:        EPL
URL:            https://www.eclipse.org/tm/
Source0:        http://git.eclipse.org/c/tm/org.eclipse.tm.terminal.git/snapshot/org.eclipse.tm.terminal-%{git_tag}.tar.xz
BuildArch:      noarch

BuildRequires:  %{?scl_prefix_maven}maven-local
BuildRequires:  %{?scl_prefix}tycho-extras
BuildRequires:  %{?scl_prefix}eclipse-license
BuildRequires: 	%{?scl_prefix}eclipse-egit
%if ! %{_bootstrap}
# Needed for additional terminal connectors
BuildRequires:  %{?scl_prefix}eclipse-cdt
BuildRequires:  %{?scl_prefix}eclipse-rse
BuildRequires:  %{?scl_prefix}eclipse-remote
%endif

%description
An integrated Eclipse View for the local command prompt (console) or
remote hosts (SSH, Telnet, Serial).

%if ! %{_bootstrap}

%package connectors
Summary:        Additional connectors for Terminal plug-in for Eclipse

%description connectors
An integrated Eclipse View for the local command prompt (console) or
remote hosts (SSH, Telnet, Serial).
%endif

%package sdk
Summary:        Terminal SDK plug-in for Eclipse
Requires:       %{name} = %{version}-%{release}
%if ! %{_bootstrap}
Requires:       %{name}-connectors = %{version}-%{release}
%endif

%description sdk
Sources and developer resources for the Terminal plug-in for Eclipse.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n org.eclipse.tm.terminal-%{git_tag}

# Don't need to build repo
%pom_disable_module repos/org.eclipse.tm.terminal.repo

# When bootstrapping, disable the plugins and features that
# create cyclical dependencies
%if %{_bootstrap}
%pom_disable_module plugins/org.eclipse.tm.terminal.connector.process
%pom_disable_module plugins/org.eclipse.tm.terminal.connector.local
%pom_disable_module features/org.eclipse.tm.terminal.connector.local.feature
%pom_disable_module features/org.eclipse.tm.terminal.connector.local.sdk.feature
%pom_disable_module plugins/org.eclipse.tm.terminal.connector.remote
%pom_disable_module features/org.eclipse.tm.terminal.connector.remote.feature
%pom_disable_module features/org.eclipse.tm.terminal.connector.remote.sdk.feature
%pom_disable_module plugins/org.eclipse.tm.terminal.view.ui.rse
%pom_disable_module features/org.eclipse.tm.terminal.view.rse.feature
%pom_disable_module features/org.eclipse.tm.terminal.view.rse.sdk.feature
%pom_xpath_remove "import[@feature='org.eclipse.tm.terminal.connector.local.feature']" \
  features/org.eclipse.tm.terminal.feature/feature.xml
%pom_xpath_remove "import[@feature='org.eclipse.tm.terminal.connector.local.sdk.feature']" \
  features/org.eclipse.tm.terminal.sdk.feature/feature.xml
%endif

#drop due to gnu.io dep not available
%pom_disable_module plugins/org.eclipse.tm.terminal.connector.serial
%pom_disable_module features/org.eclipse.tm.terminal.connector.serial.feature
%pom_disable_module features/org.eclipse.tm.terminal.connector.serial.sdk.feature
%pom_xpath_remove "import[@feature='org.eclipse.tm.terminal.connector.serial.feature']" \
  features/org.eclipse.tm.terminal.feature/feature.xml
%pom_xpath_remove "import[@feature='org.eclipse.tm.terminal.connector.serial.sdk.feature']" \
  features/org.eclipse.tm.terminal.sdk.feature/feature.xml

%pom_xpath_remove "pom:plugin[pom:artifactId[text()='tycho-packaging-plugin']]/pom:configuration" admin/pom-config.xml

sed -i -e "s|feature.properties,\\\|feature.properties|g" features/org.eclipse.tm.terminal.view.feature/build.properties
sed -i -e "s|p2.inf||g" features/org.eclipse.tm.terminal.view.feature/build.properties

# No need to install poms
%mvn_package "::pom::" __noinstall
%mvn_package "::jar:sources:" sdk
%mvn_package ":*.sdk.feature" sdk
%mvn_package ":org.eclipse.tm.terminal.connector.{local,process,remote}*" connectors
%mvn_package ":org.eclipse.tm.terminal.view.{rse,ui.rse}*" connectors
%mvn_package ":"
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

%if ! %{_bootstrap}

%files connectors -f .mfiles-connectors
%endif

%files sdk -f .mfiles-sdk

%changelog
* Fri Aug 12 2016 Mat Booth <mat.booth@redhat.com> - 4.1.0-3.1
- Auto SCL-ise package for rh-eclipse46 collection

* Fri Aug 12 2016 Mat Booth <mat.booth@redhat.com> - 4.1.0-3
- Split out remote connecter, which requires CDT via PTP Remote

* Fri Aug 12 2016 Mat Booth <mat.booth@redhat.com> - 4.1.0-2
- Improve bootstrapping mode
- Split out local connecter, which requires CDT
- Add a SDK package for source bundles

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