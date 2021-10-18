from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
import json



class ActionAchievementPropertiesIntroduction(Action):

    def name(self) -> Text:
        return "action_achievement_properties_introduction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        achievement = tracker.get_slot('achievement')
        last_intent = tracker.get_intent_of_latest_message()
        # 输出答案：查询数据库，二级结构, slots
        utterance = "查询数据库:: 二级结构: {}, achievement: {}".format(last_intent, achievement)

        dispatcher.utter_message(text=utterance)
        return []
