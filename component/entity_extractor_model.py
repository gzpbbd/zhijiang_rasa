import abc
import torch
from torch import nn, optim
import torch.nn.functional as F
from typing import Any, Optional, Text, Dict, List, Type, Set
import os
from bert_serving.client import BertClient
import numpy as np
import pickle
import json
import re


class EntityExtractorModelInterface:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, rasa_config: Dict[str, Any]) -> None:
        """
        按照配置初始化模型

        :param rasa_config: dict 类型。rasa 中给该模块定义的参数，目前自定义了 epochs。使用rasa_config.get("epochs", 100)获取
        """
        pass

    @abc.abstractmethod
    def train(self, texts: List[str], entities: List[List[Dict[str, Any]]],
              entity_set: Set[str]) -> None:
        """
        训练模型

        :param texts: 列表。每个元素是一个文本
        :param entities: 列表。训练数据的标签。每个文本都对应了一些实体
        :param entity_set: 集合。系统中声明了的所有实体名
        :return:
        """
        pass

    @abc.abstractmethod
    def save(self, target_dir: str) -> None:
        """
        保存必要的模型和数据

        :param target_dir: 目的位置的文件夹名
        :return:
        """
        pass

    @abc.abstractmethod
    def load(self, target_dir: str) -> None:
        """
        读取之前保存的模型和数据

        :param target_dir: 数据被保存的位置的文件夹名
        :return:
        """
        pass

    @abc.abstractmethod
    def process(self, text: str) -> List[Dict[str, Any]]:
        """
        给定一条文本，提取其中的所有实体并返回

        :param text: 被处理的文本
        :return: 所有的实体。一个列表，其内每个元素都是代表实体的一个字典。
                 每个实体的 keys 为 entity, start, end, value
            例如:
                如果输入的文本为：
                    投诉乱扣费，投诉时间为2021年11月25日。
                可能提取实体后返回两个命名实体如下：
                    [{'entity': 'event_name', 'start': 0, 'end': 6, 'value': '投诉乱扣费，'},
                     {'entity': 'event_time', 'start': 11, 'end': 22, 'value': '2021年11月25日'}]
        """
        return


class EntityExtractorModel(EntityExtractorModelInterface):

    def __init__(self, rasa_config: Dict[str, Any]) -> None:
        self.train_epochs = rasa_config.get("epochs", 100)
        self.event_name_pattern = None
        self.event_time_pattern = None

    def train(self, texts: List[str], entities: List[List[Dict[str, Any]]],
              entity_set: Set[str]) -> None:
        print("texts:", json.dumps(texts, indent=4, ensure_ascii=False), sep='\n')
        print("entities:", json.dumps(entities, indent=4, ensure_ascii=False), sep='\n')
        print("entity_set:", json.dumps(list(entity_set), indent=4, ensure_ascii=False), sep='\n')

        self.event_name_pattern = '投诉.+，'
        self.event_time_pattern = '\d{1,4}年\d{1,2}月\d{1,2}日'

    def save(self, target_dir: str) -> None:
        # 保存数据到指定的文件夹中
        print("save into target_dir:", target_dir)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        with open(os.path.join(target_dir, 'filename'), 'w', encoding='utf-8') as f:
            f.write("event_name:{}\n".format(self.event_name_pattern))
            f.write("event_time:{}\n".format(self.event_time_pattern))

    def load(self, target_dir: str) -> None:
        # 读取之前保存的数据
        print("load from target_dir:", target_dir)

        with open(os.path.join(target_dir, 'filename'), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                entity_name, entity_pattern = line.split(':', 1)
                if entity_name == 'event_name':
                    self.event_name_pattern = entity_pattern
                if entity_name == 'event_time':
                    self.event_time_pattern = entity_pattern

        print("event_name_pattern: {}".format(self.event_name_pattern))
        print("event_time_pattern: {}".format(self.event_time_pattern))

    def process(self, text: str) -> List[Dict[str, Any]]:
        print()
        entities = []
        # 按正则表达式匹配 投诉事件的名称
        for m in re.finditer(self.event_name_pattern, text):
            entity = {}
            entity['entity'] = 'event_name'
            entity['start'] = m.start()
            entity['end'] = m.end()
            entity['value'] = m.string[m.start(): m.end()]
            entities.append(entity)

        # 按正则表达式匹配 投诉事件的时间
        for m in re.finditer(self.event_time_pattern, text):
            entity = {}
            entity['entity'] = 'event_time'
            entity['start'] = m.start()
            entity['end'] = m.end()
            entity['value'] = m.string[m.start(): m.end()]
            entities.append(entity)
        return entities
