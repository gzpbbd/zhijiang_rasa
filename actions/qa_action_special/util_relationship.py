# 读取表 机构（多级机构及职员信息）.csv，建立(1,2,子机构)
# 读取表 机构间关系.csv，建立(之江，2，两位一体)

import pandas, os, json


# 建立子机构树结构，和集合
# 查询树中机构位置
class InquiryRelationship():
    def __init__(self, sub_institute_file, relationship_file):
        """

        :param sub_institute_file: "actions/qa_database/机构（多级机构及职员信息）.csv"
        :param relationship_file: "actions/qa_database/机构间关系.csv"
        """

        df = pandas.read_csv(sub_institute_file, sep='\t')

        self.internal_ins_paths = {}
        for level2, level3 in zip(df['二级机构'], df['三级机构']):
            level2 = str(level2)
            level3 = str(level3)
            if not level2 == 'nan':
                self.internal_ins_paths[level2] = ['之江实验室', level2]

            if not level3 == 'nan':
                self.internal_ins_paths[level3] = ['之江实验室', level2, level3]

        # 建立合作单位树结构，和集合
        df = pandas.read_csv(relationship_file, sep='\t')

        self.external_ins_paths = {}
        self.external_ins_relations = {}
        for rel, level1, level2 in zip(df['关系'], df['一级机构'], df['二级机构']):
            level1 = str(level1)
            level2 = str(level2)
            if not level1 == 'nan':
                self.external_ins_paths[level1] = ['之江实验室', level1]
                self.external_ins_relations[level1] = rel

            if not level2 == 'nan':
                self.external_ins_paths[level2] = ['之江实验室', level1, level2]
                self.external_ins_relations[level2] = rel

        self.internal_set = set(self.internal_ins_paths.keys())
        self.external_set = set(self.external_ins_paths.keys())
        self.total_set = set(['之江实验室'])
        self.total_set.update(self.internal_set, self.external_set)

    def inquiry_relationship(self, institution1, institution2):
        if institution1 == institution2:
            return "\"{}\"与\"{}\"是同一个机构".format(institution1, institution2)
        if institution1 not in self.total_set or institution2 not in self.total_set:
            return "\"{}\"与\"{}\"没有关系".format(institution1, institution2)
        if institution1 == '之江实验室' or institution2 == '之江实验室':

            if institution1 == '之江实验室':
                ins = institution2
            else:
                ins = institution1
            if ins in self.internal_set:
                return "\"{}\"是\"之江实验室\"的子机构".format(ins)
            else:
                return "\"{}\"是\"之江实验室\"的{}".format(ins, self.external_ins_relations[ins])

        if institution1 in self.internal_set and institution2 in self.internal_set:
            path1 = self.internal_ins_paths[institution1]
            path2 = self.internal_ins_paths[institution2]
            index = -1
            for i, (x, y) in enumerate(zip(path1, path2)):
                if x == y:
                    index = i
                else:
                    break

            if index == 0:
                return "\"{}\"与\"{}\"都是之江实验室的子机构".format(institution1, institution2)

            if len(path1) < len(path2):
                parent = institution1
                child = institution2
            else:
                parent = institution2
                child = institution1
            return "它们都是之江实验室的机构，并且\"{}\"是\"{}\"的子机构".format(child, parent)

        if institution1 in self.external_set and institution2 in self.external_set:
            path1 = self.external_ins_paths[institution1]
            path2 = self.external_ins_paths[institution2]
            index = -1

            min_len = min(len(path1), len(path2))
            for i, (x, y) in enumerate(zip(path1[:min_len], path2[:min_len])):
                if x == y:
                    index = i
                else:
                    break
            if index == -1:
                return "\"{}\"是之江实验室的{}，而\"{}\"是之江实验室的{}".format(institution1,
                                                                 self.external_ins_relations[
                                                                     institution1], institution2,
                                                                 self.external_ins_relations[
                                                                     institution2])

            if len(path1) < len(path2):
                parent = institution1
                child = institution2
            else:
                parent = institution2
                child = institution1
            return "\"{}\"是之江实验室的{}，而\"{}\"是\"{}\"的子机构".format(child,
                                                               self.external_ins_relations[child],
                                                               child, parent)

        if institution1 in self.internal_set:
            in_ins = institution1
            ex_ins = institution2
        else:
            in_ins = institution2
            ex_ins = institution1
        return "\"{}\"是之江实验室的子机构，而\"{}\"是之江实验室的".format(in_ins, ex_ins,
                                                        self.external_ins_relations[ex_ins])


if __name__ == '__main__':
    inquiry = InquiryRelationship("../../actions/qa_database/机构（多级机构及职员信息）.csv",
                                  "../../actions/qa_database/机构间关系.csv")

    pairs = [('之江实验室', '智能机器人研究中心'), ('之江实验室', '达摩院'), ('之江实验室', '之江实验室'), ('浙江省委组织部', '浙江省教育厅'),
             ('条件保障部', '信息化中心')]
    for ins1, ins2 in pairs:
        rel = inquiry.inquiry_relationship(ins1, ins2)
        print(rel)
