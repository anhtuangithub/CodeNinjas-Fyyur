#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from sqlalchemy import String, cast, func
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'Show'

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    genres = db.Column(db.String(255))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(255))
    website_link = db.Column(db.String(255))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref = 'venue', lazy = True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    genres = db.Column(db.String(255))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(255))
    website_link = db.Column(db.String(255))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref = 'artist', lazy = True)

with app.app_context():
    db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  date = datetime.now()
  lstVenue = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state)
  data = []
  for row in places:
    findVenues = [venue for venue in lstVenue if venue.city == row.city and venue.state == row.state]
    rsVenus = []
    for v in findVenues:
      upcomingShows = []
      for show in v.shows:
        if show.start_time > date:
          upcomingShows.append(show)
      rsVenus.append(
        {
          "id": v.id,
          "name": v.name,
          "num_upcoming_shows": len(upcomingShows)
        }
      )
    data.append({
      "city": row.city,
      "state": row.state,
      "venues": rsVenus
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  date = datetime.now()
  search = "%{}%".format(request.form["search_term"])
  posts = Venue.query.filter(Venue.name.like(search)).all()
  list = []
  for row in posts:
    upcomingShows = []
    for show in row.shows:
      if show.start_time > date:
         upcomingShows.append(show)

    list.append({
      'id': row.id,
      'name': row.name,
      'num_upcoming_shows': len(upcomingShows)
    })
  response={
    "count": len(list),
    "data": list
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  error = False
  data = {}
  date = datetime.now()
  try:
    venue = Venue.query.get(venue_id)
    upcomingShows = []
    pastShow = []
    for show in venue.shows:
      if show.start_time > date:
        upcomingShows.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.isoformat()
        })
      else :
        pastShow.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.isoformat()
        })
    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.split(', '),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": pastShow,
      "upcoming_shows": upcomingShows,
      "past_shows_count": len(pastShow),
      "upcoming_shows_count": len(upcomingShows),
    }
    db.session.commit()
  except:
    db.session.rollback()

    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return render_template('pages/show_venue.html', venue=data)
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    venue = Venue()
    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.image_link = request.form.get('image_link', '')
    venue.genres = ', '.join(request.form.getlist("genres"))
    venue.facebook_link = request.form.get('facebook_link', '')
    venue.website_link = request.form.get('website_link', '')
    if request.form.get('seeking_talent', '') == 'y':
      venue.seeking_talent = True
    else:
       venue.seeking_talent = False
    venue.seeking_description = request.form.get('seeking_description', '')
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
      venue = Venue.query.filter_by(id=venue_id).first()
      if venue is None:
        return render_template('errors/404.html')
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  if error:
      flash("An error occurred. Venue " + venue_id + " could not be deleted.")
      abort(500)
  else:
      return render_template("pages/home.html")

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  list = Artist.query.all()
  result = []
  for row in list:
     result.append({'id': row.id, 'name': row.name})
  return render_template('pages/artists.html', artists=result)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  date = datetime.now()
  search = "%{}%".format(request.form["search_term"])
  posts = Artist.query.filter(Artist.name.like(search)).all()
  list = []
  for row in posts:
    upcomingShows = []
    for show in row.shows:
      if show.start_time > date:
         upcomingShows.append(show)

    list.append({
      'id': row.id,
      'name': row.name,
      'num_upcoming_shows': len(upcomingShows)
    })
  response={
    "count": len(list),
    "data": list
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  error = False
  data = {}
  date = datetime.now()
  try:
    artist = Artist.query.get(artist_id)
    upcomingShows = []
    pastShow = []
    for show in artist.shows:
      if show.start_time > date:
        upcomingShows.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.isoformat()
        })
      else :
        pastShow.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.isoformat()
        })
    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(', '),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": pastShow,
      "upcoming_shows": upcomingShows,
      "past_shows_count": len(pastShow),
      "upcoming_shows_count": len(upcomingShows),
    }
    db.session.commit()
  except:
    db.session.rollback()

    error = True
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  findArtist = Artist.query.filter_by(id=artist_id).first()
  if findArtist is None:
    return abort(404)
  
  artist={
    "id": findArtist.id,
    "name": findArtist.name,
    "genres": findArtist.genres.split(', '),
    "city": findArtist.city,
    "state": findArtist.state,
    "phone": findArtist.phone,
    "website_link": findArtist.website_link,
    "facebook_link": findArtist.facebook_link,
    "seeking_venue": findArtist.seeking_venue,
    "seeking_description": findArtist.seeking_description,
    "image_link": findArtist.image_link
  }
  form = ArtistForm(formdata=None, data=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  if artist is None:
    abort(404)

  artist.name = request.form["name"]
  artist.genres = ', '.join(request.form.getlist("genres"))
  artist.city = request.form["city"]
  artist.state = request.form["state"]
  artist.phone = request.form["phone"]
  artist.website_link = request.form["website_link"]
  artist.facebook_link = request.form["facebook_link"]
  if request.form.get('seeking_venue', '') == 'y':
    artist.seeking_venue = True
  else:
      artist.seeking_venue = False
  artist.seeking_description = request.form["seeking_description"]
  artist.image_link = request.form["image_link"]

  db.session.commit()

  return redirect(url_for("show_artist", artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  findVenue = Venue.query.filter_by(id=venue_id).first()
  if findVenue is None:
    return abort(404)
  venue={
    "id": findVenue.id,
    "name": findVenue.name,
    "genres": findVenue.genres.split(', '),
    "address": findVenue.address,
    "city": findVenue.city,
    "state": findVenue.state,
    "phone": findVenue.phone,
    "website_link": findVenue.website_link,
    "facebook_link": findVenue.facebook_link,
    "seeking_talent": findVenue.seeking_talent,
    "seeking_description": findVenue.seeking_description,
    "image_link": findVenue.image_link
  }
  form = VenueForm(formdata=None, data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first()
  if venue is None:
    abort(404)

  venue.name = request.form["name"]
  venue.genres =  ', '.join(request.form.getlist("genres"))
  venue.city = request.form["city"]
  venue.state = request.form["state"]
  venue.phone = request.form["phone"]
  venue.website_link = request.form["website_link"]
  venue.facebook_link = request.form["facebook_link"]
  if  request.form.get('seeking_talent', '') == 'y':
    venue.seeking_talent = True
  else:
    venue.seeking_talent = False
  venue.seeking_description = request.form["seeking_description"]
  venue.image_link = request.form["image_link"]

  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form

  try:
    artist = Artist()
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.image_link = request.form.get('image_link', '')
    artist.genres = ', '.join(request.form.getlist("genres"))
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.website_link = request.form.get('website_link', '')
    if request.form.get('seeking_venue', '') == 'y':
      artist.seeking_venue = True
    else:
       artist.seeking_venue = False
    artist.seeking_description = request.form.get('seeking_description', '')
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  lstShow = Show.query.all()
  data = []
  for show in lstShow:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.isoformat()
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show()
    show.artist_id = request.form.get('artist_id', '')
    show.venue_id = request.form.get('venue_id', '')
    show.start_time = request.form.get('start_time', '')
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
