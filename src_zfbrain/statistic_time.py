import json

def calculate_average_score(path):
    total_sample_time = 0
    total_paper_head_time = 0
    total_token_usage = 0
    total = 0

    with open(path, 'r') as file:
        for line in file:
            data = json.loads(line.strip())
            sample_time = data.get('sample_time')
            paper_head_time = data.get('paper_head_time')
            token_usage = data.get('token_usage', 0)
            
            total_sample_time += sample_time
            total_paper_head_time += paper_head_time
            total_token_usage += token_usage
            total += 1

        average_sample_time = total_sample_time / total
        average_paper_head_time = total_paper_head_time / total

    return average_sample_time, average_paper_head_time, total_token_usage


if __name__ == '__main__':
    filename = 'gpt_3.jsonl'
    log_path = f'result_log/{filename}'
    average_sample_time, average_paper_head_time, total_token_usage = calculate_average_score(log_path)

    
    print(filename)
    print(f"average_sample_time: {'{:.2e}'.format(average_sample_time)}")
    print(f"average_paper_head_time: {'{:.2e}'.format(average_paper_head_time)}")
    print(f"total_token_usage: {total_token_usage}")
