# MMM

Python module that helps move all your music and other stuff from one music service to another.

## Features

Moves **tracks**, **playlists**, **albums** and **artists** between `vk`, `Yandex.Music`, `Spotify`


## Installation

```
pip install Move-My-Music
```

## Usage


### Full run (export->import)

```
MMM --source vk --source-user Admin --source-pass Admin --target sp --target-user Max --target-pass Max --alltracks --playlists
```

## Parameters

### Global

* `--log-path`: Path for the log file.
* `--data-path`: Filename for temp data.

### Common

* `--playlists`: Include playlists (Default: False)
* `--artists`: Include artists (Default: False)
* `--albums`: Include albums (Default: False)
* `--alltracks`: Include all tracks (Default: False)


### Run

* `--source`: Get music from (`vk` | `ym` | `sp`)
* `--source-user`: Login on source site.
* `--source-pass`: Password on source site.
* `--target`: Insert music into (`ym` | `sp`)
* `--target-user`: Login on target site.
* `--target-pass`: Password on target site.
