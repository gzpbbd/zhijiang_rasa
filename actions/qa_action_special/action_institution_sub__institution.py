import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
from actions.qa_action.utils import inquiry_key_value
import pandas


class ActionInstitutionSubInstitution(Action):
    def __init__(self):
        self.db_file = "actions/qa_database/机构（多级机构及职员信息）.csv"
        df = pandas.read_csv(self.db_file, '\t')

        self.sub_departments = {}
        for l1, l2, l3 in zip(df['一级机构'], df['二级机构'], df['三级机构']):
            l1 = str(l1)
            l2 = str(l2)
            l3 = str(l3)
            if l1 != 'nan':
                if l1 not in self.sub_departments.keys():
                    self.sub_departments[l1] = []
                if l2 != 'nan':
                    self.sub_departments[l1].append(l2)

            if l2 != 'nan':
                if l2 not in self.sub_departments.keys():
                    self.sub_departments[l2] = []
                if l3 != 'nan':
                    self.sub_departments[l2].append(l3)

    def name(self) -> Text:
        return "action_institution_sub__institution"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        slot_value = tracker.get_slot('institution')

        if slot_value not in self.sub_departments.keys():
            utterance = '所有候选的拥有子机构的机构为{}'.format('、'.join(self.sub_departments.keys()))
        elif len(self.sub_departments[slot_value]) != 0:
            utterance = '{}的子机构有{}'.format(slot_value, '、'.join(self.sub_departments[slot_value]))
        else:
            utterance = '{}没有子机构'.format(slot_value)

        dispatcher.utter_message(text=str(utterance))
        return []
