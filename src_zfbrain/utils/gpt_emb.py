import os
import time
import numpy as np
from .evaluate_load_data import data_loader
from openai import OpenAI
from .utils import sort_scores


input = input('You are about to using openai api, check the size of dataset, enter y to continue:')
assert input == 'y'

OPENAI_API_KEY=''
client = OpenAI(api_key=OPENAI_API_KEY)

MODEL="text-embedding-3-large" # text-embedding-3-small, text-embedding-3-large	


def cosine_similarity(embedding1: list, embedding2: list):
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    similarity = dot_product / (norm1 * norm2)
    
    return similarity


def cosine_similarity_scores(emb_query: list, emb_candidate_list: list[list]):
    scores = []
    for emb_candidate in emb_candidate_list:
        similarity = cosine_similarity(emb_query, emb_candidate)
        scores.append(similarity)

    return scores


def text_2_emb(text, model):
    response = client.embeddings.create(
        input=text,
        model=model
    )

    return response.data[0].embedding
    

def gpt_emb_by_paper(queries, targets, candidates, candidate_labels, paper_id, threshold='N/A'):
    paper_head_start_time = time.time()
    
    total = 0
    recall_1 = 0
    recall_5 = 0
    recall_n_2 = 0
    mrr = 0
    logs = []
    n_2 = round(len(candidates)/2)

    candidate_embs = []

    for candidate in candidates:
        emb = text_2_emb(candidate, MODEL)
        candidate_embs.append(emb)
    
    paper_head_time = time.time() - paper_head_start_time

    for query, target in zip(queries, targets):
        sample_start_time = time.time()
        
        total += 1

        embeddings_query = text_2_emb(query, MODEL)
        similarities = cosine_similarity_scores(embeddings_query, candidate_embs)

        sorted_scores, sorted_labels, gt_rank = sort_scores(target, similarities, candidate_labels, threshold)

        if target == sorted_labels[0]:
            recall_1 += 1
        if target in sorted_labels[:5]:
            recall_5 += 1
        if target in sorted_labels[:n_2]:
            recall_n_2 += 1
        mrr += 1/gt_rank

        sample_time = time.time() - sample_start_time

        log = {}
        log['method'] = 'sbert'
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

