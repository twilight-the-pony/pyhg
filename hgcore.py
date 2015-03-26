import os
import MySQLdb
import random
import config

neutrals = [
	"%s asked %s to kill them, but decided to spare their life",
	"%s runs away from %s",
]

injures = [
	"%s got pricked by thorns while picking berries",
	"%s sprained their leg"
]

deaths   = [
	"%s stabbed %s",
	"%s shot %s",
	"%s drowned in %s's saliva"
]

inventory = [
	"%s finds some rope",
	"%s finds some explosives",
	"%s finds some water",
	"%s finds some clean water",
	"%s finds a bow"
]

options = """
HG - possible options:
 about - Who had extra time
 new - starts new game
 districts - show district information
 kill - kills a tribute
 cycle - starts a new round
 stats - gets user stats
 help - this screen
 quit / exit - quits the game
______________________________________


"""

class HgCore:
	def __init__(self):
		self.db = MySQLdb.connect(config.host, config.user, config.password, config.db)

	def sort_users_by_districts(self, game_id):
		print 'Sorting users across the districts!'
		cursor = self.db.cursor()
		cursor.execute('SELECT user_id, username FROM users WHERE in_game = 0')
		tmpnames = []
		for u in cursor.fetchall():
			tmpnames.append(u)

		random.shuffle(tmpnames)
		out = []
		for i in xrange(0, len(tmpnames), 4):
			out.append(tmpnames[i:i+4])

		d = []
		for district in self.get_district_list():
			d.append(district)

		
		d_count = 0;
		for item in out:
			for i in item:
				self.bind_user_to_district(i[0], d[d_count][0], game_id)

			print 'Sorting users for ' + d[d_count][1]
			d_count = d_count + 1

	def new_game(self):
		if self.game_running(self.get_last_game()) == 0:
			print 'Setting up a new game!'
			cursor = self.db.cursor()
			cursor.execute('INSERT INTO game (is_running) VALUES (1)')

			self.sort_users_by_districts(self.get_last_game())
		else:
			print "\x1b[31m[Warning]\x1b[0m Game already running!"

	def new_round(self):
		print "Prepairing for a new round!"

	def get_stats(self):
		pass

	def bind_user_to_district(self, user_id, district_id, game_id):
		cursor = self.db.cursor()
		cursor.execute("INSERT INTO users_district_game (user_id, district_id, game_id) VALUES (%s, %s, %s)", (user_id, district_id, game_id))
		cursor.execute("UPDATE users SET  in_game = 1 WHERE user_id = %s", (user_id))

		return

	def get_district_list(self):
		cursor = self.db.cursor()
		cursor.execute('SELECT district_id, district_name FROM districts')

		return cursor.fetchall()

	def get_district_info(self):
		print "Detailed district information:"
		cursor = self.db.cursor()
		cursor.execute('SELECT d.district_name, u.username, udg.game_id, udg.status_id FROM users_district_game udg \
			LEFT JOIN users u ON (udg.user_id = u.user_id) \
			LEFT JOIN districts d ON (d.district_id = udg.district_id) \
			ORDER BY d.district_id \
		')

		district_list = []
		tmpitems = {}
		for items in cursor.fetchall():
			if not tmpitems.has_key(items[0]):
				tmpitems[items[0]] = []
				tmpitems[items[0]].append(items)
				district_list.append(items[0])
			else:
				tmpitems[items[0]].append(items)

		for item in district_list:
			print "\x1b[33m" + item + "\x1b[0m:"
			for i in tmpitems[item]:
				print "  " +  i[1].ljust(25)  + self.get_status(i[3])

			print

	def get_status(self, status_id):
		if status_id == 0:
			return "(\x1b[32mAlive\x1b[0m)"

	def injure_user(self, user_id):
		pass

	def heal_user(self, user_id):
		pass

	def kill_user(self, user_id):
		pass

	def end_game(self):
		pass

	def game_running(self, game_id):
		cursor = self.db.cursor()
		return cursor.execute('SELECT is_running FROM game WHERE game_id = %s', (game_id))

	def get_last_game(self):
		cursor = self.db.cursor()
		return cursor.execute('SELECT game_id FROM game ORDER BY game_id DESC LIMIT 1')


if __name__ == "__main__":
	hg = HgCore()
	print options
	while True:
		try:
			option = raw_input('Enter command: ').strip()
			opt = option.split(' ')
			if opt[0] == 'new':
				hg.new_game()
			elif opt[0] == 'districts':
				hg.get_district_info()
			elif opt[0] == 'help':
				print options
			elif opt[0] == 'kill':
				tmp = opt[1::]
				if len(tmp) > 0:
					print ' '.join(tmp)
				else:
					print 'Usage: kill <name>'
			elif opt[0] == 'exit' or opt[0] == 'quit':
				print 'I quit!'
				raise SystemExit
			else:
				print 'Unknown command!'
		except KeyboardInterrupt:
			print '\nI quit!'
			raise SystemExit

