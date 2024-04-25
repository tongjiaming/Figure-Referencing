from transformers import AutoTokenizer, OPTForCausalLM, StoppingCriteria
from .utils import sort_scores
import torch
import time

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained("facebook/galactica-6.7b")
model = OPTForCausalLM.from_pretrained("facebook/galactica-6.7b")
model.to(device)

DATA_PATH = '../output/PMCOA_out.json'

def calculate_score(candidate, query):
    prompt = candidate + ' ' + query
    
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    
    logits = model(input_ids).logits
    query_position = len(tokenizer(candidate, return_tensors="pt").input_ids[0])

    query_logits = logits[0, query_position-1: -1]
    query_ids = input_ids[0][query_position:]

    query_probs = torch.softmax(query_logits, dim=-1)
    probs = torch.softmax(logits[0], dim=-1)

    acc_prob = 1
    for prob, query_id in zip(query_probs, query_ids):
        value, idx = torch.max(prob, dim=0)
        acc_prob *= prob[query_id]
            
    return acc_prob


def galactica_by_paper(queries, targets, candidates, candidate_labels, paper_id, threshold=0):
    total = 0
    recall_1 = 0
    recall_5 = 0
    recall_n_2 = 0
    mrr = 0
    logs = []
    n_2 = round(len(candidates)/2)
    
    paper_head_time = 0
    
    with torch.no_grad():
        for query, target in zip(queries, targets):
            sample_start_time = time.time()

            total = total + 1
            
            candidate_scores = []
            for candidate in candidates:
                score = calculate_score(candidate, query)
                candidate_scores.append(score)

            sorted_scores, sorted_labels, gt_rank = sort_scores(target, candidate_scores, candidate_labels, threshold)
            
            if target == sorted_labels[0]:
                recall_1 += 1
            if target in sorted_labels[:5]:
                recall_5 += 1
            if target in sorted_labels[:n_2]:
                recall_n_2 += 1
            mrr += 1/gt_rank
    
            sample_time = time.time() - sample_start_time
    
            log = {}
            log['method'] = 'galactica'
            log['paper_id'] = paper_id
            log['query'] = query
            log['target'] = target
            log['threshold'] = threshold
            log['top_5_socres'] = [float(score) for score in sorted_scores[:5]]
            log['top_5_labels'] = sorted_labels[:5]
            log['gt_rank'] = gt_rank
            log['paper_head_time'] = paper_head_time
            log['sample_time'] = sample_time
            logs.append(log)
    
    return total, recall_1, recall_5, recall_n_2, mrr, logs
