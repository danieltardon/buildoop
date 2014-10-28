# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%define hue_version 3.5.0.produban
%define hue_base_version 3.5.0
%define hue_release openbus0.0.1_1

Name:    hue
Version: %{hue_version}
Release: %{hue_release}
Group: Applications/Engineering
Summary: The hue metapackage
License: ASL 2.0
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id} -u -n)
Source0: hue.git.tar.gz
Source1: %{name}.init
Source2: rpm-build-stage
Source3: install_hue.sh
Patch0: hue-pom-cdh5.0.1.patch 
URL: http://github.com/cloudera/hue
Requires: %{name}-plugins = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
Requires: %{name}-server = %{version}-%{release}
Requires: %{name}-beeswax = %{version}-%{release}
Requires: %{name}-pig = %{version}-%{release}
Requires: %{name}-impala = %{version}-%{release}
Requires: %{name}-hbase = %{version}-%{release}
Requires: %{name}-sqoop = %{version}-%{release}
Requires: %{name}-search = %{version}-%{release}
Requires: %{name}-zookeeper = %{version}-%{release}
Requires: %{name}-rdbms = %{version}-%{release}
Requires: %{name}-spark = %{version}-%{release}

################ RPM CUSTOMIZATION ##############################
# Disable automatic Provides generation - otherwise we will claim to provide all of the
# .so modules that we install inside our private lib directory, which will falsely
# satisfy dependencies for other RPMs on the target system.
AutoProv: no
AutoReqProv: no
%define _use_internal_dependency_generator 0

# Disable post hooks (brp-repack-jars, etc) that just take forever and sometimes cause issues
%define __os_install_post \
    %{!?__debug_package:/usr/lib/rpm/brp-strip %{__strip}} \
%{nil}
%define __jar_repack %{nil}
%define __prelink_undo_cmd %{nil}

# Disable debuginfo package, since we never need to gdb
# our own .sos anyway
%define debug_package %{nil}

# there are some file by-products we don't want to actually package
%define _unpackaged_files_terminate_build 0

# Init.d directory has different locations dependeing on the OS
%if  %{!?suse_version:1}0
%define alternatives_cmd alternatives
%global initd_dir %{_sysconfdir}/rc.d/init.d
%else
%define alternatives_cmd update-alternatives
%global initd_dir %{_sysconfdir}/rc.d
%endif

############### DESKTOP SPECIFIC CONFIGURATION ##################

# customization of install spots
%define hue_dir /usr/lib/hue
%define hadoop_home /usr/lib/hadoop
%define hadoop_lib %{hadoop_home}/lib
%define username hue

%define apps_dir %{hue_dir}/apps
%define about_app_dir %{hue_dir}/apps/about
%define beeswax_app_dir %{hue_dir}/apps/beeswax
%define oozie_app_dir %{hue_dir}/apps/oozie
%define pig_app_dir %{hue_dir}/apps/pig
%define metastore_app_dir %{hue_dir}/apps/metastore
%define filebrowser_app_dir %{hue_dir}/apps/filebrowser
%define help_app_dir %{hue_dir}/apps/help
%define jobbrowser_app_dir %{hue_dir}/apps/jobbrowser
%define jobsub_app_dir %{hue_dir}/apps/jobsub
%define proxy_app_dir %{hue_dir}/apps/proxy
%define useradmin_app_dir %{hue_dir}/apps/useradmin
%define etc_hue /etc/hue/conf 
%define impala_app_dir %{hue_dir}/apps/impala
%define hbase_app_dir %{hue_dir}/apps/hbase
%define sqoop_app_dir %{hue_dir}/apps/sqoop
%define search_app_dir %{hue_dir}/apps/search
%define zookeeper_app_dir %{hue_dir}/apps/zookeeper
%define rdbms_app_dir %{hue_dir}/apps/rdbms
%define spark_app_dir %{hue_dir}/apps/spark

# Path to the HADOOP_HOME to build against - these
# are not substituted into the build products anywhere!
%if ! %{?build_hadoop_home:1} %{!?build_hadoop_home:0}
  %define build_hadoop_home %{hadoop_home}
%endif

# Post macro for apps
%define app_post_macro() \
%post -n %{name}-%1 \
export ROOT=%{hue_dir} \
export DESKTOP_LOGLEVEL=WARN \
export DESKTOP_LOG_DIR=/var/log/hue \
if [ "$1" != 1 ] ; then \
  echo %{hue_dir}/apps/%1 >> %{hue_dir}/.re_register \
