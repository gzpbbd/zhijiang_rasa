import spacy
import os
# 指定使用0,1,2三块卡
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

spacy_en = spacy.load("zh_core_web_md")


def tokenize_en(text):
    return [tok.text for tok in spacy_en.tokenizer(text)]




text = ['陈航住在哪里', '温远周住在哪里']
for t in text:
    spacy_en.tokenizer(t)
