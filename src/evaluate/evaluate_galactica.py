from transformers import AutoTokenizer, OPTForCausalLM, StoppingCriteria
import torch

tokenizer = AutoTokenizer.from_pretrained("facebook/galactica-6.7b")
model = OPTForCausalLM.from_pretrained("facebook/galactica-6.7b", device_map="auto")

eos_token_id = int(tokenizer('\n', return_tensors="pt").input_ids[0][0])

input_text = "{}\nThe caption of the Figure/Table mentioned in the above sentence should be:\n".format(referencing_sentence)
input_ids = tokenizer(input_text, return_tensors="pt").input_ids

outputs = model.generate(input_ids, min_new_tokens=5, max_new_tokens=20, eos_token_id=eos_token_id)
# outputs = model.generate(input_ids, max_new_tokens=20)
print(outputs[0])
print(tokenizer.decode(outputs[0]))