fi \
%{hue_dir}/build/env/bin/python %{hue_dir}/tools/app_reg/app_reg.py --install %{apps_dir}/%1 --relative-paths \
chown -R hue:hue /var/log/hue /var/lib/hue

# Preun macro for apps
%define app_preun_macro() \
%preun -n %{name}-%1 \
if [ "$1" = 0 ] ; then \
  export ROOT=%{hue_dir} \
  export DESKTOP_LOGLEVEL=WARN \
  export DESKTOP_LOG_DIR=/var/log/hue \
  if [ -e $ENV_PYTHON ] ; then \
    %{hue_dir}/build/env/bin/python %{hue_dir}/tools/app_reg/app_reg.py --remove %1 ||: \
  fi \
  find %{apps_dir}/%1 -name \*.egg-info -type f -print0 | xargs -0 /bin/rm -fR   \
fi \
find %{apps_dir}/%1 -iname \*.py[co] -type f -print0 | xargs -0 /bin/rm -f \
chown -R hue:hue /var/log/hue /var/lib/hue || :

%description
Hue is a browser-based desktop interface for interacting with Hadoop.
It supports a file browser, job tracker interface, cluster health monitor, and more.

%files -n hue

%clean
%__rm -rf $RPM_BUILD_ROOT

%prep
%setup -n %{name}.git

%patch0 -p1

########################################
# Build
########################################
%build

%if 0%{?rhel:%{rhel}} < 6
# Python 2.5+ is required, but RHEL 5's `python` is 2.4
export SYS_PYTHON=`which python2.6`
export SKIP_PYTHONDEV_CHECK=true
%endif

env FULL_VERSION=%{hue_base_version} bash -x %{SOURCE2}  

########################################
# Install
########################################
%install
bash -x %{SOURCE3} \
	--prefix=$RPM_BUILD_ROOT \
	--build-dir=${PWD}/build/release/prod/hue-%{hue_base_version}

%if  %{?suse_version:1}0
orig_init_file=$RPM_SOURCE_DIR/%{name}.init.suse
%else
orig_init_file=$RPM_SOURCE_DIR/%{name}.init
%endif

# TODO maybe dont need this line anymore:
%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}
cp $orig_init_file $RPM_BUILD_ROOT/%{initd_dir}/hue

#### PLUGINS ######

%package -n %{name}-common
Summary: A browser-based desktop interface for Hadoop
BuildRequires: gcc, gcc-c++
BuildRequires: libxml2-devel, libxslt-devel, zlib-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: openssl
BuildRequires: krb5-devel
Group: Applications/Engineering
Requires: cyrus-sasl-gssapi, libxml2, libxslt, zlib, sqlite
# The only reason we need the following is because we also have AutoProv: no
Conflicts: hue-about, hue-filebrowser, hue-help, hue-jobbrowser, hue-jobsub, hue-metastore, hue-oozie, hue-proxy, hue-shell, hue-useradmin
Provides: config(%{name}-common) = %{version}

%if %{?suse_version:1}0
BuildRequires: sqlite3-devel, openldap2-devel, libmysqlclient-devel, libopenssl-devel, python-devel, python-setuptools
Requires: insserv, python-xml, python
%else
BuildRequires: /sbin/runuser, sqlite-devel, openldap-devel, mysql-devel, openssl-devel
Requires: redhat-lsb
%if 0%{?rhel:%{rhel}} < 6
# Python 2.5+ is required, but RHEL 5's `python` is 2.4
BuildRequires: python26-devel, python26-distribute
Requires: python26
%else
BuildRequires: python-devel, python-setuptools
Requires: python
%endif
%endif

# Disable automatic Provides generation - otherwise we will claim to provide all of the
# .so modules that we install inside our private lib directory, which will falsely
# satisfy dependencies for other RPMs on the target system.
AutoReqProv: no

%description -n %{name}-common
Hue is a browser-based desktop interface for interacting with Hadoop.
It supports a file browser, job tracker interface, cluster health monitor, and more.

########################################
# Preinstall
########################################
%pre -n %{name}-common -p /bin/bash
getent group %{username} 2>/dev/null >/dev/null || /usr/sbin/groupadd -r %{username}
getent passwd %{username} 2>&1 > /dev/null || /usr/sbin/useradd -c "Hue" -s /sbin/nologin -g %{username} -r -d %{hue_dir} %{username} 2> /dev/null || :

