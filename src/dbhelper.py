import sqlite3

class DBHelper():
    def __init__(self, dbname="bot_db.sqlite", db_dir = "data/"):
        self.dbname = dbname
        self.conn = sqlite3.connect(db_dir + dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS arb (time text, arb real, zarusd real)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_arb(self, time, arb, zarusd):
        stmt = "INSERT INTO arb (time, arb, zarusd) VALUES (?, ?, ?)"
        args = (time, arb, zarusd)
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