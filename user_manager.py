from data_structures import LinkedList  # Bỏ HashMap
import pickle
import os
from datetime import datetime

class User:
    def __init__(self,username):
        self.name=username
        self.games=LinkedList()
        #Lưu các thông số của trò chơi
        self.total_time=0.0
        self.total_games=0
        self.total_wins=0
        self.avg_time=0.0
        self.best_time=None
        self.created_at=datetime.now().isoformat()#Ngày tạo account
        #Lưu reset/chơi vô hạn lần
        self.last_played=None
        self.plays_today=0
        self.last_play_date=None
        self.next_reset_time=None
        self.coins=0
        
class GameRecord:
    def __init__(self,time,attempts,won,mode):
        #Lưu các thông số của Game vừa chơi
        self.time=time
        self.attempts=attempts
        self.won=won
        self.mode=mode
        self.timestamp=datetime.now().isoformat()
        self.date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")#thời gian chơi gần nhất
        self.coins=0
        
#Lớp quản Lý user
class UserManager:
    def __init__(self,data_file="data/users.dat"):
        self.data_file=data_file
        self.users={}
        self._load_users()
    #Kiểm tra xem có thể chơi hôm nay được không
    def can_play(self,username,unlimited=False,reset_mode="daily",max_plays=1):
        if unlimited:
            return(True,"Unlimited plays",-1)
        user=self.users.get(username)        
        if not user:
            return(False,"User not found",0)
            
        now=datetime.now()
        #Mode Daily
        if reset_mode=="daily":
            today=now.date().isoformat()
            if user.last_play_date!=today:
                user.plays_today=0
                user.last_play_date=today
        #Mode interval
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
    def record_play(self,username,reset_mode="daily",reset_interval_minutes=10):#Lưu lịch sử
        user=self.users.get(username)
        if not user:
            return False
        user.plays_today+=1
        if reset_mode=="interval":
            from datetime import timedelta
            next_reset=datetime.now()+timedelta(minutes=reset_interval_minutes)
            user.next_reset_time=next_reset.isoformat()
        self._save_users()
        return True
    #Tải lịch sử user lên
    def _load_users(self):
        if os.path.exists(self.data_file):
            with open(self.data_file,"rb")as f:
                user_dict=pickle.load(f)
                for username,user_data in user_dict.items():
                    user=User(username)
                    #Lấy hết thông số của user
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
                    user.coins=user_data.get('coins',0)
                    #Lấy hết các game của user
                    for game_data in user_data.get("games",[]):
                        game=GameRecord(game_data["time"],game_data["attempts"],game_data["won"],game_data["mode"])
                        game.timestamp=game_data["timestamp"]
                        game.date=game_data["date"]
                        user.games.append(game)
                    self.users[username]=user 
    #Lưu user               
    def _save_users(self):
        os.makedirs(os.path.dirname(self.data_file),exist_ok=True)
        users_dict={}
        #Duyệt qua và lấy từng thông số của user
        for username,user in self.users.items(): 
            games_list=[]
            game_current=user.games.head
            while game_current is not None:
                game=game_current.data
                games_list.append({"time": game.time,"attempts": game.attempts,"won": game.won,"mode": game.mode,
                                   "timestamp": game.timestamp,
                                    "date": game.date
                })
                game_current=game_current.next
                
            users_dict[username]={"name": user.name,"games": games_list,"total_time": user.total_time,
                                "total_games": user.total_games,"total_wins": user.total_wins,
                                "avg_time": user.avg_time,"best_time": user.best_time,"created_at": user.created_at,
                                "last_played": user.last_played,"plays_today": user.plays_today,
                                "last_play_date": user.last_play_date,"coins": user.coins,"next_reset_time": user.next_reset_time}
        with open(self.data_file,"wb")as f:#Lưu user
            pickle.dump(users_dict,f)
    #Lấy hoặc thêm một user
    def add_or_get_user(self,username):
        if username not in self.users:
            user=User(username)
            self.users[username]=user
            self._save_users()
            return user
        return self.users[username]
    #Thêm game vào kết quả
    def add_game_result(self,username,time_elapsed,attempts,won,mode="english"):
        user=self.users.get(username)        
        if not user:
            return False
        game_record=GameRecord(time_elapsed,attempts,won,mode)
        user.games.append(game_record)
        user.total_games+=1
        user.last_played=datetime.now().isoformat()
        coins_earned = 0
        if won:
            user.total_wins+=1
            user.total_time+=time_elapsed
            user.avg_time=user.total_time/user.total_wins
            if user.best_time is None or time_elapsed<user.best_time:
                user.best_time=time_elapsed
            # Tặng coins khi thắng
            coins_earned = 10  # Base reward
            # Bonus: Thắng nhanh
            if time_elapsed < 60:
                coins_earned += 5
            # Bonus: Ít lượt
            if attempts <= 3:
                coins_earned += 5
            # Bonus: Math mode 
            if mode == "math":
                coins_earned += 3
            user.coins += coins_earned
            
        self._save_users()
        return coins_earned 
        
    def get_top20(self):
        players=[]
        for username,user in self.users.items():
            if user.total_wins>0:
                players_data={"rank": 0,"name": user.name,"avg_time": user.avg_time,"best_time": user.best_time,
                                "total_wins": user.total_wins,"total_games": user.total_games
                                }
                players.append(players_data)
        
        # Sắp xếp dùng bubble sort
        n=len(players)
        for i in range(n):
            for j in range(n-1-i):
                if players[j]["avg_time"]>players[j+1]["avg_time"]:
                    players[j],players[j+1]=players[j+1],players[j]
        
        # Lấy top 20
        result=[]
        limit=min(20,len(players))
        for i in range(limit):
            players[i]["rank"]=i+1
            result.append(players[i])
        return result
    #Lấy lịch sử User
    def get_user_history(self,username):
        user=self.users.get(username)        
        if not user:
            return[]
        history=[]
        current=user.games.head
        index=0
        while current is not None:
            game=current.data
            game_data={"index": index,"time": game.time,"attempts": game.attempts,
                        "won": game.won,"mode": game.mode,"timestamp": game.timestamp,"date": game.date}
            history.append(game_data)
            current=current.next
            index+=1
        history.reverse()
        return history
    #Thêm coin vào account
    def add_coins(self, username, amount):
        user = self.users.get(username)        
        if not user:
            return False
        user.coins += amount
        self._save_users()
        return True
    def spend_coins(self, username, amount):
        user = self.users.get(username)        
        if not user:
            return False
        if user.coins < amount:
            return False  # Không đủ coins
        user.coins -= amount
        self._save_users()
        return True
    
    def get_coins(self, username):
        user = self.users.get(username)        
        if not user:
            return 0
        return user.coins