[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/QM6TDYML)

Team Members:

Dimple Singh
Jay Balaram Sankhe
Debangana Ghosh
Jeremy Anton
Ritika Sanjay Kale


Introduction: The core objective of our study is to gain insights into the ever-changing landscape of movie trends. We want to identify and understand what makes a movie popular at any given time. To achieve this, we focus on several key aspects such as what topics are currently trending, how audiences rate these movies, and the discussions and interactions happening on platforms like TMDb and Reddit.

Our ultimate goal is to uncover the key factors that contribute to a movie's popularity. Our research findings are expected to reveal emerging patterns within the movie industry. They will also provide valuable insights into what audiences like and dislike, and how social media plays a crucial role in determining a movie's success in today's world.

This exploration offers valuable insights for professionals in the film industry, filmmakers, and movie enthusiasts who want to better understand and navigate the ever-changing landscape of movie popularity trends.

The Reddit and TMDB Data Crawler is a Python script developed for the purpose of collecting data from two prominent online platforms: Reddit and The Movie Database (TMDB).

This script serves as a tool to extract vital information related to movies and television shows, including their levels of popularity, and relevant posts and discussions on Reddit. All the collected data is then stored neatly in a PostgreSQL database for later analysis.


Libraries requirements:

1)flask
2)psycopg2
3)pandas
4)io
5)base64
6)matplotlib.pyplot
7)seaborn
8)os



How to Run the code:
Run the python file directly by creating python virtual environment(myenv) or run the bash script.

Create Virtual Environment using virtualenv package
virtualenv -p python3 env
Create postgres database and keep it open for connection
systemctl restart postgresql@16-main.service
Activate the virtual environment
 source env/bin/activate
Run the python script
python3 app.py


