#The role of this repository is to communicate between our Branch class and the database
#We want to be able to save our branches, Kampala,Mukono and Kabale, in SQLite, retrieve them later and convert the retrived information back into Python Branch objects
import sqlite3

from domainExceptions import DuplicateBranchError
from branch_class import Branch

class BranchRepository:
    #Convert branch rows to domain objects and back The connection is injected, never created here, so a service can pass one connection (and thereforemone transaction) to several repositories. #

    def __init__(self,conn): #Receives and stored the database connection
        self._conn = conn #conn shortform for connection, we want all the methods in this repository to use the same datbase connection

    def add(self, branch):
        #Insert a branch. The caller owns commit/roolback.#
        try: 
            self._conn.execute("Insert into branch (branch_id, name)Values (?,?)", (branch.branch_id,branch.name),) #allows the repository to execute SQL commands using that connection.
        except sqlite3.IntegrityError as exc: 
            raise DuplicateBranchError(f"Branch already exists: {branch.name}") from exc #this supplies the actual values for the question marks
#We use question marks because we don't want to manually insert values into the SQL statement.
#IntegrityError can occur when a database rule is broken, such as trying to insert a duplicate primary key. 
    
    def get(self, branch_id):
        #Return a Branch, or None if there is no such id
        row = self._conn.execute("Select branch_id, name FROM branch WHERE branch_id = ?", (branch_id,),).fetchone()
        return self._to_domain(row) if row is not None eslse None
        
    def list_all(self):
        rows = self.conn.execute("SELECT branch_id, name FROM branch ORDERBY name").fetchall()
            return [self._to_domain(row) for row in rows]

    @staticmethod 
    def _to_domain(row):
        #the branch table has no is_main column, so it defaults to False.
        #Add that coulumn to the schema if the UI needs to show "Main"
        return Branch(branch_id = row["branch_id"],name=row["name"])