import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

import pickle
import os

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata


class MyComponent(Component):
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
    defaults = {}

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

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
        print("--- MyComponent __init__")
        print("*** component_config \n", component_config)

        self.alias = component_config.get('alias', 'alias')
        self.save_dir = 'pipeline_data'

        save_dir = os.path.join(self.save_dir, self.alias)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        with open(os.path.join(self.save_dir, self.alias, '__init__-component_config.pkl'),
                  'wb') as \
                file:
            pickle.dump(component_config, file, True)

    def train(
            self,
            training_data: TrainingData,
            config: Optional[RasaNLUModelConfig] = None,
            **kwargs: Any,
    ) -> None:
        """Train this component.

        This is the components chance to train itself provided
        with the training data. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.train`
        of components previous to this one."""
        print("--- MyComponent train")
        print("*** TrainingData \n", TrainingData)
        print("*** config \n", config)

        with open(os.path.join(self.save_dir, self.alias, 'train-training_data.pkl'), 'wb') as \
                file:
            pickle.dump(training_data, file, True)

        with open(os.path.join(self.save_dir, self.alias, 'train-config.pkl'), 'wb') as file:
            pickle.dump(config, file, True)

        pass

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
        print("--- MyComponent process")
        print("*** message \n", message)

        with open(os.path.join(self.save_dir, self.alias, 'process-message.pkl'), 'wb') as file:
            pickle.dump(message, file, True)

        pass

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""

        print("--- MyComponent persist")
        print("*** file_name \n", file_name)
        print("*** model_dir \n", model_dir)
        pass

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

        print("--- MyComponent load")
        print("*** meta \n", meta)
        print("*** model_dir \n", model_dir)
        print("*** model_metadata \n", model_metadata)
        print("*** cached_component \n", cached_component)

        if cached_component:
            return cached_component
        else:
            return cls(meta)
