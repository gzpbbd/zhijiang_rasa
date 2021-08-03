from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered

top_level_list = ['团队信息', '深海软体机器人', '陆地双足机器人', '空中载人机器人', '地外探测机器人', '智能机器人云脑平台']
second_level_list = {'团队信息': ['人数及平均年龄', '人员组成'],
                     '深海软体机器人': ['结构特点', '成果'],
                     '陆地双足机器人': ['成立时间', '足球机器人', '二代机器人', '弹琴机器人'],
                     '空中载人机器人': ['目标', '研究重点', '当前进度'],
                     '地外探测机器人': ['背景', '合作单位', '目前成果'],
                     '智能机器人云脑平台': ['背景']}
domain_to_top_level = {'team': '团队信息', 'ocean_bot': '深海软体机器人', 'land_bot': '陆地双足机器人', 'sky_bot': '空中载人机器人',
                       'space_bot': '地外探测机器人', 'cloud_brain': '智能机器人云脑平台'}


def create_window(title='', buttons=[]):
    window = {'type': 'window', 'title': title, 'button': buttons}
    return window


def create_move_action(target_location=''):
    return {'type': 'bot_action', 'name': 'move', 'target_location': target_location}


class ActionDisplayMainInterface(Action):

    def name(self) -> Text:
        return "action_display_main_interface"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        buttons = []
        for top_level in top_level_list:
            buttons.append({'name': top_level, 'value': top_level})
        window = create_window(title='主界面', buttons=buttons)
        dispatcher.utter_message(text="可以看一下我屏幕上提供的界面哟，你想要了解哪个方面的内容呢？", json_message=window)
        return []


class ActionDisplaySecondInterface(Action):

    def name(self) -> Text:
        return "action_display_second_interface"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        domain = tracker.get_slot('domain')
        top_level = domain_to_top_level[domain]

        buttons = []
        for second_level in second_level_list[top_level]:
            buttons.append({'name': second_level, 'value': second_level})
        window = create_window(title=top_level, buttons=buttons)
        dispatcher.utter_message(json_message=window)
        # if domain == 'team':
        #     buttons = []
        #     # for key in
        #
        #     dispatcher.utter_message(text="DISPLAY:{人数及平均年龄,人员组成}")
        # elif domain == 'ocean_bot':
        #     dispatcher.utter_message(text="DISPLAY:{结构特点,成果}")
        # elif domain == 'land_bot':
        #     dispatcher.utter_message(text="DISPLAY:{成立时间,足球机器人,二代机器人,弹琴机器人}")
        # elif domain == 'sky_bot':
        #     dispatcher.utter_message(text="DISPLAY:{目标,研究重点,当前进度}")
        # elif domain == 'space_bot':
        #     dispatcher.utter_message(text="DISPLAY:{背景,合作单位,目前成果}")
        # elif domain == 'cloud_brain':
        #     dispatcher.utter_message(text="DISPLAY:{背景}")
        return []


class ActionSetSlotDomain(Action):

    def name(self) -> Text:
        return "action_set_slot_domain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        last_intent = tracker.get_intent_of_latest_message()
        domain_slot = None
        if last_intent == 'to_domain_team':
            domain_slot = SlotSet('domain', 'team')
        elif last_intent == 'to_domain_ocean_bot':
            domain_slot = SlotSet('domain', 'ocean_bot')
        # elif last_intent == 'to_land_bot_domain':
        #     domain_slot = SlotSet('domain', 'land_bot')
        # elif last_intent == 'to_sky_bot_domain':
        #     domain_slot = SlotSet('domain', 'sky_bot')
        # elif last_intent == 'to_space_bot_domain':
        #     domain_slot = SlotSet('domain', 'space_bot')
        # elif last_intent == 'to_cloud_brain_domain':
        #     domain_slot = SlotSet('domain', 'cloud_brain')

        if domain:
            return [domain_slot]
        else:
            return []


class ActionCommandToTargetLocation(Action):

    def name(self) -> Text:
        return "action_command_to_target_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        domain = tracker.get_slot('domain')
        dispatcher.utter_message(json_message=create_move_action(target_location=domain))
        return []


class ActionCommandReturnHome(Action):

    def name(self) -> Text:
        return "action_command_return_home"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message=create_window(title='smile'))
        dispatcher.utter_message(json_message=create_move_action(target_location='home'))
        return [SlotSet('domain', None)]


class ActionSecondInterfaceRequestSelectingContent(Action):

    def name(self) -> Text:
        return "action_second_interface_request_selecting_content"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        domain = tracker.get_slot('domain')
        domain_text = ''
        if domain in domain_to_top_level.keys():
            domain_text = domain_to_top_level[domain]

        dispatcher.utter_message(text="{}方面包括屏幕上显示的这些内容，我可以为你顺序介绍，也可以你说出其中一项的名字，我为你单独介绍哟。".format(domain_text))
        return []
