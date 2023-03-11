#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from sqlalchemy import String, cast, func
from forms import *
from flask_migrate import Migrate
import sys
from models import db, Show, Artist, Venue
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

with app.app_context():
    db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
      date = dateutil.parser.parse(value)
  else:
      date = value
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
          "start_time": show.start_time
        })
      else :
        pastShow.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time
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
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue = Venue(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          address=form.address.data,
          phone=form.phone.data,
          genres=form.genres.data,
          facebook_link=form.facebook_link.data,
          image_link=form.image_link.data,
          website_link = form.website_link.data,
          seeking_talent = form.seeking_talent.data,
          seeking_description = form.seeking_description.data
      )
      venue.genres = ', '.join(venue.genres)
      db.session.add(venue)
      db.session.commit()
      flash('Venue: {0} created successfully'.format(venue.name))
    except Exception as err:
      flash('An error occurred creating the Venue: {0}. Error: {1}'.format(venue.name, err), 'error')
      db.session.rollback()
    finally:
      db.session.close()
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message), 'error')
    return render_template('forms/new_venue.html', form=form)

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
          "start_time": show.start_time
        })
      else :
        pastShow.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time
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
  form = ArtistForm(request.form)
  if form.validate():
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(artist)

    db.session.commit()

    return redirect(url_for("show_artist", artist_id=artist_id))
  else:
    message = []
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message), 'error')
    return render_template('forms/edit_artist.html', form=form, artist=artist)

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
  form = VenueForm(request.form)
  if form.validate():
    form.genres.data = ', '.join(form.genres.data)
    form.populate_obj(venue)

    db.session.commit()

    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    message = []
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message), 'error')
    return render_template('forms/edit_venue.html', form=form, venue=venue)
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=form.genres.data,
          facebook_link=form.facebook_link.data,
          image_link=form.image_link.data,
          website_link = form.website_link.data,
          seeking_venue = form.seeking_venue.data,
          seeking_description = form.seeking_description.data
      )
      artist.genres = ', '.join(artist.genres)
      db.session.add(artist)
      db.session.commit()
      flash('Artist: {0} created successfully'.format(artist.name))
    except Exception as err:
      flash('An error occurred creating the Artist: {0}. Error: {1}'.format(artist.name, err))
      db.session.rollback()
    finally:
      db.session.close()
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message), 'error')
    return render_template('forms/new_artist.html', form=form)
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
      "start_time": show.start_time
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
    form = ShowForm(request.form)
    show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    flash('Show: created successfully')
  except Exception as err:
    flash('An error occurred creating the Show. Error: {0}'.format(err))
    db.session.rollback()
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
