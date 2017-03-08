# Bitrix lang parser #

Скрипт найдет все однострочные фразы и предложения на русском языке, заменит их на вызов Loc::getMessage()

## Как пользоваться ##
### Установка ###
Копируем файл из папки bin/ в папку ~/bin/
```
$ cp
```

### Запуск ###

Запускать можно из любой директории. Путь указывается до самого названия компонента или шаблона.
После выполнения, обязательно проверить. Просьба, прислать примеры некорректных выполнений, а также ошибок.

```
$ bxlang [-t, -c] /local/components/custom/news.list/
```
-t или -c в зависимости от того, компонент это или шаблон

Параметры обязательны

## Result ##
### class.php ###

```
<?php
$MESS["NAZWANIE"] = "Название";
$MESS["OPISANIE"] = "Описание";
$MESS["DOCERNEE__MENU"] = "Дочернее - меню";

```

### lang/class.php ###

```
<?php
if (!defined("B_PROLOG_INCLUDED") || B_PROLOG_INCLUDED!==true) die();

$arComponentDescription = array(
	"NAME" => \Bitrix\Main\Localization\Loc::getMessage("NAZWANIE"),
	"DESCRIPTION" => \Bitrix\Main\Localization\Loc::getMessage("OPISANIE"),
	"CACHE_PATH" => "Y",
	"PATH" => array(
		"ID" => "sonoteka",
		"CHILD" => array(
			"ID" => "contacts",
			"NAME" => \Bitrix\Main\Localization\Loc::getMessage("DOCERNEE__MENU")
		)
	),
);

```