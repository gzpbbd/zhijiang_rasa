from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
import pandas


class ActionAchievementPropertiesIntroduction(Action):
    def __init__(self):
        db = pandas.read_csv("data/qa_database/科研成果.csv", sep='\t')
        self.dic = {}
        for key, value in zip(db['成果名称'], db['简介']):
            self.dic[key] = value

    def name(self) -> Text:
        return "action_achievement_properties_introduction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        slot_value = tracker.get_slot('achievement')
        last_intent = tracker.get_intent_of_latest_message()

        # 查询数据库，得到话语
        if slot_value not in self.dic.keys():
            utterance = '{} 没在数据库中。可能的值为: {}'.format(slot_value, self.dic.keys())
        else:
            utterance = self.dic[slot_value]

        dispatcher.utter_message(text=utterance)
        return []
