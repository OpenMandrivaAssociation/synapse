%undefine _debugsource_packages

# Recreate the vendor archive after a version bump:
#   tar xf synapse-VERSION.tar.gz && cd synapse-VERSION
#   cargo vendor --locked vendor
#   tar cJf rust-vendor.tar.xz vendor
#   abb store synapse-VERSION.tar.gz rust-vendor.tar.xz

Name:		synapse
Version:	1.161.0
Release:	1
Source0:	https://github.com/element-hq/synapse/archive/v%{version}/synapse-%{version}.tar.gz
Source1:	rust-vendor.tar.xz
Source2:	synapse.sysconfig
Source3:	synapse.service
Source4:	synapse-setup
Source5:	homeserver.yaml
Summary:	Server ("homeserver") for the Matrix instant messaging and VoIP system
URL:		https://github.com/element-hq/synapse
License:	AGPL-3.0+
Group:		Servers
BuildSystem:	python
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(maturin)
BuildRequires:	pkgconfig(python)
BuildRequires:	rust
BuildRequires:	cargo
# Postgres is the production database.  sqlite works for a test instance
# (SYNAPSE_DATABASE=sqlite).  The server package is only a Recommend so a
# remote or containerised Postgres is a supported layout.
Requires:	python%{pyver}dist(psycopg2)
Requires:	python%{pyver}dist(systemd-python)
Recommends:	postgresql-server

%patchlist
0001-pyo3-Disable-abi3-feature.patch

%description
Synapse is a reference homeserver for the Matrix instant messaging and
VoIP protocol.

On first start, /usr/libexec/synapse-setup generates homeserver.yaml
from /etc/sysconfig/synapse.  Set SYNAPSE_SERVER_NAME there before
enabling the service.

If SYNAPSE_DATABASE=postgres (the default) and SYNAPSE_PG_HOST is empty,
localhost, or a local unix socket, the setup script creates the
PostgreSQL role and database on the local cluster (which must already
be running).  Any other SYNAPSE_PG_HOST is treated as remote: only the
connection settings are written, the remote server is not touched.

%prep -a
tar xf %{S:1}

mkdir -p .cargo
cat >.cargo/config.toml <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"

[net]
offline = true
EOF

%build -p
export CARGO_HOME=$PWD/.cargo
export CARGO_NET_OFFLINE=true

%install -a
install -p -D -T -m 0644 contrib/systemd/log_config.yaml %{buildroot}%{_sysconfdir}/synapse/log_config.yaml
install -p -D -T -m 0644 %{S:2} %{buildroot}%{_sysconfdir}/sysconfig/synapse
install -p -D -T -m 0644 %{S:3} %{buildroot}%{_unitdir}/synapse.service
install -p -D -T -m 0755 %{S:4} %{buildroot}%{_libexecdir}/synapse-setup
install -p -D -T -m 0644 %{S:5} %{buildroot}%{_docdir}/%{name}/homeserver.yaml.example
install -d -m 0750 %{buildroot}%{_sysconfdir}/synapse/conf.d
install -d -m 0750 %{buildroot}/srv/synapse
install -d -m 0750 %{buildroot}/srv/synapse/media_store
cat >%{buildroot}%{_sysconfdir}/synapse/conf.d/logging.yaml <<'EOF'
# Use the journal handler shipped as /etc/synapse/log_config.yaml
log_config: "/etc/synapse/log_config.yaml"
pid_file: /run/synapse/homeserver.pid
EOF
# %ghost: created on first start by synapse-setup
touch %{buildroot}%{_sysconfdir}/synapse/homeserver.yaml
touch %{buildroot}%{_sysconfdir}/synapse/conf.d/database.yaml

mkdir -p %{buildroot}%{_sysusersdir}
cat >%{buildroot}%{_sysusersdir}/synapse.conf <<'EOF'
u	synapse	-	"The Synapse Matrix homeserver"	/srv/synapse	%{_bindir}/nologin
EOF

%files
%{_docdir}/%{name}/homeserver.yaml.example
%attr(750,synapse,synapse) %dir /srv/synapse
%attr(750,synapse,synapse) %dir /srv/synapse/media_store
%attr(750,synapse,synapse) %dir %{_sysconfdir}/synapse
%attr(750,synapse,synapse) %dir %{_sysconfdir}/synapse/conf.d
%attr(640,synapse,synapse) %config(noreplace) %{_sysconfdir}/synapse/log_config.yaml
%attr(640,synapse,synapse) %config(noreplace) %{_sysconfdir}/synapse/conf.d/logging.yaml
%ghost %config(noreplace) %attr(640,synapse,synapse) %{_sysconfdir}/synapse/homeserver.yaml
%ghost %config(noreplace) %attr(640,synapse,synapse) %{_sysconfdir}/synapse/conf.d/database.yaml
%config(noreplace) %attr(640,root,synapse) %{_sysconfdir}/sysconfig/synapse
%{_libexecdir}/synapse-setup
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
