from flask import Flask,render_template,request,jsonify,session
from datetime import datetime
import os
from game_logic import WordleGame
from file_handler import FileHandler
from user_manager import UserManager
from data_structures import LinkedList
from file_handler import Account
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","cr7-ronaldo")
file_handler=FileHandler()
user_manager=UserManager()
active_games={}
game_settings={"unlimited":True,"reset_mode":"daily","max_plays":1,"reset_interval":10}#Xử lý khi set chế độ chơi là gì(vô hạn hay reset)
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/api/login",methods=["POST"])
def login():# Xử lý Đăng nhập
    data=request.get_json()
    username=data.get("username","").strip()
    password=data.get("password","").strip()
    accounts=file_handler.load_accounts()
    found=None
    current=accounts.head
    #Tìm Account
    while current:
        if current.data.username==username:
            found=current.data
            break
        current=current.next
    if not found:
        return jsonify({"success":False,"message":"Tài khoản không tồn tại!"})
    
    if not found.check_password(password):
        return jsonify({"success":False,"message":"Sai mật khẩu!"})
    found.last_played=datetime.now().isoformat()
    file_handler.save_accounts(accounts)
    session["username"]=username
    has_saved=file_handler.has_saved_game(username)
    user_manager.add_or_get_user(username)
    #Trả về JS
    return jsonify({"success":True,"username":username,
                    "has_saved_game":has_saved,
                    "message":"Đăng nhập thành công!"})

@app.route("/api/register",methods=["POST"])
def register():#Xử lý đăng ký
    data=request.get_json()
    username=data.get("username","")
    password=data.get("password","")
    if not username or not password:
        return jsonify({"success":False,"message":"Vui lòng nhập đủ thông tin!"})
    if len(password)<6:
        return jsonify({"success":False,"message":"Mật khẩu phải có ít nhất 6 ký tự!"})
    accounts=file_handler.load_accounts()
    current=accounts.head
    while current:
        if current.data.username==username:
            return jsonify({"success":False,"message":"Tên đăng nhập đã tồn tại!"})
        current=current.next
    if accounts.length()>=5:
        return jsonify({"success":False,"message":"Đã đạt giới hạn 5 tài khoản!"})
    #Tạo và lưu Account
    new_account=Account(username,password)
    accounts.append(new_account)
    file_handler.save_accounts(accounts)
    user_manager.add_or_get_user(username)
    session["username"]=username
    return jsonify({"success":True,"username":username,"message":"Đăng ký thành công!"})
#API xử lý đăng xuất
@app.route("/api/logout",methods=["POST"])
def logout():
    session.pop("username",None)#Xóa username ở session hiện tại
    return jsonify({"success":True,"message":"Đã đăng xuất!"})
@app.route("/api/new_game",methods=["POST"])
def new_game():#Bắt đầu trò chơi
    username=session.get("username")
    if not username:
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    #Xử lý các trò chơi
    data=request.get_json()
    mode=data.get("mode","english")
    max_attempts=int(data.get("max_attempts",6))
    can_play,message,remaining=user_manager.can_play(username,unlimited=game_settings["unlimited"],
    reset_mode=game_settings["reset_mode"],
        max_plays=game_settings["max_plays"])
    if not can_play:
        return jsonify({"success":False,"message":message,"blocked":True})
    game=WordleGame(mode=mode,max_attempts=max_attempts)

    active_games[username]=game
    file_handler.delete_game_state(username)
    #Lưu lịch sử
    user_manager.record_play(username,reset_mode=game_settings["reset_mode"],reset_interval_minutes=game_settings["reset_interval"])
    #Trả về cho JS xử lý
    return jsonify({"success":True,"mode":mode,"max_attempts":max_attempts,"word_length":game.word_length,
                    "attempts":0,"remaining_plays":remaining})

@app.route("/api/guess",methods=["POST"])
def make_guess():#THực hiện một lần đoán
    username=session.get("username")
    if not username:
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    
    game=active_games.get(username)
    if not game:
        return jsonify({"success":False,"message":"Không có game nào đang chơi!"})
    
    data=request.get_json()
    word=data.get("word","").strip().upper()
    if not word:
        return jsonify({"success":False,"message":"Vui lòng nhập từ!"})
    if not game.is_valid_word(word):
        return jsonify({"success":False,"message":"Từ không hợp lệ!"})
    #Xử lý response trả về cho JS
    result=game.make_guess(word)
    response={"success":result.get("success",False),"word":word,
        "result":result.get("result",[]),
        "attempts":result.get("attempts",0),
        "max_attempts":result.get("max_attempts",6),
        "game_over":result.get("game_over",False),
        "won":result.get("won",False),
        "used_letters":result.get("used_letters",{"correct":[],"present":[],"absent":[]}),
        "can_undo":result.get("can_undo",False),
        "can_redo":result.get("can_redo",False),
        "message":result.get("message","")
    }
    if result.get("game_over"):
        response["target_word"]=result.get("target_word")
        response["time_elapsed"]=result.get("time_elapsed",0)
        user_manager.add_game_result(username=username,
            time_elapsed=result.get("time_elapsed",0),
            attempts=result.get("attempts",0),
            won=result.get("won",False),
            mode=game.mode
        )
        if username in active_games:
            del active_games[username]
        file_handler.delete_game_state(username)
    else:
        data=request.get_json(silent=True)or{}
        elapsed_seconds=int(data.get("elapsed_seconds",0))
        state=game.get_state()
        state["elapsed_seconds"]=elapsed_seconds
        file_handler.save_game_state(username,state)
    return jsonify(response)
