import os
import re
from abc import abstractmethod
from typing import Iterator, Tuple, Dict

from gi.module import maketrans

from logger.logger import Logger


class Parser:
    LANG_FILE_LINE = "$MESS[\"{code}\"] = \"{mess}\";\n"
    PATH_FILE = "{file_name}.php"
    FULL_PATH_FILE = "{path}/{file}"
    PATH_LANG_DIR_ROOT = '{root}/lang/'
    PATH_LANG_DIR = '{lang_id}/'
    _map_char = maketrans(
        'йцукенгшщзхъфывапролджэячсмитьбюё ',
        'ICUKENGSSZHBFYWAPROLDZEYCSMITPBUE_'
    )
    _lang_id = 'ru'
    _regexp_list = {}
    _map = []
    _replace_rule = Dict[str, str]
    _path = ''
    __lang_dir_path = ''
    __logger = Logger

    def __init__(self, **kwargs):
        self.__logger = Logger()
        if 'lang_id':
            self._lang_id = kwargs['lang_id']
        else:
            raise KeyError('lang_id')
        if 'path' in kwargs:
            if kwargs['path'][-1] == '/':
                self._path = kwargs['path'][:-1]
            else:
                self._path = kwargs['path']
            self.__lang_dir_path = self.__make_lang_dir(self._path)
        if 'lang_id' in kwargs:
            self._lang_id = kwargs['lang_id']

    def _log(self, mess: str):
        self.__logger.log(__name__, mess)

    def __make_lang_dir(self, path: str):
        lang_dir_root = self.PATH_LANG_DIR_ROOT.format(root=path)
        if not os.path.isdir(lang_dir_root):
            os.mkdir(lang_dir_root)
        lang_dir_path = lang_dir_root + self.PATH_LANG_DIR.format(lang_id=self._lang_id)
        if not os.path.isdir(lang_dir_path):
            os.mkdir(lang_dir_path)
        return lang_dir_path

    def _make_lang_file(self, file_path: str, langs: Iterator[Tuple]):
        file = open(self.__lang_dir_path + file_path, 'w+')
        lang_file_code = "<?php\n"
        for code, mess in langs:
            lang_file_code += self.LANG_FILE_LINE.format(code=code, mess=mess)
        file.write(lang_file_code)
        file.close()

    @abstractmethod
    def _collect_messages(self, php_code: str):
        """
        :param php_code: string
        :return: list
        """
        return []

    @abstractmethod
    def _replace_messages(self, php_code: str, langs: Iterator[Tuple]):
        """
        :param php_code: 
        :param langs: 
        :return: 
        """
        return []

    @staticmethod
    def get_additional_map():
        return []

    def _make_code(self, message: str):
        code = message.lower().translate(self._map_char)
        reg_filer = re.compile("[^a-zA-Z_]+")
        code = reg_filer.sub('', code)
        return code[:30], message

    def run(self):
        for file_name in self._map + self.get_additional_map():
            try:
                file_path = self.PATH_FILE.format(file_name=file_name)
                full_path_file = self.FULL_PATH_FILE.format(path=self._path, file=file_path)
                file = open(full_path_file)
                php_code = file.read()
                file.close()

                messages = self._collect_messages(php_code)
                if len(messages) <= 0:
                    self._log("~ {file_name}".format(file_name=file_name))
                    continue

                map(self._log, messages)

                langs = map(self._make_code, messages)
                self._make_lang_file(file_path, langs)

                file = open(full_path_file, 'w')
                langs = map(self._make_code, messages)
                php_code = self._replace_messages(php_code, langs)
                print(php_code)
                file.write(php_code)
                file.close()

            except FileNotFoundError:
                self._log("~ {file_name}".format(file_name=file_name))
                continue
            self._log("+ {file_name} {messages}".format(file_name=file_name, messages=messages.__str__()))


class ComponentParser(Parser):
    _map = [
        'component',
        'class',
        '.parameters',
        '.description',
    ]
    _replace_rule = [
        ("\"{}\"", "\Bitrix\Main\Localization\Loc::getMessage(\"{}\")"),
        ("\'{}\'", "\Bitrix\Main\Localization\Loc::getMessage(\"{}\")")
    ]

    def _collect_messages(self, php_code):
        messages = re.findall(r'[а-яА-Я]+[\s,().\-_а-яА-Я]+[.,а-яА-Я]', php_code)
        return messages

    def _replace_messages(self, php_code, langs):
        for code, mess in langs:
            for temp, lang in self._replace_rule:
                php_code = php_code.replace(temp.format(mess), lang.format(code))
        return php_code


class TemplateParser(Parser):
    _map = [
        'template',
        'result_modifier',
        'component_epilog',
        '.description',
    ]
    _replace_rule = [
        ("\"{}\"", "\Bitrix\Main\Localization\Loc::getMessage(\"{}\")"),
        ("\'{}\'", "\Bitrix\Main\Localization\Loc::getMessage(\"{}\")"),
        ("{}", "<?= \Bitrix\Main\Localization\Loc::getMessage(\"{}\") ?>")
    ]

    def _collect_messages(self, php_code):
        messages = re.findall(r'[а-яА-Я]+[\s,().-_а-яА-Я]+[.,а-яА-Я]', php_code)
        return messages

    def _replace_messages(self, php_code, langs):
        for code, mess in langs:
            for temp, lang in self._replace_rule:
                php_code = php_code.replace(temp.format(code), lang.format(mess))


class StrategyParser:
    __map_commands = [
        ('-c', ComponentParser),
        ('-t', TemplateParser),
    ]
    __path = ""
    __lang_id = "ru"

    def execute(self, parser: Parser.__class__):
        p = parser(path=self.__path, lang_id=self.__lang_id)
        p.run()

    def run(self, argv):
        self.__path = argv[-1]
        for command, parser in self.__map_commands:
            if command in argv:
                self.execute(parser)
