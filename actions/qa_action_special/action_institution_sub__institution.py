import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
from actions.qa_action.utils import inquiry_key_value


class ActionInstitutionSubInstitution(Action):
    def __init__(self):
        self.db_file = "actions/qa_database/"
        self.key_column = ""
        self.value_column = ""
        self.dic = inquiry_key_value(self.db_file, self.key_column, self.value_column)

    def name(self) -> Text:
        return "action_institution_sub__institution"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        slot_value = tracker.get_slot('institution')

        # 查询数据库，得到话语
        if slot_value not in self.dic.keys():
            utterance = '"{}" 没在数据文件"{}[column:{}]"中。可能的值为: \n\n'.format(slot_value,
                                                                         self.db_file,
                                                                         self.key_column)
            for x in self.dic.keys():
                utterance += '- ' + x + '\n'
        else:
            utterance = self.dic[slot_value]

        dispatcher.utter_message(text=str(utterance))
        return []