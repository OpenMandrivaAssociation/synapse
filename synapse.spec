%undefine _debugsource_packages

Name:		synapse
Version:	1.116.0
Release:	1
Source0:	https://github.com/element-hq/synapse/archive/v%{version}/synapse-%{version}.tar.gz
Source1:	rust-vendor.tar.xz
Source2:	https://src.fedoraproject.org/rpms/matrix-synapse/raw/rawhide/f/synapse.sysconfig
Source3:	https://src.fedoraproject.org/rpms/matrix-synapse/raw/rawhide/f/synapse.service
Summary:	Server ("homeserver") for the Matrix instant messaging and VoIP system
URL:		https://pypi.org/project/synapse/
License:	AGPL-3.0+
Group:		Servers
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(poetry)
BuildRequires:	python%{pyver}dist(setuptools-rust)
BuildRequires:	rust

%patchlist
https://src.fedoraproject.org/rpms/matrix-synapse/raw/rawhide/f/0001-pyo3-Disable-abi3-feature.patch

%description
Server ("homeserver") for the Matrix instant messaging and VoIP system

%prep
%autosetup -p1 -n synapse-%{version} -a 1
mkdir .cargo
cat >>.cargo/config.toml <<EOF

[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF


%build
%py_build

%install
%py_install

install -p -D -T -m 0644 contrib/systemd/log_config.yaml %{buildroot}%{_sysconfdir}/synapse/log_config.yaml
install -p -D -T -m 0644 %{S:2} %{buildroot}%{_sysconfdir}/sysconfig/synapse
install -p -D -T -m 0644 %{S:3} %{buildroot}%{_unitdir}/synapse.service
install -p -d -m 755 %{buildroot}%{_sharedstatedir}/synapse

mkdir -p %{buildroot}%{_sysusersdir}
cat >%{buildroot}%{_sysusersdir}/synapse.conf <<'EOF'
u	synapse	-	"The Synapse Matrix homeserver"	/run/synapse	%{_bindir}/nologin
EOF

%files
%attr(755,synapse,synapse) %dir %{_sharedstatedir}/synapse
%attr(755,synapse,synapse) %dir %{_sysconfdir}/synapse
%attr(644,synapse,synapse) %config(noreplace) %{_sysconfdir}/synapse/log_config.yaml
%config(noreplace) %attr(644,synapse,synapse) %ghost %{_sysconfdir}/synapse/homeserver.yaml
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
