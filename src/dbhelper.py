import sqlite3

class DBHelper():
    def __init__(self, dbname="bot_db.sqlite", db_dir = "data/"):
        self.dbname = dbname
        self.conn = sqlite3.connect(db_dir + dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS arb (time datetime, zarusd real, luno_btc_arb real, ice3x_btc_arb real, ice3x_ltc_arb real, luno_btc_revarb real, ice3x_btc_revarb real, ice3x_ltc_revarb real)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_arb(self, time, zarusd, luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb, luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb):
        stmt = "INSERT INTO arb (time, zarusd, luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb, luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        args = (time, zarusd, luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb, luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text, owner):
        stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, owner):
        stmt = "SELECT description FROM items WHERE owner = (?)"
        args = (owner,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_latest_arb(self):
        stmt = "SELECT * FROM arb ORDER BY time DESC LIMIT 1"
        schema = self.conn.cursor().execute("PRAGMA table_info(arb)").fetchall()
        values = self.conn.execute(stmt).fetchall()
        return schema, values