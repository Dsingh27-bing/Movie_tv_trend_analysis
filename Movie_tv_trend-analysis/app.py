from flask import Flask, render_template, jsonify, request
import psycopg2
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as font_manager
import os
from flask import Flask, render_template, jsonify, request, url_for


app = Flask(__name__)


def connect_to_postgresql():
    try:
        connection = psycopg2.connect("dbname=crawler user=postgres")
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        return None    

@app.route('/')
def show_links():
    return render_template('index.html')


# toxicity across tv series -> tv_genre.html

@app.route('/genre_tv')
def genre_tv():
    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """SELECT genre, SUM(normal) AS total_normal, SUM(flag) AS total_flag 
                       FROM (SELECT unnest(string_to_array(regexp_replace(genres::text, '[{}" ]', '', 'g'), ',')) AS genre, normal, flag 
                             FROM tmdb_tv_new) AS unnested_data 
                       GROUP BY genre 
                       ORDER BY genre"""
            cursor.execute(query)
            data_given = cursor.fetchall()
            result = [{'genre': row[0], 'total_normal': row[1], 'total_flag': row[2]} for row in data_given]
            return render_template('tv_genre.html', genre_data=result)

        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL:", error)
            # Return an error page or message
            return "An error occurred while fetching data"
        finally:
            cursor.close()
            connection.close()
    else:
        # Return an error page or message
        return "Database connection failed"


# toxicity across movies -> movies_genre.html

@app.route('/genre_movies')
def genre_movies():
    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """SELECT genre, SUM(normal) AS total_normal, SUM(flag) AS total_flag 
                       FROM (SELECT unnest(string_to_array(regexp_replace(genres::text, '[{}" ]', '', 'g'), ',')) AS genre, normal, flag 
                             FROM tmdb_movies_new) AS unnested_data 
                       GROUP BY genre 
                       ORDER BY genre"""
            cursor.execute(query)
            data_given = cursor.fetchall()
            result = [{'genre': row[0], 'total_normal': row[1], 'total_flag': row[2]} for row in data_given]
            return render_template('movies_genre.html', genre_data=result)

        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL:", error)
            # Return an error page or message
            return "An error occurred while fetching data"
        finally:
            cursor.close()
            connection.close()
    else:
        # Return an error page or message
        return "Database connection failed"
    

# movies popularity by total mentions -> dynamic_movie.html

@app.route('/movies_list')
def get_option():
    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """SELECT rm.name, SUM(mc.comment_count) AS total_comment_count
                       FROM reddit_movies AS rm
                       JOIN (
                           SELECT post_id, COUNT(*) AS comment_count
                           FROM movies_comments
                           GROUP BY post_id
                       ) AS mc
                       ON rm.post_id = mc.post_id
                       GROUP BY rm.name
                       ORDER BY total_comment_count DESC;"""
            cursor.execute(query)
            data_given = cursor.fetchall()
            data = pd.DataFrame(data_given, columns=['title', 'popularity'])
            return render_template('dynamic_movie.html', movies=data.to_dict(orient='records'))
        
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching and plotting data"
        finally:
            cursor.close()
            connection.close()
    else:
        return "Database connection failed"

# Tv popularity by total mentions -> dynamic_tv.html
@app.route('/tv_list')
def get_option_tv():
    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """SELECT rm.name, SUM(mc.comment_count) AS total_comment_count
                       FROM reddit_tv AS rm
                       JOIN (
                           SELECT post_id, COUNT(*) AS comment_count
                           FROM tv_comments
                           GROUP BY post_id
                       ) AS mc
                       ON rm.post_id = mc.post_id
                       GROUP BY rm.name
                       ORDER BY total_comment_count DESC;"""
            cursor.execute(query)
            data_given = cursor.fetchall()
            data = pd.DataFrame(data_given, columns=['title', 'popularity'])
            return render_template('dynamic_tv.html', tv=data.to_dict(orient='records'))
        
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching and plotting data"
        finally:
            cursor.close()
            connection.close()
    else:
        return "Database connection failed"


