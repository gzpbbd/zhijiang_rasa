import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
from actions.qa_action.utils import inquiry_key_value
from actions.qa_action_special.util_relationship import InquiryRelationship


class ActionInstitutionInstitutionRelationship(Action):
    def __init__(self):
        self.inquiry = InquiryRelationship("actions/qa_database/机构（多级机构及职员信息）.csv",
                                           "actions/qa_database/机构间关系.csv")

        # 读取表 机构（多级机构及职员信息）.csv，建立(1,2,子机构)
        # 读取表 机构间关系.csv，建立(之江，2，两位一体)

    def name(self) -> Text:
        return "action_institution_institution_relationship"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        slot_value = tracker.get_slot('institution')
        ins_list = list(tracker.get_latest_entity_values('institution'))

        if len(ins_list) != 2:
            utterance = "只支持查询两个机构间的关系。而给定的机构有{}个，分别是{}".format(len(ins_list), '、'.join(ins_list))
        else:
            utterance = self.inquiry.inquiry_relationship(ins_list[0], ins_list[1])

        dispatcher.utter_message(text=utterance)
        return []
