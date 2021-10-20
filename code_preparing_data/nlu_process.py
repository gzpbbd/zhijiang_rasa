import pandas
import sys
import yaml
import os


# ------------ 标注数据

def annotating_from_entity_values(entity_name, entity_values, templates, verbose=0):
    """

    :param entity_name: 实体名. str
    :param entity_values: 实体可能值的列表
    :param templates: 模板列表。如模板 [{}有什么成果,]。其中{}表示实体信息插入的位置
    :param verbose: 大于 0 时打印所有标注数据；否则不输出信息
    :return:

    example:
        input:
            entity_name = 'institution'
            entity_values = ['之江实验室', '智能机器人研究中心']
            templates = [
                '[%s](%s)有什么科研成果',
                '[%s](%s)的科研成果有哪些',
                '[%s](%s)的科研成果有科研成果吗',
            ]
        return:
            [之江实验室](institution)有什么科研成果
            [之江实验室](institution)的科研成果有哪些
            [之江实验室](institution)的科研成果有科研成果吗
            [智能机器人研究中心](institution)有什么科研成果
            [智能机器人研究中心](institution)的科研成果有哪些
            [智能机器人研究中心](institution)的科研成果有科研成果吗


    """
    all_annotation = []
    for value in entity_values:
        for template in templates:
            template = template.format('[%s](%s)')  # 模板改为 rasa NLU的模板
            entry = template % (value, entity_name)
            all_annotation.append(entry)

    if verbose > 0:
        print('--- number of the labeled data:', len(all_annotation))
        for entry in all_annotation:
            print(entry)
    return all_annotation


def annotating_nlu_data(intent, entity_name, entity_values, templates, verbose=0):
    """

    :param intent: str
    :param entity_name: str
    :param entity_values: [str, str, ...]
    :param templates: 模板列表。如模板 [{}有什么成果,]。其中{}表示实体信息插入的位置
    :param verbose: 大于 0 时打印所有标注数据
    :return:
    """
    # 标注，及打印
    if verbose > 0:
        print('\n--- intent: {}'.format(intent))
    all_annotation = annotating_from_entity_values(entity_name, entity_values, templates, verbose)
    # return intent, all_annotation
    return {'intent': intent, 'entity': entity_name, 'examples': all_annotation}


# ------------ 写 rasa 文件

def write_nlu_file(all_nlu_data, filename=None):
    if filename:
        print('write data into', filename)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        file = open(filename, 'w', encoding='utf-8')
    else:
        file = sys.stdout

    print('version: "2.0"', file=file)
    print('nlu:', file=file)
    for entry in all_nlu_data:
        intent = entry['intent']
        examples = entry['examples']

        print('- intent: {}'.format(intent), file=file)
        print('  examples: |', file=file)
        for example in examples:
            print('    - {}'.format(example), file=file)

    if filename:
        file.close()


def write_domain_file(all_nlu_data, filename=None):
    if filename:
        print('write data into', filename)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        file = open(filename, 'w', encoding='utf-8')
    else:
        file = sys.stdout

    # 取出 intents 集合
    intents = []
    for entry in all_nlu_data:
        intent = entry['intent']
        intents.append(intent)
    intents = sorted(set(intents))

    # 写 intents
    print('version: "2.0"', file=file)
    print('intents:', file=file)
    for intent in intents:
        print('  - {}'.format(intent), file=file)

    # 取出 entities 集合
    entities = []
    for entry in all_nlu_data:
        entity = entry['entity']
        if isinstance(entity, str):
            entities.append(entity)
        else:  # 如果是多个实体
            entities = entities + entity
    entities = set(entities)

    # 写 entities
    print(file=file)
    print('entities:', file=file)
    for entity in entities:
        print('  - {}'.format(entity), file=file)

    # 写 entities 为 slots
    print(file=file)
    print('slots:', file=file)
    for entity in entities:
        print('  {}:'.format(entity), file=file)
        print('    type: text', file=file)

    # 写 action
    print(file=file)
    print('actions:', file=file)
    for intent in intents:
        print('  - action_{}'.format(intent), file=file)

    if filename:
        file.close()


def write_rules_file(all_nlu_data, filename=None):
    if filename:
        print('write rules into', filename)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        file = open(filename, 'w', encoding='utf-8')
    else:
        file = sys.stdout

    # 取出 intents 集合
    intents = []
    for entry in all_nlu_data:
        intent = entry['intent']
        intents.append(intent)
    intents = set(intents)

    # 读取 intent 对应的中文名
    english2chinese = {}
    df = pandas.read_csv('data/qa_database/二级结构中英文名.csv', sep='\t')
    for english, chinese in zip(df['english'], df['chinese']):
        english2chinese[english] = chinese

    # 写 规则
    print('version: "2.0"', file=file)
    print('rules:', file=file)
    for intent in intents:
        print('  - rule: {}'.format(english2chinese[intent]), file=file)
        print('    steps:', file=file)
        print('      - intent: {}'.format(intent), file=file)
        print('      - action: action_{}'.format(intent), file=file)

    if filename:
        file.close()


