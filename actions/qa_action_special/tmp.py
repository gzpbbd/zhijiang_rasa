# 读取表 机构（多级机构及职员信息）.csv，建立(1,2,子机构)
# 读取表 机构间关系.csv，建立(之江，2，两位一体)

import pandas, os, json

print(os.getcwd())

# 建立子机构树结构，和集合
# 查询树中机构位置


sub_institute_file = "../../actions/qa_database/机构（多级机构及职员信息）.csv"
df = pandas.read_csv(sub_institute_file, sep='\t')

institute_tree = {'之江实验室': {}}
institute_set = set('之江实验室')
for level2, level3 in zip(df['二级机构'], df['三级机构']):
    if str(level2) == 'nan':
        continue
    if level2 not in institute_tree['之江实验室'].keys():
        institute_tree['之江实验室'][level2] = {}
        institute_set.add(level2)

    if str(level3) == 'nan':
        continue
    if level3 not in institute_tree['之江实验室'][level2].keys():
        institute_tree['之江实验室'][level2][level3] = {}
        institute_set.add(level3)

# 建立合作单位树结构，和集合
relationship_file = "../../actions/qa_database/机构间关系.csv"
df = pandas.read_csv(relationship_file, sep='\t')

relationship_tree = {'之江实验室': {}}
relationship_set = set('之江实验室')
for rel, level2, level3 in zip(df['关系'], df['一级机构'], df['二级机构']):
    if str(level2) == 'nan':
        continue
    if level2 not in relationship_tree['之江实验室'].keys():
        relationship_tree['之江实验室'][level2] = {}
        relationship_set.add(level2)

    if str(level3) == 'nan':
        continue
    if level3 not in relationship_tree['之江实验室'][level2].keys():
        relationship_tree['之江实验室'][level2][level3] = rel
        relationship_set.add(level3)

print(json.dumps(institute_tree, indent=4,ensure_ascii=False))
print(institute_set)
print(json.dumps(relationship_tree, indent=4,ensure_ascii=False))
print(relationship_set)