# movies popularity w/ genres by tmdb (original stuff) -> dynamic_tmdb_movie.html

@app.route('/tmdb_movies')
def get_tmdb_movies_list():
    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """select title, popularity, genres from tmdb_movies_new order by popularity desc;"""
            cursor.execute(query)
            data_given = cursor.fetchall()
            data = pd.DataFrame(data_given, columns=['title', 'popularity', 'genres'])
            return render_template('tmdb_movies.html', movies=data.to_dict(orient='records'))
        
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching and plotting data"
        finally:
            cursor.close()
            connection.close()
    else:
        return "Database connection failed"
# tv popularity by tmdb (original stuff) -> dynamic_tmdb_tv.html
@app.route('/tmdb_tv')
def get_tmdb_tv_list():
    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """select title, popularity, genres from tmdb_tv_new order by popularity desc;"""
            cursor.execute(query)
            data_given = cursor.fetchall()
            data = pd.DataFrame(data_given, columns=['title', 'popularity', 'genres'])
            return render_template('tmdb_tv.html', tv=data.to_dict(orient='records'))
        
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching and plotting data"
        finally:
            cursor.close()
            connection.close()
    else:
        return "Database connection failed"
    


@app.route('/generate_movie_plot', methods=['POST'])
def generate_movie_plot():
    n = request.form.get('n', default=5, type=int)  # Get 'n' from query parameter

    # Calculate bar width based on the number of movies
    bar_width = min(0.8, 10.0 / max(n, 1))  



    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """SELECT rm.name, SUM(mc.comment_count) AS total_comment_count
                       FROM reddit_movies AS rm
                       JOIN (
                           SELECT post_id, COUNT(*) AS comment_count
                           FROM movies_comments
                           GROUP BY post_id
                       ) AS mc
                       ON rm.post_id = mc.post_id
                       GROUP BY rm.name
                       ORDER BY total_comment_count DESC;"""
            cursor.execute(query)
            data_given = cursor.fetchall()
            data = pd.DataFrame(data_given, columns=['title', 'popularity'])
            data_custom = data[data["popularity"] > 0].sort_values(by="popularity", ascending=False).head(n)

# Set the aesthetic style of the plots
            sns.set_style("white")
            sns.set_palette("pastel")

            
            fig, ax = plt.subplots(figsize=(14, 8))
            fig.set_facecolor("#fffcf2")
            ax.set_facecolor("#fffcf2")

            bar_plot = sns.barplot(x="title", y="popularity",
                                    data=data_custom, palette="Set2", 
                                    edgecolor="white",
                                    width=bar_width)
            for bar in bar_plot.patches:
                bar.set_linestyle("-")
                bar.set_linewidth(1)

            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.7)

            
            plt.xlabel("Movie Title", fontsize=14)
            plt.ylabel("Popularity", fontsize=14)
            plt.title(f"Top {n} Popular Movies", fontsize=16)
            plt.xticks(rotation=45, ha="right")

            plt.tight_layout()
            # Save the plot
            plot_filename = f'top_{n}_movies.png'
            plot_path = os.path.join(app.root_path, 'static', 'img', plot_filename)
            plt.savefig(plot_path, facecolor=fig.get_facecolor())
            plt.close()

            # Generate the URL for the saved plot
            plot_url = url_for('static', filename=f'img/{plot_filename}')

            # Return the URL for the plot in the JSON response
            return jsonify({'plot_url': plot_url})

        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching and plotting data"
        finally:
            cursor.close()
            connection.close()
    else:
        return "Database connection failed"


# returns json plots
@app.route('/generate_tv_plot', methods=['POST'])
def generate_tv_plot():
    n = request.form.get('n', default=5, type=int)  # Get 'n' from query parameter

    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """SELECT rm.name, SUM(mc.comment_count) AS total_comment_count
                        FROM reddit_tv AS rm
                        JOIN (
                            SELECT post_id, COUNT(*) AS comment_count
                            FROM tv_comments
                            GROUP BY post_id
                        ) AS mc
                        ON rm.post_id = mc.post_id
                        GROUP BY rm.name
                        order by total_comment_count desc;"""
            cursor.execute(query)
            data_given = cursor.fetchall()
            data = pd.DataFrame(data_given, columns=['title', 'popularity'])
            data_custom = data[data["popularity"] > 0].sort_values(by="popularity", ascending=False).head(n)

