from __future__ import absolute_import
from pokesite.celery import app
from datetime import datetime
from celery import shared_task
import time
from pgoapi import PGoApi
from pgoapi.utilities import f2i, h2f
from django.core.cache import cache
from s2sphere import Cell, CellId, LatLng
from mapview.models import Player, City


def get_cell_ids(lat, long, radius = 10):
	origin = CellId.from_lat_lng(LatLng.from_degrees(lat, long)).parent(15)
	walk = [origin.id()]
	right = origin.next()
	left = origin.prev()
	# Search around provided radius
	for i in range(radius):
		walk.append(right.id())
		walk.append(left.id())
		right = right.next()
		left = left.prev()

	# Return everything
	return sorted(walk)


@app.task()
def player_scan(id):
	player = Player.objects.get(id=id)
	cache_name = player.name
	api = PGoApi()
	api.set_position(player.points.all()[0].lat, player.points.all()[0].lon, 0.0)
	api.get_player()
	api_login_result = False
	while not api_login_result:
		try:
			print(':::login')
			api_login_result = api.login('ptc', player.name, player.password)
		except ValueError:
			api_login_result = False
			player.can_login = 0
			player.save()

	player.can_login = 1
	player.save()

	number_of_failures = 0

	# setting account is_celery_run to True to avoid duplicates 
	player.is_celery_run = True
	player.save()

	database_counter = 10	# indicates after how many cycles we check player state Activer or Passive
	player_state = Player.objects.get(id=id).state
	while player_state == True:
		for i, tile in enumerate(player.points.all()):
			if number_of_failures < 10:
				try:
					api.set_position(tile.lat, tile.lon, 0.0)
					print('Step {0}'.format(i))
					cell_ids = get_cell_ids(tile.lat, tile.lon)
					timestamps = [0,] * len(cell_ids)
					api.get_map_objects(
						latitude=f2i(tile.lat), 
						longtitude=f2i(tile.lon), 
						since_timestamp_ms=timestamps, 
						cell_id=cell_ids
						)

					
					
					response_dict = api.call()
					for map_cell in response_dict['responses']['GET_MAP_OBJECTS']['map_cells']:
						if 'catchable_pokemons' in map_cell.keys():
							for pokemon in map_cell['catchable_pokemons']:
								expiration_time = int((datetime.fromtimestamp(int(pokemon['expiration_timestamp_ms'])/1000) - datetime.now()).total_seconds())
								pokemon['expirationtime'] = datetime.fromtimestamp(float(pokemon['expiration_timestamp_ms'])/1000).strftime("%H:%M:%S")
								pokemon['final_time'] = float(pokemon['expiration_timestamp_ms'])/1000
								if int(pokemon['expiration_timestamp_ms']) != -1:
									cache.add('pokemon_{0}'.format(pokemon['encounter_id']), pokemon, expiration_time)
				except:
					number_of_failures += 1
				# time.sleep(1)
			else:
				player.is_celery_run = False
				player.can_login = 0
				player.save()
				return

		database_counter -= 1
		if database_counter < 0:	# then updating state from database
			player_state = Player.objects.get(id=id).state
			database_counter = 10
