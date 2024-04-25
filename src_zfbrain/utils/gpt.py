import os
import time
from .utils import data_loader
from openai import OpenAI


input = input('You are about to using openai api, check the size of dataset, enter y to continue:')
assert input == 'y'

OPENAI_API_KEY=''
client = OpenAI(api_key=OPENAI_API_KEY)


def post_process(prediction):
    prediction = prediction.strip().replace('[', '').replace('[', '')


def gpt_by_paper(queries, targets, candidates, candidate_labels, paper_id, threshold='N/A'):
    paper_head_start_time = time.time()
    
    total = 0
    tp = 0
    logs = []
    
    system_message = "You are a scientific assistant and your job is to identify the most appropriate figure or table to reference in a given sentence. I will give you several lines with the format of 'label:caption'. For example: 'Fig1:This is a caption'. Do not generate anything other than the label of the appropriate candidate. If none of the candidate figures and tables are appropriate, generate 'None'. Do not go online."

    # query_paper_id = 'PMC8998009'

    label2caption = {}
    for candidate, label in zip(candidates, candidate_labels):
        label2caption[label] = candidate

        concatenated_candidates = ''.join([
            f"- {label}: {caption}\n" for label, caption in label2caption.items()
        ])

    paper_head_time = time.time() - paper_head_start_time

    for query, target in zip(queries, targets):
        sample_start_time = time.time()
        
        total += 1
        
        user_message = f"""
        I need to reference a figure or table at the position indicated by <ref> in the following sentence:
        
        {query}
        
        Below are the labels and captions of all candidate figures and tables. Which should I reference?
        
        {concatenated_candidates}
        """.strip()
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ]
        )

        prediction = completion.choices[0].message.content

        sample_time = time.time() - sample_start_time

        log = {}
        log['paper_id'] = paper_id
        log['query'] = query
        log['target'] = target
        log['top_5_socres'] = 'N/A'
        log['top_5_labels'] = prediction
        log['gt_rank'] = 'N/A'
        log['method'] = 'gpt'
        log['paper_head_time'] = paper_head_time
        log['sample_time'] = sample_time
        log['threshold'] = threshold
        logs.append(log)

        print(prediction)
        print(target)

        if prediction == target:
            tp += 1

    return total, tp, 0, 0, 0, logs


def test():
    DATA_PATH = '../data/pmcoa/jsonl/pmcoa_test.jsonl'
    loader = data_loader(DATA_PATH)

    data = None
    while data == None:
        data = next(loader)
        
    gpt_by_paper(*data)


if __name__ == '__main__':
    from evaluate_load_data import data_loader
    from openai import OpenAI
    test()
