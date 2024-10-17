# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'
%define with_maven 0

%define section   free
%define base_name commons-configuration

Name:           jakarta-commons-configuration
Version:        1.5
Release:        %mkrel 3.0.4
Epoch:          0
Summary:        Commons Configuration Package

Group:          Development/Java
License:        Apache Software License 2.0
URL:            https://commons.apache.org/configuration/
Source0:        http://www.apache.org/dist/commons/configuration/source/%{base_name}-%{version}-src.tar.gz
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        %{base_name}-%{version}-jpp-depmap.xml
Patch0:         disable_test.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRequires:  java-rpmbuild
BuildRequires:  jpackage-utils >= 0:1.7.2
BuildRequires:  junit
#BuildRequires:  junit-addons
BuildRequires:  ant >= 0:1.6
%if %{with_maven}
BuildRequires:  maven2 
%endif
#BuildRequires:  dbunit
BuildRequires:  hsqldb
#BuildRequires:  mockobjects
#BuildRequires:  mockobjects-jdk1.4-j2ee1.4
BuildRequires:  xalan-j2
#
BuildRequires:  jakarta-commons-beanutils >= 0:1.7.0
BuildRequires:  jakarta-commons-codec
BuildRequires:  jakarta-commons-collections
BuildRequires:  jakarta-commons-dbcp
BuildRequires:  jakarta-commons-digester
BuildRequires:  jakarta-commons-jxpath
BuildRequires:  jakarta-commons-lang
BuildRequires:  jakarta-commons-logging
BuildRequires:  jakarta-commons-pool
BuildRequires:  servletapi5
BuildRequires:  xerces-j2
BuildRequires:  xml-commons-apis 
Requires:  jakarta-commons-beanutils >= 0:1.7.0
Requires:  jakarta-commons-codec
Requires:  jakarta-commons-collections
Requires:  jakarta-commons-dbcp
Requires:  jakarta-commons-digester
Requires:  jakarta-commons-jxpath
Requires:  jakarta-commons-lang
Requires:  jakarta-commons-logging
Requires:  jakarta-commons-pool
Requires:  servletapi5
Requires:  xerces-j2
Requires:  xml-commons-apis 
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif

%description
Configuration is a project to provide a generic Configuration 
interface and allow the source of the values to vary. It 
provides easy typed access to single, as well as lists of 
configuration values based on a 'key'. 

Right now you can load properties from a simple properties 
file, a properties file in a jar, an XML file, JNDI settings, 
as well as use a mix different sources using a 
ConfigurationFactory and CompositeConfiguration. 
Custom configuration objects are very easy to create now 
by just subclassing AbstractConfiguration. This works 
similar to how AbstractList works.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description    javadoc
Javadoc for %{name}


%prep
%setup -q -n %{base_name}-%{version}-src
%remove_java_binaries
%patch0 -b .sav
if [ ! -f %{SOURCE4} ]; then
export DEPCAT=$(pwd)/%{base_name}-%{version}-depcat.new.xml
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    /usr/bin/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
/usr/bin/saxon $DEPCAT %{SOURCE2} > %{base_name}-%{version}-depmap.new.xml
fi
sed -i -e "s/manifest\.mf/MANIFEST\.MF/g" build.xml

%build
%if %{with_maven}
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mkdir external_repo
ln -s %{_javadir} external_repo/JPP

mvn-jpp \
        -e \
        -s $(pwd)/settings.xml \
        -Dmaven2.jpp.mode=true \
        -Dmaven.test.skip=true \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        install site
%else
export CLASSPATH=$(build-classpath \
servletapi5 \
commons-beanutils \
commons-codec \
commons-collections \
commons-dbcp \
commons-digester \
commons-jxpath \
commons-lang \
commons-logging \
commons-pool \
hsqldb \
):target/classes:target/test-classes:target/conf
%ant -Dbuild.sysclasspath=only jar javadoc
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -Dpm 644 target/%{base_name}-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
ln -s %{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar
ln -s %{name}-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{base_name}-%{version}.jar
ln -s %{base_name}-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{base_name}.jar
install -dm 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%if %{with_maven}
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%else
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%endif
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} 
%{gcj_compile}

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}
%endif

%if %{gcj_support}
%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root,-)
%doc LICENSE.txt
%{_javadir}/*.jar
%{gcj_files}

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}