# Set the aesthetic style of the plots
            sns.set_style("white")
            sns.set_palette("pastel")

            
            fig, ax = plt.subplots(figsize=(14, 8))
            fig.set_facecolor("#fffcf2")
            ax.set_facecolor("#fffcf2")

            bar_plot = sns.barplot(x="title", y="popularity", data=data_custom, palette="Set2", edgecolor="white")
            for bar in bar_plot.patches:
                bar.set_linestyle("-")
                bar.set_linewidth(1)

            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.7)

           
            plt.xlabel("Show Title", fontsize=14)
            plt.ylabel("Popularity", fontsize=14)
            plt.title(f"Top {n} Popular Shows", fontsize=16)
            plt.xticks(rotation=45, ha="right")

            plt.tight_layout()

            # Save the plot
            plot_filename = f'top_{n}_tv.png'
            plot_path = os.path.join(app.root_path, 'static', 'img', plot_filename)
            plt.savefig(plot_path, facecolor=fig.get_facecolor())
            plt.close()

            # Generate the URL for the saved plot
            plot_url = url_for('static', filename=f'img/{plot_filename}')

            # Return the URL for the plot in the JSON response
            return jsonify({'plot_url': plot_url})

        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching and plotting data"
        finally:
            cursor.close()
            connection.close()
    else:
        return "Database connection failed"
    
    
@app.route('/tv_toxic_list')
def toxic_tv():
    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """UPDATE tmdb_tv_new AS tb                                                      
                SET
                    flag = COALESCE(subquery.flag_count, 0),
                    normal = COALESCE(subquery.normal_count, 0)
                FROM (
                    SELECT
                        name,
                        SUM(flag_count) AS flag_count,
                        SUM(normal_count) AS normal_count
                    FROM
                        reddit_tv
                    GROUP BY
                        name
                ) AS subquery
                WHERE tb.title = subquery.name;
            """
            cursor.execute(query)
            query = """SELECT * FROM tmdb_tv_new
                        ORDER BY flag DESC;
                        """
            cursor.execute(query)
            data_given = cursor.fetchall()
            result = [{'title':row[0], 'normal':row[3], 'flag':row[4]} for row in data_given]
            return render_template('dynamic_tv_toxic.html', toxic_tv_shows=result)

        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL:", error)
            # Return an error page or message
            return "An error occurred while fetching data"
        finally:
            cursor.close()
            connection.close()
    else:
        # Return an error page or message
        return "Database connection failed"
    

# generate_tv_toxic_plot
@app.route('/generate_tv_toxic_plot', methods=['POST'])
def generate_tv_toxic_plot():
    n = request.form.get('n', default=5, type=int)

    # Calculate bar width based on the number of movies
    bar_width = min(0.8, 10.0 / max(n, 1)) 

    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """SELECT * FROM tmdb_tv_new
                        ORDER BY flag DESC;
                        """
            cursor.execute(query)
            data_given = cursor.fetchall()
            data = pd.DataFrame(data_given, columns=['title', 'popularity', 'genre','normal', 'flag'])
            data_custom = data[data["flag"] > 0].sort_values(by="flag", ascending=False).head(n)

# Set the aesthetic style of the plots
            sns.set_style("white")
            sns.set_palette("pastel")

            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            fig.set_facecolor("#fffcf2")
            fig.set_facecolor("#fffcf2")

            bar_plot = sns.barplot(x="title", y="flag", data=data_custom, palette="Set2", edgecolor="white")
            for bar in bar_plot.patches:
                bar.set_linestyle("-")
                bar.set_linewidth(1)
                bar.width = bar_width


          
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.7)

           
            plt.xlabel("Show Title", fontsize=14)
            plt.ylabel("Flag", fontsize=14)
            plt.title(f"Top {n} Toxic Shows", fontsize=16)
            plt.xticks(rotation=45, ha="right")

            plt.tight_layout()

            # Save the plot
            plot_filename = f'top_{n}_tv_toxic.png'
            plot_path = os.path.join(app.root_path, 'static', 'img', plot_filename)
            plt.savefig(plot_path, facecolor=fig.get_facecolor())
            plt.close()


            # Generate the URL for the saved plot
            plot_url = url_for('static', filename=f'img/{plot_filename}')

            # Return the URL for the plot in the JSON response
            return jsonify({'plot_url': plot_url})
        
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching and plotting data"
        finally:
            cursor.close()
            connection.close()
    else:
        return "Database connection failed"




