import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    admin_id: list


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    # config.read(path)
    with open(path, encoding='utf-8') as fp:
        config.read_file(fp)

    tg_bot = config["tg_bot"]

    # print((tg_bot["admin_id"]))

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            admin_id=tg_bot["admin_id"]
        )
    )
