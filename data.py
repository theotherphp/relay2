from datetime import datetime
import logging
import pickle
import time

"""
teams is a dict of team info and walker info

tag_team_map is a reverse lookup table to get from tag ID to team ID. Maybe that 
would be better with a real database, but that had different problems 

The team carries the lap count, duplicating the walker lap count. Not normal form
but makes it faster to calculate the team rank (vs. adding up all tags dicts)
"""

class LapData:

    min_lap_time = 10.0  # seconds

    def __init__(self):
        self.teams = {}
        self.tag_team_map = {}


    # Write the internal dict format out to disk
    def serialize(self):
        fname = str(datetime.now())
        try:
            with open(fname, 'wx') as fp:
                pickle.dump(fp, self.teams)
        except Exception as e:
            logging.error('serialize: %s', e)


    # Read a backup file in from disk to internal dict format
    def deserialize(self, fname):
        try:
            with open(fname, 'rb') as fp:
                self.teams = pickle.load(fp)
                for t in self.teams.keys():
                    for w in self.teams[t]['tags'].keys():
                        self.tag_team_map[w] = t

            logging.debug('deserialized %d teams, %d tags, %d total laps',
                len(self.teams),
                len(self.tag_team_map),
                self.get_total_laps()
            )
        except Exception as e:
            logging.error('deserialize: %s', e)


    def add_tag_to_team(self, tag, team_id):
        if tag in self.tag_team_map:
            logging.error('tag %d already registered', tag)
        else:
            self.teams[team_id]['tags'][tag] = dict(
                laps=0,
                last_updated_time=0.0,
                team_id=team_id
            )
            tag_team_map[tag] = team_id


    def add_team(self, team_name):
        next_team_id = max(self.teams.keys()) + 1
        self.teams[next_team_id] = dict(
            laps=0,
            name=team_name,
            tags=dict()
        )


    def get_team_rank(self, team):
        return 1


    def get_pretty_time(self, ts):
        # e.g. 'Thursday 12:02:27 AM'
        return '{0:%A %I:%M:%S %p}'.format(datetime.fromtimestamp(ts))


    def get_total_laps(self):
        lap_count = 0
        for t in self.teams.values():
            for w in t['tags'].values():
                lap_count += w['laps']
        return lap_count


    def increment_laps(self, tag_key):
        team = self.teams[self.tag_team_map[tag_key]]
        tag = team['tags'].get(tag_key)
        if tag is None:
            logging.error('Unregistered tag: %d', tag_key)
            return

        now = time.time()
        if now - tag['last_updated_time'] > LapData.min_lap_time:
            tag['last_updated_time'] = now
            tag['laps'] += 1
            team['laps'] += 1

            notification = dict(
                laps=team['laps'],
                name=team['name'],
                rank=self.get_team_rank(team),
                tag=tag_key
            )
            return notification
        return None

