# Система динамического эмбиента для Ren'Py

[English](../README.md) | **Русский**

Гибкая система управления динамическим эмбиентом для Ren'Py 8.4+, позволяющая воспроизводить несколько аудиодорожек одновременно с настраиваемыми параметрами случайности, громкости, плавными переходами и сложными аудио-сценами.

**Версия:** 2.0.0  
**CDS:** Ren'Py 8.5.0+  
**Лицензия:** MIT

## Основные возможности

- **YAML конфигурация** — Не нужен Python-код, только чистые YAML-файлы
- **Аранжировки** — Аудио-сцены как пресеты со слоями
- **CDS команды** — Нативные команды Ren'Py: `ambient play`, `ambient layer`, `ambient stop`
- **Обязательные треки** — Воспроизводятся постоянно с момента запуска
- **Случайные треки** — Воспроизводятся с настраиваемой вероятностью через wave-систему
- **Плавные переходы** — Все изменения громкости происходят плавно
- **Слои** — Динамические группы треков (погода, напряжение, время суток)
- **Строгая изоляция** — Треки вне текущей аранжировки автоматически останавливаются
- **Random Containers** — Несколько файлов на трек для разнообразия
- **Авто-переходы** — Аранжировки могут автоматически переключаться (интро → луп)
- **Debug UI** — Оверлей мониторинга в реальном времени

## Быстрый старт

### 1. Установите PyYAML

```bash
pip install pyyaml -t game/python-packages
```

### 2. Скопируйте файлы

Скопируйте в папку `game/`:
- `dynamic_ambient.rpy` (обязательно)
- `audio_assets.yaml` (обязательно)
- `arrangements.yaml` (обязательно)
- `ambient_auto_start.rpy` (опционально — автозапуск в главном меню)
- `ambient_integration.rpy` (опционально — UI настроек)
- `libs/rpda/02-rpda-cds.rpy` (опционально — CDS команды)

### 3. Настройте треки

```yaml
# audio_assets.yaml
tracks:
  forest_base:
    file: "audio/forest.ogg"
    type: "mandatory"
    volume: 0.6

  birds:
    file: "audio/birds.ogg"
    type: "random"
    volume: 0.5
    chance: 0.4
    interval: [30, 90]
```

### 4. Создайте аранжировки

```yaml
# arrangements.yaml
arrangements:
  forest_day:
    tracks:
      forest_base: { volume: 0.6 }
      birds: { volume: 0.5 }
    layers:
      rain:
        rain_sound: { volume: 0.7 }
```

### 5. Используйте в сценарии

```renpy
label forest_scene:
    ambient play "forest_day"
    "Вы входите в лес..."
    
    ambient layer "rain" on fade 3.0
    "Начинается дождь."
```

## CDS команды (Ren'Py 8.5.0+)

```renpy
ambient play "arrangement_name"       # Воспроизвести аранжировку
ambient play "name" fade 3.0          # С кастомным временем перехода
ambient stop                          # Остановить систему
ambient layer "rain" on               # Включить слой
ambient layer "rain" off fade 2.0     # Выключить слой с переходом
ambient volume 0.5                    # Установить громкость
ambient pause                         # Пауза
ambient resume                        # Продолжить
ambient schedule "name" in 30.0       # Запланировать переход
ambient debug ui                      # Переключить debug overlay
```

## Python API

```renpy
$ ambient.play_arrangement("forest_day")
$ ambient.play_arrangement("forest_day", fade_time=3.0)
$ ambient.set_layer("rain", True, fade_time=2.0)
$ ambient.set_base_volume(0.5)
$ ambient.stop_ambient()
$ ambient.pause_ambient()
$ ambient.resume_ambient()
```

## Демо-проект

Полный демо-проект включён в `example/RPDA_Demo_Project/`. См. [Руководство по демо-проекту](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Demo-Project) для инструкций по запуску.

## Документация

Полная документация доступна на **[Wiki](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki)**:

- [Установка](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Installation)
- [Быстрый старт](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Quick-Start)
- [Типы треков](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Track-Types)
- [Аранжировки](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Arrangements)
- [Слои](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Layers)
- [Справочник CDS](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/CDS-Reference)
- [Python API](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Python-API)
- [Справочник конфигурации](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki/Configuration-Reference)

## Требования

- **Ren'Py:** 8.4+ (основная система)
- **Ren'Py:** 8.5.0+ (для CDS команд)
- **PyYAML:** Требуется для парсинга YAML

## Структура файлов

```
game/
├── dynamic_ambient.rpy       # Основная система
├── ambient_auto_start.rpy    # Автозапуск (опционально)
├── ambient_integration.rpy   # UI настроек (опционально)
├── audio_assets.yaml         # Конфигурация треков
├── arrangements.yaml         # Конфигурация аранжировок
└── libs/rpda/
    └── 02-rpda-cds.rpy       # CDS команды (опционально)
```

## Changelog v2.0.0

- **YAML конфигурация** — Замена Python-конфигов на `audio_assets.yaml` и `arrangements.yaml`
- **CDS команды** — Добавлены команды `ambient` для управления из сценария
- **Система аранжировок** — Аудио-сцены со слоями и авто-переходами
- **Строгая изоляция** — Треки вне аранжировки автоматически останавливаются
- **Random Containers** — Несколько файлов на один ID трека
- **Автоматическая инициализация** — Не нужны ручные вызовы setup
- **Debug UI** — Улучшенная отладка через `ambient debug ui`

## Лицензия

MIT License — Свободное использование и модификация в любых проектах.

## Ссылки

- [GitHub репозиторий](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient)
- [Wiki документация](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/wiki)
- [Issues](https://github.com/ElysiumTeamDevelopment/RenPyDynamicAmbient/issues)
