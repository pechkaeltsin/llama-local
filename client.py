import requests


def generate_text(prompt):
    url = 'http://10.0.50.2:5000/generate'
    data = {'prompt': prompt}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        return response.json()['text']
    else:
        return f"Error: {response.status_code}"


if __name__ == '__main__':
    prompt = "Что такое стройка?"
    generated_text = generate_text(prompt)
    print(generated_text)
