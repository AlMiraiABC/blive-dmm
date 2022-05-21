# Bilibili live danmaku manager（B站直播间弹幕管理器）

Dependencies on [blivedm](https://github.com/xfgryujk/blivedm) and [bilibili_api](https://github.com/MoyuScript/bilibili-api)

依赖于 [blivedm](https://github.com/xfgryujk/blivedm) 和 [bilibili_api](https://github.com/MoyuScript/bilibili-api)

## Quick Start / 开箱即用

### Config / 配置

#### Config file / 通过配置文件

You can set `config.json` to config app.

The minimum configuration as below in `config.json`. You can reference JSON schema in [./schema/index.json](<./schema/index.json>) for tips and ignore `Missing property` schema warnings.

可通过文件`config.json`设置应用程序。

在配置文件`config.json`内，至少配置如下。可引用JSON规范[./schema/index.json](<./schema/index.json>)获得提示信息，并忽略属性缺失(`Missing property`)的警告。

```json
{
    "$schema": "./schema/index.json",
    "user": {
        "id": "<user id / UP主ID>"
    },
    "room": {
        "id": "<live room id / 直播间号>"
    },
    "credential": {
        "buvid3": "buvid3 in cookie",
        "sessdata": "sessdata in cookie",
        "bili_jct": "bili_jct in cookie",
    }
}
```

All of values in `credential` should be copied from cookies after loged in browser.

其中，`credential`的所有值需在网页登录后，在cookies中复制。

#### Set envs / 通过设置环境变量

Or, you can set system environments without configuration file. All of keys have to starts with `BLDM_`.

或者，设置环境变量，而不需要配置文件。所有环境变量需以`BLDM_`为前缀。

|key / 环境变量|description / 说明| config / 配置文件
-|-|-
BLDM_USER_ID | user id / UP主ID | user.id
BLDM_ROOM_ID | live room id / 直播间号 | room.id
BLDM_BUVID3 | buvid3 in cookie | credential.buvid3
BLDM_SESSDATA | sessdata in cookie | credential.sessdata
BLDM_BILI_JCT | bili_jct in cookie | credential.bili_jct

### Startup / 启动

#### Console / 控制台启动

```python
python app.py
```

#### Docker / 容器启动

1. Pull image / 下载镜像

    ```sh
    docker pull almirai/blive-dmm
    ```

2. Start container / 启动容器

    * config.json / 通过配置文件

        Copy config.json to container.

        将配置文件`config.json`映射到容器内。

        ```sh
        docker run -itd -v /path/to/config.json:/blive-dmm/config.json almirai/blive-dmm
        ```

    * .env / 通过设置环境变量

        Set env in `.env` file

        将环境变量保存为`.env`文件传入容器内。

        ```sh
        docker run -itd --env-file .env almirai/blive-dmm
        ```

## Features / 功能

### auto reply / 自动回复

Send danmaku automatically when triggerd  events.

发生某些事件时，自动发送指定弹幕。

event / 事件 | description / 说明
-|-
welcome | user visit live room / 用户进入直播间
gift | user give gifts/ 用户赠送礼物
follow | user follow you / 用户关注UP主

```json
{
    "reply": {
        "welcome": "<message>",
        "gift": "<message>",
        "follow": "<message>",
        "enable": ["welcome", "gift", "follow"]
    }
}
```

### keyword reply / 关键词回复

Send danmaku when get keyword.

当用户弹幕出发关键词时，发送指定弹幕。

```json
{
    "reply":{
        "keyword":{
            "key": "<key or list of keys / 关键词或关键词列表>",
            "message": "<send message / 发送的弹幕内容>"
        }
    }
}
```

### scheduled  / 定时弹幕

Send danmaku interval.

指定间隔时间发送弹幕。

```json
{
    "schedule": [
        {
            "message": "<message / 弹幕内容>",
            "interval": "<interval / 间隔时间>"
        }
    ]
}
```

### email notify / 邮件通知

Send email when triggered events.

发生某些事件时，自动向置顶用户发送通知邮件。

event /事件 | description / 说明
-|-
live_room_closed | live room closed / 直播间已关闭

```json
{
    "notify":{
        "when": {
            "live_room_closed": {
                "template": "<email content / 邮件内容>"
            },
            "enable": ["live_room_closed"]
        }
    }
}
```
