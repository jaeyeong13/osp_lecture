from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
# render_template 함수는 HTML 템플릿을 렌더링하여 웹 브라우저에 동적으로 생성된 내용을 보여줄 수 있게 도와줌
from database import DBhandler
import hashlib
import sys

app = Flask(__name__)
app.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

@app.route('/')
def hello():
    # return render_template("index.html")
    return redirect(url_for("view_list"))

@app.route("/list")
def view_list():
    page=request.args.get("page", 0, type=int)
    per_page=6
    per_row=3
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_items()
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template(
        "list.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1),
        total=item_counts
    )

@app.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")

# @app.route("/reg_reviews")
# def reg_review():
#     return render_template("reg_reviews.html")

@app.route("/subit_item")
def reg_item_submit():
    name=request.args.get("name")
    seller=request.args.get("seller")
    addr=request.args.get("addr")
    email=request.args.get("email")
    category=request.args.get("category")
    card=request.args.get("card")
    status=request.args.get("status")
    phone=request.args.get("phone")
    
    print(name, seller, addr, email, category, card, status, phone)
    # return render_template("reg_items.html")

@app.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.insert_item(data['name'], data, image_file.filename)
    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data, pw_hash):
        return render_template("login.html")
    else:
        flash("user id already exists!")
        return render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_confirm", methods=['POST'])
def login_user():
    id_ = request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_, pw_hash):
        session['id']=id_   # Session에 id 정보 넣어줌. 어떤 페이지에서든 session으로 접근하여 id정보 참조 가능
        return redirect(url_for('view_list'))
    else:
        flash("Wrong ID or PW!")    # DB에 넘겨받은 ID&PW 매칭되는 정보가 없으면 flash msg 생성
        return render_template("login.html")
    
@app.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('view_list'))

@app.route("/view_detail/<name>/")
def view_item_detail(name):
    data = DB.get_item_byname(str(name))
    return render_template("detail.html", name=name, data=data)

@app.route("/reg_review_init/<name>/")
def reg_review_init(name):
    return render_template("reg_reviews.html", name=name)

@app.route("/reg_review", methods=['POST'])
def reg_review():
    data=request.form
    DB.reg_review(data)
    return redirect(url_for('view_review'))

@app.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=3# item count to display per row
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_reviews() #read the table
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template(
        "review.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1),
        total=item_counts
    )

@app.route("/view_review_detail/<name>/")
def view_review_detail_test(name):
    data = DB.get_review_byname(str(name))
    return render_template("review_detail.html", data=data)

@app.route("/show_heart/<name>/", methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'], name)
    return jsonify({'my_heart': my_heart})

@app.route("/like/<name>/", methods=['POST'])
def like(name):
    my_heart = DB.update_heart(session['id'], 'Y', name)
    return jsonify({'msg': '좋아요 완료!'})

@app.route("/unlike/<name>/", methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['id'], 'N', name)
    return jsonify({'msg': '좋아요 취소 완료!'})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