########################################
# Postinstall
########################################
%post -n %{name}-common -p /bin/bash

%{alternatives_cmd} --install %{etc_hue} hue-conf %{etc_hue}.empty 30

# If there is an old DB in place, make a backup.
if [ -e %{hue_dir}/desktop/desktop.db ]; then
  echo "Backing up previous version of Hue database..."
  cp -a %{hue_dir}/desktop/desktop.db %{hue_dir}/desktop/desktop.db.rpmsave.$(date +'%Y%m%d.%H%M%S')
fi

%preun -n %{name}-common -p /bin/bash
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove hue-conf %{etc_hue}.empty || :
fi


########################################
# Post-uninstall
########################################
%postun -n %{name}-common -p /bin/bash

if [ -d %{hue_dir} ]; then
  find %{hue_dir} -name \*.py[co] -exec rm -f {} \;
fi

if [ $1 -eq 0 ]; then
  # TODO this seems awfully aggressive
  # NOTE  Despite dependency, hue-common could get removed before the apps are.
  #       We should remove app.reg because apps won't have a chance to
  #       unregister themselves.
  rm -Rf %{hue_dir}/desktop %{hue_dir}/build %{hue_dir}/pids %{hue_dir}/app.reg
fi


%files -n %{name}-common
%defattr(-,root,root)
%attr(0755,root,root) %config(noreplace) %{etc_hue}.empty 
%dir %{hue_dir}
%{hue_dir}/desktop
%{hue_dir}/ext
%{hue_dir}/LICENSE.txt
%{hue_dir}/Makefile
%{hue_dir}/Makefile.buildvars
%{hue_dir}/Makefile.sdk
%{hue_dir}/Makefile.vars
%{hue_dir}/Makefile.vars.priv
%{hue_dir}/README
%{hue_dir}/tools
%{hue_dir}/VERSION
%{hue_dir}/build/env/bin/*
%{hue_dir}/build/env/include/
%{hue_dir}/build/env/lib*/
%{hue_dir}/build/env/stamp
%{hue_dir}/app.reg
%{hue_dir}/apps/Makefile
%dir %{hue_dir}/apps
# Hue core apps
%{about_app_dir}
%{filebrowser_app_dir}
%{help_app_dir}
%{jobbrowser_app_dir}
%{jobsub_app_dir}
%{proxy_app_dir}
%{useradmin_app_dir}
%{metastore_app_dir}
%{oozie_app_dir}
%attr(0755,%{username},%{username}) /var/log/hue
%attr(0755,%{username},%{username}) /var/lib/hue

# beeswax and pig are packaged as a plugin app
%exclude %{beeswax_app_dir}
%exclude %{pig_app_dir}
%exclude %{impala_app_dir}
%exclude %{hbase_app_dir}
%exclude %{sqoop_app_dir}
%exclude %{search_app_dir}
%exclude %{zookeeper_app_dir}
%exclude %{rdbms_app_dir}
%exclude %{spark_app_dir}

############################################################
# No-arch packages - plugins and conf
############################################################

#### Service Scripts ######
%package -n %{name}-server
Summary: Service Scripts for Hue
Requires: %{name}-common = %{version}-%{release}
Requires: /sbin/chkconfig
Group: Applications/Engineering

%description -n %{name}-server

This package provides the service scripts for Hue server.

%files -n %{name}-server
%attr(0755,root,root) %{initd_dir}/hue

# Install and start init scripts

%post -n %{name}-server 
/sbin/chkconfig --add hue

# Documentation
%package -n %{name}-doc
Summary: Documentation for Hue
Group: Documentation

%description -n %{name}-doc
This package provides the installation manual, user guide, SDK documentation, and release notes.

%files -n %{name}-doc
%attr(0755,root,root) /usr/share/doc/hue

########################################
# Pre-uninstall
########################################

%preun  -n %{name}-server 
if [ $1 = 0 ] ; then 
        service %{name} stop > /dev/null 2>&1 
        chkconfig --del %{name} 
fi 
%postun  -n %{name}-server
if [ $1 -ge 1 ]; then 
        service %{name} condrestart >/dev/null 2>&1 
fi

#### PLUGINS ######
%package -n %{name}-plugins
Summary: Hadoop plugins for Hue
Requires: %{name}-common = %{version}-%{release}, hadoop
Group: Applications/Engineering
%description -n %{name}-plugins
Plugins for Hue

