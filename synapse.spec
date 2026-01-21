%undefine _debugsource_packages

Name:		synapse
Version:	1.145.0
Release:	1
Source0:	https://github.com/element-hq/synapse/archive/v%{version}/synapse-%{version}.tar.gz
Source1:	rust-vendor.tar.xz
Source2:	https://src.fedoraproject.org/rpms/matrix-synapse/raw/rawhide/f/synapse.sysconfig
Source3:	https://src.fedoraproject.org/rpms/matrix-synapse/raw/rawhide/f/synapse.service
Source4:	homeserver.yaml
Summary:	Server ("homeserver") for the Matrix instant messaging and VoIP system
URL:		https://github.com/element-hq/synapse
License:	AGPL-3.0+
Group:		Servers
BuildSystem:	python
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(poetry)
BuildRequires:	python%{pyver}dist(setuptools-rust)
BuildRequires:	rust
#Requires:	python%{pyver}dist(psycopg2)
#Requires(post): postgresql-server

%patchlist
https://src.fedoraproject.org/rpms/matrix-synapse/raw/rawhide/f/0001-pyo3-Disable-abi3-feature.patch

%description
Server ("homeserver") for the Matrix instant messaging and VoIP system

%prep -a
tar xf %{S:1}

mkdir .cargo
cat >>.cargo/config.toml <<EOF

[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%install -a
install -p -D -T -m 0644 contrib/systemd/log_config.yaml %{buildroot}%{_sysconfdir}/synapse/log_config.yaml
install -p -D -T -m 0644 %{S:2} %{buildroot}%{_sysconfdir}/sysconfig/synapse
install -p -D -T -m 0644 %{S:3} %{buildroot}%{_unitdir}/synapse.service
install -p -D -T -m 0644 %{S:4} %{buildroot}%{_sysconfdir}/synapse/homeserver.yaml
install -p -d -m 755 %{buildroot}%{_sharedstatedir}/lib/synapse

mkdir -p %{buildroot}/srv/synapse/media_store

mkdir -p %{buildroot}%{_sysusersdir}
cat >%{buildroot}%{_sysusersdir}/synapse.conf <<'EOF'
u	synapse	-	"The Synapse Matrix homeserver"	/run/synapse	%{_bindir}/nologin
EOF

%files
%attr(755,synapse,synapse) %dir %{_sharedstatedir}/lib/synapse
%attr(755,synapse,synapse) %dir %{_sysconfdir}/synapse
%attr(644,synapse,synapse) %config(noreplace) %{_sysconfdir}/synapse/log_config.yaml
%config(noreplace) %attr(644,synapse,synapse) %{_sysconfdir}/synapse/homeserver.yaml
%config(noreplace) %attr(644,synapse,synapse) %ghost %{_sysconfdir}/synapse/matrix.signing.key
%config(noreplace) %attr(644,synapse,synapse) %{_sysconfdir}/sysconfig/synapse
%{_bindir}/export_signing_key
%{_bindir}/generate_config
%{_bindir}/generate_log_config
%{_bindir}/generate_signing_key
%{_bindir}/hash_password
%{_bindir}/register_new_matrix_user
%{_bindir}/synapse_homeserver
%{_bindir}/synapse_port_db
%{_bindir}/synapse_review_recent_signups
%{_bindir}/synapse_worker
%{_bindir}/synctl
%{_bindir}/update_synapse_database
%{python_sitearch}/synapse
%{python_sitearch}/matrix_synapse-*.dist-info
%{_sysusersdir}/synapse.conf
%{_unitdir}/synapse.service
/srv/synapse/media_store

# NOT YET -- need to figure out a way to do this right (also allowing for
# the use case of the postgres server running on a different host or in
# a different container
#post
#if [ -e %{_localstatedir}/lib/pgsql/data/postmaster.pid" ]; then
#	su - postgres -c "createuser matrix"
#	su - postgres -c "createdb -l C --lc-collate=C --lc-ctype=C -O matrix -T template0 matrix"
#else
#	if ! su - postgres -c "echo |postgres --single -D %{_localstatedir}/lib/pgsql/data matrix"; then
#		su - postgres -c "postgres --single -D %{_localstatedir}/lib/pgsql/data" <<EOF
#CREATE USER matrix;
#CREATE DATABASE matrix WITH OWNER='matrix' TEMPLATE='template0' LOCALE='C' LC_COLLATE='C' LC_CTYPE='C';
#EOF
#	fi
#fi
