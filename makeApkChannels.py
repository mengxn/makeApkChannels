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
        print('ready to change channel', channel)
        replace_channel(xml_file, channel)
        channel_apk_name = '%s_%s.apk' % (apk_dir_name, channel)
        print('ready to build apk')
        os.system('apktool b %s -o %s' % (apk_dir_name, channel_apk_name))
        print('ready to sign apk')
        os.system('apksigner sign -v --ks %s --ks-key-alias %s --ks-pass pass:%s %s' % (key_path, key_alias, key_pass, channel_apk_name,))

    # clear temp data
    if os.path.exists(apk_dir_name):
        os.system('rm -rf %s' % apk_dir_name)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        dir_name = os.path.dirname(sys.argv[1])
        if dir_name:
            print('change dir ', dir_name)
            os.chdir(dir_name)
        file_name = os.path.basename(sys.argv[1])
        if file_name.endswith('.apk'):
            make_channels(file_name, channels)
    else:
        print('error: please input apk file')

    pass
