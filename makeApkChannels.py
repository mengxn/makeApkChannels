#!/usr/bin/env python3

import re
import sys
import os


channel_key = 'InstallChannel'
# you can add more channels
channels = ['myapp', 'xiaomi', 'huawei', 'vivo', 'oppo']
key_path = 'your key path'
key_alias = 'your key alias'
key_pass = 'your key password'


# parse channels
def parse_channels(path):
    if os.path.exists(path):
        with open(path, 'r') as file:
            global channels
            channels = file.readline().split(',')
    return channels


def replace_channel(path, channel):
    if not os.path.exists(path):
        print('file not exist')
        return

    if not channel:
        print('channel is invalid')
        return

    data = []
    with open(path, 'r') as file:
        for line in file.readlines():
            if channel_key in line:
                data.append(re.sub('value="\\w+"', 'value="%s"' % channel, line))
            else:
                data.append(line)

    with open(path, 'w') as file:
        file.writelines(data)


def make_channels(apk_file, channels):
    # decode apk
    apk_dir_name = apk_file[:-4]
    if os.path.exists(apk_dir_name):
        os.system('rm -rf %s' % apk_dir_name)
    os.system('apktool d %s' % apk_file)

    xml_file = '%s/%s' % (apk_dir_name, 'AndroidManifest.xml')
    for channel in channels:
        # change channel
        replace_channel(xml_file, channel)
        unaligned_apk = '%s_%s_unaligned.apk' % (apk_dir_name, channel)
        # rebuild apk
        os.system('apktool b %s -o %s' % (apk_dir_name, unaligned_apk))
        # zip align
        align_apk = '%s_%s.apk' % (apk_dir_name, channel)
        os.system('zipalign -pfv 4 %s %s' % (unaligned_apk, align_apk))
        # remove unaligned apk
        os.remove(unaligned_apk)
        # sign apk
        os.system('apksigner sign -v --ks %s --ks-key-alias %s --ks-pass pass:%s %s' % (key_path, key_alias, key_pass, align_apk,))

    # clear temp data
    if os.path.exists(apk_dir_name):
        os.system('rm -rf %s' % apk_dir_name)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        dir_name = os.path.dirname(sys.argv[1])
        if dir_name:
            print('change dir', dir_name)
            os.chdir(dir_name)
        file_name = os.path.basename(sys.argv[1])
        if file_name.endswith('.apk'):
            channels = parse_channels('channels.conf')
            make_channels(file_name, channels)
        print('Finished! Channels list ', channels)
    else:
        print('error: please input apk file')
    pass
