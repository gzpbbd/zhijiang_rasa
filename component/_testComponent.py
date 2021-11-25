import os
import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
import numpy as np
if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata

# 保存的模型名称
MODEL_NAME = "intent_model.npy"
class IntentClassifier(Component):
    """A new component"""
    provides = ['intent']   # 组件提供意图
    # Which components are required by this component.
    # Listed components should appear before the component itself in the pipeline.
    # 列出该组件需要的组件
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""
        '''
        此处由于我们采用自己的字向量，因此不需要任何前驱组件为我们提供信息
        '''
        return []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    # 应该是一些模型的默认值，可以在pipeline中自行配置，
    defaults = {
        "embedding_dim":100,
        "hidden_layers_sizes":10
    }

    # Defines what language(s) this component can handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    # 用来标识支持哪些语言，主要用在实例方法can_handle_language，None表示都支持
    supported_language_list = None

    # Defines what language(s) this component can NOT handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    # 标识不支持哪些语言
    not_supported_language_list = None

    def __init__(self,
                 component_config: Optional[Dict[Text, Any]] = None,
                 model: Optional = None) -> None:
        '''

        :param component_config: 这个是rasa自动创建的，也就是模型的一些参数
        :param model: 这个是我自己定义的，将训练好的对象的索引交给model
        '''
        super().__init__(component_config)
        print("初始化")
        print("component_config的值为：%s" % component_config)
        # 下面是我这里的值，包括一些模型参数，组件名称，索引，
        # 最后一个classifer_name是我在persist()函数中加进去的，也就是说persist函数的返回值会加入到component_config
        # {'embedding_dim': 200, 'hidden_layers_sizes': 100, 'name': 'IntentClassifier', 'index': 5, 'classifier_name': 'intent_model.npy', 'class': 'testComponent.IntentClassifier'}
        # if model==None:
        #     raise ValueError(
        #         "没有模型可被初始化"
        #     )
        self.model = model


    def train(
            self,
            training_data: TrainingData,
            config: Optional[RasaNLUModelConfig] = None,
            **kwargs: Any,
    ) -> None:
        """Train this component.
        用于训练模型
        This is the components chance to train itself provided
        with the training data. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.train`
        of components previous to this one."""
        print("开始训练")
        print("config:%s" % config)
        for t in training_data.training_examples:
            print(t.data)
            # t是Message对象的，具体可以查看Message对象的定义
            # 此处我输出的包括nlu.yml的数据
            '''
            {'text': '我想知道实验室主任', 'intent': 'answer_choose', 'entities': [{'start': 4, 'end': 9, 'value': '实验室主任', 'entity': 'secondeLvel'}], 'text_tokens': [<rasa.nlu.tokenizers.tok
            enizer.Token object at 0x0000020CB3F3FBC8>, <rasa.nlu.tokenizers.tokenizer.Token object at 0x0000020CB3F3FC08>, <rasa.nlu.tokenizers.tokenizer.Token object at 0x0000020CB3F3FB48>, <ras
            a.nlu.tokenizers.tokenizer.Token object at 0x0000020CB3F3FB88>, <rasa.nlu.tokenizers.tokenizer.Token object at 0x0000020CB3F3FC48>], 'intent_tokens': [<rasa.nlu.tokenizers.tokenizer.To
            ken object at 0x0000020CB3F3FCC8>]}
            '''
        # 假设训练好的模型为results
        results = {
            '你叫什么名字': {'name':'whoareyou','confidence':0.999999999999},
            '你名字是啥': {'name':'whoareyou','confidence':0.99999999999}
        }
        self.model = results

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
        # 用于模型推理
        print("开始推理")
        print("text:",message.get('text'))
        if message.get('text') in self.model:
            print("当前rasa识别的意图为:%s" % message.get('intent'))
            print("当前rasa识别的意图ranking为:%s" % message.get('intent'))
            message.set('intent',self.model[message.get('text')],add_to_output=True)
            print("修改后的意图为:%s" % message.get('intent'))
        print("推理结束")

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""
        # 保存模型
        classifier_file = os.path.join(model_dir,MODEL_NAME)
        print("正在保存，保存在:%s" % classifier_file)
        np.save(classifier_file,self.model)
        return {"classifier_name":MODEL_NAME}

    @classmethod
    def load(
            cls,
            meta: Dict[Text, Any],
            model_dir: Text,
            model_metadata: Optional["Metadata"] = None,
            cached_component: Optional["Component"] = None,
            **kwargs: Any,
    ) -> "Component":
        """Load this component from file."""
        print("加载模型中")
        # meta的值
        # {'name': 'sentiment', 'index': 5, 'classifier_file': 'inten_model.npy', 'class': 'senti.SentimentAnalyzer'}

        model = np.load(os.path.join(model_dir,MODEL_NAME),allow_pickle=True).item()
        print("加载完毕")
        if cached_component:
            return cached_component
        else:
            return cls(meta,model)
