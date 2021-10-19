import pandas


with open('nlu_process.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(lines)

pairs = []
for i in range(len(lines)):
    line = lines[i]
    if line[:3] == 'def':
        before = lines[i - 1]
        print(line.strip(), '\t', before.strip())
        eng = line.split(maxsplit=1)[-1].split('(')[0]
        chinese = before.split(',')[0][2:]
        print('--- ', eng, chinese)
        pairs.append([eng, chinese])

pairs = sorted(pairs)

with open('data/qa_database/二级结构中英文名.csv', 'w', encoding='utf-8') as f:
    print('chinese\tenglish', file=f)
    for eng, chinese in pairs:
        print('{}\t{}'.format(chinese,eng), file=f)

