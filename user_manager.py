from data_structures import HashMap,DynamicArray,LinkedList
import pickle
import os
from datetime import datetime
class User:
    def __init__(self,username):
        self.name=username
        self.games=LinkedList()
        self.total_time=0.0
        self.total_games=0
        self.total_wins=0
        self.avg_time=0.0
        self.best_time=None
        self.created_at=datetime.now().isoformat()
        self.last_played=None
        self.plays_today=0
        self.last_play_date=None
        self.next_reset_time=None
class GameRecord:
    def __init__(self,time,attempts,won,mode):
        self.time=time
        self.attempts=attempts
        self.won=won
        self.mode=mode
        self.timestamp=datetime.now().isoformat()
        self.date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
class UserManager:
    def __init__(self,data_file="data/users.dat"):
        self.data_file=data_file
        self.users=HashMap()
        self._load_users()
    def can_play(self,username,unlimited=False,reset_mode="daily",max_plays=1):
        if unlimited:
            return(True,"Unlimited plays",-1)
        user=self.users.get(username)
        if not user:
            return(False,"User not found",0)
        now=datetime.now()
        if reset_mode=="daily":
            today=now.date().isoformat()
            if user.last_play_date!=today:
                user.plays_today=0
                user.last_play_date=today
        elif reset_mode=="interval":
            if user.next_reset_time:
                reset_time=datetime.fromisoformat(user.next_reset_time)
                if now>=reset_time:
                    user.plays_today=0
                    user.next_reset_time=None
                    
        if user.plays_today>=max_plays:
            if reset_mode=="daily":
                return(False,f"Bạn đã hết lượt chơi hôm nay ({max_plays} lượt/ngày)",0)
            elif reset_mode=="interval"and user.next_reset_time:
                reset_time=datetime.fromisoformat(user.next_reset_time)
                minutes_left=int((reset_time-now).total_seconds()/60)
                return(False,f"Hết lượt! Reset sau {minutes_left} phút",0)
            else:
                return(False,"Bạn đã hết lượt chơi",0)
        remaining=max_plays-user.plays_today
        return(True,f"Còn {remaining} lượt",remaining)
    def record_play(self,username,reset_mode="daily",reset_interval_minutes=10):
        user=self.users.get(username)
        if not user:
            return False
        user.plays_today+=1
        if reset_mode=="interval"and user.plays_today==1:
            from datetime import timedelta
            next_reset=datetime.now()+timedelta(minutes=reset_interval_minutes)
            user.next_reset_time=next_reset.isoformat()
        self._save_users()
        return True
    def _load_users(self):
        if os.path.exists(self.data_file):
            with open(self.data_file,"rb")as f:
                user_dict=pickle.load(f)
                for username,user_data in user_dict.items():
                    user=User(username)
                    user.plays_today=user_data.get('plays_today',0)
                    user.last_play_date=user_data.get('last_play_date',None)
                    user.next_reset_time=user_data.get('next_reset_time',None)
                    user.total_time=user_data.get('total_time',0.0)
                    user.total_games=user_data.get('total_games',0)
                    user.total_wins=user_data.get('total_wins',0)
                    user.avg_time=user_data.get('avg_time',0.0)
                    user.best_time=user_data.get('best_time',None)
                    user.created_at=user_data.get('created_at',datetime.now().isoformat())
                    user.last_played=user_data.get('last_played',None)
                    for game_data in user_data.get("games",[]):
                        game=GameRecord(game_data["time"],game_data["attempts"],game_data["won"],game_data["mode"])
                        game.timestamp=game_data["timestamp"]
                        game.date=game_data["date"]
                        user.games.append(game)
                    self.users.set(username,user)
    
    def _save_users(self):
        os.makedirs(os.path.dirname(self.data_file),exist_ok=True)
        users_dict={}
        for bucket in self.users.buckets:
            current=bucket.head
            while current is not None:
                username=current.data.key
                user=current.data.value
                games_list=[]
                game_current=user.games.head
                while game_current is not None:
                    game=game_current.data
                    games_list.append({"time":game.time,"attempts":game.attempts,"won":game.won,"mode":game.mode,"timestamp":game.timestamp,"date":game.date})
                    game_current=game_current.next
                users_dict[username]={
                    "name":user.name,
                    "games":games_list,
                    "total_time":user.total_time,
                    
                    "total_games":user.total_games,
                    "total_wins":user.total_wins,
                    "avg_time":user.avg_time,
                    "best_time":user.best_time,
                    "created_at":user.created_at,
                    "last_played":user.last_played,
                    "plays_today":user.plays_today,
                    "last_play_date":user.last_play_date,
                    "next_reset_time":user.next_reset_time
                }
                current=current.next
        with open(self.data_file,"wb")as f:
            pickle.dump(users_dict,f)
    def add_or_get_user(self,username):
        if not self.users.contains(username):
            user=User(username)
            self.users.set(username,user)
            self._save_users()
            return user
        return self.users.get(username)
    def add_game_result(self,username,time_elapsed,attempts,won,mode="english"):
        user=self.users.get(username)
        if not user:
            return False
        game_record=GameRecord(time_elapsed,attempts,won,mode)
        user.games.append(game_record)
        user.total_games+=1
        user.last_played=datetime.now().isoformat()
        if won:
            user.total_wins+=1
            user.total_time+=time_elapsed
            user.avg_time=user.total_time/user.total_wins
            if user.best_time is None or time_elapsed<user.best_time:
                user.best_time=time_elapsed
        self._save_users()
        return True
    def get_top20(self):
        players=DynamicArray()
        for bucket in self.users.buckets:
            current=bucket.head
            while current is not None:
                user=current.data.value
                if user.total_wins>0:
                    players_data={
                        "rank":0,
                        "name":user.name,
                        "avg_time":user.avg_time,
                        "best_time":user.best_time,
                        "total_wins":user.total_wins,
                        "total_games":user.total_games
                    }
                    players.append(players_data)
                current=current.next
        for i in range(players.length()):
            for j in range(players.length()-1-i):
                if players.get(j)["avg_time"]>players.get(j+1)["avg_time"]:
                    temp=players.get(j)
                    players.set_value(j,players.get(j+1))
                    players.set_value(j+1,temp)
        result=[]
        limit=min(20,players.length())
        for i in range(limit):
            player=players.get(i)
            player["rank"]=i+1
            result.append(player)
        return result
    def get_user_history(self,username):
        user=self.users.get(username)
        if not user:
            return[]
        history=[]
        current=user.games.head
        index=0
        while current is not None:
            game=current.data
            game_data={
                "index":index,
                "time":game.time,
                "attempts":game.attempts,
                "won":game.won,
                "mode":game.mode,
                "timestamp":game.timestamp,
                "date":game.date
            }
            history.append(game_data)
            current=current.next
            index+=1
        history.reverse()
        return history
    def delete_user(self,username):
        if self.users.contains(username):
            self.users.delete(username)
            self._save_users()
            return True
        return False
    def get_all_usernames(self):
        usernames=LinkedList()
        for bucket in self.users.buckets:
            current=bucket.head
            while current is not None:
                usernames.append(current.data.key)
                current=current.next
        return usernames.to_array()