# zcu111-quel-app

## Pre-requirements

- Vivado 2021.1
- Petalinux 2021.1
- rdf0476-zcu111-rf-dc-eval-tool-2021-2
  - Note that, the extracted directory name is `rdf0476-zcu111-rf-dc-eval-tool-2021-1`.
  - The extracted directory path will be defined as ${DCET_HOME} bellow.

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
