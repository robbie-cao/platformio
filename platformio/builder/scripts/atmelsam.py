# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    Builder for Atmel SAM series of microcontrollers
"""

from os.path import basename, join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                          DefaultEnvironment, SConscript)

from platformio.util import get_serialports


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()

    board_type = env.subst("$BOARD")
    if "zero" not in board_type:
        env.Append(
            UPLOADERFLAGS=[
                "-U",
                "true" if ("usb" in board_type.lower(
                ) or board_type == "digix") else "false"
            ])

    upload_options = env.get("BOARD_OPTIONS", {}).get("upload", {})

    if not upload_options.get("disable_flushing", False):
        env.FlushSerialBuffer("$UPLOAD_PORT")

    before_ports = [i['port'] for i in get_serialports()]

    if upload_options.get("use_1200bps_touch", False):
        env.TouchSerialPort("$UPLOAD_PORT", 1200)

    if upload_options.get("wait_for_upload_port", False):
        env.Replace(UPLOAD_PORT=env.WaitForNewSerialPort(before_ports))

    # use only port name for BOSSA
    if "/" in env.subst("$UPLOAD_PORT"):
        env.Replace(UPLOAD_PORT=basename(env.subst("$UPLOAD_PORT")))


env = DefaultEnvironment()

SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))

if env.subst("$BOARD") == "zero":
    env.Replace(
        UPLOADER=join("$PIOPACKAGES_DIR", "tool-openocd", "bin", "openocd"),
        UPLOADERFLAGS=[
            "-d2",
            "-s",
            join(
                "$PIOPACKAGES_DIR",
                "tool-openocd", "share", "openocd", "scripts"),
            "-f",
            join(
                "$PLATFORMFW_DIR", "variants",
                "${BOARD_OPTIONS['build']['variant']}", "openocd_scripts",
                "${BOARD_OPTIONS['build']['variant']}.cfg"
            ),
            "-c", "\"telnet_port", "disabled;",
            "program", "{{$SOURCES}}",
            "verify", "reset", "0x00002000;", "shutdown\""
        ],
        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS'
    )
else:
    env.Replace(
        UPLOADER=join("$PIOPACKAGES_DIR", "$PIOPACKAGE_UPLOADER", "bossac"),
        UPLOADERFLAGS=[
            "--info",
            "--port", "$UPLOAD_PORT",
            "--erase",
            "--write",
            "--verify",
            "--reset",
            "--debug"
        ],
        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS $SOURCES'
    )

env.Append(

    CCFLAGS=[
        "--param", "max-inline-insns-single=500",
        "-MMD"
    ],

    CFLAGS=[
        "-std=gnu11"
    ],

    CXXFLAGS=[
        "-std=gnu++11",
        "-fno-threadsafe-statics"
    ],

    CPPDEFINES=[
        "USBCON",
        'USB_MANUFACTURER="PlatformIO"'
    ],

    LINKFLAGS=[
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align"
    ]
)


if "sam3x8e" in env.get("BOARD_OPTIONS", {}).get("build", {}).get("mcu", None):
    env.Append(
        CPPDEFINES=[
            "printf=iprintf"
        ],

        LINKFLAGS=[
            "-Wl,--entry=Reset_Handler",
            "-Wl,--start-group"
        ],

        UPLOADERFLAGS=[
            "--boot",
        ]

    )
elif "zero" in env.subst("$BOARD"):
    env.Append(
        LINKFLAGS=[
            "--specs=nosys.specs",
            "--specs=nano.specs"
        ]
    )

#
# Target: Build executable and linkable firmware
#

target_elf = env.BuildProgram()

#
# Target: Build the .bin file
#

if "uploadlazy" in COMMAND_LINE_TARGETS:
    target_firm = join("$BUILD_DIR", "firmware.bin")
else:
    target_firm = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
AlwaysBuild(target_size)

#
# Target: Upload by default .bin file
#

if env.subst("$BOARD") == "zero":
    upload = env.Alias(["upload", "uploadlazy"], target_firm, "$UPLOADCMD")
else:
    upload = env.Alias(["upload", "uploadlazy"], target_firm,
                       [BeforeUpload, "$UPLOADCMD"])

AlwaysBuild(upload)

#
# Setup default targets
#

Default([target_firm, target_size])