# 把 intent-entities的关系写入文件中
def write_intent_to_entities(all_nlu_data, filename=None):
    if filename:
        print('write data into', filename)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        file = open(filename, 'w', encoding='utf-8')
    else:
        file = sys.stdout

    print("intent\tentities", file=file)
    for entry in all_nlu_data:
        intent = entry['intent']
        entity = entry['entity']
        print("{}\t{}".format(intent, entity), file=file)

    if filename:
        file.close()


# ------------- 模板

# 成果-属性-简介，实体名：成果
def achievement_properties_introduction(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/科研成果.csv', sep='\t')
    achievements = list(set(df['成果名称']))

    # 模板
    entity_name = 'achievement'
    entity_values = achievements
    templates = [
        '{}是什么',
        '你知道{}吗',
        '{}有什么特点',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-成果，实体名：机构
def institution_outcome(verbose=0):
    # 模板
    entity_name = 'institution'
    entity_values = ['之江实验室', '智能机器人研究中心']
    templates = [
        '{}有什么科研成果',
        '{}的科研成果有哪些',
        '{}的科研成果有科研成果吗',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-科研装置，实体名：机构
def institution_scientific__research__device(verbose=0):
    # 模板
    entity_name = 'institution'
    entity_values = ['之江实验室', '智能机器人研究中心']
    templates = [
        '{}有哪些科研装置',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-代表歌曲,institution_attribute_representative__song，实体：机构
def institution_attribute_representative__song(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}是做什么的',
        '{}有室歌吗',
        '{}的代表歌曲是什么',
        '{}有代表歌曲吗',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-单位性质，实体：机构
def institution_attribute_nature__of__unit(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构'])
    institutions = set(institutions)
    institutions_1 = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    df = pandas.read_csv('data/qa_database/机构间关系.csv', sep='\t')
    institutions = list(df['一级机构'])
    institutions = set(institutions)
    institutions_2 = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    institutions = set(institutions_1 + institutions_2)

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的单位性质是什么',
        '{}是事业单位吗',
        '{}是企业吗',
        '{}是混合所有制单位吗',
        '{}是什么性质的单位',
        '{}是国家行政机关吗',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-奠基时间,institution_attribute_foundation__time，实体：机构
def institution_attribute_foundation__time(verbose=0):
    # 读取实体的可能值
    institutions = ['之江实验室']
    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的奠基时间是什么',
        '{}什么时候奠基的',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# -------------


# 机构-属性-吉祥物,institution_attribute_mascot，实体：机构
def institution_attribute_mascot(verbose=0):
    # 读取实体的可能值
    institutions = ['之江实验室', '阿里巴巴']
    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的吉祥物是什么',
        '{}有吉祥物吗',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-价值观,institution_attribute_values，实体：机构
def institution_attribute_values(verbose=0):
    # 读取实体的可能值
    institutions = ['之江实验室', ]
    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的价值观是什么',
        '{}有什么样的价值观',
        '{}有价值观吗',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-简介,institution_attribute_introduction，实体：机构
def institution_attribute_introduction(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}是什么样的机构',
        '{}是做什么的',
        '能不能介绍一下{}',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-建设目标,institution_attribute_construction__goal，实体：机构
def institution_attribute_construction__goal(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的建设目标是什么',
        '{}有什么样的建设目标',
        '{}计划建设为什么样的机构',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-联系电话,institution_attribute_contact__phone，实体：机构
def institution_attribute_contact__phone(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的电话是多少',
        '{}怎样通过电话联系',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-论坛,institution_attribute_forum，实体：机构
def institution_attribute_forum(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}有没有论坛',
        '{}的内部论坛在哪里',
        '{}的员工论坛怎么访问',
        '你知道{}的内部论坛吗',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-评价,institution_attribute_evaluation，实体：机构
def institution_attribute_evaluation(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}怎么样',
        '大家都怎么评价{}',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-人数,institution_attribute_number__of__people，实体：机构
def institution_attribute_number__of__people(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}一共有多少人',
        '{}的员工有多少',
        '{}有多少员工',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# ---------------------------


# 机构-属性-使命,institution_attribute_mission，实体：机构
def institution_attribute_mission(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的使命是什么',
        '{}有什么样的历史使命',
        '{}是做什么的',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-特色文化,institution_attribute_characteristic__culture，实体：机构
def institution_attribute_characteristic__culture(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的特色文化是什么',
        '{}有什么样的特色文化',
        '可以把{}的特色文化告诉我吗',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-网址,institution_attribute_url，实体：机构
def institution_attribute_url(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的官网是什么',
        '去哪里访问{}的网站',
        '去哪里能看到{}的详细信息',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-位置,institution_attribute_location，实体：机构
def institution_attribute_location(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}在哪里',
        '{}在什么位置',
        '怎么去{}',
    ]
    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-英文名,institution_attribute_english__name，实体：机构
def institution_attribute_english__name(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的英文名称是什么',
        '{}的英文简称是什么',
        '怎么用英语表达{}',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-属性-战略目标,institution_attribute_strategic__objective，实体：机构
def institution_attribute_strategic__objective(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}的战略目标是什么',
        '{}有什么战略目标',
    ]
    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-项目,institution_project，实体：机构
def institution_project(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    values = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = values
    templates = [
        '{}有哪些科研项目',
        '{}有什么科研项目',
        '{}的项目有哪些',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-子机构,institution_sub__institution，实体：机构
def institution_sub__institution(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    values = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = values
    templates = [
        '{}有哪些党支部',
        '{}有哪些部门',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 机构-项目,institution_project，实体：机构
def institution_project(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'institution'
    entity_values = institutions
    templates = [
        '{}有哪些科研项目',
        '{}有什么科研项目',
        '{}的项目有哪些',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 科研装置-属性-简介,scientific__research__device_properties_introduction，实体：科研装置
def scientific__research__device_properties_introduction(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/科研装置.csv', sep='\t')
    values = list(df['名称'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'scientific__research__device'
    entity_values = values
    templates = [
        '可以介绍一下{}吗',
        '{}是什么',
        '{}有什么特点',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 项目-属性-发布时间,project_attribute_release__time，实体：项目
def project_attribute_release__time(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/项目.csv', sep='\t')
    values = list(df['名称'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'project'
    entity_values = values
    templates = [
        '{}的发布时间是什么时候',
        '{}是什么时间发布的',
        '你知道{}的发布时间吗',
    ]
    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 项目-属性-简介,project_attribute_introduction，实体：项目
def project_attribute_introduction(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/项目.csv', sep='\t')
    values = list(df['名称'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'project'
    entity_values = values
    templates = [
        '可以介绍一下{}吗',
        '{}是什么',
        '{}有什么特点',
        '你了解{}吗',
    ]
    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 项目-属性-名称,project_attribute_name，实体：项目
def project_attribute_name(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/项目.csv', sep='\t')
    values = list(df['名称'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'project'
    entity_values = values
    templates = [
        '之江实验室的{}叫什么',
        '之江实验室的{}名字是？',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 项目-属性-上线时间,project_attribute_online__time，实体：项目
def project_attribute_online__time(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/项目.csv', sep='\t')
    values = list(df['名称'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'project'
    entity_values = values
    templates = [
        '{}全面上线时间是什么时候',
        '{}是什么时候上线的',
        '你知道{}的上线时间吗',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 员工-属性-办公地点,employee_attribute_office__location，实体：员工
def employee_attribute_office__location(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/人.csv', sep='\t')
    values = list(df['姓名'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'employee'
    entity_values = values
    templates = [
        '{}老师的办公室在哪里',
        '去哪里能找到{}老师',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 员工-属性-入职时间,employee_attribute_on_time，实体：员工
def employee_attribute_on_time(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/人.csv', sep='\t')
    values = list(df['姓名'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'employee'
    entity_values = values
    templates = [
        '{}是什么时候入职的',
        '{}是什么时候来之江实验室工作的',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 员工-属性-生日,employee_attribute_birthday，实体：员工
def employee_attribute_birthday(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/人.csv', sep='\t')
    values = list(df['姓名'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'employee'
    entity_values = values
    templates = [
        '{}的生日是什么时候',
        '应该在什么时候庆祝{}的生日',
        '{}是在什么时候出生的',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 员工-属性-住址,employee_attribute_address，实体：员工
def employee_attribute_address(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/人.csv', sep='\t')
    values = list(df['姓名'])
    values = set(values)
    values = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    entity_name = 'employee'
    entity_values = values
    templates = [
        '{}的家在哪里',
        '{}住在哪里',
        '{}住哪',
    ]

    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# 职位-属性-任期,position_attribute_term，实体：职位
def position_attribute_term(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/职位+职能.csv', sep='\t')
    values = list(df['职位'])
    values = set(values)
    values_position = [x for x in values if isinstance(x, str)]  # 移除 nan 元素
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    institutions = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    institutions = set(institutions)
    institutions = [x for x in institutions if isinstance(x, str)]  # 移除 nan 元素

    values = []
    for pos in values_position:
        for ins in institutions:
            values.append(ins + pos)

    # 模板
    entity_name = 'position'
    entity_values = values
    templates = [
        '{}的任期是多久',
    ]
    # 标注，及打印
    intent = sys._getframe(0).f_code.co_name
    return annotating_nlu_data(intent, entity_name, entity_values, templates, verbose)


# ------------------------ 以上所有 意图 只对应一个槽位

# 机构-机构-关系,institution_institution_relationship，实体：职位
def institution_institution_relationship(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    values = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    values = set(values)
    values_1 = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    df = pandas.read_csv('data/qa_database/机构间关系.csv', sep='\t')
    values = list(df['一级机构']) + list(df['二级机构'])
    values = set(values)
    values_2 = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    values = list(set(values_1 + values_2))

    # 模板
    entity_name = 'institution'
    entity_values = values
    templates = [
        '{}是什么关系',
        '{}',
        '{}',
    ]

    # 标注，及打印
    examples = []
    for i in range(len(values)):
        for j in range(0, len(values), len(values) // 3):
            entry = '[%s](%s)和[%s](%s)是什么关系' % (values[i], entity_name, values[j], entity_name)
            examples.append(entry)

    intent = sys._getframe(0).f_code.co_name
    if verbose > 0:
        print('--- intent:', intent)
        print('--- number of examples:', len(examples))
        for e in examples:
            print(e)

    return {'intent': intent, 'entity': entity_name, 'examples': examples}


# 机构-职员-属性-职位,institution_staff_attribute_position，实体：机构, 职位
def institution_staff_attribute_position(verbose=0):
    # 读取实体的可能值
    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    values = list(df['一级机构']) + list(df['二级机构']) + list(df['三级机构'])
    values = set(values)
    institutions = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    df = pandas.read_csv('data/qa_database/机构（多级机构及职员信息）.csv', sep='\t')
    values = list(df['职位'])
    values = set(values)
    positions = [x for x in values if isinstance(x, str)]  # 移除 nan 元素

    # 模板
    ins_name = 'institution'
    pos_name = 'position'

    # 标注，及打印
    examples = []
    for ins in institutions:
        for pos in positions:
            entry = '[%s](%s)的[%s](%s)是谁' % (ins, ins_name, pos, pos_name)
            examples.append(entry)

    intent = sys._getframe(0).f_code.co_name
    if verbose > 0:
        print('--- intent:', intent)
        print('--- number of examples:', len(examples))
        for e in examples:
            print(e)

    return {'intent': intent, 'entity': [ins_name, pos_name], 'examples': examples}


all_nlu_data = []
all_nlu_data.append(achievement_properties_introduction())
all_nlu_data.append(institution_outcome())
all_nlu_data.append(institution_scientific__research__device())
all_nlu_data.append(institution_attribute_representative__song())
all_nlu_data.append(institution_attribute_nature__of__unit())
all_nlu_data.append(institution_attribute_foundation__time())
all_nlu_data.append(institution_attribute_mascot())
all_nlu_data.append(institution_attribute_values())
all_nlu_data.append(institution_attribute_introduction())
all_nlu_data.append(institution_attribute_construction__goal())
all_nlu_data.append(institution_attribute_contact__phone())
all_nlu_data.append(institution_attribute_forum())
all_nlu_data.append(institution_attribute_evaluation())
all_nlu_data.append(institution_attribute_number__of__people())
all_nlu_data.append(institution_attribute_mission())
all_nlu_data.append(institution_attribute_characteristic__culture())
all_nlu_data.append(institution_attribute_url())
all_nlu_data.append(institution_attribute_location())
all_nlu_data.append(institution_attribute_english__name())
all_nlu_data.append(institution_attribute_strategic__objective())
all_nlu_data.append(institution_project())
all_nlu_data.append(institution_sub__institution())
all_nlu_data.append(institution_project())
all_nlu_data.append(scientific__research__device_properties_introduction())
all_nlu_data.append(project_attribute_release__time())
all_nlu_data.append(project_attribute_introduction())
all_nlu_data.append(project_attribute_name())
all_nlu_data.append(project_attribute_online__time())
all_nlu_data.append(employee_attribute_office__location())
all_nlu_data.append(employee_attribute_on_time())
all_nlu_data.append(employee_attribute_birthday())
all_nlu_data.append(employee_attribute_address())
all_nlu_data.append(position_attribute_term())
all_nlu_data.append(institution_institution_relationship())
all_nlu_data.append(institution_staff_attribute_position())

write_nlu_file(all_nlu_data, 'data/nlu/nlu_qa_data.yml')
# write_nlu_file(all_nlu_data)

write_domain_file(all_nlu_data, 'data/domain/domain_qa_data.yml')
# write_domain_file(all_nlu_data)

write_rules_file(all_nlu_data, 'data/core/rules_qa_data.yml')

write_intent_to_entities(all_nlu_data, 'data/schema/intent_to_entities.csv')
