import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
from actions.qa_action.utils import inquiry_key_value


class ActionProjectAttributeName(Action):
    def __init__(self):
        self.db_file = "actions/qa_database/"
        self.key_column = ""
        self.value_column = ""

    def name(self) -> Text:
        return "action_project_attribute_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        slot_value = tracker.get_slot('project')

        dispatcher.utter_message(text="不晓得，没有保存了项目别名的数据表[employee:{}]".format(slot_value))
        return []
