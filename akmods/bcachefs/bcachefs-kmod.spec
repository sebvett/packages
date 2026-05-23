%define real_name       bcachefs
%define buildforkernels akmod
%global debug_package   %{nil}

# bcachefs requires kernel >= 6.16 (upstream dkms.conf.in BUILD_EXCLUSIVE_KERNEL_MIN).
# All Fedora 44+ kernels satisfy this, but the floor is documented here so
# it stays in sync with upstream when it changes.
%global min_kver        6.16
BuildRequires:          kernel-devel >= %{min_kver}

Name:           %{real_name}-kmod
Version:        1.38.3
Release:        1%{?dist}
Summary:        bcachefs out-of-tree kernel module
License:        GPL-2.0-only
URL:            https://bcachefs.org

# The kernel module source is bundled in bcachefs-tools since 1.31.5.
# The non-vendored tarball is sufficient; we only need the C kernel module
# source (libbcachefs/) and the dkms/ build scaffolding, not the Rust tools.
Source0:        https://evilpiepirate.org/bcachefs-tools/bcachefs-tools-%{version}.tar.zst

BuildRequires:  kmodtool
BuildRequires:  make

# kmodtool generates the akmod-bcachefs subpackage and per-kernel kmod packages
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{real_name} --%{buildforkernels} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null)}

%description
Out-of-tree kernel module for the bcachefs filesystem.

bcachefs is a copy-on-write (COW) filesystem for Linux with support
for multiple devices, RAID, compression, checksumming, encryption,
and snapshots.

As of Linux 6.18 the in-tree version was removed; this package
provides the out-of-tree module built as an akmod so that immutable
Fedora systems (Aurora, Bazzite, Bluefin, Silverblue, Kinoite) can
use bcachefs without DKMS, which is incompatible with rpm-ostree.

%prep
# Abort early if kmodtool failed
%{?kmodtool_check}

# Print kmodtool output for build log debugging
kmodtool --target %{_target_cpu} --kmodname %{real_name} --%{buildforkernels} \
         %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

# Extract source tarball (Fedora 44 RPM supports .tar.zst natively)
%setup -q -n bcachefs-tools-%{version}

# Assemble the kernel module source tree using the upstream install_dkms
# target. This copies libbcachefs/ (the actual kernel source) and the
# dkms/ build scaffolding into a staging directory with the layout that
# kbuild expects: Makefile + src/fs/bcachefs/*.c/*.h
make install_dkms VERSION=%{version} DKMSDIR=$(pwd)/_kmod_staging

# Create a per-kernel copy of the assembled source tree
for kernel_version in %{?kernel_versions}; do
    cp -r _kmod_staging _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
    # The dkms/Makefile at the top of each build dir exports BCACHEFS_DKMS=1
    # and sets obj-m += src/fs/bcachefs/, which is where bcachefs.ko is built.
    make %{?_smp_mflags} \
        -C "${kernel_version##*___}" \
        M="${PWD}/_kmod_build_${kernel_version%%___*}" \
        modules
done

%install
for kernel_version in %{?kernel_versions}; do
    install -d \
        %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
    # BUILT_MODULE_LOCATION from dkms.conf.in is "src/fs/bcachefs"
    find _kmod_build_${kernel_version%%___*}/src/fs/bcachefs \
        -name 'bcachefs.ko' \
        -exec install -m 0755 {} \
            %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ \;
done
%{?akmod_install}

%changelog
* Fri May 23 2026 Sebastian Vetterlein <sebvetterlein@outlook.com> - 1.38.3-1
- Initial packaging of bcachefs akmod for ublue-os
