from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
#import tensorrt

#print(tensorrt.__version__)
#tensorrt.Builder(tensorrt.Logger())

flatten = lambda l: [item for sublist in l for item in sublist]

class Language_Model():
    def __init__(self):
        return #LAPTOP TEST!! DELETE THIS LINE!
        self.tokenizer = GPT2Tokenizer.from_pretrained("af1tang/personaGPT", padding_side='left')
        self.model = GPT2LMHeadModel.from_pretrained("af1tang/personaGPT")
        if torch.cuda.is_available():
            self.model = self.model.cuda()
                
        self.personas = []
        f = open('facts.txt','r')
        for l in f:
            response = l + self.tokenizer.eos_token
            print(response)
            self.personas.append(response)
        self.personas = self.tokenizer.encode(''.join(['<|p2|>'] + self.personas + ['<|sep|>'] + ['<|start|>']))

        self.dialogue_history = []

        
        
    def to_data(x):
        if torch.cuda.is_available():
            x = x.cpu()
        return x.data.numpy()

    def to_var(x):
        if not torch.is_tensor(x):
            x = torch.Tensor(x)
        if torch.cuda.is_available():
            x = x.cuda()
        return x

    def display_dialog_history(self, dialog_hx):
        for j, line in enumerate(dialog_hx):
            msg = self.tokenizer.decode(line)
            if j %2 == 0:
                print(">> User: "+ msg)
            else:
                print("Pepper: "+msg)
                print()

    def generate_next(self, bot_input_ids, do_sample=True, top_k=10, top_p=.92,
                    max_length=1000):
        full_msg = self.model.generate(bot_input_ids, do_sample=True,
                                                top_k=top_k, top_p=top_p, 
                                                max_length=max_length, pad_token_id=self.tokenizer.eos_token_id)
        msg = self.to_data(full_msg.detach()[0])[bot_input_ids.shape[-1]:]
        return msg

    def generate_response(self, prompt):
        return "Language model OFFLINE"#LAPTOP TEST DELETE THIS LINE
        user_inp = self.tokenizer.encode(prompt + self.tokenizer.eos_token)
        self.dialogue_history.append(user_inp)
            
        bot_input_ids = self.to_var([self.personas + flatten(self.dialogue_history)]).long()
        msg = self.generate_next(bot_input_ids)
        self.dialogue_history.append(msg)
        print("Pepper: {}".format(self.tokenizer.decode(msg, skip_special_tokens=True)))

        return self.tokenizer.decode(msg, skip_special_tokens=True)