# utils/keyword_analysis.py
import torch
from konlpy.tag import Okt
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel

class MyKeywordExtractor:
    def __init__(self, model_name="klue/bert-base", device=None, min_freq=2):
        self.okt = Okt()
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.device = device or ("mps" if torch.backends.mps.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        self.min_freq = min_freq

    def get_cls_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].cpu().numpy()

    def get_token_embedding(self, word):
        inputs = self.tokenizer(word, return_tensors="pt", truncation=True, max_length=20)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).cpu().numpy()

    def extract_keywords(self, text_list, top_k=15):
        noun_counter = Counter()
        for text in text_list:
            if not isinstance(text, str): continue
            nouns = self.okt.nouns(text)
            noun_counter.update(nouns)

        candidates = [word for word, count in noun_counter.items() if count >= self.min_freq]
        if not candidates:
            return []

        full_text = " ".join(text_list)
        doc_embedding = self.get_cls_embedding(full_text)

        scored_words = []
        for word in candidates:
            token_embed = self.get_token_embedding(word)
            similarity = cosine_similarity(doc_embedding, token_embed)[0][0]
            scored_words.append((word, similarity))

        scored_words.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in scored_words[:top_k]]


def make_keyword(
    후보명,
    df,
    extractor: MyKeywordExtractor,
    종목명="종목명",
    제목="제목",
    내용="내용",
    top_k=15,
    min_freq=2
):
    result_rows = []
    grouped_by_stock = df.groupby(종목명)

    for 종목, group in grouped_by_stock:
        title_list = group[제목].dropna().tolist()
        content_list = group[내용].dropna().tolist()
        text_list = title_list + content_list

        if not text_list:
            continue

        noun_counter = Counter()
        for text in text_list:
            if not isinstance(text, str): continue
            nouns = extractor.okt.nouns(text)
            noun_counter.update(nouns)

        candidates = {noun: count for noun, count in noun_counter.items() if count >= min_freq}
        if not candidates:
            continue

        doc_embedding = extractor.get_cls_embedding(" ".join(text_list))
        scored_keywords = []

        for word, count in candidates.items():
            token_embed = extractor.get_token_embedding(word)
            similarity = cosine_similarity(doc_embedding, token_embed)[0][0]
            scored_keywords.append((word, similarity, count))

        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        top_keywords = scored_keywords[:top_k]
        keyword_dict = {word: freq for word, _, freq in top_keywords}

        result_rows.append({
            "후보": 후보명,
            "종목명": 종목,
            "키워드": keyword_dict
        })

    return result_rows