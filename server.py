import asyncpg
from app import App
import dotenv
import os
import asyncio
from quart import current_app, jsonify, request
app = App()

@app.route('/osu-user', methods=['GET'])
async def osu_user_fetch():
    user_id = request.args.get('id', type=int)

    db = await asyncpg.create_pool("postgres://postgres:3231@db:3231/skyetest")

    new = "SELECT * FROM osu_user WHERE user_id = $1"
    
    new_schema = await db.fetch(new, user_id)
    new_info = await db.fetch(new, user_id)

    data = {
        "Info": f"{new_schema}",
        "User_Specific":{
            "osu_username":f"{new_info[0]['osu_username']}",
            "user_id":f"{new_info[0]['user_id']}"
        }
    }

    return jsonify(data)


@app.route('/osu-user/<username>', methods=['PUT'])
async def osu_user_put(username):
    db = await asyncpg.create_pool("postgres://postgres:3231@db:3231/skyetest")
    
    user_id = request.args.get('id', default = None, type = int)

    query = """
        INSERT INTO osu_user (osu_username, user_id) VALUES($1, $2)
        ON CONFLICT(user_id) DO 
        UPDATE SET osu_username = excluded.osu_username
    """

    db_execute = await db.execute(query, username, user_id)

    new = "SELECT * FROM osu_user WHERE user_id = $1"
    new_info = await db.fetch(new, user_id)
    new_schema = dict(await db.fetch(new, user_id))

    data = {
        "new_schema": f"{new_schema}",
        "new_info":{"osu_username": f"{new_info[0]['osu_username']}", "user_id":f"{new_info[0]['user_id']}"},
        "output":f"{db_execute}",
        "status": 200
    }

    return jsonify(data)

@app.route('/osu-user/<int:id>', methods=['DELETE'])
async def osu_user_delete(id):
    db = await asyncpg.create_pool("postgres://postgres:3231@db:3231/skyetest")

    query = """
        DELETE FROM osu_user WHERE user_id = $1
    """

    a  =  await db.execute(query, id)

    return jsonify(a), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=3000, debug=True)