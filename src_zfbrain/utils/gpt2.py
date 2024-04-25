import os
import time
from openai import OpenAI


input = input('You are about to using openai api, check the size of dataset, enter y to continue:')
assert input == 'y'

OPENAI_API_KEY=''
client = OpenAI(api_key=OPENAI_API_KEY)


def gpt_by_paper_2(queries, targets, candidates, candidate_labels, paper_id, threshold='N/A'):
    paper_head_start_time = time.time()
    
    total = 0
    recall_1 = 0
    recall_5 = 0
    recall_n_2 = 0
    mrr = 0
    logs = []
    n_2 = round(len(candidates)/2)
    
    system_message = "You are a scientific assistant and your job is to find out the most related caption based on the given referencing vsentence. I will give you several lines with the format of 'index:caption'. For example: '<index>1</index>:<caption>This is a caption.</caption>'. Do not generate anything other than the index of the appropriate caption."

    index = 0
    concatenated_candidates = ''
    for caption in candidates:
        concatenated_candidates += f"<index>{index}</index>: <caption>{caption}</caption>\n"
        index += 1

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
            ],
            max_tokens = 1,
            logprobs = True,
            top_logprobs = 20,
            presence_penalty = -2
        )

        predictions = []
        scores = []
        for item in completion.choices[0].logprobs.content[0].top_logprobs:
            index = item.token
            try:
                index = int(index)
                if index < len(candidate_labels):
                    predictions.append(candidate_labels[index])
                    scores.append(item.logprob)
            except ValueError:
                pass
                
        print(predictions)
        print(target)

        if target in predictions:
            gt_rank = predictions.index(target) + 1
        else:
            gt_rank = len(candidate_labels)

        if predictions:
            if target == predictions[0]:
                recall_1 += 1
            if target in predictions[:5]:
                recall_5 += 1
            if target in predictions[:n_2]:
                recall_n_2 += 1
                
        mrr += 1/gt_rank

        sample_time = time.time() - sample_start_time

        log = {}
        log['paper_id'] = paper_id
        log['query'] = query
        log['target'] = target
        log['top_5_socres'] = [float(score) for score in scores[:5]]
        log['top_5_labels'] = predictions[:5]
        log['gt_rank'] = gt_rank
        log['method'] = 'gpt_2'
        log['paper_head_time'] = paper_head_time
        log['sample_time'] = sample_time
        log['threshold'] = threshold
        log['token_usage'] = completion.usage.total_tokens
        logs.append(log)

    return total, recall_1, recall_5, recall_n_2, mrr, logs
