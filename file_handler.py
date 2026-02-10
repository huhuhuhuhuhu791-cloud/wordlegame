import pickle
import json
import os
from datetime import datetime
from data_structures import LinkedList  # Bỏ HashMap
class Account:
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.created_at=datetime.now().isoformat()
        self.last_played=None
    def check_password(self,input_password):
        return input_password==self.password   
class FileHandler:
    def __init__(self,data_dir="data"):
        self.data_dir=data_dir
        self.game_states_dir=os.path.join(data_dir,"game_states")#Tạo game_state
        self.accounts_file=os.path.join(data_dir,"accounts.dat")#Tạo accounts
        os.makedirs(self.game_states_dir,exist_ok=True)  
    def _encode_data(self,data):#mã hóa data dưới dạng bin
        return pickle.dumps(data)  
    def _decode_data(self,encoded_data): #Giải mã
        return pickle.loads(encoded_data)
    #lưu trạng thái game của người chơi
    def save_game_state(self,username,game_state):
        filename=os.path.join(self.game_states_dir,f"{username}.dat")
        data={"username":username,"game_state":game_state,"saved_at":datetime.now().isoformat()}
        encoded=self._encode_data(data)
        with open(filename,"wb") as f:
            f.write(encoded) 
    #tải trạng thái game của người chơi
    def load_game_state(self,username):
        filename=os.path.join(self.game_states_dir,f"{username}.dat")
        if not os.path.exists(filename):
            return None
        with open(filename,"rb") as f:
            encoded=f.read()
        data=self._decode_data(encoded)
        return data["game_state"]
    #Xóa một game
    def delete_game_state(self,username):
        filename=os.path.join(self.game_states_dir,f"{username}.dat")
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    #Lưu
    def has_saved_game(self,username):
        filename=os.path.join(self.game_states_dir,f"{username}.dat")
        return os.path.exists(filename)
    #Lưu account
    def save_accounts(self,accounts_list):
        if isinstance(accounts_list,LinkedList):
            accounts_array=[]
            current=accounts_list.head
            #Lấy hết account
            while current is not None:
                account=current.data
                if isinstance(account,Account):
                    accounts_array.append({'username':account.username,"password":account.password,'created_at':account.created_at,'last_played':account.last_played})
                else:
                    accounts_array.append(account)
                current=current.next
        else:
            accounts_array=accounts_list
        data={'accounts':accounts_array[:],'updated_at':datetime.now().isoformat()}
        encoded=self._encode_data(data)
        with open(self.accounts_file,'wb') as f:
            f.write(encoded)
        return True
    #Load account lên
    def load_accounts(self):
        accounts_list=LinkedList()
        if not os.path.exists(self.accounts_file):
            return accounts_list
        with open(self.accounts_file,'rb') as f:
            encoded=f.read()
        data=self._decode_data(encoded)#giải mã 
        accounts_data=data.get('accounts',[])
        #Duyệt qua hết
        for acc_data in accounts_data:
            username=acc_data.get('username','')
            password=acc_data.get('password','')
            if not username:
                continue
            account=Account(username,password)
            account.created_at=acc_data.get('created_at',datetime.now().isoformat())
            account.last_played=acc_data.get('last_played',None)
            accounts_list.append(account)
        return accounts_list
    #xuất dữ liệu game sang file json
    def export_data_json(self,username,output_file):
        game_state=self.load_game_state(username)
        if game_state:
            with open(output_file,"w",encoding="utf-8") as f:
                json.dump(game_state,f,indent=2,ensure_ascii=False)
            return True
        return False
    #Tải data json
    def import_data_json(self,username,input_file):
        with open(input_file,"r",encoding="utf-8") as f:
            game_state=json.load(f)
        return self.save_game_state(username,game_state)
    #Lấy tất cả game saved
    def get_all_saved_games(self):
        usernames=LinkedList()
        files=os.listdir(self.game_states_dir)
        for filename in files:
            if filename.endswith('.dat'):
                username=filename.replace('.dat','')
                usernames.append(username)
        return usernames
    #Account dạng array
    def get_accounts_array(self):
        accounts_list=self.load_accounts()
        result=[]
        current=accounts_list.head
        while current is not None:
            account=current.data
            result.append({'username':account.username,'created_at':account.created_at,'password':account.password,'last_played':account.last_played})
            current=current.next
        return result