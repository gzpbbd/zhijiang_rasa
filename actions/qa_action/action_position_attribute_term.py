import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
from actions.qa_action.utils import inquiry_key_value


class ActionPositionAttributeTerm(Action):
    def __init__(self):
        self.dic = inquiry_key_value("actions/qa_database/职位+智能.csv", "职位", "任期")

    def name(self) -> Text:
        return "action_position_attribute_term"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        slot_value = tracker.get_slot('position')

        # 查询数据库，得到话语
        if slot_value not in self.dic.keys():
            utterance = '\"{}\" 没在数据库中。可能的值为: \n\n'.format(slot_value)
            for x in self.dic.keys():
                utterance += '- ' + x + '\n'
        else:
            utterance = self.dic[slot_value]

        dispatcher.utter_message(text=utterance)
        return []
