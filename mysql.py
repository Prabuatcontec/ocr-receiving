import MySQLdb
import json

class Connection:
    def __init__(self):
        self.db=MySQLdb.connect(
            "crs-dev.rds.gocontec.com",
            "VulcanWebUser",
            "Vulcan123",
            "Automation"
            )
        self.db.autocommit(True)
        self.db.set_character_set('utf8mb4')
        self.cur=self.db.cursor()

    def getCustomer(self):
        self.cur.execute("select Id, Name from Customers") # This line performs query and returns json result rsundar/
        # return {'customers': [i[1] for i in self.cur.fetchall()]} # Fetches first column  
        rows = [x for x in self.cur]
        cols = [x[0] for x in self.cur.fetchall()]
        customers = []
        for row in rows:
            customer = {}
            for prop, val in zip(cols, row):
                customer[prop] = val
            customers.append(customer)
        return customers

    def getModels(self, customer_id):
        self.cur.execute("SELECT m.Id,m.Name FROM Automation.CustomerModels  cm LEFT JOIN Automation.Models m ON cm.ModelId = m.Id Where cm.CustomerId =%d" %int(customer_id)) # This line performs query and returns json result
        # return {'customers': [i[1] for i in self.cur.fetchall()]} # Fetches first column  
        rows = [x for x in self.cur]
        cols = [x[0] for x in self.cur.fetchall()]
        models = []
        for row in rows:
            model = {}
            for prop, val in zip(cols, row):
                model[prop] = val
            models.append(model)
        # Create a string representation of your array of models. 
        return models
