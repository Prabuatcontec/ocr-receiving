import MySQLdb
import json
from config import Config


class Connection:
    def __init__(self):
        self.db = MySQLdb.connect(
            Config.DATABASE_CONFIG['server'],
            Config.DATABASE_CONFIG['user'],
            Config.DATABASE_CONFIG['password'],
            Config.DATABASE_CONFIG['name']
        )
        self.db.autocommit(True)
        self.db.set_character_set('utf8mb4')
        self.cur = self.db.cursor()

    def getCustomer(self):
        self.cur.execute("select Id, Name from Customers")

        rows = [x for x in self.cur]
        cols = [x[0] for x in self.cur.fetchall()]
        customers = []
        for row in rows:
            customer = {}
            for prop, val in zip(cols, row):
                customer[prop] = val
            customers.append(customer)
        return customers

    def getModelList(self):
        self.cur.execute("SELECT id, Name FROM Automation.Models")

        rows = [x for x in self.cur]
        cols = [x[0] for x in self.cur.fetchall()]
        models1 = []

        for row in rows:
            model1 = {}
            v = 0
            for prop, val in zip(cols, row):
                v = v + 1
                model1[v] = val
                models1.append(model1)

        return models1

    def getModels(self, customer_id, model_id=""):
        self.cur.execute(
            "SELECT m.Name,m.Validation FROM Automation.CustomerModels  cm LEFT JOIN Automation.Models m ON cm.ModelId = m.Id Where cm.CustomerId =%d" % int(customer_id))

        rows = [x for x in self.cur]
        cols = [x[0] for x in self.cur.fetchall()]
        models = []

        for row in rows:
            model = {}
            v = 0
            for prop, val in zip(cols, row):
                v = v+1
                model[v] = val
            if(model_id!=""):
                if(model_id in str(model)):
                    models.append(model)
            else:
                models.append(model)

        return models

    def insertModel(self, model, serial):
        mycursor = self.cur

        sql = "INSERT INTO Automation.ScannedSerials (Serials, model) VALUES (%s, %s)"
        val = (serial, model)
        self.cur.execute(sql, val)
 
        return 1

    def insertmodeldata1(self, inpname, inpdata):

        sql1 = "INSERT INTO Automation.Models (Name, Validation) VALUES (%s, %s)"
        val1 = (inpname, inpdata)
        self.cur.execute(sql1, val1)

        return 1

    def insertcustmodel1(self, inpcust, inpmodel):

        sql1 = "INSERT INTO Automation.CustomerModels (CustomerId, ModelId) VALUES (%s, %s)"
        val1 = (inpcust, inpmodel)
        self.cur.execute(sql1, val1)

        return "Success"

