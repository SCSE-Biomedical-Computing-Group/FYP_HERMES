import os
# import sys
import yaml 
import logging
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

with open(Path(__file__).parent / "backend_radmix.yaml", 'r') as f:
    valuesYaml = yaml.load(f, Loader=yaml.FullLoader)
    
os.environ['CUDA_VISIBLE_DEVICES'] = str(valuesYaml['CUDA_VISIBLE_DEVICES'])

class radmix:
    
    def __init__(self, cfg):        
        
        self.cfg = {}
        self.cfg['max_new_tokens'] = cfg['radmix']['max_new_tokens']
        self.cfg['repetition_penalty'] = cfg['radmix']['repetition_penalty']
        self.cfg['model_path'] = cfg['radmix']['model_path']

        base_model_id = "mistralai/Mixtral-8x7B-v0.1"
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            # use_auth_token=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model_id, 
            add_bos_token=True, 
            trust_remote_code=True
        )
        self.ft_model = PeftModel.from_pretrained(self.base_model, self.cfg['model_path'])
        self.model = self.ft_model
        self.cfg['model'] = self.ft_model
        # logging.info(f'Loaded model {path_to_model}')
        logging.info(f'Loadded mode {cfg}')
        
    def __call__(self, findings):
    # def generate_inference(findings):
        model_input = self.tokenizer(findings, return_tensors="pt").to("cuda")
        self.ft_model.eval()
        with torch.no_grad():
            result = self.tokenizer.decode(
                self.ft_model.generate(
                    **model_input, 
                    max_new_tokens=self.cfg['max_new_tokens'], 
                    repetition_penalty=self.cfg['repetition_penalty'])[0], 
                skip_special_tokens=True)
        return result