# import os
#
# while True:
#     print('Please Input An image: ')
#     image_path = input()
#     if image_path.strip().lower() == "q":
#         break
#     if not os.path.exists(image_path):
#         print("ERROR: The file {} don't exists. Please input again.".format(image_path))
#         continue
#     # face_recognition_image(dataset_emb, image_path)
#     print("process:",image_path)

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

with open('data/qa_database/二级结构中英文名.csv', 'w', encoding='utf-8') as f:
    print('chinese\tenglish', file=f)
    for eng, chinese in pairs:
        print('{}\t{}'.format(chinese,eng), file=f)