#API xóa game vừa chơi(xử lý cho phần resume)
@app.route("/api/discard_game",methods=["POST"])
def discard_game():
    username=session.get("username")
    if not username:
        
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    if username in active_games:
        
        del active_games[username]
    file_handler.delete_game_state(username)
    
    return jsonify({"success":True,"message":"Đã hủy và không lưu game!"})
#APi xử lý undo
@app.route("/api/undo",methods=["POST"])
def undo():
    username=session.get("username")
    if not username:
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    game=active_games.get(username)
    
    if not game:
        return jsonify({"success":False,"message":"Không có game nào đang chơi!"})
    result=game.undo()
    #Lưu game vừa tạo và trả về
    file_handler.save_game_state(username,game.get_state())
    return jsonify({"success":result.get("success",False),
        "message":result.get("message",""),
        "attempts":result.get("attempts",0),
        "guesses":result.get("guesses",[]),
        "used_letters":result.get("used_letters",{"correct":[],"present":[],"absent":[]}),
        "can_undo":result.get("can_undo",False),
        "can_redo":result.get("can_redo",False)
    })
#reDO
@app.route("/api/redo",methods=["POST"])
def redo():
    username=session.get("username")
    if not username:
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    game=active_games.get(username)
    if not game:
        return jsonify({"success":False,"message":"Không có game nào đang chơi!"})
    result=game.redo()
    file_handler.save_game_state(username,game.get_state())
    return jsonify({"success":result.get("success",False),"message":result.get("message",""),
        "attempts":result.get("attempts",0),
        "guesses":result.get("guesses",[]),
        "used_letters":result.get("used_letters",{"correct":[],"present":[],"absent":[]}),
        "game_over":result.get("game_over",False),
        "won":result.get("won",False),
        "can_undo":result.get("can_undo",False),
        "can_redo":result.get("can_redo",False)
    })
#API xử lý khi nhấp vào resume
@app.route("/api/resume_game",methods=["POST"])
def resume_game():
    username=session.get("username")
    if not username:
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    state=file_handler.load_game_state(username)
    if not state:
        return jsonify({"success":False,"message":"Không có game nào được lưu!"})
    #lấy game vừa lưu
    game=WordleGame.from_state(state)
    active_games[username]=game
    
    return jsonify({"success":True,"state":state})
#xử lý api lấy gợi ý
@app.route("/api/get_hint",methods=["POST"])
def get_hint():
    username=session.get("username")
    if not username:
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    game=active_games.get(username)
    if not game:
        return jsonify({"success":False,"message":"Không có game đang chơi!"})
    result=game.get_hint()
    if result["success"]:
        state=game.get_state()
        file_handler.save_game_state(username,state)
    return jsonify(result)
#Xử lý khi thoát game ra
@app.route("/api/quit_game",methods=["POST"])
def quit_game():
    username=session.get("username")
    if not username:
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    game=active_games.get(username)
    if game and not game.game_over:
        data=request.get_json(silent=True)or{}
        elapsed_seconds=int(data.get("elapsed_seconds",0))
        state=game.get_state()
        state["elapsed_seconds"]=elapsed_seconds
        file_handler.save_game_state(username,state)
    if username in active_games:
        del active_games[username]
    return jsonify({"success":True,"message":"Đã thoát game!"})
#Cập nhật setting khi chọn chế độ
@app.route("/api/update_settings",methods=["POST"])
def update_settings():
    global game_settings
    data=request.json
    game_settings.update(data)
    return jsonify({"success":True,"settings":game_settings})
#Lấy setting
@app.route("/api/get_settings",methods=["GET"])
def get_settings():
    return jsonify(game_settings)
#Cập nhật bảng xếp hạng
@app.route("/api/leaderboard",methods=["GET"])
def get_leaderboard():
    top_players=user_manager.get_top20()
    if not top_players:
        top_players=[]
    return jsonify({"success":True,"leaderboard":top_players})
#Lấy lịch sử (history)
@app.route("/api/history",methods=["GET"])
def get_history():
    username=session.get("username")
    if not username:
        
        return jsonify({"success":False,"message":"Chưa đăng nhập!"})
    history=user_manager.get_user_history(username)
    if not history:
        history=[]
        
    return jsonify({"success":True,"history":history})

if __name__=="__main__":
    os.makedirs("data/game_states",exist_ok=True)
    if not os.path.exists("data/accounts.dat"):
        accounts=LinkedList()
        file_handler.save_accounts(accounts)
    app.run(debug=True,host="0.0.0.0",port=5000)
 