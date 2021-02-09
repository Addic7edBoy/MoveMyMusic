# MMM

Python module that helps move all your music and other stuff from one music service to another.

## Features

Moves **tracks**, **playlists**, **albums** and **artists** between `vk`, `Yandex.Music`, `Spotify`


## Installation

```
pip install Move-My-Music
```

## Usage

### Exporting to JSON

```
MMM export --source vk --playlists True
MMM export --source ym --artists True --albums True
```

### Full run (export->import)

```
MMM run --source vk --source-user Admin --source-pass Admin --target sp --target-user Max --target-pass Max --alltracks True --playlists True
```

## Parameters

### Global

* `--log-path`: Path for the log file.
* `--data-path`: Filename for temp data.

### Common

* `--playlists` [True/False]: Include playlists (Default: False)
* `--artists` [True/False]: Include artists (Default: False)
* `--albums` [True/False]: Include albums (Default: False)
* `--alltracks` [True/False]: Include all tracks (Default: False)

### Export

* `--source`: Get music from (`vk` | `ym` | `sp`)
* `--source-user`: Login on source site.
* `--source-pass`: Password on source site.

### Run

* `--source`: Get music from (`vk` | `ym` | `sp`)
* `--source-user`: Login on source site.
* `--source-pass`: Password on source site.
* `--target`: Insert music into (`ym` | `sp`)
* `--target-user`: Login on target site.
* `--target-pass`: Password on target site.

