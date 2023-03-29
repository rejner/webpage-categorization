from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half().quantize(8).cuda()

history = []
while True:
    print("-"*80)
    user_input = input("User: ")
    if user_input == "quit":
        break
    if user_input == "clear":
        history = []
        continue
    response, history = model.chat(tokenizer, user_input, history=history)
    print("Chatbot: ", response)
    print("-"*80)


# response, history = model.chat(tokenizer, "Hello, do you speak english?", history=[])
# print(response)
# response, history = model.chat(tokenizer, "And how are you doing?", history=history)
# print(response)