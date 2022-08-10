# zcu111-quel-app

## Build ZCU111-app

The following example is building `waveform-manage`.

Make a symbolic link to the target resources in the petalinux-app directory.

```
$ cd ${DCET_HOME}/apu/rfsoc_petalinux_bsp/project-spec/meta-user/recipes-apps
$ ln -s ${REPOSITORY_ROOT}/waveform-manage .
```

After that, add an entry to build the target.

```
$ cd ${DCET_HOME}/apu/rfsoc_petalinux_bsp/project-spec/meta-user/conf
$ echo "CONFIG_waveform-manage" >> user-rootfsconfig
```

And finally, build the rootfs with the target application binary.

```
$ cd ${DCET_HOME}/apu/rfsoc_petalinux_bsp
$ petalinux-build
```
