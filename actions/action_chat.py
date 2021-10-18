# import os
# import logging
# import random
# from itertools import chain
# from argparse import ArgumentParser
# from pprint import pformat
#
# import torch
# import torch.nn.functional as F
#
# from transformers import OpenAIGPTLMHeadModel, GPT2LMHeadModel, BertTokenizer
# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# import time
#
# os.environ["CUDA_VISIBLE_DEVICES"] = "3"
#
# SPECIAL_TOKENS = ["[CLS]", "[SEP]", "[PAD]", "[speaker1]", "[speaker2]"]
#
#
# def top_filtering(logits, top_k=0, top_p=0.0, threshold=-float('Inf'), filter_value=-float('Inf')):
#     """ Filter a distribution of logits using top-k, top-p (nucleus) and/or threshold filtering
#         Args:
#             logits: logits distribution shape (vocabulary size)
#             top_k: <=0: no filtering, >0: keep only top k tokens with highest probability.
#             top_p: <=0.0: no filtering, >0.0: keep only a subset S of candidates, where S is the smallest subset
#                 whose total probability mass is greater than or equal to the threshold top_p.
#                 In practice, we select the highest probability tokens whose cumulative probability mass exceeds
#                 the threshold top_p.
#             threshold: a minimal threshold to keep logits
#     """
#     assert logits.dim() == 1  # Only work for batch size 1 for now - could update but it would obfuscate a bit the code
#     top_k = min(top_k, logits.size(-1))
#     if top_k > 0:
#         # Remove all tokens with a probability less than the last token in the top-k tokens
#         indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
#         logits[indices_to_remove] = filter_value
#
#     if top_p > 0.0:
#         # Compute cumulative probabilities of sorted tokens
#         sorted_logits, sorted_indices = torch.sort(logits, descending=True)
#         cumulative_probabilities = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
#
#         # Remove tokens with cumulative probability above the threshold
#         sorted_indices_to_remove = cumulative_probabilities > top_p
#         # Shift the indices to the right to keep also the first token above the threshold
#         sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
#         sorted_indices_to_remove[..., 0] = 0
#
#         # Back to unsorted indices and set them to -infinity
#         indices_to_remove = sorted_indices[sorted_indices_to_remove]
#         logits[indices_to_remove] = filter_value
#
#     indices_to_remove = logits < threshold
#     logits[indices_to_remove] = filter_value
#
#     return logits
#
#
# def build_input_from_segments(history, reply, tokenizer, with_eos=True):
#     """ Build a sequence of input from 3 segments: persona, history and last reply """
#     bos, eos, pad, speaker1, speaker2 = tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS)
#     sequence = [[bos]] + history + [reply + ([eos] if with_eos else [])]
#     sequence = [sequence[0]] + [[speaker2 if i % 2 else speaker1] + s for i, s in enumerate(sequence[1:])]
#     instance = {}
#     instance["input_ids"] = list(chain(*sequence))
#     instance["token_type_ids"] = [bos] + [speaker2 if i % 2 else speaker1 for i, s in enumerate(sequence[1:])
#                                           for _ in s]
#     return instance, sequence
#
#
# def sample_sequence(history, tokenizer, model, current_output=None, max_length=30,
#                     device="cuda" if torch.cuda.is_available() else "cpu",
#                     temperature=0.7,top_k=0, top_p=0.9, no_sample=False, min_length=1):
#     special_tokens_ids = tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS)
#     if current_output is None:
#         current_output = []
#
#     for i in range(max_length):
#         instance, sequence = build_input_from_segments(history, current_output, tokenizer, with_eos=False)
#         input_ids = torch.tensor(instance["input_ids"], dtype=torch.long, device=device).unsqueeze(0)
#         token_type_ids = torch.tensor(instance["token_type_ids"], dtype=torch.long, device=device).unsqueeze(0)
#
#         logits = model(input_ids, token_type_ids=token_type_ids)['logits']
#         logits = logits[0, -1, :] / temperature
#         logits = top_filtering(logits, top_k=top_k, top_p=top_p)
#         probs = F.softmax(logits, dim=-1)
#
#         prev = torch.topk(probs, 1)[1] if no_sample else torch.multinomial(probs, 1)
#         if i < min_length and prev.item() in special_tokens_ids:
#             while prev.item() in special_tokens_ids:
#                 prev = torch.multinomial(probs, num_samples=1)
#
#         if prev.item() in special_tokens_ids:
#             break
#         current_output.append(prev.item())
#
#     return current_output
#
#
# def clip_history(history, max_len=500):
#     count = 0
#     history2 = []
#     for st in history[::-1]:
#         if count + len(st) < max_len:
#             count += len(st)
#             history2.append(st)
#         else:
#             history2.append(st[count - max_len:])
#     return history2[::-1]
#
#
# class Chatbot(object):
#     def __init__(self, model_path, seed=42):
#         random.seed(seed)
#         torch.random.manual_seed(seed)
#         torch.cuda.manual_seed(seed)
#         self.model = OpenAIGPTLMHeadModel.from_pretrained(model_path)
#         self.tokenizer = BertTokenizer(os.path.join(model_path, 'vocab.txt'),
#                                        do_lower_case=True,
#                                        never_split=["[speaker1]", "[speaker2]"])
#         self.device="cuda" if torch.cuda.is_available() else "cpu"
#         self.model.to(self.device)
#         self.model.eval()
#
#     def tokenize(self, obj):
#         if isinstance(obj, str):
#             return self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(obj))
#         if isinstance(obj, dict):
#             return dict((n, self.tokenize(o)) for n, o in obj.items())
#         return list(self.tokenize(o) for o in obj)
#
#     def response(self, history):
#         with torch.no_grad():
#             out_ids = sample_sequence(history, self.tokenizer, self.model)
#         if len(out_ids) > 5 and len(set(out_ids)) == 1:  # 避免类似"哈哈哈哈哈哈..."这种的回复
#             i = random.randint(2, 5)
#             out_ids = out_ids[:i]
#         out_text = self.tokenizer.decode(out_ids, skip_special_tokens=True)
#         return out_text
#
#
# class ActionChat(Action):
#     def __init__(self):
#         path = os.path.join(os.path.split(__file__)[0], '..', 'models', 'gpt_large')
#         self.bot = Chatbot(path)
#
#     def name(self) -> Text:
#         return "action_chat"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         tik=time.time()
#         history = self.get_history(tracker)
#         # print(history)
#         history = [self.bot.tokenize(s) for s in history]
#         text = self.bot.response(history)
#         text = text.replace(' ', '')
#         tok=time.time()
#         # print(f'{text}: response time {tok-tik} sec')
#         dispatcher.utter_message(text=text)
#         return []
#
#     def get_history(self, tracker: Tracker, max_history=5, max_len=500):
#         history = []
#         state = None
#         s = ''
#         max_count = 2 * max_history
#         count = 0
#         total_len = 0
#         for e in tracker.events[::-1]:
#             if e['event'] in {'user', 'bot'}:
#                 if state is None:
#                     s = e['text'] or ''
#                 elif state == e['event']:
#                     s += '，' + (e['text'] or '')
#                 else:
#                     if not s.strip().strip('，'):
#                         continue
#                     if total_len + len(s) < max_len:
#                         total_len += len(s)
#                         s=" ".join(list(s.strip('，').replace(" ", "")))
#                         if len(s)<=30: #排除特别长的回复，这么长的回复大概率是问答给出的，模型训练数据里没见过，会给出质量很低的回复
#                             history.append(s)
#                     else:
#                         history = history[::-1]
#                         return history
#                     count += 1
#                     s = e['text'] or ''
#                 state = e['event']
#             if count >= max_count - 1:
#                 break
#         if s.strip().strip('，') and total_len + len(s) < max_len:
#             total_len += len(s)
#             s = " ".join(list(s.strip('，').replace(" ", "")))
#             if len(s)<=30: #排除特别长的回复，这么长的回复大概率是问答给出的，模型训练数据里没见过，会给出质量很低的回复
#                 history.append(s)
#         history = history[::-1]
#         return history
#
#
# def get_history_test():
#     class MyTracker(object):
#         def __init__(self, events):
#             self.events = events
#
#     act = ActionChat()
#     event1 = {'event': 'x'}
#     event2 = {'event': 'user', 'text': None}
#     event3 = {'event': 'user', 'text': '111'}
#     event4 = {'event': 'bot', 'text': '0' * 10}
#     event5 = {'event': 'bot', 'text': '2' * 10}
#     event6 = {'event': 'bot', 'text': '3' * 10}
#     events = [event1, event2, event3, event4, event5, event6]
#     # print(act.get_history(MyTracker(events)))
#     events=[{'event':'user' if i%2==0 else 'bot', 'text':str(i)}
#             for i in range(20, 0, -1)]
#     # print(act.get_history(MyTracker(events)))
#     events=[{'event':'user' if i%2==0 else 'bot', 'text':str(i)*100}
#             for i in range(20, 0, -1)]
#     history = act.get_history(MyTracker(events))
#     history = [act.bot.tokenize(s) for s in history]
#     print(act.bot.response(history))
#
#
# def run():
#     run_parser = ArgumentParser()
#     run_parser.add_argument('--gpt2', action='store_true', help="use gpt2")
#     run_parser.add_argument("--model_checkpoint", type=str, default="gpt_large",
#                             help="Path, url or short name of the model")
#     run_parser.add_argument("--max_history", type=int, default=5,
#                             help="Number of previous utterances to keep in history")
#     run_parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu",
#                             help="Device (cuda or cpu)")
#
#     run_parser.add_argument("--no_sample", action='store_true', help="Set to use greedy decoding instead of sampling")
#     run_parser.add_argument("--max_length", type=int, default=30, help="Maximum length of the output utterances")
#     run_parser.add_argument("--min_length", type=int, default=1, help="Minimum length of the output utterances")
#     run_parser.add_argument("--seed", type=int, default=42, help="Seed")
#     run_parser.add_argument("--temperature", type=int, default=0.7, help="Sampling softmax temperature")
#     run_parser.add_argument("--top_k", type=int, default=0,
#                             help="Filter top-k tokens before sampling (<=0: no filtering)")
#     run_parser.add_argument("--top_p", type=float, default=0.9,
#                             help="Nucleus filtering (top-p) before sampling (<=0.0: no filtering)")
#     args = run_parser.parse_args()
#
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger(__file__)
#     logger.info(pformat(args))
#
#     if args.model_checkpoint == "":
#         logging.error("Checkpoint needed!")
#         return
#
#     random.seed(args.seed)
#     torch.random.manual_seed(args.seed)
#     torch.cuda.manual_seed(args.seed)
#
#     logger.info("Get pretrained model and tokenizer")
#     model_class = OpenAIGPTLMHeadModel if not args.gpt2 else GPT2LMHeadModel
#     tokenizer = BertTokenizer(os.path.join(args.model_checkpoint, 'vocab.txt'),
#                               do_lower_case=True,
#                               never_split=["[speaker1]", "[speaker2]"])
#     model = model_class.from_pretrained(args.model_checkpoint)
#
#     model.to(args.device)
#     model.eval()
#
#     def tokenize(obj):
#         if isinstance(obj, str):
#             return tokenizer.convert_tokens_to_ids(tokenizer.tokenize(obj))
#         if isinstance(obj, dict):
#             return dict((n, tokenize(o)) for n, o in obj.items())
#         return list(tokenize(o) for o in obj)
#
#     history = []
#     while True:
#         raw_text = input(">>> ")
#         while not raw_text:
#             print('Prompt should not be empty!')
#             raw_text = input(">>> ")
#         raw_text = " ".join(list(raw_text.replace(" ", "")))
#         history.append(tokenize(raw_text))
#         with torch.no_grad():
#             out_ids = sample_sequence(history, tokenizer, model, max_length=args.max_length, device=args.device,
#                                       temperature=args.temperature, top_k=args.top_k, top_p=args.top_p,
#                                       no_sample=args.no_sample, min_length=args.min_length)
#         if len(out_ids) > 5 and len(set(out_ids)) == 1:  # 避免类似"哈哈哈哈哈哈..."这种的回复
#             i = random.randint(2, 5)
#             out_ids = out_ids[:i]
#         history.append(out_ids)
#         history = history[-(2 * args.max_history + 1):]
#         history = clip_history(history)
#         out_text = tokenizer.decode(out_ids, skip_special_tokens=True)
#         print(out_text)
#
#
# if __name__ == "__main__":
#     # act = ActionChat()
#     get_history_test()
#     print('done')
