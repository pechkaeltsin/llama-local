import torch
from transformers import LlamaForCausalLM, BertTokenizer, LlamaConfig


def load_model_from_pth_files(model_dir, model_files):
    # Создание конфигурации модели на основе предполагаемых значений
    config = LlamaConfig(
        vocab_size=50265,
        n_positions=2048,
        n_ctx=2048,
        n_embd=4096,
        n_layer=24,
        n_head=16,
        layer_norm_epsilon=1e-5,
        initializer_range=0.02
    )

    # Создание модели с данной конфигурацией
    model = LlamaForCausalLM(config)

    # Загрузка весов из файлов .pth
    state_dict = {}
    for file_name in model_files:
        part_state_dict = torch.load(f"{model_dir}/{file_name}", map_location=torch.device('cpu'))
        state_dict.update(part_state_dict)

    # Обновление состояния модели
    model.load_state_dict(state_dict, strict=False)
    return model


def load_model(model_dir):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model_files = ['consolidated.00.pth', 'consolidated.01.pth', 'consolidated.02.pth', 'consolidated.03.pth',
                   'consolidated.04.pth', 'consolidated.05.pth', 'consolidated.06.pth', 'consolidated.07.pth']
    model = load_model_from_pth_files(model_dir, model_files)
    return tokenizer, model


def generate_response(model, tokenizer, text, max_length=50):
    input_ids = tokenizer(text, return_tensors="pt")["input_ids"]
    output_ids = model.generate(input_ids, max_length=max_length)
    response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return response


if __name__ == "__main__":
    tokenizer, model = load_model("model/llama-3-pytorch-70b-v1")
    input_text = "Привет. Расскажи анекдот."
    response = generate_response(model, tokenizer, input_text)
    print(response)
