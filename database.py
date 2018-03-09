import sqlite3
import logging
logger = logging.getLogger("email-app") # Need to fit module/app name
# For some reason, I can't get subloggers to propagate, so use global logger

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
    
    def __init__(self, request_form):
        for field in self.accepted_input:
            setattr(self, field, request_form[field])
        self.sent = False
    
    def insert(self):
        """Tries to insert self. Returns None if successful, or the error that occured"""
        fields = []
        for col in self.columns:
            fields.append(getattr(self, col))
        try:
            with SqliteContext() as c:
                c.execute("INSERT INTO {} VALUES (?,?,?,?,?)".format(self.tablename), fields)
                return None
        except sqlite3.DatabaseError as e:
            return e

class Recipient(object):
    tablename = "recipients"
    column_spec = ("recipient text NOT NULL",)
    columns = tuple(cspec.split()[0] for cspec in column_spec)



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
        # Debugging
        if logger.getEffectiveLevel() <= logging.DEBUG:
            all_items = conn.execute("SELECT name FROM sqlite_master").fetchall()
            logger.debug(all_items)
        conn.commit()
    finally:
        if conn is not None:
            conn.close()