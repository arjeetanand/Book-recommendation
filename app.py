from flask import Flask, render_template, request
from PIL import Image
import json
from Classifier import KNearestNeighbours
from bs4 import BeautifulSoup
import requests
import io
import PIL.Image
from urllib.request import urlopen
from Classifier import KNearestNeighbours

app = Flask(__name__)

with open('./Data/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('./Data/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)
hdr = {'User-Agent': 'Mozilla/5.0'}


# def get_movie_info(imdb_link):
#     url_data = requests.get(imdb_link, headers=hdr).text
#     s_data = BeautifulSoup(url_data, 'html.parser')
#     imdb_content = s_data.find("meta", property="og:description")
#     movie_descr = imdb_content.attrs['content']
#     movie_descr = str(movie_descr).split('.')
#     movie_director = movie_descr[0]
#     movie_cast = str(movie_descr[1]).replace('With', 'Cast: ').strip()
#     movie_story = 'Story: ' + str(movie_descr[2]).strip() + '.'
#     rating = s_data.find("span", class_="sc-bde20123-1 iZlgcd").text
#     movie_rating = 'Total Rating count: ' + str(rating)
#     return movie_director, movie_cast, movie_story, movie_rating


def KNN_Movie_Recommender(test_point, k):
    target = [0 for item in movie_titles]
    model = KNearestNeighbours(data, target, test_point, k=k)
    model.fit()
    table = []
    for i in model.indices:
        movie_title = movie_titles[i][0]
        movie_genre = movie_titles[i][1]
        movie_imdb_link = movie_titles[i][3]
        movie_rating = data[i][-1]
        table.append([movie_title, movie_genre, movie_imdb_link, movie_rating])
    return table


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        select_option = request.form.get('categorySelect')
        if select_option == 'Movie based':
            select_movie = request.form.get('movieSelect')
            if select_movie != '--Select--':
                no_of_reco = int(request.form.get('noOfRecommendations'))
                genres = None
                for movie in movie_titles:
                    if movie[0] == select_movie:
                        genres = data[movie_titles.index(movie)]
                        break
                if genres is not None:
                    test_points = genres
                    table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
                    table.pop(0)
                    return render_template('recommendations.html', table=table, genres=genres, movies=movie_titles)
                else:
                    error_message = 'Selected movie not found in the database.'
                    return render_template('index.html', error_message=error_message)
            else:
                error_message = 'Please select a movie!'
                return render_template('index.html', error_message=error_message)

        elif select_option == 'Genre based':
        # select_option = request.form.get('categorySelect')
            sel_genres = request.form.getlist('genres')
            if sel_genres:
                imdb_score = int(request.form.get('imdbScore'))
                no_of_reco = int(request.form.get('noOfRecommendations'))
                genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
                          'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
                          'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
                test_point = [1 if genre in sel_genres else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                return render_template('recommendations.html', table=table)
            else:
                error_message = 'Please select genres!'
                return render_template('index.html', error_message=error_message)
    else:

        genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
                  'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
                  'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
        movies = [title[0] for title in movie_titles]
        return render_template('index.html', genres=genres, movies=movies)


if __name__ == '__main__':
    app.run(debug=True)
