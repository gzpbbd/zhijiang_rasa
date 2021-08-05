from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
import json

# contents_table = {'团队信息': ['人数及平均年龄', '人员组成'],
#                   '深海软体机器人': ['结构特点', '成果'],
#                   '陆地双足机器人': ['成立时间', '足球机器人', '二代机器人', '弹琴机器人'],
#                   '空中载人机器人': ['目标', '研究重点', '当前进度'],
#                   '地外探测机器人': ['背景', '合作单位', '目前成果'],
#                   '智能机器人云脑平台': ['背景']}

# 读取讲解词文件
filename = 'introduction/introduction.json'
with open(filename, 'r') as f:
    all_introduction = json.load(f)
# 单独得到 入场词
beginning_text = all_introduction['入场词']
all_introduction.pop('入场词')
# 得到二层目录
contents_table = {}
for top_level in all_introduction.keys():
    second_levels = all_introduction[top_level].keys()
    contents_table[top_level] = list(second_levels)
print(contents_table)


def create_window(title='', buttons=[]):
    window = {'type': 'window', 'title': title, 'button': buttons}
    return window


def create_move_action(target_location=''):
    return {'type': 'bot_action', 'name': 'move', 'target_location': target_location}


class ActionStartIntroduce(Action):

    def name(self) -> Text:
        return "action_start_introduce"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text=beginning_text)
        return []


class ActionDisplayTopList(Action):

    def name(self) -> Text:
        return "action_display_top_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        buttons = []
        for top_level in contents_table.keys():
            buttons.append({'name': top_level, 'value': top_level})
        window = create_window(title='主界面', buttons=buttons)
        dispatcher.utter_message(text="可以看一下我屏幕上提供的界面哟，你想要了解哪个方面的内容呢？", json_message=window)
        return []


class ActionDisplaySecondList(Action):

    def name(self) -> Text:
        return "action_display_second_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        top_level = tracker.get_slot('top_level')
        if not top_level:  # 如果没有指定是哪方面的内容，直接退出
            print('ActionDisplaySecondList: top_level is null')
            return []

        buttons = []
        for second_level in contents_table[top_level]:
            buttons.append({'name': second_level, 'value': second_level})

        window = create_window(title=top_level, buttons=buttons)
        text = '关于{}的主要内容列举在了屏幕上哟，你想了解具体了解哪一个内容呢？或者我可以为你按顺序介绍哦。'.format(top_level)
        dispatcher.utter_message(json_message=window, text=text)
        return []


class ActionCommandToTargetLocation(Action):

    def name(self) -> Text:
        return "action_command_to_target_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        top_level = tracker.get_slot('top_level')
        dispatcher.utter_message(json_message=create_move_action(target_location=top_level))
        return [SlotSet('target_location', top_level)]


class ActionCommandReturnHome(Action):

    def name(self) -> Text:
        return "action_command_return_home"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message=create_window(title='smile'))
        dispatcher.utter_message(json_message=create_move_action(target_location='home'))
        return [SlotSet('top_level', None), SlotSet('second_level', None),SlotSet('target_location', 'home')]


class ActionIntroduceSecondLevelContent(Action):

    def name(self) -> Text:
        return "action_introduce_second_level_content"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        top_level = tracker.get_slot('top_level')
        second_level = tracker.get_slot('second_level')
        introduction = all_introduction[top_level][second_level]

        dispatcher.utter_message(text=introduction)
        dispatcher.utter_message(text='你还想了解什么呢？如果想要返回主界面，请说“返回主界面”。如果不需要我引导，请说”拜拜“哦。')
        return []


class ActionIntroduceOneByOne(Action):

    def name(self) -> Text:
        return "action_introduce_one_by_one"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        top_level = tracker.get_slot('top_level')
        for second_level in contents_table[top_level]:
            introduction = all_introduction[top_level][second_level]
            dispatcher.utter_message(text=introduction)

        text = '关于{}的主要内容我都已经介绍完了哟，很有趣对吧。你还想了解什么呢？如果想要返回主界面，请说“返回主界面”。如果不需要我引导，请说”拜拜“哦。'.format(top_level)
        dispatcher.utter_message(text=text)
        return []
