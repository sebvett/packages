%global real_name bcachefs

Name:           %{real_name}-kmod-common
Version:        1.38.6
Release:        1%{?dist}
Summary:        Common files for bcachefs out-of-tree kernel module
License:        GPL-2.0-only
URL:            https://bcachefs.org
BuildArch:      noarch

Requires:       %{real_name}-kmod = %{?epoch:%{epoch}:}%{version}
Provides:       %{real_name}-kmod-common = %{?epoch:%{epoch}:}%{version}

# dkms-bcachefs ships the same kernel module but uses DKMS, which cannot
# write to /var/lib/dkms on immutable Fedora systems (rpm-ostree/bootc).
# It is auto-pulled via Supplements:(bcachefs-tools and kernel-core) in the
# Fedora package. Declaring a conflict prevents that from happening when
# this akmod is already present.
Conflicts:      dkms-bcachefs

%description
Common package for the bcachefs out-of-tree kernel module.
bcachefs is a copy-on-write filesystem for Linux emphasising
reliability and robustness.

This package ensures the compiled kernel module (bcachefs-kmod)
is installed at a matching version.

As of Linux 6.18, the in-tree bcachefs was removed. This akmod
provides the out-of-tree module for immutable Fedora systems
(Aurora, Bazzite, Bluefin) where DKMS is not usable.

%prep
%build
%install

%files
# No files — this package exists only to pull in bcachefs-kmod

%changelog
* Mon Aug 11 2026 Sebastian Vetterlein <sebvetterlein@outlook.com> - 1.38.6-1
- Update to bcachefs-tools 1.38.6

* Fri May 23 2026 Sebastian Vetterlein <sebvetterlein@outlook.com> - 1.38.3-1
- Initial packaging of bcachefs akmod for ublue-os
