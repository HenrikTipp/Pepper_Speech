from datetime import datetime, timedelta
import pandas as pd



# The Employee_Register class holds all information about registered employees and known guests and provides functions to query this information.
class Employee_Register:

    #An Employee register is initialized by loading a csv file of known employees. 
    # self.storage contains the name of the csv file and self.register a dataframe loaded from storage.
    def __init__(self):
        self.storage = "employee_register.csv"
        self.register = self.load_from_storage()
        print(self.register)
        print(self.register.dtypes)


    #load_from_storage loads employee data from the given csv and ensures that the last iteraction is parsed as a satetime datatype.
    def load_from_storage(self):
        return pd.read_csv(self.storage, parse_dates=['last_interaction'])

    
    #On shutdown all employees are saved back to the csv file. This ensures that any changes to preferences are remembered and also saves the date of the last interaction.
    def store_register(self):
        print(self.register)
        print(self.register.dtypes)
        #Only employees are saved, not guests. This can only be manually entered into the csv, you cannot set your status to employee by talking to pepper.
        #"employee" in the dataframe is a boolean with True for employees and False for guests.
        employees_only = self.register[self.register["employee"]]
        employees_only.to_csv(self.storage, index = False)
        


    #add_employee takes a list
    def add_employee(self, new_employee):
        if not self.known_employee(new_employee['id']):
            self.register.loc[len(self.register)] = new_employee
        else:
            id = new_employee.pop('id')
            for key in new_employee.keys():
                print(key)
                print(new_employee.get(key))
                print(self.register.set_index('id').loc[id, key])
                self.register.loc[self.register.id == id, key] = new_employee.get(key)

    #Checks whether an ID is known or a new guest.    
    def known_employee(self, id):
        return id in self.register['id']


    def user_time(self, id):
        """Checks the time preferences and passed.
            Args:
                id: id of the person in question
            Return:
                time_passed: How much time since last interaction
                delta: How much time the user chose as a preference to need to pass for a new greeting.
        """
        now = datetime.utcnow()
        last_interaction = self.register.loc[self.register['id'] == id, 'last_interaction'].iloc[0]
        time_passed = now - last_interaction

        #Loads the time preference as a timedelta so it can be compared to the time_passed.
        delta = timedelta(hours = int(self.register.loc[self.register['id'] == id, 'time_preference'].iloc[0]))
        self.register.loc[self.register['id'] == id, 'last_interaction'] = now
        return time_passed, delta

    #Checks whether an employee has already customized their preferences. Regardless of the answer the system should not ask again so it is set to true after reading.
    def user_ask_preferences(self, id):
        already_modified = self.register.loc[self.register['id'] == id, 'customized_bool'].iloc[0]
        print(already_modified)
        self.register.loc[self.register.id == id, "customized_bool"] = True
        return already_modified

    #Get the name by ID.
    def get_name(self, id):
        return self.register.loc[self.register['id'] == id, 'name'].iloc[0]
    
    #Get the title by ID.
    def get_title(self, id):
        return self.register.loc[self.register['id'] == id, 'title'].iloc[0]
    
    #Get the language by ID.
    def get_language(self, id):
        return self.register.loc[self.register['id'] == id, 'language'].iloc[0]
    

def main():
    #main for testing purposes.
    Register = Employee_Register()




if __name__ == '__main__':
    main()