# SPDX-FileCopyrightText: 2022 Alec Delaney, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT

while read filename; do
    if [ "$1" == "install" ]; then
        echo "Copying $filename to circuitpy_composite_action_paster/"
        ln  ./submodules/adabot/tools/$filename ./circuitpy_composite_action_paster/$filename;
    elif [ "$1" == "clean" ]; then
        echo "Deleting $filename in circuitpy_composite_action_paster/"
        rm ./circuitpy_composite_action_paster/$filename;
    fi
done < tools_reqs.txt