@app.route('/movies_toxic_list')
def movies_trending_toxic():
    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            query = """UPDATE tmdb_movies_new AS tb                                                      
                SET
                    flag = COALESCE(subquery.flag_count, 0),
                    normal = COALESCE(subquery.normal_count, 0)
                FROM (
                    SELECT
                        name,
                        SUM(flag_count) AS flag_count,
                        SUM(normal_count) AS normal_count
                    FROM
                        reddit_movies
                    GROUP BY
                        name
                ) AS subquery
                WHERE tb.title = subquery.name;
            """
            cursor.execute(query)
            query = """SELECT * FROM tmdb_movies_new
                        ORDER BY flag DESC;
                        """
            cursor.execute(query)
            data_given = cursor.fetchall()
            result = [{'name':row[0], 'popularity':row[1], 'genres':row[2], 'normal':row[3], 'flag':row[4]}for row in data_given]
            return render_template('dynamic_movie_toxic.html', toxic_movies=result)

        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL:", error)
            # Return an error page or message
            return "An error occurred while fetching data"
        finally:
            cursor.close()
            connection.close()
    else:
        # Return an error page or message
        return "Database connection failed"

@app.route('/generate_movies_toxic_plot', methods=['POST'])
def generate_movies_toxic_plot():
    n = request.form.get('n', default=5, type=int)

    # Calculate bar width based on the number of movies
    bar_width = min(0.8, 10.0 / max(n, 1))

    connection = connect_to_postgresql()
    if connection is not None:
        cursor = connection.cursor()
        try:
            # Define and execute the SQL query
            query = """SELECT * FROM tmdb_movies_new
                        ORDER BY flag DESC;
                        """
            cursor.execute(query)
            
            # Fetch the data and create a DataFrame
            data_given = cursor.fetchall()
            data = pd.DataFrame(data_given, columns=['title', 'popularity', 'genres','normal', 'flag'])
            data_custom = data[data["flag"] > 0].sort_values(by="flag", ascending=False).head(n)

            # Set the aesthetic style of the plots
            sns.set_style("white")
            sns.set_palette("pastel")

            
            fig, ax = plt.subplots(figsize=(14, 8))
            fig.set_facecolor("#fffcf2")
            fig.set_facecolor("#fffcf2")

            bar_plot = sns.barplot(x="title", y="flag", data=data_custom, palette="Set2", edgecolor="white")
            for bar in bar_plot.patches:
                bar.set_linestyle("-")
                bar.set_linewidth(1)
                bar.width = bar_width

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.7)

           
            plt.xlabel("Movie Title", fontsize=14)
            plt.ylabel("Flag", fontsize=14)
            plt.title(f"Top {n} Toxic Movies", fontsize=16)
            plt.xticks(rotation=45, ha="right")

            plt.tight_layout()

            # Save the plot
            plot_filename = f'top_{n}_movies_toxic.png'
            plot_path = os.path.join(app.root_path, 'static', 'img', plot_filename)
            plt.savefig(plot_path, facecolor=fig.get_facecolor())
            plt.close()

            # Generate the URL for the saved plot
            plot_url = url_for('static', filename=f'img/{plot_filename}')

            # Return the URL for the plot in the JSON response
            return jsonify({'plot_url': plot_url})

        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while fetching and plotting data"
        finally:
            cursor.close()
            connection.close()

    else:
        return "Database connection failed"

    
if __name__ == '__main__':
    app.run(debug=True)
