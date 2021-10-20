# 读取文件
# 得到英文名，对应的数据表，key列，value列（过滤----------）
# 区分是否包含 别名
#
# 调用 读取字典的操作
import pandas, os

act_template = """import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, BotUttered
from actions.qa_action.utils import inquiry_key_value


class %s(Action):
    def __init__(self):
        self.db_file = "actions/qa_database/%s"
        self.key_column = "%s"
        self.value_column = "%s"
        self.dic = inquiry_key_value(self.db_file, self.key_column, self.value_column)

    def name(self) -> Text:
        return "%s"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取意图和槽位信息
        slot_value = tracker.get_slot('%s')

        # 查询数据库，得到话语
        if slot_value not in self.dic.keys():
            utterance = '\"{}\" 没在数据文件\"{}[column:{}]\"中。可能的值为: \\n\\n'.format(slot_value,
                                                                         self.db_file,
                                                                         self.key_column)
            for x in self.dic.keys():
                utterance += '- ' + x + '\\n'
        else:
            utterance = self.dic[slot_value]

        dispatcher.utter_message(text=str(utterance))
        return []
"""

# 需替换的值: class name,database filename,key column, value column, action name,slot name

dir = "data/action"

if not os.path.exists(dir):
    os.makedirs(dir)

int2ent_df = pandas.read_csv("data/schema/intent_to_entities.csv", sep='\t')
int2ent = {}
for i in range(len(int2ent_df)):
    int2ent[int2ent_df.iloc[i]['intent']] = int2ent_df.iloc[i]['entities']

act_df = pandas.read_csv("data/schema/action标注.csv", sep=',')
for i in range(len(act_df)):
    action_name = act_df.iloc[i]['action_name']
    db_file_name = act_df.iloc[i]['file_name']
    key_column = act_df.iloc[i]['key_column']
    value_column = act_df.iloc[i]['value_column']

    intent = action_name[len('action_'):]
    print(action_name, db_file_name, key_column, value_column,intent)
    entity = int2ent[intent]

    py_filename = action_name + '.py'
    classname = ''.join(str.capitalize(x) for x in action_name.split('_'))
    content = act_template % (
        classname, db_file_name, key_column, value_column, action_name, entity)
    with open(os.path.join(dir, py_filename), 'w', encoding='utf-8') as f:
        f.write(content)


