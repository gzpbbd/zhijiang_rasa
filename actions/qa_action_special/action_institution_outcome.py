import os

import pandas
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
from actions.qa_action.utils import inquiry_key_value


class ActionInstitutionOutcome(Action):
    def __init__(self):
        self.db_file = "actions/qa_database/科研成果.csv"
        self.outcomes = list(pandas.read_csv(self.db_file, sep='\t')['成果名称'])

    def name(self) -> Text:
        return "action_institution_outcome"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        slot_value = tracker.get_slot('institution')
        if slot_value == '之江实验室' or slot_value == '智能机器人研究中心':
            utterance = '、'.join(self.outcomes)
        else:
            utterance = '我只知道之江实验室和智能机器人研究中心有哪些成果呢'

        dispatcher.utter_message(text=str(utterance))
        return []
