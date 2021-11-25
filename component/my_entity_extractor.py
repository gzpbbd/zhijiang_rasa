import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
# from rasa.shared.nlu.constants import INTENT, TEXT
from rasa.nlu.classifiers.classifier import IntentClassifier
from rasa.utils.train_utils import override_defaults
import os
from bert_serving.client import BertClient

from component.entity_extractor_model import EntityExtractorModel
from component.intent_model import IntentModel

from rasa.nlu.extractors.extractor import EntityExtractor

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata
from rasa.shared.nlu.constants import (
    ENTITIES,
    ENTITY_ATTRIBUTE_VALUE,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
    TEXT,
    ENTITY_ATTRIBUTE_TYPE,
)


class MyEntityExtractor(EntityExtractor):
    # class MyIntentClassifier(Component):
    """A new component"""

    # Which components are required by this component.
    # Listed components should appear before the component itself in the pipeline.
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""

        return []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    defaults = {
        "epochs": 100,
    }

    # Defines what language(s) this component can handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    supported_language_list = None

    # Defines what language(s) this component can NOT handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    not_supported_language_list = None

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None, model=None) -> None:
        """

        :param component_config: 在配置文件中的键值对
        :param model:
        """
        super().__init__(component_config)
        self.component_config = override_defaults(self.defaults, component_config)

        self.model = model
        if not self.model:
            self.model = EntityExtractorModel(self.component_config)
        print('---- MyEntityExtractor init')

    def train(
            self,
            training_data: TrainingData,
            config: Optional[RasaNLUModelConfig] = None,
            **kwargs: Any,
    ) -> None:
        """

        :param training_data: 用 intents = training_data.intents 获取训练数据
        :param config: 所有 pipeline、component 的配置
        :param kwargs:
        :return:
        """
        """Train this component.

        This is the components chance to train itself provided
        with the training data. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.train`
        of components previous to this one.

        :param component_config: 在配置文件中的键值对
        """
        print('---- MyEntityExtractor train')
        entity_set = training_data.entities  # 标签的集合
        # 训练数据
        texts = []
        entities = []
        for ex in training_data.entity_examples:
            texts.append(ex.get(TEXT))
            entities.append(ex.get(ENTITIES))

        self.model.train(texts, entities, entity_set)

    def process(self, message: Message, **kwargs: Any) -> None:
        """Process an incoming message.

        This is the components chance to process an incoming
        message. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.process`
        of components previous to this one."""
        print('---- MyEntityExtractor process')
        text = message.get(TEXT)
        if not text:
            return
        print("process:", text)
        extracted_entities = self.model.process(text)
        print("call model and get entities:", extracted_entities)
        extracted_entities = self.add_extractor_name(extracted_entities)
        message.set(
            ENTITIES, message.get(ENTITIES, []) + extracted_entities, add_to_output=True
        )

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""

        print('---- MyEntityExtractor persist')

        filepath = os.path.join(model_dir, file_name)
        print('filepath')
        print(os.path.abspath(filepath))

        self.model.save(filepath)

        return {"file": file_name}

    @classmethod
    def load(
            cls,
            meta: Dict[Text, Any],
            model_dir: Text,
            model_metadata: Optional["Metadata"] = None,
            cached_component: Optional["Component"] = None,
            **kwargs: Any,
    ) -> "Component":
        """
        
        :param meta: 配置文件中的键值对，及 persist 方法返回的键值对
        :param model_dir: 
        :param model_metadata: 
        :param cached_component: 
        :param kwargs: 
        :return: 
        """
        """Load this component from file."""
        print('---- MyEntityExtractor load')

        file_name = meta.get("file")
        filepath = os.path.join(model_dir, file_name)
        # 加载模型
        model = EntityExtractorModel({})
        model.load(filepath)

        return cls(meta, model)
