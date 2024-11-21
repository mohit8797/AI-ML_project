from flask import Flask, render_template, request
import pickle
import numpy as np

# Load the necessary data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)


@app.route('/')
def index():
    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        rating=list(popular_df['avg_rating'].values)
    )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    # Normalize the user input (lowercase and strip whitespace)
    user_input = user_input.strip().lower()

    # Check if the book exists in the dataset
    if user_input not in pt.index.str.lower():
        return render_template('recommend.html', message="Book not found. Please try a different book.")

    # Get the index of the book
    index = np.where(pt.index.str.lower() == user_input)[0][0]

    # Get similar books based on similarity scores
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]

        if not temp_df.empty:
            book_title = temp_df.drop_duplicates('Book-Title')['Book-Title'].values
            book_author = temp_df.drop_duplicates('Book-Title')['Book-Author'].values
            book_image = temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values

            # Check if the necessary fields are available
            if book_title and book_image:
                item.extend(
                    [book_title[0], book_author[0], book_image[0]])  # Add the book data only if title and image exist
                data.append(item)

    # Check if no valid data was found
    if not data:
        return render_template('recommend.html', message="No valid recommendations available. Please try again.")

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
