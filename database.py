import sqlite3
import logging
logger = logging.getLogger("email-app") # Need to fit module/app name
#logger.setLevel(logging.DEBUG)
# app.logger is a FlaskDebugLogger. Which apparently python's normal logger
# doesn't make a ancestor logger nicely from. Must manually set logging level.

db_path = "email.db"

class Email(object):
    tablename = "emails"
    column_spec = ("event_id integer PRIMARY KEY NOT NULL",
                   "email_subject text",
                   "email_content text",
                   "timestamp timestamp", # "YYYY-MM-DD HH:MM:SS" in UTC+8.
                   "sent integer"
                  )
    indexes = ["'sent_index' ON emails (timestamp, sent)"]
    columns = tuple(cspec.split()[0] for cspec in column_spec)
    accepted_input = ["event_id", "email_subject", "email_content", "timestamp"]
    
    def __init__(self, info=None):
        if info is None:
            info = [None for field in self.columns]
        for i, field in enumerate(self.columns):
            setattr(self, field, info[i])
    
    def set_sent(self, sent):
        with SqliteContext() as c:
            c.execute("UPDATE {} SET sent=? WHERE event_id=?".format(self.tablename),
                      (sent, self.event_id))
            self.sent = sent
            return True
    
    @classmethod
    def create(cls, request_form):
        new_email_params = []
        for field in cls.accepted_input:
            new_email_params.append(request_form[field])
        new_email_params.append(False) # sent field
        
        with SqliteContext() as c:
            c.execute("INSERT INTO {} VALUES (?,?,?,?,?)".format(cls.tablename),
                      new_email_params)
            return cls(new_email_params)
    
    @classmethod
    def get_by_id(cls, event_id):
        with SqliteContext() as c:
            c.execute("""SELECT * FROM {} WHERE
                         event_id = ?""".format(cls.tablename), [event_id])
            row = c.fetchone()
            if row is not None:
                return cls(row)
    
    @classmethod
    def get_for_send(cls):
        with SqliteContext() as c:
            c.execute("""SELECT * FROM {} WHERE
                         timestamp <= datetime('now') AND sent=0""".format(cls.tablename))
            return (cls(row) for row in c.fetchall())



class Recipient(object):
    tablename = "recipients"
    column_spec = ("recipient_email text PRIMARY KEY",)
    columns = tuple(cspec.split()[0] for cspec in column_spec)
    
    def __init__(self, info=None):
        if info is None:
            info = [None for field in self.columns]
        for i, field in enumerate(self.columns):
            setattr(self, field, info[i])
    
    @classmethod
    def create(cls, recipient_email):
        with SqliteContext() as c:
            c.execute("INSERT INTO {} VALUES (?)".format(cls.tablename),
                      [recipient_email])
            return cls([recipient_email])
    
    @classmethod
    def get_all(cls):
        with SqliteContext() as c:
            c.execute("SELECT * FROM {}".format(cls.tablename))
            return (cls(row) for row in c.fetchall())



class DBError(Exception):
    pass



# Private classes below. Don't use outside of this module.
class SqliteContext(object):
    def __enter__(self):
        self.conn = sqlite3.connect(db_path,
                        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        # Turn on foregin keys by default in case.
        self.conn.execute('pragma foreign_keys=ON')
        c = self.conn.cursor()
        return c
    
    def __exit__(self, exc_type, exc_value, tb):
        capture = True
        if isinstance(exc_value, Exception):
            import traceback
            logger.error("{}:{}".format(exc_type,exc_value))
            traceback.print_tb(tb)
            if isinstance(exc_value, sqlite3.DatabaseError):
                raise DBError(exc_value) # Wrap error
            else:
                capture = False # repropagate exception.
        else:
            self.conn.commit()
        self.conn.close()
        return capture



# Initialize the db
def db_init():
    conn = None
    try:
        conn = sqlite3.connect(db_path,
                   detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        # Don't need foreign keys, but it's always good to turn them on by default.
        conn.execute('pragma foreign_keys=ON')
        fk_pragma = conn.execute('pragma foreign_keys').fetchone()
        if fk_pragma is None or fk_pragma[0] != 1:
            logger.warning("WARNING: Foreign keys may not be enabled."
                           " pragma foreign_keys is {}".format(fk_pragma))
        conn.commit()
        
        # Create table if it doesn't exist.
        c = conn.cursor()
        for table in [Email, Recipient]:
            c.execute("CREATE TABLE IF NOT EXISTS {}({})"
                     .format(table.tablename,
                             ", ".join(table.column_spec)
                            )
                     )
            if hasattr(table, "indexes"):
                for index_spec in table.indexes:
                    c.execute("CREATE INDEX IF NOT EXISTS " + index_spec)
        
        # Initialise some recipients (debug?)
        c.execute("SELECT COUNT(*) FROM {}".format(Recipient.tablename))
        if c.fetchone()[0] == 0:
            Recipient.create("receiver1@example.com")
            Recipient.create("receiver2@example.com")
            Recipient.create("receiver3@example.com")
        
        # Debugging
        if logger.getEffectiveLevel() <= logging.DEBUG:
            all_items = conn.execute("SELECT name FROM sqlite_master").fetchall()
            logger.debug("All items in DB: " + str(all_items))
        conn.commit()
    finally:
        if conn is not None:
            conn.close()
