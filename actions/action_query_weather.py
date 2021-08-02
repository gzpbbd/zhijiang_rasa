from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered



class ActionQueryWeather(Action):

    def name(self) -> Text:
        return "action_query_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        place = tracker.get_slot('city')
        time = tracker.get_slot('time')

        if isinstance(place, list):
            place = ' '.join(place)
        if isinstance(time, list):
            time = ' '.join(time)

        print('{}, {}'.format(place, time))
        dispatcher.utter_message(text='哇，{}的{}会出大太阳'.format(time, place))
        return []
        # return [SlotSet('city',None), BotUttered('哇，{}的{}会出大太阳'.format(time, place))]

        # dispatcher.utter_message(template='utter_submit', place=place, time=time)

        # return [SlotSet('place', None), SlotSet('time', None)]
