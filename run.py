from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os

import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn.functional as F

from transformers import (GPT2LMHeadModel, GPT2Tokenizer,
                                  cached_path, WEIGHTS_NAME, CONFIG_NAME)

import sys
sys.path.append("nlgwebsite")
from server import run

def get_ppl(input_ids, model):
    with torch.no_grad():
        lm_loss, logits = model(input_ids, labels=input_ids)[:2]
        logprobs = F.log_softmax(logits, dim=-1)
        shifted_input_ids = input_ids[:, 1:]
        nlls = (-logprobs[0, :-1, :].gather(1, shifted_input_ids.view(-1, 1))).view(-1).cpu().numpy().tolist()
        ppls = list(map(lambda nll: np.exp(nll), nlls))
    return ppls

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, default='gpt2-xl')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--gpu', type=int, default=0, help="Which GPU to run on")
    args = parser.parse_args()

    print(args)

    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    device = torch.device("cuda:%d" % args.gpu if torch.cuda.is_available() else "cpu")

    tokenizer = GPT2Tokenizer.from_pretrained(args.model_name, do_lower_case=True)
    model = GPT2LMHeadModel.from_pretrained(args.model_name)
    model.to(device)
    model.eval()

    class ppl_annotator:
      def __init__(self, args, model, encoder, device):
        self.args = args
        self.model = model
        self.encoder = encoder
        self.device = device
    
      def getOutput(self, raw_text, div=100): 
        tokens = self.encoder.encode(raw_text)
        input_ids = torch.Tensor(tokens).to(device).view(1, -1).long()
        ppls = get_ppl(input_ids, self.model)
        torch.cuda.empty_cache()
        
        blocks = [ '<span style="background-color:rgba(201, 76, 76, 1)" title="∞">%s</span>' % self.encoder.decode(tokens[0]) ]
        for word, heat in zip(tokens[1:], ppls):
            block = '<span style="background-color:rgba(201, 76, 76, %f)" title="%.0f">%s</span>' % (heat / div, heat, self.encoder.decode([word]))
            if '\n' in block:
                block = block.replace('\n', '') + '<br>'
            blocks.append(block)
        text = ''.join(blocks)
        return text

    run(nlg = ppl_annotator(args, model, tokenizer, device), port=args.port)

if __name__ == '__main__':
    main()

