import numpy as np
from collections import Counter

class Vocabulary():
    
    PADDING = '<pad>'
    UNKNOWN = '<unk>'
    BOS = '<bos>'
    EOS = '<eos>'
    TOKEN_NOT_IN_TAGVOCAB = -1
    PADTOKEN_FOR_TAGVOCAB = -2
    
    def __init__(self, data_gen, data_tag, vocab_size_gen, vocab_size_tag, alltags):
        self.vocab_size_gen = vocab_size_gen
        self.vocab_size_tag = vocab_size_tag
        self.train_gen = data_gen
        self.train_tag = data_tag
        self.alltags = alltags
        
        #create input vocab
        word_freq = Counter([word[0] for word in self.train_gen['tagged_words']])
        self.token2idx, self.idx2token = self.build_dict(word_freq, self.vocab_size_gen)
        self.vocab_size = len(self.token2idx)
        
        #create vocab for every pos tag
        tag_cntr = dict([(tag, Counter()) for tag in self.alltags])
        lis = []
        for sent in self.train_tag:
            for word in sent:
                lis.append(word)
        for tup in lis:
            if tup[1] in self.alltags:
                tag_cntr[tup[1]][tup[0]] += 1
            else:
                tag_cntr['UNKNOWN'][tup[0]] += 1
        self.tag_cntr = tag_cntr
        
        self.tag_specific_vocab = {}
        for tag in tag_cntr:
            tok2ind, ind2tok = self.build_dict(tag_cntr[tag], self.vocab_size_tag, tag)
            voc_size = len(tok2ind)
            self.tag_specific_vocab[tag] = (tok2ind, ind2tok, voc_size)

    def build_dict(self, vocab, vocab_size = None, tag_specific=None):
        """
        Generate word-index-dict
        -Args:
            vocab: Counter object generated from a dataset of interest
        -Returns:
            token2index and index2token: mapping for vocabulary
        """
        # prune vocab
        if vocab_size is not None:
            vocab = list(map(lambda tup: tup[0], vocab.most_common(vocab_size)))
        else:
            vocab = list(vocab.keys())
        
        if tag_specific is not None:
            if tag_specific == 'UNKNOWN':
                vocab = [Vocabulary.UNKNOWN, Vocabulary.EOS] + vocab
            else:
                vocab = [Vocabulary.UNKNOWN] + vocab
        else:
            vocab = [Vocabulary.BOS, Vocabulary.EOS, Vocabulary.PADDING, Vocabulary.UNKNOWN] + vocab
            
        token2idx = dict(zip(vocab, range(len(vocab))))
        idx2token = {v:k for k,v in token2idx.items()}
        return token2idx, idx2token
  
    def get_id(self, token):
        if token in self.token2idx:
            return self.token2idx[token]
        else:
            return self.token2idx[Vocabulary.UNKNOWN]
        
    def get_id_tag(self, token, tag):
        if token in self.tag_specific_vocab[tag][0]:
            return self.tag_specific_vocab[tag][0][token]
        elif token in self.tag_cntr[tag]:
            return self.tag_specific_vocab[tag][0][Vocabulary.UNKNOWN]
        else:
            return Vocabulary.TOKEN_NOT_IN_TAGVOCAB
        
    
    def get_token(self, idx):
        return self.idx2token[idx]
    
    def decode_idx_seq(self, l):
        return list(map(lambda tokid: self.idx2token[tokid], l))
    
    def encode_token_seq(self, l):
        return list(map(lambda tok: self.get_id(tok), l))
    
    def encode_token_seq_tag(self, l, tag):
        return [self.get_id_tag(tok, tag) for tok in l]