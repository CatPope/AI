# import os
# import sys
# from dotenv import load_dotenv
#
# load_dotenv()
# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# prompt_path = os.getenv("PROMPT_PATH")
# absolute_prompt_path = os.path.join(base_dir, prompt_path)
# sys.path.insert(0, absolute_prompt_path)
#
#
# import examples_tpl
# import summarys_pmpt
# import titles_pmpt
#
# examples = examples_tpl.get_tpl()
# summarys = summarys_pmpt.get_prompt()
# titles = titles_pmpt.get_prompt()
#
# for i in range(len(titles)):
#     if i > 0:
#         examples[i]["context"] = summarys[i]
#     examples[i]["answer"] = titles[i]
#
# print(examples)
