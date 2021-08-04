import yaml
import json

# filename = '20210804_introduction.yml'
# with open(filename, 'r') as f:
#     data = yaml.load(f.read())
# print(type(data))
# print(data)
#
# filename = '20210804_introduction.json'
# with open(filename, 'w') as f:
#     # yaml.dump(data, f, allow_unicode=True)
#     json.dump(data,f,ensure_ascii=False)

filename = 'introduction.json'
with open(filename, 'r') as f:
    all_introduction = json.load(f)
beginning = all_introduction['入场词']
all_introduction.pop('入场词')
# print(all_introduction)

contents_table = {}

all_second_levels = []
for top_level in all_introduction.keys():
    second_levels = all_introduction[top_level].keys()
    contents_table[top_level] = list(second_levels)
    for k in second_levels:
        all_second_levels.append(k)
    # print('- {}'.format(top_level))
# print(contents_table)

# print(all_second_levels)
for k in set(all_second_levels):
    print('- {}'.format(k))
# import json
#
# contents_table = {'团队信息': ['人数及平均年龄', '人员组成'],
#                   '深海软体机器人': ['结构特点', '成果'],
#                   '陆地双足机器人': ['成立时间', '足球机器人', '二代机器人', '弹琴机器人'],
#                   '空中载人机器人': ['目标', '研究重点', '当前进度'],
#                   '地外探测机器人': ['背景', '合作单位', '目前成果'],
#                   '智能机器人云脑平台': ['背景']}
# introduce = {}
# for top in contents_table.keys():
#     introduce[top] = {}
#     for second in contents_table[top]:
#         introduce[top][second] = {}
#
# introduce['团队信息']['人数及平均年龄'] = "我们目前的全职人员已经超过了110人了，平均年龄只有29岁呢，是一个朝气蓬勃的团队。"
# introduce['团队信息']['人员组成'] = "我们的团队里有两位院士，他们是我们的主任。另外还有首席科学家，教授pi，和一部分青年科学家。"
#
# introduce['深海软体机器人']['结构特点'] = "软体机器人与我们平常熟知的机器人不太一样，结构非常柔软。它的特点主要有两个。第一是它内部没有电机，它的驱动是靠它的两翼。它的两翼是一种人工肌肉哦。第二是它没有一般机器人需要的金属的耐压壳。"
# introduce['深海软体机器人']['成果'] = "我们的软体机器人创造了两个世界首次。第一是它在马里亚纳海沟实现了万米的无耐压壳的实验。第二是它实现了在南海三千米的自主游动的实验。这些成果发笔在了国际顶尖期刊nature的封面上面，它是一个非常轰动的创新呢！ "
#
# introduce['陆地双足机器人']['成立时间'] = "双足机器人项目大概是在19年12月份的时候成立的。这个项目大概才一年半的时间。"
# introduce['陆地双足机器人']['足球机器人'] = "足球机器人是最初的机器人，虽然看着感觉很弱，但是这个是我们的起点，确实它的成就是很大的。他获得过世界机器人足球锦标赛赛的亚军呢。"
# introduce['陆地双足机器人']['二代机器人'] = "最新在研制的二代机器人，已经突破了一个双足机器人很重要的一个功能，就是平衡控制，我们目前在这方面已经有一个很好的突破，然后相关的成果也发到了今年的机器人顶会上面。"
# introduce['陆地双足机器人']['弹琴机器人'] = "我们这个机器人主要就是搭建了一套非常灵巧的机械臂，这整套都是我们自主开发的，我们目前前期是先借助这个场景先测速、开发它灵巧操作的能力，未来想跟这个双足机器人结合，用于家庭机器人，人们提供一些服务，做这种前期的准备。"
#
# introduce['空中载人机器人']['目标'] = "解决的是比如交通拥堵、物流，包裹可以通过无人机的形式进行投递，加快效率。"
# introduce['空中载人机器人']['研究重点'] = "一个是要搭建基于分布式的冗余驱动的飞行器本体。        另外我们希望借助我们之江实验室在智能科学与技术方面的一些优势，然后去开发、研制无人驾驶技术。"
# introduce['空中载人机器人']['当前进度'] = "目前我们希望能够去突破轻量化的飞行机结构、稳定的控制、安全可靠的技术等。已经研制两台样机       我们一台样机大概在2020年的时候，在德清莫干山那边的一个通航机场已经试飞成功了。        我们的第二代样机，它的感知能力，它的一个续航能力都有一定的提升，目前大概可以有20分钟的空中载物的时间        在百年献礼的时候我们做了一个宣传片，我们在南湖那里成功试飞了。"
#
# introduce['地外探测机器人']['背景'] = "目前的地外探测器，它在火星上探测的时候会遇到的三个非常大的瓶颈问题。一是它对危险的识别是非常难的，因为火星的地质地貌是未知的。二是它的移动速度是非常慢的。三是它的作业精度也会相对很低。所以现在国内外的探测机，效率都非常低。"
# introduce['地外探测机器人']['合作单位'] = "我们的合作单位是航天五院。他们希望借助我们之江实验室在这个人工智能方面的一些优势，将这种人工智能赋能于航空航天，进而提高整个探测器的效率。"
# introduce['地外探测机器人']['目前成果'] = "目前我们搭建了一套叫做多传感系统的感知系统，它未来可以用于下一代的火星车。另外        还开发了一套场景理解的算法，我们希望在现有的这个天文一号完成既定任务之后，能够部署到天文一号上，希望能够进一步提高它的感知能力。"
#
# introduce['智能机器人云脑平台']['背景'] = "目前机器人产业的存在一些瓶颈问题。大家可能都在报道中看到过，比如说聊天机器人、家务机器人在报道中都有出现，但是它真正其实还未形成产业化的规模，这主要就是它的智能化程度很低。"
#
# with open('introduction.json', 'w') as f:
#     json.dump(introduce, f, indent=4)
# print(json.dumps(introduce, indent=4))
