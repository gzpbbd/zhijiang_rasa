# package version:
    rasa                      2.6.2                   
    rasa-sdk                  2.6.0                   
    rasa-x                    0.40.0                  
    tensorflow                2.3.2             

# 文件说明
    actions：所有的action实现
    data/nlu: 所有的 nlu 数据
    data/core: 所有的 rules/stories
    data/domain: 所有的 domain 文件
    code_preparing_data：有关自动标注数据的 python 程序

# 基于表格"问答数据-20211008.xlsx"新增的标注文件为：
    data/nlu/nlu_qa_data.yml
    data/core/rules_qa_data.yml
    data/domain/domain_qa_data.yml
    
    actions/qa_action/* 一些比较规律的 action
    actions/qa_action_special/* 需要特殊处理的 action
    actions/qa_database/* 根据表格"问答数据-20211008.xlsx"抽取出的 csv 文件，作为数据库，供 action 查询数据。

# code_preparing_data 文件夹说明（只是用于自动标注数据，可以不看）
    code_preparing_data/action_process_single_column_inquiry.py: 编写 action 的 python 程序 
    code_preparing_data/nlu_process.py： 标注 NLU 数据的 python 程序
    code_preparing_data/data/qa_database/*: 与 actions/qa_database/* 内容相同
    code_preparing_data/data/schema: 辅助自动标注程序的文件。
    
# 运行命令
    rasa train -d data： 训练模型，并指定 domain 文件在 data 文件夹内
    rasa x -d data： 启动 rasa-x，并指定 domain 文件在 data 文件夹内
    rasa run actions： 启动 action 服务器