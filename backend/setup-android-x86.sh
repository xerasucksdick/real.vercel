#!/bin/bash
set -e

ANDROID_ISO_URL="https://osdn.net/projects/android-x86/downloads/77449/android-x86_64-9.0-r2.iso"
ISO_NAME="android-x86_64-9.0-r2.iso"
QCOW2_IMG="android-x86.qcow2"
DISK_SIZE="8G"

# Download Android-x86 ISO if it doesn't exist
if [ ! -f "$ISO_NAME" ]; then
    echo "Downloading Android-x86 ISO..."
    wget -O "$ISO_NAME" "$ANDROID_ISO_URL"
else
    echo "ISO already downloaded: $ISO_NAME"
fi

# Create QEMU disk image if it doesn't exist
if [ ! -f "$QCOW2_IMG" ]; then
    echo "Creating QEMU disk image..."
    qemu-img create -f qcow2 "$QCOW2_IMG" $DISK_SIZE
else
    echo "QEMU disk image already exists: $QCOW2_IMG"
fi

echo "To install Android-x86, run the following command:"
echo
echo "qemu-system-x86_64 -m 2048 -cdrom $ISO_NAME -hda $QCOW2_IMG -boot d"
echo
echo "This will start the installer. Use your keyboard/mouse to complete the installation."
echo
echo "After install, you can boot Android with:"
echo
echo "qemu-system-x86_64 -m 2048 -enable-kvm -smp cores=2 -hda $QCOW2_IMG -net nic -net user,hostfwd=tcp::5555-:5555 -vnc :0"
echo
