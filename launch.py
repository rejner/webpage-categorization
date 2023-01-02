from flask import Flask, request, render_template
from webcat.worker import WebCatWorker

app = Flask(__name__)

# Initialize the WebCatWorker instance
worker = WebCatWorker()

@app.route('/')
def index():
    # Render the homepage template
    return render_template('index.html')

@app.route('/interactive')
def index_interactive():
    # Render the homepage template
    return render_template('interactive.html')

@app.route('/process/text', methods=['POST'])
def process_text():
    # get text from the request
    input = request.form.get('input')
    input = input.strip()
    categories, text = worker.process_raw_text(input)
    # re-render with the new data
    return render_template('interactive.html', categories=categories, text=text, original_input=input)

@app.route('/process', methods=['POST'])
def process_files():
    # Get the list of file paths from the request
    files_path = request.form.getlist('files_path')
    print(files_path)
    # Process the files
    files_list, categories_list, text_list = worker.process_files_batch(files_path, batch_size=12)
    results = [{'file': f, 'categories': c, 'text': t} for f, c, t in zip(files_list, categories_list, text_list)]
    # format each category as a string with 2 decimal places
    for result in results:
        categories = result['categories']
        categories = {k: f"{v:.2f}" for k, v in categories.items()}
        result['categories'] = categories
    # Return a response to the client
    # re-render with the new data
    return render_template('index.html', results=results)
    # return "Success"

if __name__ == "__main__":
    app.run()
