import re
from urlextract import URLExtract
from webcat.models.nlp.ner.tweetner7 import TweetNER7
from webcat.models.nlp.classification.joeddav_xlm_roberta import XLMRobertaLarge


url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_pattern = r'[\w\.-]+@[\w\.-]+'

class WebCatNLP:
    def __init__(self):
        self.classification_labels = ["drugs", "hacking", "fraud", "counterfeit goods", "cybercrime", "cryptocurrency"]
        self.classifier = XLMRobertaLarge(self.classification_labels)
        self.ner_model = TweetNER7()
        self.extractor = URLExtract()

    def classify(self, inputs):
        if not isinstance(inputs, list):
            inputs = [inputs]
        inputs = [self.clear_text(input) for input in inputs]
        categories = self.classifier.classify(inputs)
        return categories
    
    def perform_NER(self, inputs):
        if not isinstance(inputs, list):
            inputs = [inputs]
        inputs = [self.clear_text(input) for input in inputs]
        entities, text = self.ner_model.classify(inputs)
        return entities, text
    
    def clear_text(self, text):
        # remove urls
        # urls = re.findall(url_pattern, text)
        text = re.sub(url_pattern, '', text)
        # remove emails
        # emails = re.findall(email_pattern, text)
        text = re.sub(email_pattern, '', text)
        # remove html tags
        text = re.sub(r'<[^>]*>', '', text)
        return text


if __name__ == "__main__":
    # nlp = WebCatNLP()
    # from constants import dummy_corpus
    # for text in dummy_corpus:
    #     print("\n" + text)
    #     print(nlp.classify(text))
    test = "New Signup http://stackoverflow.onion/questions/74394695/how-does-one-fix-when-torch-cant-find-cuda-error-version-libcublaslt-so-11-no Link - http://abraxasdegupusel.onion/register/z5hSPCXbWZ « Last post by <person> ginga43 </person>  on Today at 03:23:38 pm » Agora as well if you need it: http://agorahooawayyfoe.onion/register/BU7ZdqhNcgAbraxas"
    extractor = URLExtract()
    urls = extractor.find_urls(test)
    for url in urls:
        test = test.replace(url, "{{URL}}")
    print(test)