This package should be installed on each node in the Hadoop cluster.

%files -n %{name}-plugins
%defattr(-,root,root)
%{hadoop_lib}/

#### HUE-BEESWAX PLUGIN ######
%package -n %{name}-beeswax
Summary: A UI for Hive on Hue
Group: Applications/Engineering
Requires: %{name}-common = %{version}-%{release}, make, cyrus-sasl-plain

%description -n %{name}-beeswax
Beeswax is a web interface for Hive.

It allows users to construct and run queries on Hive, manage tables,
and import and export data.

%app_post_macro beeswax
%app_preun_macro beeswax

%files -n %{name}-beeswax
%defattr(-, %{username}, %{username})
%{beeswax_app_dir}

#### HUE-PIG PLUGIN ######
%package -n %{name}-pig
Summary: A UI for Pig on Hue
Group: Applications/Engineering
Requires: make
Requires: %{name}-common = %{version}-%{release}

%description -n %{name}-pig
A web interface for Pig.

It allows users to construct and run Pig jobs.

%app_post_macro pig
%app_preun_macro pig

%files -n %{name}-pig
%{pig_app_dir}

#### HUE-IMPALA PLUGIN ######
%package -n %{name}-impala
Summary: A UI for Impala on Hue
Group: Applications/Engineering
Requires: make
Requires: %{name}-common = %{version}-%{release}


%description -n %{name}-impala
A web interface for Impala.

It allows users to construct and run queries on Impala, manage tables,
and import and export data.

%app_post_macro impala
%app_preun_macro impala

%files -n %{name}-impala
%defattr(-, %{username}, %{username})
%{impala_app_dir}

#### HUE-HBASE PLUGIN ######
%package -n %{name}-hbase
Summary: A UI for HBase on Hue
Group: Applications/Engineering
Requires: %{name}-common = %{version}-%{release}

%description -n %{name}-hbase
A web interface for HBase.

It allows users to construct and run HBase queries.

%app_post_macro hbase
%app_preun_macro hbase

%files -n %{name}-hbase
%defattr(-, %{username}, %{username})
%{hbase_app_dir}

#### HUE-SQOOP PLUGIN ######
%package -n %{name}-sqoop
Summary: A UI for Sqoop on Hue
Group: Applications/Engineering
Requires: %{name}-common = %{version}-%{release}

%description -n %{name}-sqoop
A web interface for Sqoop.

%app_post_macro sqoop
%app_preun_macro sqoop

%files -n %{name}-sqoop
%defattr(-, %{username}, %{username})
%{sqoop_app_dir}

#### HUE-SEARCH PLUGIN ######
%package -n %{name}-search
Summary: A UI for Search on Hue
Group: Applications/Engineering
Requires: %{name}-common = %{version}-%{release}

%description -n %{name}-search
A web interface for Search.

It allows users to interact with Solr

%app_post_macro search
%app_preun_macro search

%files -n %{name}-search
%defattr(-, %{username}, %{username})
%{search_app_dir}

#### HUE-ZOOKEEPER PLUGIN ######
%package -n %{name}-zookeeper
Summary: A UI for ZooKeeper on Hue
Group: Applications/Engineering
Requires: %{name}-common = %{version}-%{release}

%description -n %{name}-zookeeper
A web interface for ZooKeeper.

%app_post_macro zookeeper
%app_preun_macro zookeeper

%files -n %{name}-zookeeper
%defattr(-, %{username}, %{username})
%{zookeeper_app_dir}

#### HUE-RDBMS PLUGIN ######
%package -n %{name}-rdbms
Summary: A UI for relational databases on Hue
Group: Applications/Engineering
Requires: %{name}-common = %{version}-%{release}

%description -n %{name}-rdbms
A web interface for relational databases

%app_post_macro rdbms
%app_preun_macro rdbms

%files -n %{name}-rdbms
%defattr(-, %{username}, %{username})
%{rdbms_app_dir}

#### HUE-SPARK PLUGIN ######
%package -n %{name}-spark
Summary: A UI for Spark on Hue
Group: Applications/Engineering
Requires: %{name}-common = %{version}-%{release}

%description -n %{name}-spark
A web interface for Spark.

%app_post_macro spark
%app_preun_macro spark

%files -n %{name}-spark
%defattr(-, %{username}, %{username})
%{spark_app_dir}
