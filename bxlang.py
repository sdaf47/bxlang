#!/usr/bin/python3.5
import os
import re
import sys

from gi.module import maketrans

component = sys.argv[-1]

isTemplate = '-t' in sys.argv

# TODO запятые, точки, английский. Искать в тегах и в кавычках, многострочно.
charMap = maketrans(
    'йцукенгшщзхъфывапролджэячсмитьбюё,. ',
    'ICUKENGSSZHBFYWAPROLDZEYCSMITPBUE___'
)

component_map = (
    '.parameters',
    '.description',
    'class',
    'component',
)

template_map = (
    'template',
    'result_modifier',
    'component_epilog'
)

if "/" not in component:
    componentPath = component + "/"
else:
    componentPath = component

print('Component: ', component[:-1])

for file_name in component_map:
    try:
        file = open(componentPath + file_name + '.php')
    except FileNotFoundError:
        continue

    code = file.read()
    messages = re.findall(r'[а-яА-Я]+[\s,.-_а-яА-Я]+', code)

    lang_dir = componentPath + 'lang/ru/'
    if not os.path.isdir(lang_dir):
        os.mkdir(lang_dir)

    lang_file = open(lang_dir + file_name + '.php', 'w+')
    lang_file.write('<?php\n')
    lang_list = []
    for message in messages:
        lang = {
            'code': file_name.upper().replace('.', '') + '_' + message.lower().translate(charMap),
            'message': message,
        }
        lang_file.write('$MESS["' + lang['code'] + '"] = "' + lang['message'] + '";\n')
        lang_list.append(lang)

    for lang in lang_list:
        code = code.replace("\"" + lang['message'] + "\"", "\Bitrix\Main\Localization\Loc::getMessage(\"" + lang['code'] + "\")")
        code = code.replace("\'" + lang['message'] + "\'", "\Bitrix\Main\Localization\Loc::getMessage(\"" + lang['code'] + "\")")
        code = code.replace(lang['message'], "\Bitrix\Main\Localization\Loc::getMessage(\"" + lang['code'] + "\")")

    file.close()

    file = open(componentPath + file_name + '.php', 'w+')
    file.write(code)

    file.close()
